"use client";

import { useState, useEffect, useMemo } from "react";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";

const LINKEDIN_CHAR_LIMIT = 3000;
const MARKDOWN_RE = /\*\*.+?\*\*|(?<!\w)_.+?_(?!\w)|^#{1,6}\s+/m;

interface PostEditorProps {
  content: string;
  onSave: (content: string) => void;
  readOnly?: boolean;
}

export function PostEditor({ content, onSave, readOnly }: PostEditorProps) {
  const [editedContent, setEditedContent] = useState(content);

  // Sync when content prop changes (e.g. after async load or refetch)
  useEffect(() => {
    setEditedContent(content);
  }, [content]);

  const charCount = editedContent.length;
  const wordCount = editedContent.trim().split(/\s+/).filter(Boolean).length;

  const charColor =
    charCount > LINKEDIN_CHAR_LIMIT
      ? "text-red-600"
      : charCount >= 2500
        ? "text-yellow-600"
        : "text-green-600";

  const hasMarkdown = MARKDOWN_RE.test(editedContent);

  const seeMorePreview = useMemo(() => {
    if (!editedContent) return "";
    const firstNewline = editedContent.indexOf("\n");
    if (firstNewline === -1) return editedContent.slice(0, 140);
    return editedContent.slice(0, Math.min(firstNewline, 140));
  }, [editedContent]);

  return (
    <div className="space-y-3">
      <Textarea
        value={editedContent}
        onChange={(e) => setEditedContent(e.target.value)}
        rows={16}
        readOnly={readOnly}
        className="font-mono text-sm"
      />

      {/* See more preview */}
      {editedContent && (
        <div className="rounded border border-gray-200 bg-gray-50 px-3 py-2">
          <p className="text-xs text-gray-400 mb-1">LinkedIn &ldquo;See more&rdquo; preview</p>
          <p className="text-sm text-gray-700">
            {seeMorePreview}
            {editedContent.length > seeMorePreview.length && (
              <span className="text-blue-500 ml-1">...see more</span>
            )}
          </p>
        </div>
      )}

      {hasMarkdown && (
        <p className="text-xs text-amber-600">
          Markdown formatting detected — LinkedIn renders plain text only
        </p>
      )}

      <div className="flex items-center justify-between">
        <div className="text-xs text-gray-500 space-x-4">
          <span className={`font-medium ${charColor}`}>
            {charCount.toLocaleString()} / {LINKEDIN_CHAR_LIMIT.toLocaleString()}
          </span>
          <span>{wordCount} words</span>
        </div>
        {!readOnly && (
          <Button size="sm" onClick={() => onSave(editedContent)} disabled={editedContent === content}>
            Save Changes
          </Button>
        )}
      </div>
    </div>
  );
}
