"use client";

import { formatRelative } from "@/utils/formatDate";
import { Badge } from "@/components/ui/Badge";
import type { Draft } from "@/lib/types";

const STAGE_LABELS: Record<string, string> = {
  draft: "Draft",
  optimize: "Optimized",
  proofread: "Proofread",
};

const STAGE_COLORS: Record<string, string> = {
  draft: "bg-blue-100 text-blue-700",
  optimize: "bg-purple-100 text-purple-700",
  proofread: "bg-green-100 text-green-700",
};

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
            <div className="flex items-center gap-2">
              <span className="font-medium">v{draft.version}</span>
              {draft.stage && (
                <Badge className={STAGE_COLORS[draft.stage] || "bg-gray-100 text-gray-600"}>
                  {STAGE_LABELS[draft.stage] || draft.stage}
                </Badge>
              )}
            </div>
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
