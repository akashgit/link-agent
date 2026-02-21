import os
import uuid
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse
from langgraph.types import Command

from app.dependencies import get_db
from app.models.post import Post, Draft, PostStatus
from app.models.media_asset import MediaAsset, MediaSource
from app.agent.graph import build_graph
from app.agent.checkpointer import get_checkpointer
from app.schemas.agent import (
    AgentRunRequest,
    AgentRunResponse,
    AgentResumeRequest,
    AgentStatusResponse,
)

router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)


def _disk_path_to_url(disk_path: str) -> str:
    """Convert a disk file path to an HTTP URL for the file serving endpoint."""
    if not disk_path:
        return ""
    filename = os.path.basename(disk_path)
    return f"/api/uploads/file/{filename}"


def _build_event_data(node_name: str, node_output: dict) -> dict:
    """Build enriched SSE event data with stage descriptions and content previews."""
    event_data: dict = {
        "node": node_name,
        "stage": node_output.get("current_stage", node_name),
    }

    if node_name == "research":
        angles = node_output.get("trending_angles", [])
        event_data["description"] = f"Found {len(angles)} trending angles"
        if angles:
            event_data["details"] = angles[:3]

    elif node_name == "draft":
        content = node_output.get("draft_content", "")
        event_data["description"] = f"Draft created ({len(content)} chars)"
        if content:
            event_data["draft_content"] = content
        hook = node_output.get("draft_hook", "")
        if hook:
            event_data["draft_hook"] = hook

    elif node_name == "generate_image":
        status = node_output.get("image_generation_status", "")
        if status == "skipped_no_key":
            event_data["description"] = "Image generation skipped (no API key)"
        elif node_output.get("image_url"):
            event_data["description"] = "Image generated successfully"
        else:
            event_data["description"] = "Image generation attempted"

    elif node_name == "optimize":
        changes = node_output.get("optimization_changes", [])
        fact_checked = node_output.get("fact_check_performed", False)
        parts = []
        if changes:
            parts.append(f"{len(changes)} optimizations applied")
        if fact_checked:
            claims = node_output.get("fact_check_results", [])
            parts.append(f"{len(claims)} claims fact-checked")
        img_decision = node_output.get("image_source_decision", "")
        if img_decision == "retrieved":
            parts.append("web image selected")
        event_data["description"] = ", ".join(parts) if parts else "Post optimized"
        if changes:
            event_data["details"] = changes[:5]

    elif node_name == "proofread":
        corrections = node_output.get("proofread_corrections", [])
        tone_passed = node_output.get("tone_check_passed", True)
        parts = []
        if corrections:
            parts.append(f"{len(corrections)} corrections")
        parts.append("tone check " + ("passed" if tone_passed else "failed"))
        char_count = node_output.get("linkedin_char_count", 0)
        if char_count:
            parts.append(f"{char_count} chars")
        event_data["description"] = ", ".join(parts)

    return event_data


@router.post("/run", response_model=AgentRunResponse)
async def run_agent(request: AgentRunRequest, db: AsyncSession = Depends(get_db)):
    # Verify post exists
    result = await db.execute(select(Post).where(Post.id == uuid.UUID(request.post_id)))
    post = result.scalar_one_or_none()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    thread_id = str(uuid.uuid4())

    # Update post
    post.thread_id = thread_id
    post.status = PostStatus.DRAFTING
    if request.user_input:
        post.user_input = request.user_input
    if request.uploaded_file_text:
        post.uploaded_file_text = request.uploaded_file_text
    await db.commit()

    return AgentRunResponse(
        thread_id=thread_id,
        post_id=request.post_id,
        status="started",
    )


