import logging
import re

from app.agent.state import AgentState
from app.agent.prompts.optimize import build_optimize_prompt
from app.config import settings
from app.services.llm import llm_completion
from app.utils.linkedin import strip_markdown, validate_linkedin_post

logger = logging.getLogger(__name__)


async def optimize_node(state: AgentState) -> dict:
    draft_content = state.get("draft_content", "")
    post_format = state.get("post_format", "")
    content_pillar = state.get("content_pillar", "")

    fact_check_results = []
    fact_check_performed = False

    # Phase 1: Fact-check web search (if Tavily API key is configured)
    if settings.tavily_api_key:
        try:
            from app.services.tavily_search import fact_check_search

            fc_result = await fact_check_search(draft_content, content_pillar)

            if isinstance(fc_result, dict):
                fact_check_results = fc_result.get("claims_checked", [])
                fact_check_performed = fc_result.get("search_performed", False)
            else:
                logger.error(f"Fact-check search error: {fc_result}")

        except Exception as e:
            logger.error(f"Web search phase failed: {e}")

    # Phase 2: Build prompt + call LLM
    prompt = build_optimize_prompt(
        draft_content=draft_content,
        post_format=post_format,
        content_pillar=content_pillar,
        fact_check_results=fact_check_results if fact_check_performed else None,
    )

    if state.get("uploaded_file_text"):
        prompt += f"\n\nOriginal source material (verify facts against this):\n{state['uploaded_file_text'][:3000]}"

    result = await llm_completion(prompt)

    # Phase 3: Parse response
    optimized = ""
    changes = []
    hashtags = []

    opt_match = re.search(r"## Optimized Post\n(.*?)(?=## Changes Made|\Z)", result, re.DOTALL)
    if opt_match:
        optimized = opt_match.group(1).strip()

    changes_match = re.search(
        r"## Changes Made\n(.*?)(?=## Suggested Hashtags|\Z)", result, re.DOTALL
    )
    if changes_match:
        changes = [
            line.strip().lstrip("0123456789.-) ")
            for line in changes_match.group(1).strip().split("\n")
            if line.strip()
        ]

    tags_match = re.search(
        r"## Suggested Hashtags\n(.*?)(?=## Sources|\Z)", result, re.DOTALL
    )
    if tags_match:
        hashtags = [
            tag.strip().lstrip("- ")
            for tag in tags_match.group(1).strip().split("\n")
            if tag.strip()
        ]

    # Parse sources section (from fact-check)
    sources_match = re.search(r"## Sources\n(.*?)$", result, re.DOTALL)
    if sources_match:
        for fc in fact_check_results:
            fc["sources_in_post"] = True

    final_optimized = strip_markdown(optimized) if optimized else draft_content
    validation = validate_linkedin_post(final_optimized)

    return {
        "optimized_content": final_optimized,
        "optimization_changes": changes,
        "suggested_hashtags": hashtags,
        "linkedin_char_count": validation["char_count"],
        "linkedin_warnings": validation["warnings"],
        "current_stage": "optimize",
        "fact_check_results": fact_check_results,
        "fact_check_performed": fact_check_performed,
    }
