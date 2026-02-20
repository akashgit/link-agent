"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchCalendar, createCalendarEntry, updateCalendarEntry, deleteCalendarEntry } from "@/lib/api";
import type { CalendarEntry } from "@/lib/types";

export function useCalendar(month?: number, year?: number) {
  return useQuery<CalendarEntry[]>({
    queryKey: ["calendar", month, year],
    queryFn: () => fetchCalendar(month && year ? { month, year } : undefined),
  });
}

export function useCreateCalendarEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: createCalendarEntry,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["calendar"] }),
  });
}

export function useUpdateCalendarEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ id, data }: { id: string; data: Record<string, unknown> }) =>
      updateCalendarEntry(id, data),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["calendar"] }),
  });
}

export function useDeleteCalendarEntry() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: deleteCalendarEntry,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["calendar"] }),
  });
}
