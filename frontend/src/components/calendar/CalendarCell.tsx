"use client";

import { Badge } from "@/components/ui/Badge";
import { PILLAR_COLORS } from "@/lib/constants";
import type { CalendarEntry } from "@/lib/types";

interface CalendarCellProps {
  day: number | null;
  date: string | null;
  entries: CalendarEntry[];
  onClick: () => void;
  onEntryClick: (entry: CalendarEntry) => void;
}

export function CalendarCell({ day, entries, onClick, onEntryClick }: CalendarCellProps) {
  if (day === null) {
    return <div className="bg-gray-50 min-h-[100px]" />;
  }

  return (
    <div className="bg-white min-h-[100px] p-1.5 cursor-pointer hover:bg-gray-50" onClick={onClick}>
      <span className="text-sm text-gray-600">{day}</span>
      <div className="mt-1 space-y-1">
        {entries.map((entry) => (
          <button
            key={entry.id}
            className="w-full text-left"
            onClick={(e) => { e.stopPropagation(); onEntryClick(entry); }}
          >
            <Badge className={`${PILLAR_COLORS[entry.content_pillar] || "bg-gray-100 text-gray-700"} text-[10px] w-full justify-start truncate`}>
              {entry.topic.length > 25 ? entry.topic.slice(0, 25) + "..." : entry.topic}
            </Badge>
          </button>
        ))}
      </div>
    </div>
  );
}
