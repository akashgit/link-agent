import os
import uuid
import logging

import httpx
from tavily import AsyncTavilyClient

from app.config import settings
from app.services.llm import llm_completion

logger = logging.getLogger(__name__)

CLAIM_EXTRACTION_PROMPT = """Extract the 2-4 most important factual claims from this LinkedIn post draft. Return ONLY the claims as a newline-separated list, nothing else. Focus on statistics, data points, named entities, and specific assertions that can be verified.

Draft:
{draft_content}

Content pillar: {content_pillar}"""


async def fact_check_search(draft_content: str, content_pillar: str) -> dict:
    """Search the web to fact-check key claims in the draft content."""
    try:
        # Extract claims using LLM
        prompt = CLAIM_EXTRACTION_PROMPT.format(
            draft_content=draft_content,
            content_pillar=content_pillar,
        )
        claims_text = await llm_completion(prompt, max_tokens=300)

        claims = [c.strip() for c in claims_text.strip().split("\n") if c.strip()]
        claims = claims[:4]  # Cap at 4 claims

        if not claims:
            return {"claims_checked": [], "search_performed": False}

        client = AsyncTavilyClient(api_key=settings.tavily_api_key)
        claims_checked = []

        for claim in claims:
            try:
                result = await client.search(
                    query=claim,
                    search_depth="advanced",
                    max_results=3,
                    include_answer=True,
                )
                sources = [
                    {
                        "title": r.get("title", ""),
                        "url": r.get("url", ""),
                        "snippet": r.get("content", "")[:300],
                    }
                    for r in result.get("results", [])
                ]
                claims_checked.append(
                    {
                        "claim": claim,
                        "search_answer": result.get("answer", ""),
                        "sources": sources,
                    }
                )
            except Exception as e:
                logger.warning(f"Tavily search failed for claim '{claim[:50]}...': {e}")
                continue

        return {"claims_checked": claims_checked, "search_performed": True}

    except Exception as e:
        logger.error(f"Fact-check search failed: {e}")
        return {"claims_checked": [], "search_performed": False}


async def search_relevant_images(draft_content: str, content_pillar: str) -> list[dict]:
    """Search the web for relevant images (charts, infographics, data tables)."""
    try:
        query = f"{draft_content[:150]} {content_pillar} data chart infographic statistics"
        client = AsyncTavilyClient(api_key=settings.tavily_api_key)

        result = await client.search(
            query=query,
            include_images=True,
            max_results=5,
        )

        images = result.get("images", [])
        candidates = []
        for img in images[:3]:
            if isinstance(img, str):
                candidates.append({"url": img, "description": ""})
            elif isinstance(img, dict):
                candidates.append(
                    {
                        "url": img.get("url", ""),
                        "description": img.get("description", ""),
                    }
                )

        return candidates

    except Exception as e:
        logger.error(f"Image search failed: {e}")
        return []


async def download_image(image_url: str) -> dict:
    """Download an image from a URL and save it to the uploads directory."""
    save_dir = settings.upload_dir
    os.makedirs(save_dir, exist_ok=True)

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(image_url, follow_redirects=True)
            response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        valid_types = ("image/png", "image/jpeg", "image/webp", "image/gif")
        if not any(t in content_type for t in valid_types):
            return {
                "file_path": None,
                "filename": None,
                "success": False,
                "error": f"Invalid content type: {content_type}",
                "source_url": image_url,
            }

        # Determine extension from content type
        ext_map = {
            "image/png": ".png",
            "image/jpeg": ".jpg",
            "image/webp": ".webp",
            "image/gif": ".gif",
        }
        ext = ".jpg"
        for mime, extension in ext_map.items():
            if mime in content_type:
                ext = extension
                break

        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(save_dir, filename)

        with open(file_path, "wb") as f:
            f.write(response.content)

        return {
            "file_path": file_path,
            "filename": filename,
            "success": True,
            "error": None,
            "source_url": image_url,
        }

    except Exception as e:
        logger.error(f"Image download failed for {image_url}: {e}")
        return {
            "file_path": None,
            "filename": None,
            "success": False,
            "error": str(e),
            "source_url": image_url,
        }