@router.get("/stream/{thread_id}")
async def stream_agent(thread_id: str, db: AsyncSession = Depends(get_db)):
    async def event_generator():
        try:
            checkpointer = await get_checkpointer()
            graph = build_graph()
            compiled = graph.compile(checkpointer=checkpointer)

            # Get post by thread_id
            result = await db.execute(select(Post).where(Post.thread_id == thread_id))
            post = result.scalar_one_or_none()
            if not post:
                yield {"event": "error", "data": json.dumps({"error": "Post not found"})}
                return

            config = {"configurable": {"thread_id": thread_id}}

            # Query extracted images for this post
            uploaded_images = []
            img_result = await db.execute(
                select(MediaAsset).where(
                    MediaAsset.post_id == post.id,
                    MediaAsset.source == MediaSource.EXTRACTED,
                )
            )
            for asset in img_result.scalars().all():
                uploaded_images.append(asset.file_path)

            initial_state = {
                "user_input": post.user_input or post.title,
                "content_pillar": post.content_pillar,
                "post_format": post.post_format,
                "post_id": str(post.id),
                "uploaded_file_text": post.uploaded_file_text or "",
                "uploaded_images": uploaded_images,
                "revision_count": 0,
            }

            async for event in compiled.astream(initial_state, config, stream_mode="updates"):
                for node_name, node_output in event.items():
                    if node_name == "__interrupt__":
                        # Convert image_url from disk path to HTTP URL
                        interrupt_value = node_output[0].value if node_output else {}
                        if isinstance(interrupt_value, dict):
                            if interrupt_value.get("image_url"):
                                interrupt_value["image_url"] = _disk_path_to_url(
                                    interrupt_value["image_url"]
                                )
                            if interrupt_value.get("original_image_url"):
                                interrupt_value["original_image_url"] = _disk_path_to_url(
                                    interrupt_value["original_image_url"]
                                )
                        yield {
                            "event": "interrupt",
                            "data": json.dumps(interrupt_value),
                        }
                    else:
                        event_data = _build_event_data(node_name, node_output)

                        # Handle image generation completion
                        if node_name == "generate_image" and node_output.get("image_url"):
                            disk_path = node_output["image_url"]
                            http_url = _disk_path_to_url(disk_path)
                            event_data["image_url"] = http_url

                            # Create MediaAsset record for generated image
                            if os.path.exists(disk_path):
                                img_asset = MediaAsset(
                                    post_id=post.id,
                                    filename=os.path.basename(disk_path),
                                    file_path=disk_path,
                                    content_type="image/png",
                                    file_size=os.path.getsize(disk_path),
                                    source=MediaSource.GENERATED,
                                    prompt_used=node_output.get("image_prompt", ""),
                                )
                                db.add(img_asset)
                                await db.commit()

                        # Handle optimize node image changes
                        if node_name == "optimize":
                            if node_output.get(
                                "image_source_decision"
                            ) == "retrieved" and node_output.get("image_url"):
                                disk_path = node_output["image_url"]
                                http_url = _disk_path_to_url(disk_path)
                                event_data["image_url"] = http_url

                                if os.path.exists(disk_path):
                                    img_asset = MediaAsset(
                                        post_id=post.id,
                                        filename=os.path.basename(disk_path),
                                        file_path=disk_path,
                                        content_type="image/jpeg",
                                        file_size=os.path.getsize(disk_path),
                                        source=MediaSource.WEB_RETRIEVED,
                                    )
                                    db.add(img_asset)
                                    await db.commit()

                            if node_output.get("fact_check_performed"):
                                event_data["fact_check_performed"] = True
                                event_data["claims_checked"] = len(
                                    node_output.get("fact_check_results", [])
                                )

                        yield {
                            "event": "node_complete",
                            "data": json.dumps(event_data),
                        }

                        # Save draft if draft node completed
                        if node_name == "draft" and node_output.get("draft_content"):
                            max_ver = await db.execute(
                                select(func.coalesce(func.max(Draft.version), 0)).where(
                                    Draft.post_id == post.id
                                )
                            )
                            next_version = max_ver.scalar() + 1
                            draft = Draft(
                                post_id=post.id,
                                version=next_version,
                                content=node_output["draft_content"],
                                hook=node_output.get("draft_hook"),
                                cta=node_output.get("draft_cta"),
                            )
                            db.add(draft)
                            await db.commit()

            # Check final state
            state = await compiled.aget_state(config)
            final = state.values
            if final.get("approval_status") == "approved":
                post.status = PostStatus.APPROVED
                post.final_content = final.get("proofread_content", "")
                post.revision_count = final.get("revision_count", 0)
                await db.commit()
                yield {
                    "event": "complete",
                    "data": json.dumps({"status": "approved", "post_id": str(post.id)}),
                }
            else:
                yield {
                    "event": "paused",
                    "data": json.dumps({"status": "awaiting_approval"}),
                }

        except Exception as e:
            logger.error(f"Agent stream error: {e}", exc_info=True)
            yield {"event": "error", "data": json.dumps({"error": str(e)})}

    return EventSourceResponse(event_generator())


