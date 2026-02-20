from app.agent.state import AgentState


def route_after_approval(state: AgentState) -> str:
    if state.get("approval_status") == "approved":
        return "__end__"
    return "draft"
