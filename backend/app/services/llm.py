import litellm

from app.config import settings


async def llm_completion(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> str:
    model = model or settings.litellm_model
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await litellm.acompletion(
        model=model,
        messages=messages,
        max_tokens=max_tokens,
        temperature=temperature,
        api_key=settings.anthropic_api_key,
        num_retries=2,
    )
    return response.choices[0].message.content or ""
