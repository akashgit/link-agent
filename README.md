# Link Agent

AI-powered LinkedIn content creation system with a multi-stage agent pipeline, human-in-the-loop approval, and a real-time streaming UI.

## How It Works

Link Agent runs a LangGraph pipeline that takes a topic and produces a publish-ready LinkedIn post:

```
Research → Draft → Image Generation → Optimize → Proofread → Approve
```

Each stage runs sequentially and streams progress to the frontend via SSE. At the **Approve** stage, the pipeline pauses for human review — you can approve the post, make manual edits, or send it back for revision with feedback.

## Features

- **Multi-format content** — Framework posts, strong POV, simplification, stories, and leader lens formats, each with tailored prompts
- **Fact-checking** — The optimize stage cross-references claims against web sources via Tavily and corrects inaccuracies
- **AI image generation** — Generates post images using Google Gemini
- **Human-in-the-loop** — LangGraph interrupt mechanism lets you review, edit, and approve before finalizing
- **Version history** — Every pipeline stage (draft, optimize, proofread) saves a versioned snapshot with stage badges
- **Content calendar** — Plan and schedule posts across content pillars
- **LinkedIn preview** — Real-time preview showing how your post will look on LinkedIn, with automatic markdown stripping
- **Typefully integration** — Push approved posts to Typefully for scheduling and publishing

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Frontend (Next.js 16 / React 19 / TanStack Query)      │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐ │
│  │ Create   │ │ Post     │ │ Calendar │ │ Settings   │ │
│  │ Wizard   │ │ Detail   │ │          │ │            │ │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘ │
│         │           ▲ SSE                               │
│         ▼           │                                   │
├─────────────────────────────────────────────────────────┤
│  Backend (FastAPI / async SQLAlchemy / PostgreSQL)       │
│  ┌──────────────────────────────────────────────────┐   │
│  │  LangGraph Agent Pipeline                        │   │
│  │  research → draft → image → optimize → proofread │   │
│  │                                    ↓             │   │
│  │                              [interrupt]         │   │
│  │                           approve / revise       │   │
│  └──────────────────────────────────────────────────┘   │
│  LLM: Claude CLI subprocess    Images: Google Gemini    │
└─────────────────────────────────────────────────────────┘
```

### Backend (`/backend`)

- **FastAPI** with async SQLAlchemy (asyncpg) and PostgreSQL
- **LangGraph** state graph with 6 nodes and interrupt-based human review
- **Claude CLI** as the LLM backend (subprocess, not API SDK) — requires `claude` CLI installed and authenticated
- **Google Gemini** for image generation
- **Tavily** for fact-check web search (optional)
- **Alembic** for database migrations

### Frontend (`/frontend`)

- **Next.js 16** with App Router and React 19
- **TanStack React Query v5** for data fetching
- **SSE streaming** for real-time pipeline progress
- **Tailwind CSS 4** for styling

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL (via Docker or local install)
- [Claude CLI](https://docs.anthropic.com/en/docs/claude-code) installed and authenticated

### 1. Clone and configure

```bash
git clone https://github.com/akashgit/link-agent.git
cd link-agent
cp .env.example .env
# Edit .env with your API keys
```

### 2. Start PostgreSQL

```bash
docker-compose up -d
```

### 3. Backend setup

```bash
cd backend
pip install -e ".[dev]"
alembic upgrade head
uvicorn app.main:app --reload
```

The API runs at `http://localhost:8000`.

### 4. Frontend setup

```bash
cd frontend
npm install
npm run dev
```

The UI runs at `http://localhost:3000`.

### 5. (Optional) Seed the content calendar

```bash
cd backend
python seed_calendar.py
```

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `DATABASE_URL` | Yes | PostgreSQL connection (asyncpg) |
| `CHECKPOINT_DATABASE_URL` | Yes | PostgreSQL connection (psycopg, for LangGraph) |
| `CLAUDE_MODEL` | No | Claude model to use (default: `sonnet`) |
| `GEMINI_API_KEY` | No | Google Gemini API key for image generation |
| `TAVILY_API_KEY` | No | Enables fact-checking in the optimize stage |
| `TYPEFULLY_API_KEY` | No | Enables publishing to LinkedIn via Typefully |
| `OPENROUTER_API_KEY` | No | Alternative image generation via OpenRouter |
| `CORS_ORIGINS` | No | Allowed CORS origins (default: `http://localhost:3000`) |

## Development

### Backend

```bash
ruff check .          # Lint
ruff format .         # Format
pytest                # Run tests
```

### Frontend

```bash
npm run lint          # ESLint
npm run build         # Production build
```

### Database migrations

```bash
cd backend
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Content Pillars

The system organizes content around five pillars:

- **AgentOps** — Production agent systems, reliability, evaluation
- **Inference Scaling** — Latency, throughput, reasoning at scale
- **Enterprise Reality** — Real-world deployment vs. benchmarks
- **Research to Product** — Bridging the gap from papers to production
- **Leadership** — Team building, hiring, strategic decisions

Each pillar pairs with one of five post formats (Framework, Strong POV, Simplification, Story, Leader Lens) to produce varied, consistent content.

## Project Structure

```
link-agent/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph pipeline
│   │   │   ├── graph.py    # State graph definition
│   │   │   ├── nodes/      # Pipeline stage implementations
│   │   │   ├── prompts/    # Format-specific prompt templates
│   │   │   └── state.py    # AgentState TypedDict
│   │   ├── api/            # FastAPI route handlers
│   │   ├── models/         # SQLAlchemy models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # LLM, image gen, file parsing
│   │   └── utils/          # LinkedIn validation, markdown stripping
│   └── alembic/            # Database migrations
├── frontend/
│   └── src/
│       ├── app/            # Next.js pages
│       ├── components/     # UI components (by domain)
│       ├── hooks/          # React Query hooks
│       ├── lib/            # API client, types, constants
│       └── utils/          # Formatting, markdown stripping
└── docs/                   # Strategy and planning docs
```

## License

MIT
