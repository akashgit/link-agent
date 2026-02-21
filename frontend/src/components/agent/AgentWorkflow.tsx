"use client";

import { cn } from "@/utils/cn";
import { AGENT_STAGES } from "@/lib/constants";
import type { SSEEvent } from "@/lib/types";

interface AgentWorkflowProps {
  currentStage: string | null;
  completedStages: string[];
  events: SSEEvent[];
}

const stageConfig: Record<string, { label: string; activeLabel: string; icon: string }> = {
  research: { label: "Research", activeLabel: "Researching trends & angles...", icon: "🔍" },
  draft: { label: "Draft", activeLabel: "Writing your post...", icon: "✍️" },
  generate_image: { label: "Image", activeLabel: "Generating image...", icon: "🎨" },
  optimize: { label: "Optimize", activeLabel: "Optimizing for LinkedIn & fact-checking...", icon: "⚡" },
  proofread: { label: "Proofread", activeLabel: "Proofreading & tone check...", icon: "✅" },
  approve: { label: "Review", activeLabel: "Ready for your review", icon: "👁️" },
};

export function AgentWorkflow({ currentStage, completedStages, events }: AgentWorkflowProps) {
  // Find the description from the most recent event for the current or last completed stage
  const getStageDescription = (stage: string): string | null => {
    const stageEvent = [...events].reverse().find(
      (e) =>
        e.event === "node_complete" &&
        (e.data as Record<string, string>).node === stage &&
        (e.data as Record<string, string>).description,
    );
    if (stageEvent) {
      return (stageEvent.data as Record<string, string>).description;
    }
    return null;
  };

  const currentStageIndex = currentStage ? AGENT_STAGES.indexOf(currentStage as typeof AGENT_STAGES[number]) : -1;
  const progress = completedStages.length / AGENT_STAGES.length;

  return (
    <div className="space-y-3">
      {/* Overall progress bar */}
      <div className="flex items-center justify-between mb-1">
        <h4 className="text-sm font-medium text-gray-700">Pipeline Progress</h4>
        <span className="text-xs text-gray-400">{completedStages.length}/{AGENT_STAGES.length}</span>
      </div>
      <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
        <div
          className={cn(
            "h-full rounded-full transition-all duration-700 ease-out",
            progress >= 1 ? "bg-green-500" : "bg-blue-500"
          )}
          style={{ width: `${Math.max(progress * 100, currentStage ? ((currentStageIndex + 0.5) / AGENT_STAGES.length) * 100 : 0)}%` }}
        />
      </div>

      {/* Active stage indicator */}
      {currentStage && !completedStages.includes(currentStage) && stageConfig[currentStage] && (
        <div className="flex items-center gap-2 py-2 px-3 bg-blue-50 rounded-lg border border-blue-100">
          <span className="text-base">{stageConfig[currentStage].icon}</span>
          <div className="flex-1 min-w-0">
            <p className="text-sm font-medium text-blue-800">{stageConfig[currentStage].activeLabel}</p>
          </div>
          <div className="flex gap-0.5">
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "0ms" }} />
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "150ms" }} />
            <span className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce" style={{ animationDelay: "300ms" }} />
          </div>
        </div>
      )}

      {/* Stage list */}
      <div className="space-y-1">
        {AGENT_STAGES.map((stage) => {
          const isCompleted = completedStages.includes(stage);
          const isCurrent = stage === currentStage && !isCompleted;
          const config = stageConfig[stage];
          const description = isCompleted ? getStageDescription(stage) : null;

          return (
            <div
              key={stage}
              className={cn(
                "flex items-center gap-2 px-2 py-1 rounded text-sm transition-colors",
                isCompleted && "text-gray-700",
                isCurrent && "text-blue-700 font-medium",
                !isCompleted && !isCurrent && "text-gray-300"
              )}
            >
              {/* Status indicator */}
              <div className="w-5 text-center flex-shrink-0">
                {isCompleted ? (
                  <span className="text-green-500 text-xs">✓</span>
                ) : isCurrent ? (
                  <span className="inline-block w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
                ) : (
                  <span className="inline-block w-2 h-2 rounded-full bg-gray-200" />
                )}
              </div>

              {/* Label */}
              <span className="flex-shrink-0">{config.label}</span>

              {/* Description from completed event */}
              {description && (
                <span className="text-xs text-gray-400 truncate ml-1">— {description}</span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
