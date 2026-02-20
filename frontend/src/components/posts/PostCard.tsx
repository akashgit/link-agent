"use client";

import Link from "next/link";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";
import { PILLAR_COLORS, STATUS_COLORS } from "@/lib/constants";
import { formatRelative } from "@/utils/formatDate";
import type { Post } from "@/lib/types";

export function PostCard({ post }: { post: Post }) {
  return (
    <Link href={`/posts/${post.id}`}>
      <Card className="hover:shadow-md transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-3">
          <h3 className="font-semibold text-gray-900 line-clamp-2">{post.title}</h3>
          <Badge className={STATUS_COLORS[post.status] || "bg-gray-100 text-gray-700"}>
            {post.status.replace("_", " ")}
          </Badge>
        </div>
        <div className="flex items-center gap-2 mb-3">
          <Badge className={PILLAR_COLORS[post.content_pillar] || "bg-gray-100 text-gray-700"}>
            {post.content_pillar.replace("_", " ")}
          </Badge>
          <Badge className="bg-gray-100 text-gray-600">
            {post.post_format.replace("_", " ")}
          </Badge>
        </div>
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>{formatRelative(post.created_at)}</span>
          {post.revision_count > 0 && <span>v{post.revision_count + 1}</span>}
        </div>
      </Card>
    </Link>
  );
}
