from app.agent.state import AgentState
from app.agent.prompts.image_prompt import IMAGE_PROMPT_TEMPLATE
from app.services.llm import llm_completion
from app.services.image_gen import generate_image


async def generate_image_node(state: AgentState) -> dict:
    # If uploaded images exist, use the first one instead of generating
    uploaded_images = state.get("uploaded_images", [])
    if uploaded_images:
        return {
            "image_prompt": "",
            "image_url": uploaded_images[0],
            "image_generation_status": "uploaded",
            "current_stage": "generate_image",
        }

    # Generate image prompt from post content
    prompt = IMAGE_PROMPT_TEMPLATE.format(
        post_content=state.get("draft_content", ""),
        post_format=state.get("post_format", ""),
        content_pillar=state.get("content_pillar", ""),
    )

    image_prompt = await llm_completion(prompt, max_tokens=200, temperature=0.5)

    # Generate image
    result = await generate_image(image_prompt.strip())

    if result["success"]:
        return {
            "image_prompt": image_prompt.strip(),
            "image_url": result["file_path"],
            "image_generation_status": "success",
            "current_stage": "generate_image",
        }
    else:
        return {
            "image_prompt": image_prompt.strip(),
            "image_url": "",
            "image_generation_status": f"failed: {result['error']}",
            "current_stage": "generate_image",
        }
