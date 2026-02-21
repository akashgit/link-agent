"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";
import { Card } from "@/components/ui/Card";
import { Badge } from "@/components/ui/Badge";

interface ApprovalPanelProps {
  onApprove: () => void;
  onRequestEdit: (feedback: string) => void;
  isLoading?: boolean;
  charCount?: number;
  warnings?: string[];
}

export function ApprovalPanel({
  onApprove,
  onRequestEdit,
  isLoading,
  charCount,
  warnings,
}: ApprovalPanelProps) {
  const [feedback, setFeedback] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);

  const charColor =
    charCount !== undefined && charCount > 3000
      ? "bg-red-100 text-red-700"
      : charCount !== undefined && charCount >= 2500
        ? "bg-yellow-100 text-yellow-700"
        : "bg-green-100 text-green-700";

  return (
    <Card className="border-amber-200 bg-amber-50">
      <h4 className="font-semibold text-amber-900 mb-2">Review Required</h4>
      <p className="text-sm text-amber-800 mb-4">
        The agent has finished drafting. Review the content and approve or request changes.
      </p>

      {charCount !== undefined && (
        <div className="mb-3">
          <Badge className={charColor}>
            {charCount.toLocaleString()} / 3,000 chars
          </Badge>
        </div>
      )}

      {warnings && warnings.length > 0 && (
        <div className="mb-4 rounded border border-amber-300 bg-amber-100 px-3 py-2">
          <p className="text-xs font-medium text-amber-800 mb-1">LinkedIn Warnings</p>
          <ul className="text-xs text-amber-700 space-y-1">
            {warnings.map((w, i) => (
              <li key={i}>• {w}</li>
            ))}
          </ul>
        </div>
      )}

      {showFeedback ? (
        <div className="space-y-3">
          <Textarea
            label="What changes would you like?"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="e.g. Make the hook more provocative, shorten the third paragraph..."
            rows={4}
          />
          <div className="flex gap-2">
            <Button
              variant="primary"
              onClick={() => onRequestEdit(feedback)}
              disabled={!feedback.trim()}
              loading={isLoading}
            >
              Submit Feedback
            </Button>
            <Button variant="ghost" onClick={() => setShowFeedback(false)}>
              Cancel
            </Button>
          </div>
        </div>
      ) : (
        <div className="flex gap-3">
          <Button onClick={onApprove} loading={isLoading}>
            Approve Post
          </Button>
          <Button variant="secondary" onClick={() => setShowFeedback(true)}>
            Request Changes
          </Button>
        </div>
      )}
    </Card>
  );
}
