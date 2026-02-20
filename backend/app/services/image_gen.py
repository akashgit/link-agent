import os
import uuid
import logging

from app.config import settings

logger = logging.getLogger(__name__)


async def generate_image(prompt: str, save_dir: str | None = None) -> dict:
    """Generate an image using Gemini and save to disk.

    Returns dict with keys: file_path, filename, success, error
    """
    save_dir = save_dir or settings.upload_dir
    os.makedirs(save_dir, exist_ok=True)

    try:
        from google import genai

        client = genai.Client(api_key=settings.gemini_api_key)
        response = client.models.generate_content(
            model="gemini-2.0-flash-exp",
            contents=prompt,
            config=genai.types.GenerateContentConfig(
                response_modalities=["image", "text"],
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
        logger.error(f"Image generation failed: {e}")
        return {
            "file_path": None,
            "filename": None,
            "success": False,
            "error": str(e),
        }
