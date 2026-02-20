"use client";

import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Textarea } from "@/components/ui/Textarea";
import { Card } from "@/components/ui/Card";

interface ApprovalPanelProps {
  onApprove: () => void;
  onRequestEdit: (feedback: string) => void;
  isLoading?: boolean;
}

export function ApprovalPanel({ onApprove, onRequestEdit, isLoading }: ApprovalPanelProps) {
  const [feedback, setFeedback] = useState("");
  const [showFeedback, setShowFeedback] = useState(false);

  return (
    <Card className="border-amber-200 bg-amber-50">
      <h4 className="font-semibold text-amber-900 mb-2">Review Required</h4>
      <p className="text-sm text-amber-800 mb-4">
        The agent has finished drafting. Review the content and approve or request changes.
      </p>

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
