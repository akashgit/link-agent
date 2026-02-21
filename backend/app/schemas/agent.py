from pydantic import BaseModel


class AgentRunRequest(BaseModel):
    post_id: str
    user_input: str | None = None
    content_pillar: str | None = None
    post_format: str | None = None
    uploaded_file_text: str | None = None


class AgentRunResponse(BaseModel):
    thread_id: str
    post_id: str
    status: str = "started"


class AgentResumeRequest(BaseModel):
    status: str  # "approved" or "edit_requested"
    feedback: str | None = None
    content_override: str | None = None


class AgentStatusResponse(BaseModel):
    thread_id: str
    current_stage: str | None
    status: str
