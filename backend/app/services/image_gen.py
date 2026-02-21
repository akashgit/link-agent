import base64
import os
import uuid
import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

OPENROUTER_MODEL = "google/gemini-2.5-flash-image"


async def generate_image(prompt: str, save_dir: str | None = None) -> dict:
    """Generate an image using Gemini via OpenRouter and save to disk.

    Falls back to the direct Gemini API if no OpenRouter key is configured.

    Returns dict with keys: file_path, filename, success, error
    """
    save_dir = save_dir or settings.upload_dir
    os.makedirs(save_dir, exist_ok=True)

    if settings.openrouter_api_key:
        return await _generate_via_openrouter(prompt, save_dir)
    elif settings.gemini_api_key:
        return await _generate_via_gemini(prompt, save_dir)
    else:
        return {
            "file_path": None,
            "filename": None,
            "success": False,
            "error": "No image generation API key configured",
        }


async def _generate_via_openrouter(prompt: str, save_dir: str) -> dict:
    """Generate image using Gemini model via OpenRouter API.

    Uses httpx directly because OpenRouter returns images in a `message.images`
    field that the OpenAI SDK doesn't parse.
    """
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {settings.openrouter_api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": OPENROUTER_MODEL,
                    "modalities": ["text", "image"],
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"type": "text", "text": prompt}],
                        }
                    ],
                },
            )
            resp.raise_for_status()
            data = resp.json()

        # Images are in message.images (not in content)
        for choice in data.get("choices", []):
            msg = choice.get("message", {})
            images = msg.get("images", [])
            for img in images:
                if img.get("type") == "image_url":
                    data_url = img.get("image_url", {}).get("url", "")
                    if data_url:
                        return _save_base64_image(data_url, save_dir)

        return {
            "file_path": None,
            "filename": None,
            "success": False,
            "error": "No image found in OpenRouter response",
        }

    except Exception as e:
        logger.error(f"OpenRouter image generation failed: {e}")
        return {
            "file_path": None,
            "filename": None,
            "success": False,
            "error": str(e),
        }


def _save_base64_image(data_url: str, save_dir: str) -> dict:
    """Save a base64-encoded image (data URL or raw base64) to disk."""
    try:
        if data_url.startswith("data:"):
            header, b64_data = data_url.split(",", 1)
            if "png" in header:
                ext = ".png"
            elif "webp" in header:
                ext = ".webp"
            elif "gif" in header:
                ext = ".gif"
            else:
                ext = ".jpg"
        else:
            b64_data = data_url
            ext = ".png"

        image_bytes = base64.b64decode(b64_data)
        filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(save_dir, filename)

        with open(file_path, "wb") as f:
            f.write(image_bytes)

        return {
            "file_path": file_path,
            "filename": filename,
            "success": True,
            "error": None,
        }
    except Exception as e:
        logger.error(f"Failed to save base64 image: {e}")
        return {
            "file_path": None,
            "filename": None,
            "success": False,
            "error": f"Failed to decode image: {e}",
        }


async def _generate_via_gemini(prompt: str, save_dir: str) -> dict:
    """Generate image using the direct Gemini API (legacy fallback)."""
    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model="gemini-2.5-flash-image",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                filename = f"{uuid.uuid4()}.png"
                file_path = os.path.join(save_dir, filename)
                with open(file_path, "wb") as f:
                    f.write(part.inline_data.data)
                return {
                    "file_path": file_path,
                    "filename": filename,
                    "success": True,
                    "error": None,
                }

        return {
            "file_path": None,
            "filename": None,
            "success": False,
            "error": "No image generated in response",
        }

    except Exception as e:
        logger.error(f"Gemini image generation failed: {e}")
        return {
            "file_path": None,
            "filename": None,
            "success": False,
            "error": str(e),
        }
