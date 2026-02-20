"use client";

import { useState, useEffect } from "react";
import { Modal } from "@/components/ui/Modal";
import { Input } from "@/components/ui/Input";
import { Select } from "@/components/ui/Select";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { CONTENT_PILLARS, POST_FORMATS } from "@/lib/constants";
import type { CalendarEntry } from "@/lib/types";

interface ScheduleModalProps {
  open: boolean;
  onClose: () => void;
  onSave: (data: {
    scheduled_date: string;
    content_pillar: string;
    post_format: string;
    topic: string;
    notes?: string;
  }) => void;
  onDelete?: () => void;
  entry?: CalendarEntry | null;
  defaultDate?: string;
}

export function ScheduleModal({ open, onClose, onSave, onDelete, entry, defaultDate }: ScheduleModalProps) {
  const [date, setDate] = useState(defaultDate || "");
  const [pillar, setPillar] = useState("");
  const [format, setFormat] = useState("");
  const [topic, setTopic] = useState("");
  const [notes, setNotes] = useState("");

  useEffect(() => {
    if (entry) {
      setDate(entry.scheduled_date.split("T")[0]);
      setPillar(entry.content_pillar);
      setFormat(entry.post_format);
      setTopic(entry.topic);
      setNotes(entry.notes || "");
    } else {
      setDate(defaultDate || "");
      setPillar("");
      setFormat("");
      setTopic("");
      setNotes("");
    }
  }, [entry, defaultDate]);

  const handleSubmit = () => {
    onSave({
      scheduled_date: date,
      content_pillar: pillar,
      post_format: format,
      topic,
      notes: notes || undefined,
    });
    onClose();
  };

  return (
    <Modal open={open} onClose={onClose} title={entry ? "Edit Calendar Entry" : "New Calendar Entry"}>
      <div className="space-y-4">
        <Input label="Date" type="date" value={date} onChange={(e) => setDate(e.target.value)} />
        <Select label="Content Pillar" options={CONTENT_PILLARS.map((p) => ({ value: p.value, label: p.label }))} value={pillar} onChange={(e) => setPillar(e.target.value)} placeholder="Select pillar" />
        <Select label="Post Format" options={POST_FORMATS.map((f) => ({ value: f.value, label: f.label }))} value={format} onChange={(e) => setFormat(e.target.value)} placeholder="Select format" />
        <Input label="Topic" value={topic} onChange={(e) => setTopic(e.target.value)} placeholder="Post topic or title" />
        <Textarea label="Notes (optional)" value={notes} onChange={(e) => setNotes(e.target.value)} rows={3} />
        <div className="flex justify-between pt-2">
          {entry && onDelete ? (
            <Button variant="danger" size="sm" onClick={onDelete}>Delete</Button>
          ) : (
            <div />
          )}
          <div className="flex gap-2">
            <Button variant="ghost" onClick={onClose}>Cancel</Button>
            <Button onClick={handleSubmit} disabled={!date || !pillar || !format || !topic}>
              {entry ? "Update" : "Create"}
            </Button>
          </div>
        </div>
      </div>
    </Modal>
  );
}