@router.post("/resume/{thread_id}")
async def resume_agent(
    thread_id: str, request: AgentResumeRequest, db: AsyncSession = Depends(get_db)
):
    try:
        checkpointer = await get_checkpointer()
        graph = build_graph()
        compiled = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}}

        # Resume with user's decision
        command = Command(resume={"status": request.status, "feedback": request.feedback or ""})

        async def event_generator():
            try:
                result = await db.execute(select(Post).where(Post.thread_id == thread_id))
                post = result.scalar_one_or_none()

                async for event in compiled.astream(command, config, stream_mode="updates"):
                    for node_name, node_output in event.items():
                        if node_name == "__interrupt__":
                            interrupt_value = node_output[0].value if node_output else {}
                            if isinstance(interrupt_value, dict):
                                if interrupt_value.get("image_url"):
                                    interrupt_value["image_url"] = _disk_path_to_url(
                                        interrupt_value["image_url"]
                                    )
                                if interrupt_value.get("original_image_url"):
                                    interrupt_value["original_image_url"] = _disk_path_to_url(
                                        interrupt_value["original_image_url"]
                                    )
                            yield {
                                "event": "interrupt",
                                "data": json.dumps(interrupt_value),
                            }
                        else:
                            event_data = _build_event_data(node_name, node_output)

                            # Handle image generation completion
                            if node_name == "generate_image" and node_output.get("image_url"):
                                disk_path = node_output["image_url"]
                                http_url = _disk_path_to_url(disk_path)
                                event_data["image_url"] = http_url

                                if post and os.path.exists(disk_path):
                                    img_asset = MediaAsset(
                                        post_id=post.id,
                                        filename=os.path.basename(disk_path),
                                        file_path=disk_path,
                                        content_type="image/png",
                                        file_size=os.path.getsize(disk_path),
                                        source=MediaSource.GENERATED,
                                        prompt_used=node_output.get("image_prompt", ""),
                                    )
                                    db.add(img_asset)
                                    await db.commit()

                            # Handle optimize node image changes
                            if node_name == "optimize" and post:
                                if node_output.get(
                                    "image_source_decision"
                                ) == "retrieved" and node_output.get("image_url"):
                                    disk_path = node_output["image_url"]
                                    http_url = _disk_path_to_url(disk_path)
                                    event_data["image_url"] = http_url

                                    if os.path.exists(disk_path):
                                        img_asset = MediaAsset(
                                            post_id=post.id,
                                            filename=os.path.basename(disk_path),
                                            file_path=disk_path,
                                            content_type="image/jpeg",
                                            file_size=os.path.getsize(disk_path),
                                            source=MediaSource.WEB_RETRIEVED,
                                        )
                                        db.add(img_asset)
                                        await db.commit()

                                if node_output.get("fact_check_performed"):
                                    event_data["fact_check_performed"] = True
                                    event_data["claims_checked"] = len(
                                        node_output.get("fact_check_results", [])
                                    )

                            yield {
                                "event": "node_complete",
                                "data": json.dumps(event_data),
                            }

                            # Save draft if draft node completed
                            if post and node_name == "draft" and node_output.get("draft_content"):
                                max_ver = await db.execute(
                                    select(func.coalesce(func.max(Draft.version), 0)).where(
                                        Draft.post_id == post.id
                                    )
                                )
                                next_version = max_ver.scalar() + 1
                                draft = Draft(
                                    post_id=post.id,
                                    version=next_version,
                                    content=node_output["draft_content"],
                                    hook=node_output.get("draft_hook"),
                                    cta=node_output.get("draft_cta"),
                                )
                                db.add(draft)
                                await db.commit()

                # Check final state
                state = await compiled.aget_state(config)
                final = state.values

                if final.get("approval_status") == "approved" and post:
                    post.status = PostStatus.APPROVED
                    post.final_content = final.get("proofread_content", "")
                    post.revision_count = final.get("revision_count", 0)
                    await db.commit()
                    yield {
                        "event": "complete",
                        "data": json.dumps({"status": "approved", "post_id": str(post.id)}),
                    }
                else:
                    yield {
                        "event": "paused",
                        "data": json.dumps({"status": "awaiting_approval"}),
                    }

            except Exception as e:
                logger.error(f"Agent resume error: {e}", exc_info=True)
                yield {"event": "error", "data": json.dumps({"error": str(e)})}

        return EventSourceResponse(event_generator())

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{thread_id}", response_model=AgentStatusResponse)
async def agent_status(thread_id: str):
    try:
        checkpointer = await get_checkpointer()
        graph = build_graph()
        compiled = graph.compile(checkpointer=checkpointer)
        config = {"configurable": {"thread_id": thread_id}}

        state = await compiled.aget_state(config)
        if state and state.values:
            return AgentStatusResponse(
                thread_id=thread_id,
                current_stage=state.values.get("current_stage"),
                status=state.values.get("approval_status", "in_progress"),
            )
        return AgentStatusResponse(
            thread_id=thread_id,
            current_stage=None,
            status="not_found",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
