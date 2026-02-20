"use client";

import { useMemo } from "react";
import { CalendarCell } from "./CalendarCell";
import type { CalendarEntry } from "@/lib/types";

interface CalendarGridProps {
  year: number;
  month: number;
  entries: CalendarEntry[];
  onDayClick: (date: string) => void;
  onEntryClick: (entry: CalendarEntry) => void;
}

export function CalendarGrid({ year, month, entries, onDayClick, onEntryClick }: CalendarGridProps) {
  const days = useMemo(() => {
    const firstDay = new Date(year, month - 1, 1);
    const lastDay = new Date(year, month, 0);
    const startPad = firstDay.getDay();
    const totalDays = lastDay.getDate();

    const cells: { date: string | null; day: number | null }[] = [];
    for (let i = 0; i < startPad; i++) cells.push({ date: null, day: null });
    for (let d = 1; d <= totalDays; d++) {
      const dateStr = `${year}-${String(month).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
      cells.push({ date: dateStr, day: d });
    }
    return cells;
  }, [year, month]);

  const entriesByDate = useMemo(() => {
    const map: Record<string, CalendarEntry[]> = {};
    entries.forEach((e) => {
      const date = e.scheduled_date.split("T")[0];
      if (!map[date]) map[date] = [];
      map[date].push(e);
    });
    return map;
  }, [entries]);

  return (
    <div>
      <div className="grid grid-cols-7 gap-px bg-gray-200 rounded-t-lg overflow-hidden">
        {["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"].map((d) => (
          <div key={d} className="bg-gray-50 py-2 text-center text-xs font-medium text-gray-500">{d}</div>
        ))}
      </div>
      <div className="grid grid-cols-7 gap-px bg-gray-200 rounded-b-lg overflow-hidden">
        {days.map((cell, i) => (
          <CalendarCell
            key={i}
            day={cell.day}
            date={cell.date}
            entries={cell.date ? entriesByDate[cell.date] || [] : []}
            onClick={() => cell.date && onDayClick(cell.date)}
            onEntryClick={onEntryClick}
          />
        ))}
      </div>
    </div>
  );
}
