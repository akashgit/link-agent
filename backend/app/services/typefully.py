import httpx

from app.config import settings

BASE_URL = "https://api.typefully.com"


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {settings.typefully_api_key}",
        "Content-Type": "application/json",
    }


async def get_social_sets() -> list[dict]:
    """List available social sets (connected accounts)."""
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{BASE_URL}/v2/social-sets", headers=_headers())
        resp.raise_for_status()
        return resp.json()


async def get_linkedin_profile() -> dict:
    """Fetch LinkedIn profile info from the configured social set."""
    social_set_id = settings.typefully_social_set_id
    if not social_set_id:
        return {}
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/v2/social-sets/{social_set_id}/",
            headers=_headers(),
        )
        resp.raise_for_status()
        data = resp.json()

    linkedin = data.get("platforms", {}).get("linkedin", {})
    return {
        "name": linkedin.get("name", ""),
        "profile_image_url": linkedin.get("profile_image_url", ""),
        "username": linkedin.get("username", ""),
        "profile_url": linkedin.get("profile_url", ""),
    }


async def create_draft(
    text: str,
    hashtags: list[str] | None = None,
    publish_at: str | None = None,
    media_ids: list[str] | None = None,
) -> dict:
    """Create a LinkedIn draft in Typefully.

    Hashtags are appended to the post body. media_ids attach uploaded media.
    publish_at (ISO 8601) schedules the draft.
    """
    social_set_id = settings.typefully_social_set_id
    body_text = text
    if hashtags:
        body_text += "\n\n" + " ".join(
            tag if tag.startswith("#") else f"#{tag}" for tag in hashtags
        )

    post_payload: dict = {"text": body_text}
    if media_ids:
        post_payload["media_ids"] = media_ids

    payload: dict = {
        "platforms": {
            "linkedin": {
                "enabled": True,
                "posts": [post_payload],
            }
        },
    }
    if publish_at:
        payload["publish_at"] = publish_at

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{BASE_URL}/v2/social-sets/{social_set_id}/drafts",
            headers=_headers(),
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def get_draft(draft_id: str) -> dict:
    """Fetch a draft's current status from Typefully."""
    social_set_id = settings.typefully_social_set_id
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            f"{BASE_URL}/v2/social-sets/{social_set_id}/drafts/{draft_id}",
            headers=_headers(),
        )
        resp.raise_for_status()
        return resp.json()


async def upload_media(file_path: str, content_type: str) -> str:
    """Upload a media file to Typefully and return the media_id."""
    social_set_id = settings.typefully_social_set_id

    async with httpx.AsyncClient() as client:
        # Get presigned upload URL
        resp = await client.post(
            f"{BASE_URL}/v2/social-sets/{social_set_id}/media",
            headers=_headers(),
            json={"content_type": content_type},
        )
        resp.raise_for_status()
        upload_data = resp.json()

        # Upload file to presigned URL
        with open(file_path, "rb") as f:
            file_bytes = f.read()

        await client.put(
            upload_data["upload_url"],
            content=file_bytes,
            headers={"Content-Type": content_type},
        )

        return upload_data["media_id"]


async def schedule_draft(draft_id: str, publish_at: str) -> dict:
    """Schedule (or reschedule) a Typefully draft."""
    social_set_id = settings.typefully_social_set_id
    async with httpx.AsyncClient() as client:
        resp = await client.patch(
            f"{BASE_URL}/v2/social-sets/{social_set_id}/drafts/{draft_id}",
            headers=_headers(),
            json={"publish_at": publish_at},
        )
        resp.raise_for_status()
        return resp.json()
