from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.router import api_router
from app.agent.checkpointer import init_checkpointer, close_checkpointer


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_checkpointer()
    yield
    await close_checkpointer()


app = FastAPI(
    title="Link Agent API",
    description="AI-powered LinkedIn content agent",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)
