"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Button } from "@/components/ui/Button";
import { Spinner } from "@/components/ui/Spinner";
import { CalendarGrid } from "@/components/calendar/CalendarGrid";
import { ScheduleModal } from "@/components/calendar/ScheduleModal";
import { useCalendar, useCreateCalendarEntry, useUpdateCalendarEntry, useDeleteCalendarEntry } from "@/hooks/useCalendar";
import { useToast } from "@/components/ui/Toast";
import type { CalendarEntry } from "@/lib/types";

const MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];

export default function CalendarPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [modalOpen, setModalOpen] = useState(false);
  const [selectedEntry, setSelectedEntry] = useState<CalendarEntry | null>(null);
  const [selectedDate, setSelectedDate] = useState<string>("");

  const { data: entries, isLoading } = useCalendar(month, year);
  const createEntry = useCreateCalendarEntry();
  const updateEntry = useUpdateCalendarEntry();
  const deleteEntry = useDeleteCalendarEntry();
  const { toast } = useToast();

  const prevMonth = () => {
    if (month === 1) { setMonth(12); setYear(year - 1); }
    else setMonth(month - 1);
  };

  const nextMonth = () => {
    if (month === 12) { setMonth(1); setYear(year + 1); }
    else setMonth(month + 1);
  };

  const handleDayClick = (date: string) => {
    setSelectedEntry(null);
    setSelectedDate(date);
    setModalOpen(true);
  };

  const handleEntryClick = (entry: CalendarEntry) => {
    setSelectedEntry(entry);
    setSelectedDate("");
    setModalOpen(true);
  };

  const handleSave = async (data: {
    scheduled_date: string;
    content_pillar: string;
    post_format: string;
    topic: string;
    notes?: string;
  }) => {
    try {
      if (selectedEntry) {
        await updateEntry.mutateAsync({ id: selectedEntry.id, data });
        toast("Entry updated", "success");
      } else {
        await createEntry.mutateAsync(data);
        toast("Entry created", "success");
      }
    } catch {
      toast("Failed to save entry", "error");
    }
  };

  const handleDelete = async () => {
    if (!selectedEntry) return;
    try {
      await deleteEntry.mutateAsync(selectedEntry.id);
      toast("Entry deleted", "success");
      setModalOpen(false);
    } catch {
      toast("Failed to delete entry", "error");
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="sm" onClick={prevMonth}>&larr;</Button>
          <h3 className="text-lg font-semibold">{MONTH_NAMES[month - 1]} {year}</h3>
          <Button variant="ghost" size="sm" onClick={nextMonth}>&rarr;</Button>
        </div>
        <Button size="sm" onClick={() => { setSelectedEntry(null); setSelectedDate(""); setModalOpen(true); }}>
          Add Entry
        </Button>
      </div>

      {isLoading ? (
        <div className="flex justify-center py-20"><Spinner size="lg" /></div>
      ) : (
        <CalendarGrid
          year={year}
          month={month}
          entries={entries || []}
          onDayClick={handleDayClick}
          onEntryClick={handleEntryClick}
        />
      )}

      <ScheduleModal
        open={modalOpen}
        onClose={() => setModalOpen(false)}
        onSave={handleSave}
        onDelete={selectedEntry ? handleDelete : undefined}
        entry={selectedEntry}
        defaultDate={selectedDate}
      />
    </div>
  );
}
