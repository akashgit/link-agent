import re

from app.agent.state import AgentState
from app.agent.prompts.optimize import OPTIMIZE_PROMPT
from app.services.llm import llm_completion


async def optimize_node(state: AgentState) -> dict:
    prompt = OPTIMIZE_PROMPT.format(
        draft_content=state.get("draft_content", ""),
        post_format=state.get("post_format", ""),
        content_pillar=state.get("content_pillar", ""),
    )

    result = await llm_completion(prompt)

    # Parse sections
    optimized = ""
    changes = []
    hashtags = []

    opt_match = re.search(r"## Optimized Post\n(.*?)(?=## Changes Made|\Z)", result, re.DOTALL)
    if opt_match:
        optimized = opt_match.group(1).strip()

    changes_match = re.search(r"## Changes Made\n(.*?)(?=## Suggested Hashtags|\Z)", result, re.DOTALL)
    if changes_match:
        changes = [
            line.strip().lstrip("0123456789.-) ")
            for line in changes_match.group(1).strip().split("\n")
            if line.strip()
        ]

    tags_match = re.search(r"## Suggested Hashtags\n(.*?)$", result, re.DOTALL)
    if tags_match:
        hashtags = [
            tag.strip().lstrip("- ")
            for tag in tags_match.group(1).strip().split("\n")
            if tag.strip()
        ]

    return {
        "optimized_content": optimized or state.get("draft_content", ""),
        "optimization_changes": changes,
        "suggested_hashtags": hashtags,
        "current_stage": "optimize",
    }
