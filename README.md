# AI Agent Platform

A production-grade, multi-channel **AI Agent Platform** that connects conversational LLM agents to real messaging channels (WhatsApp today, with a channel-agnostic core ready for Telegram, Slack, Discord, Teams, and web). The platform is built on **FastAPI** for the HTTP layer, **LangGraph** for agent orchestration, **Groq / LangChain** as the LLM backend, and **SQLAlchemy + PostgreSQL** for persistence.

At its heart, every inbound message follows one deterministic pipeline:

```
Channel (WhatsApp) ─► Adapter (normalize) ─► ChannelService ─► AgentService
                                                                    │
                                          User / Conversation / Message persistence
                                                                    │
                                            LangGraph workflow (chat → tool → chat)
                                                                    │
                          LLM provider (Groq) ◄── PromptComposer / ToolDecisionEngine
                                                                    │
                       OutgoingChannelMessage ─► WhatsApp Cloud API (reply)
```

The codebase follows a strict layered architecture: the **API layer contains no business logic**, **services own transactions and orchestration**, **repositories own data access**, and the **agent subsystem is completely independent of FastAPI and the database**.

---

## Table of Contents

- [Overview](#overview)
- [Project Architecture & Structure](#project-architecture--structure)
- [How the Agent Works](#how-the-agent-works)
- [Core Database Models](#core-database-models)
- [API Endpoints](#api-endpoints)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Getting Started & Installation](#getting-started--installation)
- [Testing](#testing)
- [Configuration Reference](#configuration-reference)
- [Author & Social Links](#author--social-links)

---

## Overview

The AI Agent Platform is an extensible backend for running tool-using conversational agents across communication channels. It provides:

- **Agent orchestration** with a LangGraph state machine (nodes, conditional edges, and a memory checkpointer).
- **A provider-agnostic LLM abstraction** (`BaseLLMProvider`) with a Groq implementation and a factory for adding new providers.
- **A provider-agnostic tool framework**: a registry, a decision engine that adapts to provider capabilities, tool-calling adapters, and concrete tools (calculator, datetime, web search, HTTP client).
- **Channel abstraction** (`BaseChannelAdapter` + normalized domain models) so vendor-specific payloads never leak into business logic. WhatsApp Cloud API is fully wired; other channels are enumerated and ready to implement.
- **Persistent conversation memory** in PostgreSQL (users, conversations, messages) plus a LangGraph checkpointer for graph state.
- **Clean dependency injection** through FastAPI `Depends`, with composable repositories and services.

---

## Project Architecture & Structure

```
ai-agent-platform/
├── app/                          # Application package (all runtime code)
│   ├── main.py                   # FastAPI app factory, middleware, router registration
│   ├── agents/                   # Agent subsystem (LLM orchestration, tools, prompts)
│   ├── api/                      # HTTP layer: routers, schemas, dependencies, middleware
│   ├── channels/                 # Messaging channel adapters (WhatsApp, Telegram, ...)
│   ├── core/                     # Cross-cutting config, logging, security, constants
│   ├── database/                 # SQLAlchemy engine, session, base model, ORM models
│   ├── exceptions/               # Global exception handlers
│   ├── llm/                      # LLM provider abstraction and implementations
│   ├── repositories/             # Data-access layer (one repository per model)
│   ├── services/                 # Business logic & transaction orchestration
│   └── utils/                    # Shared helper utilities
├── alembic/                      # Database migration environment
│   ├── env.py                    # Alembic runtime config (loads settings + metadata)
│   └── versions/                 # Migration scripts (initial schema)
├── tests/                        # Pytest suite (unit + end-to-end)
│   └── fixtures/                 # Reusable test doubles (e.g. DummyLLMProvider)
├── flow/                         # Architecture flow diagrams (PDFs)
├── docs/                         # Additional documentation
├── scripts/                      # Operational / helper scripts
├── alembic.ini                   # Alembic configuration
├── pyproject.toml                # Project metadata
├── requirements.txt              # Python dependencies
├── .env                          # Local environment variables (not committed)
└── README.md
```

### `app/agents` — Agent Subsystem

The intelligence of the platform. Fully decoupled from FastAPI and SQLAlchemy.

| Path | Responsibility |
| --- | --- |
| `agents/runner.py` | `AgentRunner`: builds runtime context + compiled graph, then executes the workflow. |
| `agents/graph/builder.py` | `GraphBuilder`: constructs and compiles the LangGraph `StateGraph`. |
| `agents/state/conversation_state.py` | `ConversationState` TypedDict — the shared state flowing through the graph. |
| `agents/nodes/chat.py` | `chat_node`: calls the LLM and asks the decision engine whether a tool is needed. |
| `agents/nodes/tool_execution.py` | `tool_execution_node`: runs a requested tool with timeout + error handling. |
| `agents/edges/tool_routing.py` | `route_after_chat`: conditional edge deciding `tool_execution` vs `END`. |
| `agents/runtime/builder.py` / `context.py` | `RuntimeBuilder` + `AgentContext`: assembles shared runtime dependencies. |
| `agents/memory/checkpointer.py` | LangGraph checkpointer (InMemory by default, optional PostgreSQL). |
| `agents/composer/prompt_composer.py` | `PromptComposer`: merges system + chat prompts with history. |
| `agents/prompts/` | Prompt providers (`SystemPrompt`, `ChatPrompt`) behind a `PromptManager`. |
| `agents/tools/` | Tool framework: `base`, `registry`, `decision_engine`, `selector`, `metadata`, `parameters`, `schemas`, `exceptions`. |
| `agents/tools/implementations/` | Concrete tools: `calculator`, `datetime_tool`, `search_tool`, `http_tool`. |
| `agents/tools/adapters/` | Provider tool-call adapters (`groq_adapter`, `openai_adapter`) + `factory`. |

### `app/api` — HTTP Layer

| Path | Responsibility |
| --- | --- |
| `api/routers/` | Route modules: `health`, `chat`, `webhook`, `admin`. Aggregated under `/api/v1`. |
| `api/schemas/` | Pydantic request/response models (`ChatRequest`, `ChatResponse`). |
| `api/dependencies/` | FastAPI DI providers: `database`, `repositories`, `services`, `agent`, `llm`, `channels`. |
| `api/middleware/request_logger.py` | `RequestLoggerMiddleware`: logs method, path, status, and duration. |

### `app/channels` — Messaging Channels

| Path | Responsibility |
| --- | --- |
| `channels/base.py` | `BaseChannelAdapter` ABC (`normalize_incoming`, `denormalize_outgoing`). |
| `channels/schemas.py` | Channel-agnostic models: `ChannelType`, `MessageType`, `IncomingChannelMessage`, `OutgoingChannelMessage`. |
| `channels/whatsapp/` | WhatsApp implementation: `router` (webhook), `adapter`, `client`, `schemas`. |
| `channels/telegram/` | Placeholder for the Telegram channel. |

### `app/core` — Cross-Cutting Concerns

| Path | Responsibility |
| --- | --- |
| `core/config.py` | Pydantic `Settings` loaded from `.env` (cached via `lru_cache`). |
| `core/logger.py` | Rich-based logging setup. |
| `core/security.py` | `verify_whatsapp_signature`: HMAC-SHA256 webhook signature validation. |
| `core/constants.py` | Application constants. |

### `app/database` — Persistence

| Path | Responsibility |
| --- | --- |
| `database/base.py` | `Base` declarative class + `BaseModel` (UUID PK, `created_at`, `updated_at`). |
| `database/session.py` | Engine + `SessionLocal` + `get_db` request-scoped session generator. |
| `database/models/` | ORM models: `user.py`, `conversation.py`, `message.py`. |

### `app/llm` — LLM Abstraction

| Path | Responsibility |
| --- | --- |
| `llm/providers/base.py` | `BaseLLMProvider` interface + capability helpers. |
| `llm/providers/groq_provider.py` | `GroqProvider` (LangChain `ChatGroq`, temperature 0). |
| `llm/factory.py` | `LLMFactory.create_provider()` — resolves provider from `LLM_PROVIDER`. |
| `llm/schemas.py` | `MessageRole`, `LLMMessage`, `LLMResponse`. |
| `llm/capabilities.py` | `LLMCapabilities` (streaming, tool calling, structured output, vision). |

### `app/repositories` & `app/services` — Domain Logic

- **Repositories** (`repositories/`): `BaseRepository` generic CRUD plus `UserRepository`, `ConversationRepository`, `MessageRepository`. Transaction management is intentionally left to services.
- **Services** (`services/`): `UserService`, `ConversationService`, `MessageService`, `AgentService` (owns the transaction boundary), and `ChannelService` (bridges channels to the AI core and dispatches replies).

---

## How the Agent Works

1. **Message intake** — A channel webhook (e.g. `POST /api/v1/channels/whatsapp/webhook`) is validated (optional HMAC signature), parsed, and normalized by the channel adapter into `IncomingChannelMessage` objects.
2. **Channel orchestration** — `ChannelService.process_incoming_message` converts the normalized message into a `ChatRequest` and delegates to `AgentService`.
3. **Persistence & state** — `AgentService` finds/creates the user, gets/creates the conversation, saves the user message, and builds the recent-message window (`MEMORY_WINDOW_SIZE`) as `ConversationState`.
4. **Graph execution** — `AgentRunner` invokes the compiled LangGraph:
   - `chat` node composes the prompt, calls the LLM, and asks `ToolDecisionEngine` whether a tool is required.
   - `route_after_chat` conditionally routes to `tool_execution` or ends.
   - `tool_execution` node looks the tool up in `ToolRegistry`, executes it with a timeout, and stores a `ToolResult`.
   - Control returns to `chat`, which folds the tool output back into the prompt and produces the final answer.
5. **Response delivery** — The assistant message is persisted, the transaction commits, and `ChannelService` sends the reply via the channel client (e.g. `WhatsAppClient.send_text_message`) and marks the inbound message as read.

**Tool selection strategies** (`ToolDecisionEngine`) adapt to provider capabilities:

- **Native tool calling** — provider supports function calling.
- **Structured output** — provider supports structured outputs.
- **Fallback selector** — rule-based heuristic: messages beginning with `/tool <name> ...` map to `calculator`, `datetime`, `web_search`, `http_client`, or `echo`.

**Built-in tools:**

| Tool | Name | Description |
| --- | --- | --- |
| Calculator | `calculator` | Safe AST-based arithmetic evaluation. |
| DateTime | `datetime` | Current date/time in a given timezone. |
| Web Search | `web_search` | Lightweight DuckDuckGo lookup. |
| HTTP Client | `http_client` | GET/POST/PUT/DELETE external HTTP requests. |

---

## Core Database Models

All models extend `BaseModel` and therefore share a UUID primary key and `created_at` / `updated_at` timestamps.

| Model | Table | Key Fields | Relationships |
| --- | --- | --- | --- |
| `User` | `users` | `platform`, `platform_user_id` (unique, indexed), `display_name`, `is_active` | has many `Conversation` (cascade delete) |
| `Conversation` | `conversations` | `user_id` FK, `title` | belongs to `User`; has many `Message` (cascade delete) |
| `Message` | `messages` | `conversation_id` FK (indexed), `role`, `content` | belongs to `Conversation` |

---

## API Endpoints

All application routes are mounted under the `/api/v1` prefix.

| Method | Path | Description |
| --- | --- | --- |
| `GET` | `/` | Root status endpoint (service online + version). |
| `GET` | `/api/v1/health` | Health check; verifies database connectivity with `SELECT 1`. |
| `POST` | `/api/v1/chat` | Send a chat message through the full AI pipeline (returns `conversation_id` + `response`). |
| `GET` | `/api/v1/channels/whatsapp/webhook` | Meta webhook verification challenge (`hub.mode`, `hub.verify_token`, `hub.challenge`). |
| `POST` | `/api/v1/channels/whatsapp/webhook` | Receives WhatsApp events, validates signature, processes messages, replies. |

**Example — chat request:**

```bash
curl -X POST http://localhost:8000/api/v1/chat \
  -H "Content-Type: application/json" \
  -d '{
    "platform": "web",
    "platform_user_id": "user_123",
    "display_name": "Jane Doe",
    "message": "/tool Calculate 25 * 4"
  }'
```

Interactive API docs are available at `/docs` (Swagger UI) and `/redoc` when the server is running.

---

## Features

- **Multi-channel architecture** with vendor-agnostic normalized message models.
- **WhatsApp Cloud API integration** — webhook verification, HMAC-SHA256 signature validation, text send/reply, and read receipts.
- **LangGraph agent workflow** — chat and tool-execution nodes with conditional routing and a pluggable checkpointer.
- **Provider-agnostic LLM layer** — `BaseLLMProvider` interface, `LLMFactory`, Groq implementation, and capability discovery.
- **Extensible tool framework** — registry, metadata/parameters schema, decision engine, and provider adapters (Groq/OpenAI function calling).
- **Concrete tools** — safe calculator, timezone-aware datetime, web search, and HTTP client.
- **Persistent conversation memory** — users, conversations, and messages stored in PostgreSQL with a configurable memory window.
- **Layered, testable design** — clean separation of API, services, repositories, and domain/adapter layers with FastAPI DI.
- **Database migrations** managed with Alembic.
- **Structured observability** — request logging middleware, Rich logging, and optional LangSmith tracing.
- **Global error handling** and CORS support out of the box.

---

## Tech Stack

- **Web framework:** FastAPI + Uvicorn
- **Agent orchestration:** LangGraph / LangChain
- **LLM provider:** Groq (`langchain-groq`), extensible via `LLMFactory`
- **Database:** PostgreSQL via SQLAlchemy 2.x + `psycopg`
- **Migrations:** Alembic
- **Validation / config:** Pydantic + pydantic-settings
- **HTTP client:** httpx
- **Logging:** structlog + Rich
- **Testing:** pytest (+ pytest-asyncio)

---

## Getting Started & Installation

### Prerequisites

- **Python 3.11+** (developed and tested with a recent CPython; a Python 3.14 environment is present in `.venv`).
- **PostgreSQL** database (a managed instance such as Neon works well). Ensure `sslmode=require` if required by your host.
- **Git** and a shell.
- A **Groq API key** — https://console.groq.com/
- (Optional) Meta WhatsApp Cloud API credentials for the WhatsApp channel.
- (Optional) A public HTTPS URL / tunnel (e.g. Cloudflare Tunnel) to receive WhatsApp webhooks locally.

### 1. Clone and enter the project

```bash
git clone https://github.com/ehsanaiverse/ai-agent-platform.git
cd ai-agent-platform
```

### 2. Create and activate a virtual environment (`.venv`)

```bash
python -m venv .venv

# Linux / macOS
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

Dependencies are listed in `requirements.txt`. Install them into the virtual environment:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

> `pyproject.toml` holds project metadata. If your workflow uses it for packaging, install with `pip install -e .` after adding dependencies there. The tested dependency set for this project is `requirements.txt`.

### 4. Configure environment variables (`.env`)

Create a `.env` file in the project root. `app/core/config.py` loads it automatically via pydantic-settings.

```dotenv
# ==========================
# Groq AI
# ==========================
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
LLM_PROVIDER=groq

# ==========================
# Database
# ==========================
DATABASE_URL=postgresql+psycopg://user:password@host:5432/dbname?sslmode=require

# ==========================
# FastAPI
# ==========================
APP_NAME=AI Agent Platform
DEBUG=True

# ==========================
# WhatsApp (optional)
# ==========================
WHATSAPP_ACCESS_TOKEN=
WHATSAPP_PHONE_NUMBER_ID=
WHATSAPP_APP_SECRET=
WHATSAPP_API_VERSION=v21.0
WHATSAPP_BASE_URL=https://graph.facebook.com
VERIFY_TOKEN=your_webhook_verify_token
WEBHOOK_VERIFY_TOKEN=your_webhook_verify_token
WEBHOOK_URL=

# ==========================
# Memory & Tools
# ==========================
MEMORY_WINDOW_SIZE=20
TOOL_EXECUTION_TIMEOUT=15
CHECKPOINTER_TYPE=memory   # "memory" or "postgres"

# ==========================
# LangSmith (optional)
# ==========================
LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=False
LANGCHAIN_PROJECT=AI Agent Platform
```

> **Security note:** `.env` is git-ignored. Never commit real API keys, database URLs, or channel tokens. Rotate any credentials that may have been exposed.

### 5. Run database migrations

The initial schema (users, conversations, messages) is managed by Alembic. Apply all migrations:

```bash
alembic upgrade head
```

Useful related commands:

```bash
alembic current                          # Show the current revision
alembic history                          # List migration history
alembic revision --autogenerate -m "msg" # Create a new migration from model changes
alembic downgrade -1                     # Roll back one revision
```

### 6. Run the application

The application entry point is `app/main.py`. Start it directly:

```bash
python app/main.py
```

Or run it with Uvicorn (recommended for reload / custom options):

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The server will be available at:

- API root: http://localhost:8000/
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 7. (Optional) Connect the WhatsApp channel

1. Expose your local server over HTTPS using a tunnel, then set `WEBHOOK_URL` to `https://<your-domain>/api/v1/channels/whatsapp/webhook`.
2. In the Meta App dashboard, set the webhook callback URL and verify token (`VERIFY_TOKEN` / `WEBHOOK_VERIFY_TOKEN`).
3. Provide `WHATSAPP_ACCESS_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID`. Set `WHATSAPP_APP_SECRET` to enable HMAC-SHA256 signature verification (recommended in production).

---

## Testing

The test suite lives in `tests/` and uses **pytest** (with **pytest-asyncio** for async tests and FastAPI's `TestClient` for end-to-end flows). Test cache artifacts are written to `.pytest_cache/`.

Make sure the virtual environment is active and test dependencies are installed:

```bash
pip install pytest pytest-asyncio
```

Run the full suite:

```bash
pytest
```

Run verbosely, or target a specific module:

```bash
pytest -v
pytest tests/test_e2e_workflow.py
```

Coverage:

```bash
pytest --cov=app
```

Test modules include:

- `test_e2e_workflow.py` — health, root, end-to-end chat, and tool-execution workflows.
- `test_registry.py`, `test_selector.py`, `test_decision_engine.py` — tool framework behavior.
- `test_groq_adapter.py`, `test_concrete_tools.py`, `test_tool_execution_node.py`, `test_tool_routing.py` — adapters, tools, nodes, and routing.
- `test_runtime_builder.py` — runtime dependency assembly.
- `test_whatsapp_channel.py` — webhook verification, signature validation, and message flow.
- `fixtures/llm.py` — `DummyLLMProvider`, a deterministic LLM test double.

> Some end-to-end tests exercise the full pipeline and therefore require a reachable database and a valid `GROQ_API_KEY`.

---

## Configuration Reference

All settings are defined in `app/core/config.py` and sourced from `.env`:

| Variable | Default | Purpose |
| --- | --- | --- |
| `GROQ_API_KEY` | — | Groq API key (required). |
| `GROQ_MODEL` | — | Groq model name (e.g. `openai/gpt-oss-120b`). |
| `LLM_PROVIDER` | `groq` | Active LLM provider resolved by `LLMFactory`. |
| `DATABASE_URL` | — | SQLAlchemy database URL (required). |
| `APP_NAME` | — | Application title. |
| `DEBUG` | `False` | Enables debug mode / SQL echo / reload. |
| `WHATSAPP_ACCESS_TOKEN` | `""` | Meta WhatsApp Cloud API token. |
| `WHATSAPP_PHONE_NUMBER_ID` | `""` | Meta phone number ID. |
| `WHATSAPP_APP_SECRET` | `""` | Enables webhook HMAC signature verification. |
| `WHATSAPP_API_VERSION` | `v21.0` | Meta Graph API version. |
| `WHATSAPP_BASE_URL` | `https://graph.facebook.com` | Meta Graph API base URL. |
| `VERIFY_TOKEN` / `WEBHOOK_VERIFY_TOKEN` | `""` | Webhook verification token. |
| `WEBHOOK_URL` | `""` | Public webhook URL (informational). |
| `MEMORY_WINDOW_SIZE` | `20` | Number of recent messages sent to the LLM. |
| `TOOL_EXECUTION_TIMEOUT` | `15` | Tool execution timeout (seconds). |
| `CHECKPOINTER_TYPE` | `memory` | LangGraph checkpointer (`memory` or `postgres`). |
| `LANGCHAIN_API_KEY` | `""` | LangSmith API key (optional tracing). |
| `LANGCHAIN_TRACING_V2` | `False` | Enable LangSmith tracing. |
| `LANGCHAIN_PROJECT` | `""` | LangSmith project name. |

---

## Author & Social Links

Created and maintained by **ehsanaiverse**.

- GitHub: https://github.com/ehsanaiverse
- LinkedIn: https://linkedin.com/in/ehsanaiverse
- Twitter / X: https://x.com/ehsanaiverse

---

<p align="center">Built with ❤️ using FastAPI, LangGraph, and Groq.</p>
