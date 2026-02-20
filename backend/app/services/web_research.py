import logging
import time

import httpx

logger = logging.getLogger(__name__)

_cache: dict[str, tuple[float, list[dict]]] = {}
CACHE_TTL = 3600  # 1 hour


async def fetch_trending_topics() -> list[dict]:
    """Fetch trending AI topics from HackerNews."""
    cache_key = "hn_ai_topics"
    now = time.time()

    if cache_key in _cache:
        cached_time, cached_data = _cache[cache_key]
        if now - cached_time < CACHE_TTL:
            return cached_data

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                "https://hacker-news.firebaseio.com/v0/topstories.json"
            )
            story_ids = resp.json()[:30]

            topics = []
            for story_id in story_ids[:15]:
                resp = await client.get(
                    f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"
                )
                story = resp.json()
                if story and any(
                    kw in (story.get("title", "") or "").lower()
                    for kw in ["ai", "llm", "agent", "model", "gpt", "inference", "ml"]
                ):
                    topics.append({
                        "title": story.get("title", ""),
                        "url": story.get("url", ""),
                        "score": story.get("score", 0),
                    })

            _cache[cache_key] = (now, topics)
            return topics

    except Exception as e:
        logger.error(f"Failed to fetch trending topics: {e}")
        return []
