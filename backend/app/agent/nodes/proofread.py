import re

from app.agent.state import AgentState
from app.agent.prompts.proofread import PROOFREAD_PROMPT
from app.services.llm import llm_completion


async def proofread_node(state: AgentState) -> dict:
    prompt = PROOFREAD_PROMPT.format(
        optimized_content=state.get("optimized_content", ""),
    )

    result = await llm_completion(prompt)

    # Parse sections
    proofread = ""
    corrections = []
    tone_passed = True

    proof_match = re.search(r"## Proofread Post\n(.*?)(?=## Corrections Made|\Z)", result, re.DOTALL)
    if proof_match:
        proofread = proof_match.group(1).strip()

    corr_match = re.search(r"## Corrections Made\n(.*?)(?=## Tone Check|\Z)", result, re.DOTALL)
    if corr_match:
        corrections = [
            line.strip().lstrip("0123456789.-) ")
            for line in corr_match.group(1).strip().split("\n")
            if line.strip()
        ]

    tone_match = re.search(r"## Tone Check\n(.*?)$", result, re.DOTALL)
    if tone_match:
        tone_text = tone_match.group(1).strip().upper()
        tone_passed = "PASS" in tone_text

    return {
        "proofread_content": proofread or state.get("optimized_content", ""),
        "proofread_corrections": corrections,
        "tone_check_passed": tone_passed,
        "current_stage": "proofread",
    }
