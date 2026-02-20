import re

from app.agent.state import AgentState
from app.agent.prompts.research import RESEARCH_PROMPT
from app.services.llm import llm_completion


async def research_node(state: AgentState) -> dict:
    file_context = ""
    if state.get("uploaded_file_text"):
        file_context = f"Uploaded file content:\n{state['uploaded_file_text'][:3000]}"

    prompt = RESEARCH_PROMPT.format(
        content_pillar=state.get("content_pillar", ""),
        post_format=state.get("post_format", ""),
        user_input=state.get("user_input", ""),
        file_context=file_context,
    )

    result = await llm_completion(prompt)

    # Parse trending angles
    angles = []
    hooks = []
    angles_match = re.search(r"## Trending Angles\n(.*?)(?=##|\Z)", result, re.DOTALL)
    if angles_match:
        angles = [
            line.strip().lstrip("0123456789.-) ")
            for line in angles_match.group(1).strip().split("\n")
            if line.strip()
        ]

    hooks_match = re.search(r"## Hook Ideas\n(.*?)(?=##|\Z)", result, re.DOTALL)
    if hooks_match:
        hooks = [
            line.strip().lstrip("0123456789.-) ")
            for line in hooks_match.group(1).strip().split("\n")
            if line.strip()
        ]

    return {
        "research_results": result,
        "trending_angles": angles[:5],
        "recommended_hook_ideas": hooks[:5],
        "current_stage": "research",
    }
