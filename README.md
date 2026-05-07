# ARIA — Agentic RAG Intelligence Architecture

> **Status: Active Development** — Core infrastructure is complete. Agent logic is currently being implemented incrementally.

ARIA is a multi-agent RAG system built on LangGraph. A user submits a research query via a REST API; the request is dispatched asynchronously to a Celery worker, which runs a LangGraph agent pipeline that plans, researches, critiques, evaluates, and synthesizes a response. The system is designed from the ground up for multi-tenancy and production deployment.

---

## Architecture

```
User Request
     │
     ▼
FastAPI (REST API)
     │  auth middleware (per-tenant)
     ▼
Celery Worker (async task queue)
     │  backed by Redis
     ▼
LangGraph Agent Pipeline
     │
     ├── Planner      — breaks the query into a research plan
     ├── Researcher   — retrieves relevant information (RAG + web search)
     ├── Critic       — evaluates quality and identifies gaps
     ├── Evaluator    — scores and filters results
     └── Synthesizer  — produces the final structured response
     │
     ▼
PostgreSQL (job tracking, tenant management)
```

---

## Tech Stack

| Layer | Technology |
|---|---|
| Agent framework | LangGraph |
| LLM (current) | Ollama (qwen3) — abstracted for API swap |
| API | FastAPI |
| Task queue | Celery + Redis |
| Database | PostgreSQL + SQLAlchemy (async) |
| Migrations | Alembic |
| Retrieval | RAG search + web search tools |
| Containerisation | Docker + Docker Compose |
| CI/CD | GitHub Actions |
| Dependency management | uv |

---

## Project Structure

```
src/
├── agent/          # LangGraph graph definition and agent nodes
│   └── nodes/      # planner, researcher, critic, evaluator, synthesizer
├── api/            # FastAPI app, routes, auth middleware
├── core/           # config, logging, error handling
├── db/             # SQLAlchemy models, session, repository pattern
├── llm/            # LLM abstraction layer (Ollama, extensible to API)
├── tools/          # RAG search, web search, tool registry
└── workers/        # Celery app and async task definitions
migrations/         # Alembic migration versions
```

---

## Getting Started

### Prerequisites

- Docker and Docker Compose
- [Ollama](https://ollama.com) running locally

### 1. Pull the LLM model

```bash
ollama pull qwen3:0.6b
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start the stack

```bash
docker compose up --build
```

This starts: FastAPI, PostgreSQL, Redis, Celery worker, and Ollama.

### 4. Run database migrations

```bash
make migrate
# or: uv run alembic upgrade head
```

### 5. Test the API

```bash
curl -X POST http://localhost:8000/research \
  -H "Content-Type: application/json" \
  -d '{"query": "your research question here"}'
```

---

## Roadmap

- [x] FastAPI backend with tenant-aware auth middleware
- [x] Async task queue (Celery + Redis)
- [x] PostgreSQL with Alembic migrations and repository pattern
- [x] LangGraph agent pipeline scaffold (planner, researcher, critic, evaluator, synthesizer)
- [x] LLM abstraction layer (Ollama, extensible to OpenAI / Anthropic)
- [x] RAG search and web search tools
- [x] Docker + GitHub Actions CI/CD
- [ ] Full agent node implementation
- [ ] Vector database integration
- [ ] Prompt optimisation and evaluation framework
- [ ] Shift to production LLM API
- [ ] Frontend interface

---

## Development Notes

### Adding a new Alembic migration

```bash
uv run alembic revision --autogenerate -m "describe your change"
uv run alembic upgrade head
```

> When adding a non-nullable column to an existing table: first migrate with `nullable=True`, populate the column, then migrate again with `nullable=False`.

---

## Contributing

This project is under active development. Feel free to open issues or submit pull requests.

---

## License

MIT
