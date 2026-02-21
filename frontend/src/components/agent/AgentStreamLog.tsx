"use client";

import { useRef, useEffect } from "react";
import { cn } from "@/utils/cn";
import type { SSEEvent } from "@/lib/types";

interface AgentStreamLogProps {
  events: SSEEvent[];
}

const nodeLabels: Record<string, string> = {
  research: "Research",
  draft: "Draft",
  generate_image: "Image Generation",
  optimize: "Optimization",
  proofread: "Proofreading",
  approve: "Review",
};

export function AgentStreamLog({ events }: AgentStreamLogProps) {
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [events]);

  if (events.length === 0) {
    return (
      <div className="text-center py-4">
        <p className="text-sm text-gray-400 italic">Waiting for agent to start...</p>
      </div>
    );
  }

  return (
    <div className="space-y-2">
      <h4 className="text-sm font-medium text-gray-700">Activity Log</h4>
      <div ref={scrollRef} className="space-y-1.5 max-h-64 overflow-y-auto">
        {events.map((evt, i) => {
          const data = evt.data as Record<string, unknown>;
          const nodeName = (data.node || data.stage || "") as string;
          const label = nodeLabels[nodeName] || nodeName;
          const description = (data.description || "") as string;
          const details = (data.details || []) as string[];

          if (evt.event === "node_complete") {
            return (
              <div key={i} className="flex items-start gap-2 text-sm py-0.5">
                <span className="text-green-500 mt-0.5 flex-shrink-0">●</span>
                <div className="min-w-0">
                  <span className="font-medium text-gray-700">{label}</span>
                  {description && (
                    <span className="text-gray-500 ml-1.5">{description}</span>
                  )}
                  {details.length > 0 && (
                    <ul className="mt-0.5 text-xs text-gray-400">
                      {details.slice(0, 3).map((d, j) => (
                        <li key={j} className="truncate">→ {d}</li>
                      ))}
                    </ul>
                  )}
                </div>
              </div>
            );
          }

          if (evt.event === "interrupt") {
            return (
              <div key={i} className="flex items-start gap-2 text-sm py-0.5">
                <span className="text-amber-500 mt-0.5 flex-shrink-0">●</span>
                <span className="text-amber-700 font-medium">Awaiting your review</span>
              </div>
            );
          }

          if (evt.event === "complete") {
            return (
              <div key={i} className="flex items-start gap-2 text-sm py-0.5">
                <span className="text-blue-500 mt-0.5 flex-shrink-0">●</span>
                <span className="text-blue-700 font-medium">Post approved</span>
              </div>
            );
          }

          if (evt.event === "error") {
            return (
              <div key={i} className="flex items-start gap-2 text-sm py-0.5">
                <span className="text-red-500 mt-0.5 flex-shrink-0">●</span>
                <span className="text-red-700">{(data.error || "Unknown error") as string}</span>
              </div>
            );
          }

          if (evt.event === "paused") {
            return (
              <div key={i} className="flex items-start gap-2 text-sm py-0.5">
                <span className="text-amber-500 mt-0.5 flex-shrink-0">●</span>
                <span className="text-amber-700">Pipeline paused</span>
              </div>
            );
          }

          return null;
        })}
      </div>
    </div>
  );
}
