"use client";

import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { fetchSettings, upsertSetting } from "@/lib/api";
import type { Setting } from "@/lib/types";

export function useSettings() {
  return useQuery<Setting[]>({
    queryKey: ["settings"],
    queryFn: fetchSettings,
  });
}

export function useUpsertSetting() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ key, value }: { key: string; value: string }) =>
      upsertSetting(key, value),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["settings"] }),
  });
}
