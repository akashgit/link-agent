"use client";

import { cn } from "@/utils/cn";
import { CONTENT_PILLARS, PILLAR_COLORS } from "@/lib/constants";

interface PillarSelectorProps {
  selected: string;
  onChange: (value: string) => void;
}

export function PillarSelector({ selected, onChange }: PillarSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">Content Pillar</label>
      <div className="grid grid-cols-1 gap-2">
        {CONTENT_PILLARS.map((pillar) => (
          <button
            key={pillar.value}
            type="button"
            onClick={() => onChange(pillar.value)}
            className={cn(
              "px-4 py-3 rounded-lg border-2 text-left text-sm font-medium transition-colors",
              selected === pillar.value
                ? "border-blue-500 bg-blue-50 text-blue-900"
                : "border-gray-200 hover:border-gray-300 text-gray-700"
            )}
          >
            <span className={cn("inline-block px-2 py-0.5 rounded text-xs mr-2", PILLAR_COLORS[pillar.value])}>
              {pillar.value.replace("_", " ")}
            </span>
            {pillar.label}
          </button>
        ))}
      </div>
    </div>
  );
}
