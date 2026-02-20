"use client";

import { useState } from "react";
import { Card } from "@/components/ui/Card";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { Button } from "@/components/ui/Button";
import { Skeleton } from "@/components/ui/Skeleton";
import { useSettings, useUpsertSetting } from "@/hooks/useSettings";
import { useToast } from "@/components/ui/Toast";

const SETTINGS_SCHEMA = [
  { key: "author_name", label: "Author Name", type: "input", placeholder: "Akash Srivastava" },
  { key: "author_title", label: "Author Title", type: "input", placeholder: "Director of Core AI at IBM" },
  { key: "litellm_model", label: "LLM Model", type: "input", placeholder: "anthropic/claude-sonnet-4-20250514" },
  { key: "default_tone", label: "Default Tone", type: "input", placeholder: "executive, clear, no hype" },
  { key: "custom_instructions", label: "Custom Instructions", type: "textarea", placeholder: "Any additional instructions for the AI agent..." },
];

export default function SettingsPage() {
  const { data: settings, isLoading } = useSettings();
  const upsertSetting = useUpsertSetting();
  const { toast } = useToast();
  const [values, setValues] = useState<Record<string, string>>({});
  const [dirty, setDirty] = useState<Set<string>>(new Set());

  const getVal = (key: string) => {
    if (key in values) return values[key];
    return settings?.find((s) => s.key === key)?.value || "";
  };

  const setVal = (key: string, value: string) => {
    setValues((prev) => ({ ...prev, [key]: value }));
    setDirty((prev) => new Set(prev).add(key));
  };

  const handleSave = async () => {
    try {
      for (const key of dirty) {
        await upsertSetting.mutateAsync({ key, value: getVal(key) });
      }
      setDirty(new Set());
      toast("Settings saved", "success");
    } catch {
      toast("Failed to save settings", "error");
    }
  };

  return (
    <div className="max-w-2xl space-y-6">
      <Card>
        <h3 className="font-semibold mb-4">Agent Configuration</h3>
        {isLoading ? (
          <div className="space-y-4">{[...Array(4)].map((_, i) => <Skeleton key={i} className="h-10 w-full" />)}</div>
        ) : (
          <div className="space-y-4">
            {SETTINGS_SCHEMA.map((s) =>
              s.type === "textarea" ? (
                <Textarea key={s.key} label={s.label} value={getVal(s.key)} onChange={(e) => setVal(s.key, e.target.value)} placeholder={s.placeholder} rows={4} />
              ) : (
                <Input key={s.key} label={s.label} value={getVal(s.key)} onChange={(e) => setVal(s.key, e.target.value)} placeholder={s.placeholder} />
              )
            )}
            <div className="pt-2">
              <Button onClick={handleSave} disabled={dirty.size === 0} loading={upsertSetting.isPending}>
                Save Settings
              </Button>
            </div>
          </div>
        )}
      </Card>

      <Card>
        <h3 className="font-semibold mb-2">About</h3>
        <p className="text-sm text-gray-500">
          Link Agent v0.1.0 — AI-powered LinkedIn content agent for thought leadership growth.
        </p>
      </Card>
    </div>
  );
}
