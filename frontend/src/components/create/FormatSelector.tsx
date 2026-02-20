"use client";

import { cn } from "@/utils/cn";
import { POST_FORMATS } from "@/lib/constants";

interface FormatSelectorProps {
  selected: string;
  onChange: (value: string) => void;
}

export function FormatSelector({ selected, onChange }: FormatSelectorProps) {
  return (
    <div className="space-y-3">
      <label className="block text-sm font-medium text-gray-700">Post Format</label>
      <div className="grid grid-cols-1 gap-2">
        {POST_FORMATS.map((format) => (
          <button
            key={format.value}
            type="button"
            onClick={() => onChange(format.value)}
            className={cn(
              "px-4 py-3 rounded-lg border-2 text-left transition-colors",
              selected === format.value
                ? "border-blue-500 bg-blue-50"
                : "border-gray-200 hover:border-gray-300"
            )}
          >
            <div className="font-medium text-sm text-gray-900">{format.label}</div>
            <div className="text-xs text-gray-500 mt-0.5">{format.description}</div>
          </button>
        ))}
      </div>
    </div>
  );
}
