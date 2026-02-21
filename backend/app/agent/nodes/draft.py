from app.agent.state import AgentState
from app.agent.prompts.framework import FRAMEWORK_PROMPT
from app.agent.prompts.strong_pov import STRONG_POV_PROMPT
from app.agent.prompts.simplification import SIMPLIFICATION_PROMPT
from app.agent.prompts.story import STORY_PROMPT
from app.agent.prompts.leader_lens import LEADER_LENS_PROMPT
from app.services.llm import llm_completion

FORMAT_PROMPTS = {
    "framework": FRAMEWORK_PROMPT,
    "strong_pov": STRONG_POV_PROMPT,
    "simplification": SIMPLIFICATION_PROMPT,
    "story": STORY_PROMPT,
    "leader_lens": LEADER_LENS_PROMPT,
}


async def draft_node(state: AgentState) -> dict:
    post_format = state.get("post_format", "framework")
    prompt_template = FORMAT_PROMPTS.get(post_format, FRAMEWORK_PROMPT)

    revision_context = ""
    if state.get("approval_feedback"):
        revision_context = (
            f"REVISION REQUESTED. Previous feedback from reviewer:\n"
            f"{state['approval_feedback']}\n\n"
            f"Previous draft:\n{state.get('draft_content', '')}\n\n"
            f"Please revise the post addressing the feedback above."
        )

    prompt = prompt_template.format(
        research_results=state.get("research_results", ""),
        user_input=state.get("user_input", ""),
        revision_context=revision_context,
    )

    if state.get("uploaded_file_text"):
        prompt += f"\n\nSource material from uploaded file:\n{state['uploaded_file_text'][:5000]}"

    result = await llm_completion(prompt)

    # Extract hook (first 2 lines) and CTA (last line with ?)
    lines = [l for l in result.strip().split("\n") if l.strip()]
    hook = "\n".join(lines[:2]) if lines else ""
    cta = ""
    for line in reversed(lines):
        if "?" in line:
            cta = line.strip()
            break

    revision_count = state.get("revision_count", 0)
    if state.get("approval_feedback"):
        revision_count += 1

    return {
        "draft_content": result,
        "draft_hook": hook,
        "draft_cta": cta,
        "revision_count": revision_count,
        "current_stage": "draft",
    }
