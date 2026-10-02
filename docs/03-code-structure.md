# 03 · Code structure — how the project is organised and why

## 1. The folder layout

```
Meridian-AI/
├── backend/                     Python application (the "brain")
│   ├── api/                     The web layer (FastAPI)
│   │   ├── main.py                 Creates the app, middleware, serves the React build
│   │   ├── endpoints.py            All URLs ("routes"); each one is short
│   │   └── schemas.py              Shapes of requests and responses (Pydantic)
│   ├── rag/                     Document question answering
│   │   ├── llm.py                  The Gemini chat model
│   │   ├── embeddings.py           Text → numbers (768-number vectors)
│   │   ├── vector_store.py         Connection to Vertex AI Vector Search
│   │   ├── data_ingestion.py       PDF → pages → chunks → stored vectors
│   │   └── retrieval.py            Question → find chunks → prompt → answer
│   ├── agent/                   The multi-agent audit
│   │   ├── tools.py                Five functions the agents can call
│   │   ├── prompts.py              Instructions for each agent and the CFO
│   │   └── agents.py               Builds the agents and runs them in order
│   ├── config/
│   │   └── settings.py             Reads configuration from environment / .env
│   ├── logger/
│   │   └── custom_logger.py        Structured (JSON) logging, uploads logs on shutdown
│   └── tests/                   Automated checks that need no cloud
├── frontend/                    React + TypeScript user interface
│   └── src/
│       ├── lib/api.ts              The only place that calls the backend
│       ├── components/             The four tabs
│       └── pages/Index.tsx         The page layout
├── course/sample_docs/          Four fictional PDFs for trying the app
├── docs/                        These learner documents
├── course/                      Teaching notes (for instructors)
├── .github/workflows/deploy.yml Automated cloud deployment
├── Dockerfile                   Packages frontend + backend into one image
├── requirements.txt             Pinned Python packages
├── requirements-dev.txt         + test tools
├── .env.example                 Template for your settings
└── README.md
```

## 2. Why not one big file?

A first version of a project like this is often written as one script, or as a few large files. The code in this repository still mentions `agent.py` and `rag.py` in its comments, left over from that earlier stage. A single file is fine for a quick experiment. It becomes a problem as soon as the project grows.

| Problem with one big file | How the folder structure solves it |
|---|---|
| **Everything is tangled.** Web code, database code, prompts and agent logic sit together, so a change in one place can break another | Each folder has **one job**: `api` talks HTTP, `rag` answers from documents, `agent` runs audits |
| **Hard to find things.** Where is the chunk size? Where is the tax prompt? | Names say where: chunk size is in `rag/data_ingestion.py`; prompts are in `agent/prompts.py` |
| **Copy-and-paste duplication.** The same chunking and question-answering code can appear in several places and drift apart | One function per idea, reused. For example `ingest_pdf()` serves both the upload route and the Cloud Storage import |
| **Hard to test.** Importing the file starts connecting to cloud services | Connections are created **only when first used**, so tests and the health check run with no cloud setup |
| **Hard to configure.** Keys and IDs are scattered through the code | All settings are read in one place, `config/settings.py`, from environment variables |
| **Hard to learn.** A 1,000-line file gives no map | You can read one small file at a time, in the order in this guide |
| **Hard to work in a team.** Everyone edits the same file and creates merge conflicts | People work in different files |

Splitting by **responsibility** (not by file size) is the guiding rule. The `api` package does not know how an embedding works. The `rag` package does not know what a URL is. They meet at one point: `endpoints.py` calls functions from `rag` and `agent`.

## 3. How the pieces depend on each other

```
frontend (browser)
     │  HTTP + JSON
     ▼
 api/endpoints.py ──► rag/retrieval.py ──► rag/vector_store.py ──► Vertex AI Vector Search
        │                    │                  │
        │                    ├──► rag/llm.py    └──► rag/embeddings.py ──► Vertex AI
        │                    └──► (Gemini API)
        ├──► rag/data_ingestion.py ──► rag/vector_store.py
        └──► agent/agents.py ──► agent/tools.py, agent/prompts.py, rag/llm.py
                  all of the above read: config/settings.py   and write logs via logger/
```

Rules that keep it tidy:

1. **Arrows only point downwards.** `rag` never imports from `api`. `config` imports nothing from the project.
2. **`api/endpoints.py` stays thin.** A route validates input, calls one function, returns the result.
3. **External connections are created lazily.** `get_llm()`, `get_embeddings()`, `get_vector_store()` and the audit supervisor are built the first time they are needed and then reused (`functools.lru_cache`).

## 4. What each file does

