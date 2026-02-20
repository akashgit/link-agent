export interface Post {
  id: string;
  title: string;
  content_pillar: string;
  post_format: string;
  status: string;
  final_content: string | null;
  thread_id: string | null;
  user_input: string | null;
  revision_count: number;
  created_at: string;
  updated_at: string;
}

export interface Draft {
  id: string;
  post_id: string;
  version: number;
  content: string;
  hook: string | null;
  cta: string | null;
  hashtags: string | null;
  feedback: string | null;
  created_at: string;
}

export interface PostWithDrafts extends Post {
  drafts: Draft[];
}

export interface CalendarEntry {
  id: string;
  scheduled_date: string;
  content_pillar: string;
  post_format: string;
  topic: string;
  status: string;
  post_id: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface MediaAsset {
  id: string;
  post_id: string | null;
  filename: string;
  file_path: string;
  content_type: string;
  file_size: number;
  prompt_used: string | null;
  created_at: string;
}

export interface Setting {
  key: string;
  value: string;
  updated_at: string;
}

export interface AgentRunRequest {
  post_id: string;
  user_input?: string;
  content_pillar?: string;
  post_format?: string;
  uploaded_file_text?: string;
}

export interface AgentRunResponse {
  thread_id: string;
  post_id: string;
  status: string;
}

export interface AgentResumeRequest {
  status: "approved" | "edit_requested";
  feedback?: string;
}

export interface SSEEvent {
  event: string;
  data: Record<string, unknown>;
}
