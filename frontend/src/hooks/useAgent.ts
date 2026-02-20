"use client";

import { useMutation } from "@tanstack/react-query";
import { runAgent } from "@/lib/api";

export function useRunAgent() {
  return useMutation({
    mutationFn: runAgent,
  });
}