### `backend/api/`
| File | Purpose |
|---|---|
| `main.py` | Creates the FastAPI app, enables CORS, registers the routers, runs a shutdown step that uploads logs, and serves the built React app when it exists |
| `endpoints.py` | All routes (list below) |
| `schemas.py` | `AuditRequest`, `AuditResponse`, `QueryRequest`, `QueryResponse`. FastAPI uses these to check input and document the API |

Routes:

| Method and path | What it does |
|---|---|
| `GET /api/health` | Returns `{"status": "ok"}` |
| `GET /api/status` | Shows configuration (project, region, models, index IDs). Does not call Google Cloud |
| `POST /api/agent/audit` | Runs the multi-agent audit |
| `POST /api/rag/ask` | Answers a question from the stored documents |
| `POST /api/rag/upload` | Accepts PDFs, saves a copy in Cloud Storage, indexes them |
| `GET /api/rag/uploads` | Lists uploads since the server started |
| `POST /api/rag/ingest-gcs` | Indexes every PDF already in the Cloud Storage bucket |

Interactive documentation for all of these is at `http://localhost:8080/docs` when the backend is running.

### `backend/rag/`
| File | Purpose |
|---|---|
| `llm.py` | `get_llm()` returns the Gemini chat model. `extract_text()` turns Gemini's reply into plain text |
| `embeddings.py` | `get_embeddings()` returns the Vertex AI embedding model (`text-embedding-005`, 768 dimensions) |
| `vector_store.py` | `get_vector_store()` connects to your Vector Search index and endpoint |
| `data_ingestion.py` | `split_into_chunks()`, `ingest_pdf()`, `ingest_data_from_gcs()` |
| `retrieval.py` | `build_retriever()` (three strategies) and `ask_question()` |

### `backend/agent/`
| File | Purpose |
|---|---|
| `tools.py` | `check_sanctions_list`, `get_vendor_credit_score`, `calculate_cross_border_tax`, `validate_fx_hedge`, `categorize_expense` |
| `prompts.py` | One instruction text per agent, plus the CFO summary template |
| `agents.py` | `ProcurementSupervisor`: creates the three agents with `create_agent`, runs them one after another, then asks the model for the CFO memo |

### `backend/config/` and `backend/logger/`
| File | Purpose |
|---|---|
| `settings.py` | One `Settings` object with every setting and its default |
| `custom_logger.py` | JSON log lines to the console and a file; uploads the file to Cloud Storage when the server stops |

### `backend/tests/`
Eight automated checks that run without Google Cloud: the health and status routes, an unknown `/api/...` URL returning 404, the question route and audit route with the AI replaced by a stub, non-PDF rejection, PDF chunking, and loading the four sample PDFs. Run them with `pytest backend/tests`.

## 5. Configuration in one place

Every setting comes from environment variables, usually from a `.env` file (copy `.env.example`):

| Variable | Meaning | Default |
|---|---|---|
| `ENVIRONMENT` | `local` or `production` | empty |
| `GOOGLE_API_KEY` | Gemini API key | empty |
| `GCP_PROJECT_ID` | Google Cloud project | empty |
| `GCP_REGION` | Region, e.g. `us-central1` | empty |
| `GCS_BUCKET_NAME` | Cloud Storage bucket | empty |
| `GCS_PREFIX` | Folder inside the bucket for uploads | empty (set `uploads/`) |
| `GCP_SERVICE_ACCOUNT_PATH` | Path to a service-account JSON file (optional) | empty |
| `VECTOR_SEARCH_INDEX_ID` | Vector Search index ID | empty |
| `VECTOR_SEARCH_INDEX_ENDPOINT_ID` | Vector Search endpoint ID | empty |
| `VERTEX_LLM_MODEL_NAME` | Chat model | `gemini-3.8-flash` |
| `VERTEX_EMBEDDING_MODEL_NAME` | Embedding model (must output 768 numbers) | `text-embedding-005` |
| `LLM_TEMPERATURE` | 0 = most repeatable | `0.0` |

Code never contains keys. `.env` and `credentials/` are listed in `.gitignore` and `.dockerignore`, so they are not committed and not baked into the Docker image.

## 6. Which parts need which accounts?

| Part | Gemini key | Google Cloud |
|---|:---:|:---:|
| `/api/health`, `/api/status` | – | – |
| `/api/agent/audit` | ✔ | – |
| `/api/rag/ask`, `/api/rag/upload`, `/api/rag/ingest-gcs` | ✔ | ✔ (Vertex AI, Vector Search, Storage) |

This is why path A in [00](00-overview.md) works with only a Gemini key.

## 7. Where to read next

1. [04 · Architecture](04-architecture.md): the big picture and request flows
2. [06 · Run it locally](06-run-locally.md): run the code
3. [07](07-backend-api.md), [08](08-rag-pipeline.md), [09](09-agents.md): the code, one package at a time
