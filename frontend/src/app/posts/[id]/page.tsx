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
import {
  resumeAgent,
  fetchPostMedia,
  deletePost,
  pushToTypefully,
  scheduleOnTypefully,
  getTypefullyStatus,
} from "@/lib/api";
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

  // Typefully state
  const [typefullyLoading, setTypefullyLoading] = useState(false);
  const [typefullyStatus, setTypefullyStatus] = useState<string | null>(null);
  const [scheduleDate, setScheduleDate] = useState("");
  const [showScheduler, setShowScheduler] = useState(false);

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

  // Extract image URL from node_complete events (generate_image or optimize)
  const generatedImageUrl = useMemo(() => {
    // Check optimize node first (may override with retrieved image)
    const optimizeEvent = events.find(
      (e) =>
        e.event === "node_complete" &&
        (e.data as Record<string, string>).node === "optimize" &&
        (e.data as Record<string, string>).image_url,
    );
    if (optimizeEvent) {
      return (optimizeEvent.data as Record<string, string>).image_url;
    }
    // Fall back to generate_image node
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

  // Extract draft content from SSE events as soon as draft node completes
  const liveDraftContent = useMemo(() => {
    const draftEvent = [...events].reverse().find(
      (e) =>
        e.event === "node_complete" &&
        (e.data as Record<string, string>).node === "draft" &&
        (e.data as Record<string, string>).draft_content,
    );
    if (draftEvent) {
      return (draftEvent.data as Record<string, string>).draft_content;
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
  const interruptCharCount = interruptData?.linkedin_char_count as number | undefined;
  const interruptWarnings = interruptData?.linkedin_warnings as string[] | undefined;

  const displayContent =
    selectedDraft?.content ||
    interruptContent ||
    liveDraftContent ||
    post?.final_content ||
    post?.drafts?.[0]?.content ||
    "";

  const displayHashtags =
    interruptHashtags ||
    selectedDraft?.hashtags?.split(",").map((h) => h.trim()) ||
    [];

  // Use interrupt image URL, SSE event URL, or fall back to first image in media list
  const mediaImageUrl = useMemo(() => {
    const imageAsset = mediaAssets.find((a: MediaAsset) => a.content_type.startsWith("image/"));
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

  const handlePushToTypefully = async () => {
    if (!post) return;
    setTypefullyLoading(true);
    try {
      await pushToTypefully(post.id);
      toast("Draft created in Typefully", "success");
      refetch();
    } catch {
      toast("Failed to push to Typefully", "error");
    } finally {
      setTypefullyLoading(false);
    }
  };

  const handleScheduleTypefully = async () => {
    if (!post || !scheduleDate) return;
    setTypefullyLoading(true);
    try {
      const publishAt = new Date(scheduleDate).toISOString();
      await scheduleOnTypefully(post.id, publishAt);
      toast("Post scheduled in Typefully", "success");
      setShowScheduler(false);
      refetch();
    } catch {
      toast("Failed to schedule", "error");
    } finally {
      setTypefullyLoading(false);
    }
  };

  const handleRefreshTypefullyStatus = async () => {
    if (!post) return;
    setTypefullyLoading(true);
    try {
      const result = await getTypefullyStatus(post.id);
      setTypefullyStatus(result.status);
    } catch {
      toast("Failed to fetch Typefully status", "error");
    } finally {
      setTypefullyLoading(false);
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
              <AgentWorkflow currentStage={currentNode} completedStages={completedStages} events={events} />
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
            charCount={interruptCharCount}
            warnings={interruptWarnings}
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

        {/* Typefully publish section */}
        {post.status === "approved" && (
          <Card>
            <h4 className="font-semibold text-sm mb-3">Publish to LinkedIn</h4>

            {!post.typefully_draft_id ? (
              <div className="space-y-3">
                <Button
                  size="sm"
                  onClick={handlePushToTypefully}
                  loading={typefullyLoading}
                  className="w-full"
                >
                  Push to Typefully
                </Button>

                <div>
                  {!showScheduler ? (
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setShowScheduler(true)}
                      className="w-full"
                    >
                      Schedule
                    </Button>
                  ) : (
                    <div className="space-y-2">
                      <input
                        type="datetime-local"
                        value={scheduleDate}
                        onChange={(e) => setScheduleDate(e.target.value)}
                        className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
                      />
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          onClick={handleScheduleTypefully}
                          disabled={!scheduleDate}
                          loading={typefullyLoading}
                        >
                          Confirm
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          onClick={() => setShowScheduler(false)}
                        >
                          Cancel
                        </Button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <span className="text-xs text-gray-500">Typefully Draft</span>
                  <Badge className="bg-blue-100 text-blue-700">
                    {typefullyStatus || "draft"}
                  </Badge>
                </div>

                {!showScheduler ? (
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="secondary"
                      onClick={() => setShowScheduler(true)}
                    >
                      Schedule
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={handleRefreshTypefullyStatus}
                      loading={typefullyLoading}
                    >
                      Refresh
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-2">
                    <input
                      type="datetime-local"
                      value={scheduleDate}
                      onChange={(e) => setScheduleDate(e.target.value)}
                      className="w-full rounded border border-gray-300 px-2 py-1 text-sm"
                    />
                    <div className="flex gap-2">
                      <Button
                        size="sm"
                        onClick={handleScheduleTypefully}
                        disabled={!scheduleDate}
                        loading={typefullyLoading}
                      >
                        Confirm
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        onClick={() => setShowScheduler(false)}
                      >
                        Cancel
                      </Button>
                    </div>
                  </div>
                )}
              </div>
            )}
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
