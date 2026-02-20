"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import type { SSEEvent } from "@/lib/types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

interface UseSSEOptions {
  threadId: string | null;
  isResume?: boolean;
}

interface UseSSEReturn {
  events: SSEEvent[];
  currentNode: string | null;
  isInterrupted: boolean;
  interruptData: Record<string, unknown> | null;
  isComplete: boolean;
  isConnected: boolean;
  error: string | null;
}

export function useSSE({ threadId, isResume }: UseSSEOptions): UseSSEReturn {
  const [events, setEvents] = useState<SSEEvent[]>([]);
  const [currentNode, setCurrentNode] = useState<string | null>(null);
  const [isInterrupted, setIsInterrupted] = useState(false);
  const [interruptData, setInterruptData] = useState<Record<string, unknown> | null>(null);
  const [isComplete, setIsComplete] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const sourceRef = useRef<EventSource | null>(null);

  const cleanup = useCallback(() => {
    if (sourceRef.current) {
      sourceRef.current.close();
      sourceRef.current = null;
    }
  }, []);

  useEffect(() => {
    if (!threadId) return;

    cleanup();

    const path = isResume
      ? `${API_URL}/agent/resume/${threadId}`
      : `${API_URL}/agent/stream/${threadId}`;

    const source = new EventSource(path);
    sourceRef.current = source;

    source.onopen = () => setIsConnected(true);
    source.onerror = () => {
      setError("Connection lost");
      setIsConnected(false);
    };

    source.addEventListener("node_complete", (e) => {
      const data = JSON.parse(e.data);
      const evt: SSEEvent = { event: "node_complete", data };
      setEvents((prev) => [...prev, evt]);
      setCurrentNode(data.node || data.stage);
    });

    source.addEventListener("interrupt", (e) => {
      const data = JSON.parse(e.data);
      setEvents((prev) => [...prev, { event: "interrupt", data }]);
      setIsInterrupted(true);
      setInterruptData(data);
    });

    source.addEventListener("complete", (e) => {
      const data = JSON.parse(e.data);
      setEvents((prev) => [...prev, { event: "complete", data }]);
      setIsComplete(true);
      cleanup();
    });

    source.addEventListener("paused", (e) => {
      const data = JSON.parse(e.data);
      setEvents((prev) => [...prev, { event: "paused", data }]);
      setIsInterrupted(true);
    });

    source.addEventListener("error", (e) => {
      if (e instanceof MessageEvent) {
        const data = JSON.parse(e.data);
        setError(data.error || "Unknown error");
      }
      cleanup();
    });

    return cleanup;
  }, [threadId, isResume, cleanup]);

  return { events, currentNode, isInterrupted, interruptData, isComplete, isConnected, error };
}
