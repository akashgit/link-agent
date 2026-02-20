"use client";

import { cn } from "@/utils/cn";
import type { SSEEvent } from "@/lib/types";

interface AgentStreamLogProps {
  events: SSEEvent[];
}

const eventIcons: Record<string, string> = {
  node_complete: "text-green-500",
  interrupt: "text-amber-500",
  complete: "text-blue-500",
  error: "text-red-500",
  paused: "text-amber-500",
};

export function AgentStreamLog({ events }: AgentStreamLogProps) {
  if (events.length === 0) {
    return <p className="text-sm text-gray-400 italic">Waiting for agent to start...</p>;
  }

  return (
    <div className="space-y-2 max-h-64 overflow-y-auto">
      <h4 className="text-sm font-medium text-gray-700">Agent Log</h4>
      {events.map((evt, i) => (
        <div key={i} className="flex items-start gap-2 text-sm">
          <div className={cn("mt-1 h-2 w-2 rounded-full flex-shrink-0", eventIcons[evt.event] || "bg-gray-300")} style={{ backgroundColor: "currentColor" }} />
          <div>
            <span className="font-medium text-gray-700">{evt.event}</span>
            {evt.data && (
              <span className="text-gray-500 ml-2">
                {(evt.data as Record<string, unknown>).node as string || (evt.data as Record<string, unknown>).stage as string || (evt.data as Record<string, unknown>).status as string || ""}
              </span>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
