import uuid
import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sse_starlette.sse import EventSourceResponse
from langgraph.types import Command

from app.dependencies import get_db
from app.models.post import Post, Draft, PostStatus
from app.agent.graph import build_graph
from app.agent.checkpointer import get_checkpointer
from app.schemas.agent import AgentRunRequest, AgentRunResponse, AgentResumeRequest, AgentStatusResponse
from app.utils.sse import format_sse

router = APIRouter(prefix="/agent", tags=["agent"])
logger = logging.getLogger(__name__)


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

            initial_state = {
                "user_input": post.user_input or post.title,
                "content_pillar": post.content_pillar,
                "post_format": post.post_format,
                "post_id": str(post.id),
                "revision_count": 0,
            }

            async for event in compiled.astream(initial_state, config, stream_mode="updates"):
                for node_name, node_output in event.items():
                    if node_name == "__interrupt__":
                        yield {
                            "event": "interrupt",
                            "data": json.dumps(node_output[0].value if node_output else {}),
                        }
                    else:
                        yield {
                            "event": "node_complete",
                            "data": json.dumps({
                                "node": node_name,
                                "stage": node_output.get("current_stage", node_name),
                            }),
                        }

                        # Save draft if draft node completed
                        if node_name == "draft" and node_output.get("draft_content"):
                            draft = Draft(
                                post_id=post.id,
                                version=(post.revision_count or 0) + 1,
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
                async for event in compiled.astream(command, config, stream_mode="updates"):
                    for node_name, node_output in event.items():
                        if node_name == "__interrupt__":
                            yield {
                                "event": "interrupt",
                                "data": json.dumps(node_output[0].value if node_output else {}),
                            }
                        else:
                            yield {
                                "event": "node_complete",
                                "data": json.dumps({
                                    "node": node_name,
                                    "stage": node_output.get("current_stage", node_name),
                                }),
                            }

                # Check final state
                result = await db.execute(select(Post).where(Post.thread_id == thread_id))
                post = result.scalar_one_or_none()
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
