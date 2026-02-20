export const CONTENT_PILLARS = [
  { value: "agentops", label: "AgentOps / Production Systems" },
  { value: "inference_scaling", label: "Inference-time Scaling" },
  { value: "enterprise_reality", label: "Enterprise AI Reality" },
  { value: "research_to_product", label: "Research to Product" },
  { value: "leadership", label: "Leadership Stories" },
] as const;

export const POST_FORMATS = [
  { value: "framework", label: "Framework", description: "Saveable, structured content with numbered points" },
  { value: "strong_pov", label: "Strong POV", description: "Contrarian, shareable opinion piece" },
  { value: "simplification", label: "Simplification", description: "Complex topics made accessible" },
  { value: "story", label: "Story", description: "Narrative leadership post" },
  { value: "leader_lens", label: "Leader Lens", description: "Business leadership perspective" },
] as const;

export const POST_STATUSES = [
  { value: "idea", label: "Idea" },
  { value: "drafting", label: "Drafting" },
  { value: "in_review", label: "In Review" },
  { value: "approved", label: "Approved" },
  { value: "scheduled", label: "Scheduled" },
  { value: "published", label: "Published" },
] as const;

export const PILLAR_COLORS: Record<string, string> = {
  agentops: "bg-blue-100 text-blue-800",
  inference_scaling: "bg-purple-100 text-purple-800",
  enterprise_reality: "bg-amber-100 text-amber-800",
  research_to_product: "bg-green-100 text-green-800",
  leadership: "bg-rose-100 text-rose-800",
};

export const STATUS_COLORS: Record<string, string> = {
  idea: "bg-gray-100 text-gray-700",
  drafting: "bg-yellow-100 text-yellow-800",
  in_review: "bg-blue-100 text-blue-800",
  approved: "bg-green-100 text-green-800",
  scheduled: "bg-indigo-100 text-indigo-800",
  published: "bg-emerald-100 text-emerald-800",
};

export const AGENT_STAGES = [
  "research",
  "draft",
  "generate_image",
  "optimize",
  "proofread",
  "approve",
] as const;
