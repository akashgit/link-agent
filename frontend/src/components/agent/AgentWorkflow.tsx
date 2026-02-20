"use client";

import { cn } from "@/utils/cn";
import { AGENT_STAGES } from "@/lib/constants";

interface AgentWorkflowProps {
  currentStage: string | null;
  completedStages: string[];
}

const stageLabels: Record<string, string> = {
  research: "Research",
  draft: "Draft",
  generate_image: "Image",
  optimize: "Optimize",
  proofread: "Proofread",
  approve: "Review",
};

export function AgentWorkflow({ currentStage, completedStages }: AgentWorkflowProps) {
  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700">Workflow Progress</h4>
      <div className="flex items-center gap-1">
        {AGENT_STAGES.map((stage, i) => {
          const isCompleted = completedStages.includes(stage);
          const isCurrent = stage === currentStage;
          return (
            <div key={stage} className="flex items-center gap-1 flex-1">
              <div
                className={cn(
                  "flex-1 h-2 rounded-full transition-colors",
                  isCompleted ? "bg-green-500" : isCurrent ? "bg-blue-500 animate-pulse" : "bg-gray-200"
                )}
              />
              {i < AGENT_STAGES.length - 1 && <div className="w-1" />}
            </div>
          );
        })}
      </div>
      <div className="flex justify-between text-[10px] text-gray-500">
        {AGENT_STAGES.map((stage) => (
          <span key={stage} className={cn(stage === currentStage && "text-blue-600 font-medium")}>
            {stageLabels[stage]}
          </span>
        ))}
      </div>
    </div>
  );
}
