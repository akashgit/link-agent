"use client";

import { getFileUrl } from "@/lib/api";
import { stripMarkdown } from "@/utils/stripMarkdown";

interface PostPreviewProps {
  content: string;
  hashtags?: string[];
  imageUrl?: string;
  authorName?: string;
  authorTitle?: string;
  authorImageUrl?: string;
}

export function PostPreview({
  content,
  hashtags,
  imageUrl,
  authorName,
  authorTitle,
  authorImageUrl,
}: PostPreviewProps) {
  const resolvedImageUrl = imageUrl ? getFileUrl(imageUrl) : null;
  const cleanContent = stripMarkdown(content);

  const displayName = authorName || "Your Name";
  const displayTitle = authorTitle || "Your Title";
  const initials = displayName
    .split(" ")
    .map((w) => w[0])
    .join("")
    .slice(0, 2)
    .toUpperCase();

  return (
    <div className="bg-white rounded-xl border border-gray-200 shadow-sm max-w-[520px]">
      {/* LinkedIn header mockup */}
      <div className="flex items-center gap-3 p-4">
        {authorImageUrl ? (
          <img
            src={authorImageUrl}
            alt={displayName}
            className="h-12 w-12 rounded-full object-cover"
          />
        ) : (
          <div className="h-12 w-12 rounded-full bg-blue-600 flex items-center justify-center text-white font-semibold">
            {initials}
          </div>
        )}
        <div>
          <p className="font-semibold text-sm text-gray-900">{displayName}</p>
          <p className="text-xs text-gray-500">{displayTitle}</p>
          <p className="text-xs text-gray-400">Just now</p>
        </div>
      </div>

      {/* Content */}
      <div className="px-4 pb-3">
        <div className="text-sm text-gray-800 whitespace-pre-wrap leading-relaxed">
          {cleanContent}
        </div>
        {hashtags && hashtags.length > 0 && (
          <p className="text-sm text-blue-600 mt-3">{hashtags.join(" ")}</p>
        )}
      </div>

      {/* Image */}
      {resolvedImageUrl && (
        <div className="border-t border-gray-100">
          <img
            src={resolvedImageUrl}
            alt="Generated post image"
            className="w-full aspect-video object-cover"
            onError={(e) => {
              // Fall back to placeholder on error
              const target = e.target as HTMLImageElement;
              target.style.display = "none";
              target.parentElement!.innerHTML =
                '<div class="aspect-video bg-gray-100 flex items-center justify-center text-gray-400 text-sm">Image failed to load</div>';
            }}
          />
        </div>
      )}

      {/* Engagement bar mockup */}
      <div className="border-t border-gray-100 px-4 py-2 flex items-center justify-between text-xs text-gray-500">
        <span>Like</span>
        <span>Comment</span>
        <span>Repost</span>
        <span>Send</span>
      </div>
    </div>
  );
}
