"use client";

import { useState } from "react";
import { PostCard } from "@/components/posts/PostCard";
import { Select } from "@/components/ui/Select";
import { Input } from "@/components/ui/Input";
import { Skeleton } from "@/components/ui/Skeleton";
import { usePosts } from "@/hooks/usePosts";
import { CONTENT_PILLARS, POST_FORMATS, POST_STATUSES } from "@/lib/constants";

export default function PostsPage() {
  const [status, setStatus] = useState("");
  const [pillar, setPillar] = useState("");
  const [format, setFormat] = useState("");
  const [search, setSearch] = useState("");

  const params: Record<string, string> = {};
  if (status) params.status = status;
  if (pillar) params.content_pillar = pillar;
  if (format) params.post_format = format;
  if (search) params.search = search;

  const { data: posts, isLoading } = usePosts(params);

  return (
    <div className="space-y-6">
      {/* Filters */}
      <div className="flex gap-4 flex-wrap">
        <div className="w-48">
          <Input placeholder="Search posts..." value={search} onChange={(e) => setSearch(e.target.value)} />
        </div>
        <div className="w-40">
          <Select options={POST_STATUSES.map((s) => ({ value: s.value, label: s.label }))} value={status} onChange={(e) => setStatus(e.target.value)} placeholder="All statuses" />
        </div>
        <div className="w-48">
          <Select options={CONTENT_PILLARS.map((p) => ({ value: p.value, label: p.label }))} value={pillar} onChange={(e) => setPillar(e.target.value)} placeholder="All pillars" />
        </div>
        <div className="w-40">
          <Select options={POST_FORMATS.map((f) => ({ value: f.value, label: f.label }))} value={format} onChange={(e) => setFormat(e.target.value)} placeholder="All formats" />
        </div>
      </div>

      {/* Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => <Skeleton key={i} className="h-40 w-full rounded-xl" />)}
        </div>
      ) : !posts || posts.length === 0 ? (
        <p className="text-gray-500 text-center py-12">No posts found. Create your first post to get started.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {posts.map((post) => (
            <PostCard key={post.id} post={post} />
          ))}
        </div>
      )}
    </div>
  );
}
