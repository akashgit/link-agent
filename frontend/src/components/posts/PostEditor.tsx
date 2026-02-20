"use client";

import { useState } from "react";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";

interface PostEditorProps {
  content: string;
  onSave: (content: string) => void;
  readOnly?: boolean;
}

export function PostEditor({ content, onSave, readOnly }: PostEditorProps) {
  const [editedContent, setEditedContent] = useState(content);
  const charCount = editedContent.length;
  const wordCount = editedContent.trim().split(/\s+/).filter(Boolean).length;

  return (
    <div className="space-y-3">
      <Textarea
        value={editedContent}
        onChange={(e) => setEditedContent(e.target.value)}
        rows={16}
        readOnly={readOnly}
        className="font-mono text-sm"
      />
      <div className="flex items-center justify-between">
        <div className="text-xs text-gray-500 space-x-4">
          <span>{charCount} chars</span>
          <span>{wordCount} words</span>
          <span className={charCount >= 1300 && charCount <= 2000 ? "text-green-600 font-medium" : charCount > 2000 ? "text-red-600 font-medium" : ""}>
            {charCount >= 1300 && charCount <= 2000 ? "Optimal length" : charCount > 2000 ? "Too long" : "Could be longer"}
          </span>
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
