# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Link Agent is an AI-powered LinkedIn content creation system. It uses a LangGraph agent pipeline (research → draft → image generation → optimize → proofread → approve) with human-in-the-loop approval. The backend calls Claude via the `claude` CLI subprocess (not the API SDK), and uses Google Gemini for image generation.

## Commands

### Database
```bash
docker-compose up -d              # Start PostgreSQL
docker-compose down               # Stop PostgreSQL
docker-compose --profile tools up -d  # Start with pgAdmin (localhost:5050)
```

### Backend (from /backend)
```bash
pip install -e ".[dev]"           # Install with dev dependencies
alembic upgrade head              # Run migrations
alembic revision --autogenerate -m "description"  # Create migration
uvicorn app.main:app --reload     # Dev server (localhost:8000)
ruff check .                      # Lint
ruff format .                     # Format
pytest                            # Run tests
pytest tests/test_foo.py::test_bar  # Single test
```

### Frontend (from /frontend)
```bash
npm install                       # Install dependencies
npm run dev                       # Dev server (localhost:3000)
npm run build                     # Production build
npm run lint                      # ESLint
```

## Architecture

### Backend (`/backend/app/`)

**FastAPI** application with async SQLAlchemy (asyncpg) and PostgreSQL.

- **`main.py`** — App entry point. Initializes the LangGraph checkpointer in a lifespan handler.
- **`config.py`** — Pydantic Settings loading from `.env` (DATABASE_URL, CLAUDE_MODEL, GEMINI_API_KEY, etc.)
- **`dependencies.py`** — FastAPI dependency injection for DB sessions.

**API routes** (`api/`): `posts`, `agent`, `calendar`, `uploads`, `settings`, `health`. The agent route streams real-time updates via SSE.

**Agent pipeline** (`agent/`):
- `state.py` — `AgentState` TypedDict defining all fields passed between nodes.
- `graph.py` — Builds the LangGraph `StateGraph` with 6 linear nodes. The `approve` node uses LangGraph's interrupt mechanism for human review.
- `nodes/` — One file per pipeline stage. Each node calls `llm_completion()` and returns state updates.
- `prompts/` — Format-specific prompt templates (framework, strong_pov, simplification, story, leader_lens).

**Services** (`services/`):
- `llm.py` — Wraps the `claude` CLI as a subprocess (not the Anthropic SDK). Requires `claude` CLI installed and authenticated. Strips `CLAUDECODE` env var to avoid nesting issues.
- `image_gen.py` — Google Gemini (`google-genai`) image generation.
- `file_parser.py` — Extracts text from PDF, PPTX, TXT uploads.

**Models** (`models/`): SQLAlchemy models with enums — `Post`, `Draft`, `CalendarEntry`, `MediaAsset`, `UserSettings`.

**Migrations**: Alembic in `alembic/`. Uses async engine. Two DATABASE_URL env vars: `DATABASE_URL` (asyncpg for app) and `CHECKPOINT_DATABASE_URL` (psycopg for LangGraph checkpointer).

### Frontend (`/frontend/src/`)

**Next.js 16** with App Router, React 19, TypeScript, Tailwind CSS 4.

- **`app/`** — Pages: home, `create/` (multi-step wizard), `posts/[id]/`, `calendar/`, `settings/`.
- **`hooks/`** — Custom hooks using TanStack React Query v5: `usePosts`, `useAgent`, `useSSE` (EventSource streaming), `useCalendar`, `useSettings`.
- **`lib/api.ts`** — Axios client pointing at `NEXT_PUBLIC_API_URL`. All backend calls go through here.
- **`lib/types.ts`** — TypeScript interfaces mirroring backend schemas.
- **`lib/constants.ts`** — Content pillars, formats, statuses with display labels/colors.
- **`components/`** — Organized by domain: `ui/`, `layout/`, `posts/`, `create/`, `calendar/`, `agent/`.

### Key Data Flow

1. User fills `CreatePostForm` → POST to `/api/posts/` creates a Post record
2. Frontend calls `/api/agent/run/{post_id}` and opens SSE stream at `/api/agent/stream/{thread_id}`
3. LangGraph runs nodes sequentially; each node updates state and the API emits SSE events
4. At `approve` node, LangGraph interrupts — user can accept or provide revision feedback
5. On revision, the graph resumes from `draft` with feedback in state; on accept, post status becomes APPROVED

## Environment Setup

Copy `.env.example` to `.env`. The `claude` CLI must be installed globally (`npm install -g @anthropic-ai/claude-code`) and authenticated. A Gemini API key is required for image generation.

## Code Style

- **Python**: Ruff (target Python 3.11+, 100 char line length). Async/await throughout.
- **TypeScript**: ESLint with Next.js config. No import aliases.
