from langgraph.types import interrupt, Command

from app.agent.state import AgentState


async def approve_node(state: AgentState) -> Command:
    review_payload = {
        "proofread_content": state.get("proofread_content", ""),
        "suggested_hashtags": state.get("suggested_hashtags", []),
        "image_url": state.get("image_url", ""),
        "image_generation_status": state.get("image_generation_status", ""),
        "optimization_changes": state.get("optimization_changes", []),
        "proofread_corrections": state.get("proofread_corrections", []),
        "tone_check_passed": state.get("tone_check_passed", True),
        "revision_count": state.get("revision_count", 0),
    }

    user_response = interrupt(review_payload)

    status = user_response.get("status", "approved")
    feedback = user_response.get("feedback", "")

    if status == "approved":
        return Command(
            update={
                "approval_status": "approved",
                "approval_feedback": feedback,
                "current_stage": "approved",
            }
        )
    else:
        return Command(
            goto="draft",
            update={
                "approval_status": "edit_requested",
                "approval_feedback": feedback,
                "current_stage": "revision",
            },
        )
