"use client";

import { useState, useEffect, useMemo, use } from "react";
import { useRouter } from "next/navigation";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Badge } from "@/components/ui/Badge";
import { Spinner } from "@/components/ui/Spinner";
import { PostEditor } from "@/components/posts/PostEditor";
import { PostPreview } from "@/components/posts/PostPreview";
import { PostVersionHistory } from "@/components/posts/PostVersionHistory";
import { PostStatusBadge } from "@/components/posts/PostStatusBadge";
import { PostMedia } from "@/components/posts/PostMedia";
import { AgentWorkflow } from "@/components/agent/AgentWorkflow";
import { AgentStreamLog } from "@/components/agent/AgentStreamLog";
import { ApprovalPanel } from "@/components/agent/ApprovalPanel";
import { usePost } from "@/hooks/usePosts";
import { useUpdatePost } from "@/hooks/usePosts";
import { useSSE } from "@/hooks/useSSE";
import { useQuery } from "@tanstack/react-query";
import { resumeAgent, fetchPostMedia, deletePost } from "@/lib/api";
import { useToast } from "@/components/ui/Toast";
import { PILLAR_COLORS } from "@/lib/constants";
import type { Draft, MediaAsset } from "@/lib/types";

export default function PostDetailPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();
  const { toast } = useToast();
  const { data: post, isLoading, refetch } = usePost(id);
  const updatePost = useUpdatePost();

  const [selectedDraft, setSelectedDraft] = useState<Draft | null>(null);
  const [resuming, setResuming] = useState(false);

  const { data: mediaAssets = [] } = useQuery({
    queryKey: ["post-media", id],
    queryFn: () => fetchPostMedia(id),
  });

  const {
    events,
    currentNode,
    isInterrupted,
    interruptData,
    isComplete,
    error: sseError,
  } = useSSE({
    threadId: post?.thread_id || null,
  });

  const completedStages = events
    .filter((e) => e.event === "node_complete")
    .map((e) => (e.data as Record<string, string>).node || (e.data as Record<string, string>).stage);

  // Extract image URL from node_complete events for generate_image
  const generatedImageUrl = useMemo(() => {
    const imageEvent = events.find(
      (e) =>
        e.event === "node_complete" &&
        (e.data as Record<string, string>).node === "generate_image" &&
        (e.data as Record<string, string>).image_url,
    );
    if (imageEvent) {
      return (imageEvent.data as Record<string, string>).image_url;
    }
    return undefined;
  }, [events]);

  // Refetch post data when agent pauses (interrupt) or completes
  useEffect(() => {
    if (isComplete || isInterrupted) refetch();
  }, [isComplete, isInterrupted, refetch]);

  // Get content from interrupt data (proofread_content), drafts, or final_content
  const interruptContent = interruptData?.proofread_content as string | undefined;
  const interruptHashtags = interruptData?.suggested_hashtags as string[] | undefined;
  const interruptImageUrl = interruptData?.image_url as string | undefined;

  const displayContent =
    selectedDraft?.content ||
    interruptContent ||
    post?.final_content ||
    post?.drafts?.[0]?.content ||
    "";

  const displayHashtags =
    interruptHashtags ||
    selectedDraft?.hashtags?.split(",").map((h) => h.trim()) ||
    [];

  // Use interrupt image URL, SSE event URL, or fall back to first image in media list
  const mediaImageUrl = useMemo(() => {
    const imageAsset = mediaAssets.find((a) => a.content_type.startsWith("image/"));
    if (imageAsset) {
      return `/api/uploads/file/${imageAsset.file_path.split("/").pop()}`;
    }
    return undefined;
  }, [mediaAssets]);

  const displayImageUrl = interruptImageUrl || generatedImageUrl || mediaImageUrl;

  const handleApprove = async () => {
    if (!post?.thread_id) return;
    setResuming(true);
    try {
      await resumeAgent(post.thread_id, { status: "approved" });
      toast("Post approved!", "success");
      refetch();
    } catch {
      toast("Failed to approve", "error");
    } finally {
      setResuming(false);
    }
  };

  const handleRequestEdit = async (feedback: string) => {
    if (!post?.thread_id) return;
    setResuming(true);
    try {
      await resumeAgent(post.thread_id, { status: "edit_requested", feedback });
      toast("Edit requested, agent is revising...", "info");
      refetch();
    } catch {
      toast("Failed to submit feedback", "error");
    } finally {
      setResuming(false);
    }
  };

  const handleSaveContent = async (content: string) => {
    if (!post) return;
    await updatePost.mutateAsync({ id: post.id, data: { final_content: content } });
    toast("Content saved", "success");
  };

  const [confirmDelete, setConfirmDelete] = useState(false);

  const handleDelete = async () => {
    if (!post) return;
    try {
      await deletePost(post.id);
      toast("Post deleted", "success");
      router.push("/posts");
    } catch {
      toast("Failed to delete post", "error");
    }
  };

  if (isLoading) {
    return <div className="flex justify-center py-20"><Spinner size="lg" /></div>;
  }

  if (!post) {
    return <p className="text-center text-gray-500 py-20">Post not found.</p>;
  }

  return (
    <div className="grid grid-cols-12 gap-6">
      {/* Left column: Editor */}
      <div className="col-span-5 space-y-4">
        <div className="flex items-center gap-3">
          <h2 className="text-lg font-semibold truncate">{post.title}</h2>
          <PostStatusBadge status={post.status} />
          <div className="ml-auto">
            {confirmDelete ? (
              <div className="flex items-center gap-2">
                <span className="text-xs text-red-600">Delete this post?</span>
                <Button size="sm" variant="danger" onClick={handleDelete}>Yes</Button>
                <Button size="sm" variant="ghost" onClick={() => setConfirmDelete(false)}>No</Button>
              </div>
            ) : (
              <Button size="sm" variant="ghost" onClick={() => setConfirmDelete(true)}>
                Delete
              </Button>
            )}
          </div>
        </div>
        <div className="flex gap-2">
          <Badge className={PILLAR_COLORS[post.content_pillar]}>{post.content_pillar.replace("_", " ")}</Badge>
          <Badge className="bg-gray-100 text-gray-600">{post.post_format.replace("_", " ")}</Badge>
        </div>

        <PostEditor
          content={displayContent}
          onSave={handleSaveContent}
          readOnly={post.status === "drafting"}
        />

        {post.drafts && post.drafts.length > 0 && (
          <Card>
            <PostVersionHistory
              drafts={post.drafts}
              selectedId={selectedDraft?.id}
              onSelect={setSelectedDraft}
            />
          </Card>
        )}
      </div>

      {/* Middle column: Preview + Media */}
      <div className="col-span-4 space-y-4">
        <h3 className="text-sm font-medium text-gray-500 mb-3">LinkedIn Preview</h3>
        <PostPreview
          content={displayContent}
          hashtags={displayHashtags}
          imageUrl={displayImageUrl}
        />
        <PostMedia postId={id} />
      </div>

      {/* Right column: Workflow */}
      <div className="col-span-3 space-y-4">
        {post.thread_id && (
          <>
            <Card>
              <AgentWorkflow currentStage={currentNode} completedStages={completedStages} />
            </Card>
            <Card>
              <AgentStreamLog events={events} />
            </Card>
          </>
        )}

        {sseError && (
          <Card className="border-red-200 bg-red-50">
            <p className="text-sm text-red-700">{sseError}</p>
          </Card>
        )}

        {isInterrupted && (
          <ApprovalPanel
            onApprove={handleApprove}
            onRequestEdit={handleRequestEdit}
            isLoading={resuming}
          />
        )}

        {isComplete && (
          <Card className="border-green-200 bg-green-50">
            <p className="text-sm text-green-800 font-medium">Post approved and finalized.</p>
            <Button variant="ghost" size="sm" className="mt-2" onClick={() => router.push("/posts")}>
              Back to Posts
            </Button>
          </Card>
        )}

        {!post.thread_id && post.status === "idea" && (
          <Card>
            <p className="text-sm text-gray-500">This post hasn&apos;t been processed by the agent yet. Go to Create Post to generate content.</p>
          </Card>
        )}
      </div>
    </div>
  );
}
