"use client";

import { formatRelative } from "@/utils/formatDate";
import type { Draft } from "@/lib/types";

interface PostVersionHistoryProps {
  drafts: Draft[];
  onSelect: (draft: Draft) => void;
  selectedId?: string;
}

export function PostVersionHistory({ drafts, onSelect, selectedId }: PostVersionHistoryProps) {
  if (drafts.length === 0) {
    return <p className="text-sm text-gray-500">No versions yet.</p>;
  }

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700">Version History</h4>
      {drafts.map((draft) => (
        <button
          key={draft.id}
          onClick={() => onSelect(draft)}
          className={`w-full text-left px-3 py-2 rounded-lg text-sm border transition-colors ${
            selectedId === draft.id ? "border-blue-500 bg-blue-50" : "border-gray-200 hover:bg-gray-50"
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="font-medium">v{draft.version}</span>
            <span className="text-xs text-gray-500">{formatRelative(draft.created_at)}</span>
          </div>
          {draft.feedback && (
            <p className="text-xs text-gray-500 mt-1 truncate">Feedback: {draft.feedback}</p>
          )}
        </button>
      ))}
    </div>
  );
}
