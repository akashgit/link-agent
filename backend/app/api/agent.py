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
from app.schemas.agent import AgentRunRequest, AgentRunResponse, AgentResumeRequest, AgentStatusResponse

router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)


def _disk_path_to_url(disk_path: str) -> str:
    """Convert a disk file path to an HTTP URL for the file serving endpoint."""
    if not disk_path:
        return ""
    filename = os.path.basename(disk_path)
    return f"/api/uploads/file/{filename}"


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
                        if isinstance(interrupt_value, dict) and interrupt_value.get("image_url"):
                            interrupt_value["image_url"] = _disk_path_to_url(interrupt_value["image_url"])
                        yield {
                            "event": "interrupt",
                            "data": json.dumps(interrupt_value),
                        }
                    else:
                        event_data = {
                            "node": node_name,
                            "stage": node_output.get("current_stage", node_name),
                        }

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

                        yield {
                            "event": "node_complete",
                            "data": json.dumps(event_data),
                        }

                        # Save draft if draft node completed
                        if node_name == "draft" and node_output.get("draft_content"):
                            max_ver = await db.execute(
                                select(func.coalesce(func.max(Draft.version), 0))
                                .where(Draft.post_id == post.id)
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
                            if isinstance(interrupt_value, dict) and interrupt_value.get("image_url"):
                                interrupt_value["image_url"] = _disk_path_to_url(interrupt_value["image_url"])
                            yield {
                                "event": "interrupt",
                                "data": json.dumps(interrupt_value),
                            }
                        else:
                            event_data = {
                                "node": node_name,
                                "stage": node_output.get("current_stage", node_name),
                            }

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

                            yield {
                                "event": "node_complete",
                                "data": json.dumps(event_data),
                            }

                            # Save draft if draft node completed
                            if post and node_name == "draft" and node_output.get("draft_content"):
                                max_ver = await db.execute(
                                    select(func.coalesce(func.max(Draft.version), 0))
                                    .where(Draft.post_id == post.id)
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
