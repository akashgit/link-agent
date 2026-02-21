import asyncio
import logging
import os
import subprocess

from openai import AsyncOpenAI

from app.config import settings

logger = logging.getLogger(__name__)


def _call_claude(prompt: str, system: str = "", model: str = "") -> str:
    """Call the Claude CLI subprocess. Requires `claude` to be installed and authenticated."""
    model = model or settings.claude_model
    cmd = ["claude", "-p", "--model", model, "--no-session-persistence"]
    if system:
        cmd += ["--system-prompt", system]

    # Strip CLAUDECODE env var so the CLI doesn't think it's nested
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE"}

    result = subprocess.run(
        cmd, input=prompt, capture_output=True, text=True, timeout=120, env=env
    )
    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI error: {result.stderr.strip()}")
    return result.stdout.strip()


async def llm_completion(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> str:
    """Async wrapper around the Claude CLI. Runs the subprocess in a thread pool."""
    try:
        return await asyncio.to_thread(
            _call_claude,
            prompt,
            system or "",
            model or "",
        )
    except subprocess.TimeoutExpired:
        logger.error("Claude CLI timed out")
        raise RuntimeError("LLM request timed out")
    except FileNotFoundError:
        raise RuntimeError(
            "Claude CLI not found. Install it with: npm install -g @anthropic-ai/claude-code"
        )


async def openai_completion(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 2000,
    temperature: float = 0.7,
) -> str:
    """Call OpenAI via the official SDK."""
    api_key = settings.openai_api_key
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")

    client = AsyncOpenAI(api_key=api_key)
    messages: list[dict] = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = await client.chat.completions.create(
        model=model or settings.openai_model,
        messages=messages,
        max_completion_tokens=max_tokens,
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()
