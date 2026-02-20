IMAGE_PROMPT_TEMPLATE = """Based on the following LinkedIn post, generate a concise image generation prompt for a professional, minimal visual that would accompany this post.

The image should:
- Be clean and professional (not stock-photo-like)
- Use a minimal color palette (blues, grays, whites)
- Work well as a LinkedIn post image
- Convey the core concept visually
- Be abstract/conceptual rather than literal

Post content:
{post_content}

Post format: {post_format}
Content pillar: {content_pillar}

Return ONLY the image generation prompt, nothing else. Keep it under 100 words."""
