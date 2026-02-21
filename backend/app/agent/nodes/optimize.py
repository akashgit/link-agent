import asyncio
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
    retrieved_images = []
    downloaded_images = []

    # Phase 1: Web search (if Tavily API key is configured)
    if settings.tavily_api_key:
        try:
            from app.services.tavily_search import (
                fact_check_search,
                search_relevant_images,
                download_image,
            )

            results = await asyncio.gather(
                fact_check_search(draft_content, content_pillar),
                search_relevant_images(draft_content, content_pillar),
                return_exceptions=True,
            )

            # Process fact-check results
            if isinstance(results[0], dict):
                fact_check_results = results[0].get("claims_checked", [])
                fact_check_performed = results[0].get("search_performed", False)
            else:
                logger.error(f"Fact-check search error: {results[0]}")

            # Process image search results
            raw_images = []
            if isinstance(results[1], list):
                raw_images = results[1]
            else:
                logger.error(f"Image search error: {results[1]}")

            # Download image candidates
            if raw_images:
                download_tasks = [
                    download_image(img["url"]) for img in raw_images if img.get("url")
                ]
                download_results = await asyncio.gather(*download_tasks, return_exceptions=True)

                for i, dl_result in enumerate(download_results):
                    if isinstance(dl_result, dict) and dl_result.get("success"):
                        downloaded_images.append(
                            {
                                "index": i + 1,
                                "file_path": dl_result["file_path"],
                                "filename": dl_result["filename"],
                                "source_url": dl_result.get("source_url", ""),
                                "description": raw_images[i].get("description", ""),
                            }
                        )

                retrieved_images = [
                    {
                        "url": img.get("url", ""),
                        "description": img.get("description", ""),
                    }
                    for img in raw_images
                ]

        except Exception as e:
            logger.error(f"Web search phase failed: {e}")

    # Phase 2: Build prompt + call LLM
    current_image_info = ""
    current_image_url = state.get("image_url", "")
    if current_image_url:
        status = state.get("image_generation_status", "generated")
        current_image_info = f"AI-generated image ({status})"

    prompt = build_optimize_prompt(
        draft_content=draft_content,
        post_format=post_format,
        content_pillar=content_pillar,
        fact_check_results=fact_check_results if fact_check_performed else None,
        current_image_info=current_image_info,
        retrieved_images=retrieved_images if downloaded_images else None,
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
        r"## Suggested Hashtags\n(.*?)(?=## Sources|## Image Decision|\Z)", result, re.DOTALL
    )
    if tags_match:
        hashtags = [
            tag.strip().lstrip("- ")
            for tag in tags_match.group(1).strip().split("\n")
            if tag.strip()
        ]

    # Parse sources section (from fact-check)
    sources_match = re.search(r"## Sources\n(.*?)(?=## Image Decision|\Z)", result, re.DOTALL)
    if sources_match:
        for fc in fact_check_results:
            fc["sources_in_post"] = True

    # Parse image decision
    image_choice = ""
    image_reasoning = ""
    image_decision_match = re.search(r"## Image Decision\n(.*?)$", result, re.DOTALL)
    if image_decision_match:
        decision_text = image_decision_match.group(1).strip()
        choice_match = re.search(r"Choice:\s*(\S+)", decision_text)
        if choice_match:
            image_choice = choice_match.group(1).strip()
        reasoning_match = re.search(r"Reasoning:\s*(.+?)(?:\n|$)", decision_text, re.DOTALL)
        if reasoning_match:
            image_reasoning = reasoning_match.group(1).strip()

    final_optimized = strip_markdown(optimized) if optimized else draft_content
    validation = validate_linkedin_post(final_optimized)

    # Phase 4: Image resolution
    image_source_decision = "generated"
    original_image_url = current_image_url
    new_image_url = current_image_url
    new_image_status = state.get("image_generation_status", "")

    if not current_image_url and state.get("image_generation_status") == "skipped_no_key":
        image_source_decision = "uploaded" if state.get("uploaded_images") else "generated"

    if image_choice and image_choice.startswith("retrieved_"):
        try:
            idx = int(image_choice.split("_")[1]) - 1
            if 0 <= idx < len(downloaded_images) and downloaded_images[idx].get("file_path"):
                new_image_url = downloaded_images[idx]["file_path"]
                new_image_status = "retrieved"
                image_source_decision = "retrieved"
        except (ValueError, IndexError):
            logger.warning(f"Invalid image choice: {image_choice}")

    return_dict = {
        "optimized_content": final_optimized,
        "optimization_changes": changes,
        "suggested_hashtags": hashtags,
        "linkedin_char_count": validation["char_count"],
        "linkedin_warnings": validation["warnings"],
        "current_stage": "optimize",
        "fact_check_results": fact_check_results,
        "fact_check_performed": fact_check_performed,
        "retrieved_images": retrieved_images,
        "image_source_decision": image_source_decision,
        "image_decision_reasoning": image_reasoning,
        "original_image_url": original_image_url,
    }

    # Override image if retrieved was chosen
    if image_source_decision == "retrieved":
        return_dict["image_url"] = new_image_url
        return_dict["image_generation_status"] = new_image_status

    return return_dict
