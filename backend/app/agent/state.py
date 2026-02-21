from typing import TypedDict


class AgentState(TypedDict, total=False):
    # Input
    user_input: str
    content_pillar: str
    post_format: str
    uploaded_file_text: str
    uploaded_images: list[str]
    post_id: str

    # Research
    research_results: str
    trending_angles: list[str]
    recommended_hook_ideas: list[str]

    # Draft
    draft_content: str
    draft_hook: str
    draft_cta: str

    # Image
    image_prompt: str
    image_url: str
    image_generation_status: str

    # Optimize
    optimized_content: str
    optimization_changes: list[str]
    suggested_hashtags: list[str]

    # Proofread
    proofread_content: str
    proofread_corrections: list[str]
    tone_check_passed: bool

    # Approval
    approval_status: str
    approval_feedback: str
    revision_count: int

    # Meta
    current_stage: str
    error: str
