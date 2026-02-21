import axios from "axios";
import type { FileUploadResponse, LinkedInValidation, MediaAsset } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";

export const api = axios.create({
  baseURL: API_URL,
  headers: { "Content-Type": "application/json" },
});

/**
 * Convert a relative API path (e.g. /api/uploads/file/xxx.png) to a full URL.
 */
export function getFileUrl(path: string): string {
  if (!path) return "";
  // If it's already an absolute URL, return as-is
  if (path.startsWith("http://") || path.startsWith("https://")) return path;
  // Strip /api prefix if present since API_URL already includes it
  const baseUrl = API_URL.replace(/\/api$/, "");
  return `${baseUrl}${path}`;
}

// Posts
export const fetchPosts = (params?: Record<string, string>) =>
  api.get("/posts", { params }).then((r) => r.data);

export const fetchPost = (id: string) =>
  api.get(`/posts/${id}`).then((r) => r.data);

export const createPost = (data: {
  title: string;
  content_pillar: string;
  post_format: string;
  user_input?: string;
}) => api.post("/posts", data).then((r) => r.data);

export const updatePost = (id: string, data: Record<string, unknown>) =>
  api.patch(`/posts/${id}`, data).then((r) => r.data);

export const deletePost = (id: string) =>
  api.delete(`/posts/${id}`);

export const fetchPostVersions = (id: string) =>
  api.get(`/posts/${id}/versions`).then((r) => r.data);

// Agent
export const runAgent = (data: {
  post_id: string;
  user_input?: string;
  content_pillar?: string;
  post_format?: string;
  uploaded_file_text?: string;
}) => api.post("/agent/run", data).then((r) => r.data);

export const resumeAgent = (
  threadId: string,
  data: { status: string; feedback?: string; content_override?: string },
) => api.post(`/agent/resume/${threadId}`, data).then((r) => r.data);

export const fetchAgentStatus = (threadId: string) =>
  api.get(`/agent/status/${threadId}`).then((r) => r.data);

// Calendar
export const fetchCalendar = (params?: { month?: number; year?: number }) =>
  api.get("/calendar", { params }).then((r) => r.data);

export const createCalendarEntry = (data: {
  scheduled_date: string;
  content_pillar: string;
  post_format: string;
  topic: string;
  notes?: string;
}) => api.post("/calendar", data).then((r) => r.data);

export const updateCalendarEntry = (id: string, data: Record<string, unknown>) =>
  api.patch(`/calendar/${id}`, data).then((r) => r.data);

export const deleteCalendarEntry = (id: string) =>
  api.delete(`/calendar/${id}`);

// Uploads
export const uploadFile = (file: File): Promise<FileUploadResponse> => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post("/uploads", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then((r) => r.data);
};

// Media (per-post)
export const fetchPostMedia = (postId: string): Promise<MediaAsset[]> =>
  api.get(`/posts/${postId}/media`).then((r) => r.data);

export const uploadPostMedia = (postId: string, file: File): Promise<MediaAsset> => {
  const formData = new FormData();
  formData.append("file", file);
  return api.post(`/posts/${postId}/media`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  }).then((r) => r.data);
};

export const deletePostMedia = (postId: string, assetId: string): Promise<void> =>
  api.delete(`/posts/${postId}/media/${assetId}`).then(() => undefined);

// Settings
export const fetchSettings = () =>
  api.get("/settings").then((r) => r.data);

export const fetchSetting = (key: string) =>
  api.get(`/settings/${key}`).then((r) => r.data);

export const upsertSetting = (key: string, value: string) =>
  api.put(`/settings/${key}`, { value }).then((r) => r.data);

// Typefully / LinkedIn
export const validateLinkedIn = (content: string): Promise<LinkedInValidation> =>
  api.post("/typefully/validate", { content }).then((r) => r.data);

export const pushToTypefully = (postId: string): Promise<{ draft_id: string }> =>
  api.post("/typefully/draft", { post_id: postId }).then((r) => r.data);

export const scheduleOnTypefully = (
  postId: string,
  publishAt: string,
): Promise<{ draft_id: string }> =>
  api.post("/typefully/schedule", { post_id: postId, publish_at: publishAt }).then((r) => r.data);

export const getTypefullyStatus = (
  postId: string,
): Promise<{ status: string; draft: Record<string, unknown> }> =>
  api.get(`/typefully/draft/${postId}`).then((r) => r.data);

// Health
export const fetchHealth = () =>
  api.get("/health").then((r) => r.data);
