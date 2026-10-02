# Meridian AI — Complete Learner Guide

All learner documents in one file. Section numbers match the individual files in the `docs/` folder.

## Contents

- [00 · Overview — what you will build](#00--overview--what-you-will-build)
- [01 · Requirements](#01--requirements)
- [02 · Accounts, the $300 credit and costs](#02--accounts-the-300-credit-and-costs)
- [03 · Code structure — how the project is organised and why](#03--code-structure--how-the-project-is-organised-and-why)
- [04 · Architecture](#04--architecture)
- [05 · Google Cloud setup (paths B and C)](#05--google-cloud-setup-paths-b-and-c)
- [06 · Run the project on your computer](#06--run-the-project-on-your-computer)
- [07 · The web API (`backend/api/`)](#07--the-web-api-backendapi)
- [08 · Document question answering — the RAG pipeline (`backend/rag/`)](#08--document-question-answering--the-rag-pipeline-backendrag)
- [09 · The audit agents (`backend/agent/`)](#09--the-audit-agents-backendagent)
- [10 · The user interface (`frontend/`)](#10--the-user-interface-frontend)
- [11 · Docker and Cloud Run](#11--docker-and-cloud-run)
- [12 · Automated deployment with GitHub Actions](#12--automated-deployment-with-github-actions)
- [13 · Cleanup — stop all charges](#13--cleanup--stop-all-charges)
- [14 · Troubleshooting](#14--troubleshooting)
- [15 · Alternatives and next steps](#15--alternatives-and-next-steps)
- [16 · Glossary](#16--glossary)

---

<a id="chapter-00"></a>

## 00 · Overview — what you will build

**Meridian AI** is a web application that helps a company check a purchase before paying for it. It has two features:

1. **Document Q&A (RAG).** You upload PDFs (policies, contracts, reports). You ask questions in plain English and get answers based on those documents.
2. **Procurement audit (agents).** You paste a purchase request. Three specialist AI agents review it, then a "CFO" step writes one summary memo:

   | Agent | Checks |
   |---|---|
   | Risk & Compliance | Is the vendor on a sanctions list? How financially safe is the vendor? |
   | Tax & Treasury | What VAT and import duty apply? Is the quoted exchange rate reasonable? |
   | Financial Control | Is it a capital or an operating expense? Who must approve it? |

The company in the examples, **Aldermoor Industries**, is **fictional**. Its documents are made-up teaching data.

> The audit tools ask an AI model from its general knowledge (only the exchange-rate check uses a live data source). This project teaches the architecture. It is **not** a real compliance system.

### What you will learn

| Topic | Where it appears |
|---|---|
| Building a web API with **FastAPI** | `backend/api/` |
| **RAG**: PDF → chunks → embeddings → vector database → answers | `backend/rag/` |
| **Agents** with LangChain: tools, prompts, a supervisor | `backend/agent/` |
| **Google Cloud**: projects, IAM, Cloud Storage, Vertex AI, Cloud Run, Secret Manager | [05](#chapter-05), [11](#chapter-11) |
| **Docker** packaging | `Dockerfile` |
| **CI/CD** with GitHub Actions | `.github/workflows/deploy.yml` |
| Organising a project into modules, configuration and tests | [03](#chapter-03) |

### What the finished app looks like

Four screens (tabs):

| Tab | What you do |
|---|---|
| **Document Upload** | Upload PDFs so they can be searched |
| **RAG Q&A** | Ask questions about the uploaded documents |
| **Audit** | Run the multi-agent audit on a purchase request |
| **System Status** | See configuration and health |

### Three ways to use this repository

| Path | You need | You get |
|---|---|---|
| **A. Audit only, on your computer** | Gemini API key | The audit feature. Quickest start (about 20 minutes). |
| **B. Everything on your computer** | A + Google Cloud project + GitHub account | Audit **and** document Q&A. The cloud resources (vector database, storage) are created once by the GitHub workflow, then you run the app locally against them |
| **C. Deployed on the internet** | B | The same app on a public Cloud Run URL (the workflow in B already deploys it) |

Read the documents in order: the numbers in the file names are the suggested reading order.


---

<a id="chapter-01"></a>

## 01 · Requirements

Check this list before you start. Details for accounts and costs are in [02 · Accounts, credits and costs](#chapter-02).

### Knowledge you need

| You should know | Level |
|---|---|
| Python | Comfortable with functions, classes, packages, virtual environments |
| **LangChain basics** | Prompts, chat models, chains, what a tool is |
| Command line | Run commands, change directories, set environment variables |
| Git | Clone a repository |

You do **not** need prior experience with Google Cloud, FastAPI, vector databases, Docker, or CI/CD. They are explained in these documents.

### Accounts you need

| Account | Needed for | Cost | Required for path |
|---|---|---|---|
| **Google account** (Gmail or Workspace) | Everything Google | Free | A, B, C |
| **Gemini API key** from Google AI Studio | The chat model (answers and agents) | Free tier available | A, B, C |
| **Google Cloud account** with billing enabled | Vector database, storage, Cloud Run | $300 free credit for new customers (see 02) | B, C |
| **GitHub account** | Creates the cloud resources and deploys the app (GitHub Actions) | Free | B, C |

A **credit or debit card is required** to create a Google Cloud account, even for the free trial. Google places a temporary authorisation hold to verify it. It is not a charge.

### Software you need

| Tool | Version | Used for | Check with |
|---|---|---|---|
| **Python** | 3.12 | Backend | `python3 --version` |
| **Node.js** and npm | 20 or newer | Frontend | `node --version` |
| **Git** | any recent | Getting the code | `git --version` |
| **Google Cloud CLI** (`gcloud`) | recent | Cloud setup (paths B, C) | `gcloud --version` |
| **Docker Desktop** | recent | Optional, container run | `docker --version` |
| A code editor | e.g. VS Code | Reading and editing | — |
| A web browser | any | The app and Google Cloud console | — |

Install links:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- Google Cloud CLI: https://cloud.google.com/sdk/docs/install
- Docker: https://docs.docker.com/get-docker/

**Windows users:** the commands in these documents use macOS/Linux syntax. Use **WSL 2** (Windows Subsystem for Linux) for the smoothest experience, or use the Windows variants shown where they differ.

### Computer and network

| Item | Minimum |
|---|---|
| RAM | 8 GB |
| Free disk space | 3 GB (Python packages, Node packages, Docker image) |
| Internet | Required (Google APIs, package downloads) |

### Time you should plan

| Task | Time |
|---|---|
| Path A (audit only, local) | about 20–30 minutes |
| Google Cloud setup | about 30–45 minutes |
| First cloud deployment (mostly waiting for the vector index) | **30–45 minutes**, unattended |
| Reading the code walkthroughs | 2–3 hours |

### Before you continue

- [ ] I have a Google account.
- [ ] I can create a Gemini API key (see 02).
- [ ] I have Python 3.12, Node.js 20+, and Git installed.
- [ ] For paths B and C: I have a payment card for Google Cloud verification, and I have read the cost warnings in 02.
- [ ] For paths B and C: I have a GitHub account.


---

<a id="chapter-02"></a>

## 02 · Accounts, the $300 credit and costs

> Prices and free-tier limits change. The numbers below were checked in October 2026. Always confirm on the linked official pages before relying on them.

### 1. Gemini API key (Google AI Studio)

The chat model (`gemini-3.8-flash`) is called with an **API key**. It does not use your Google Cloud billing.

1. Open https://aistudio.google.com/apikey and sign in with your Google account.
2. Choose **Create API key**. Copy it.
3. Keep it secret. Treat it like a password. Never commit it to Git or paste it into screenshots.

| Fact | Detail |
|---|---|
| Free tier | Yes. For `gemini-3.8-flash`, the free tier is "free of charge" for input and output, subject to rate limits. |
| Privacy on the free tier | Google states that free-tier content may be **used to improve its products**. Do not send confidential data. Use only the fictional sample documents. |
| Paid tier | Prices per 1 million tokens: input $0.75, output $3.75 through 31 Dec 2026. From 1 Jan 2027: input $1.50, output $7.50. Paid-tier data is not used to improve products. |
| Rate limits | https://ai.google.dev/gemini-api/docs/rate-limits |
| Model list and retirements | https://ai.google.dev/gemini-api/docs/models |

Models are retired regularly. The project's earlier default, `gemini-2.5-pro`, stops working in October 2026. The model name is a setting (`VERTEX_LLM_MODEL_NAME`), so you can change it without touching code.

### 2. Google Cloud account and the $300 free trial

Google Cloud is needed for the vector database (Vertex AI Vector Search), file storage, and hosting (Cloud Run). Path A does not need it.

#### How the free trial works

| Question | Answer (from Google's Free Trial documentation) |
|---|---|
| How much credit? | **$300** of "Welcome credit" |
| For how long? | **90 days** (about three months) from sign-up |
| Who qualifies? | **New customers only**: you have never been a paying Google Cloud, Google Maps Platform or Firebase customer and have not used the trial before |
| Is a card needed? | **Yes.** A valid payment method is required. The authorisation is "a hold, not an actual charge." |
| Do I get charged automatically? | **No.** You are billed only if you manually upgrade to a paid account |
| What if the 90 days or $300 run out first? | The trial ends. After that there is a **30-day grace period**, then free-trial resources are **permanently deleted** unless you upgrade |
| If I upgrade? | You are billed for usage **not covered by the remaining credit**, and for products that are not part of the free trial |

Source: https://docs.cloud.google.com/free/docs/free-cloud-features

The credit is a **balance in dollars**. Every Google Cloud service you use subtracts from it. The 90-day limit and the $300 limit apply together: the trial ends at whichever comes first.

#### Trial limitations to know

Google lists these limits for free-trial accounts:

- No GPUs on virtual machines
- No Google Cloud Marketplace
- No quota increase requests
- No Windows Server VMs
- Certain generative AI services are restricted

Some users also report that Vertex AI model requests on trial accounts are throttled hard, with fixed rate limits. In this project the **chat model uses your AI Studio key**, so it is unaffected. **Embeddings use Vertex AI**, so they are the part that could hit a trial limit. If you see a message such as *"Project is not allowed to use …"* or repeated rate-limit errors during document upload, see [14 · Troubleshooting](#chapter-14). The usual remedy is to **activate the full (paid) account** in Billing. Your remaining credit still applies first. Only usage beyond it is charged.

#### Create the account

1. Go to https://cloud.google.com/free and choose **Get started for free**.
2. Sign in, accept the terms, add your payment method.
3. Create a project (done in [05](#chapter-05)).

### 3. Where the money goes

| Service | How it is billed | Expected cost for this project |
|---|---|---|
| **Vertex AI Vector Search** | **Per hour, for as long as an index is deployed to an endpoint, even with zero traffic** | **The main cost.** See the warning below |
| **Cloud Run** | Per use (CPU time, memory, requests). Scales to zero when idle | Usually inside the monthly free allowance for light use (about 2 million requests, 180,000 vCPU-seconds, 360,000 GiB-seconds per month) |
| **Cloud Build** | Per build minute | A monthly free allowance exists (reported as 2,500 minutes) |
| **Cloud Storage** | Per GB stored | A few cents or less for sample PDFs and logs |
| **Artifact Registry** | Per GB of stored images | Small |
| **Secret Manager** | Per active secret version and per access | Small (6 active versions free per month) |
| **Vertex AI embeddings** | Per characters embedded | Small for a few documents |
| **Gemini API chat** | Free tier, or per token on the paid tier | Free tier for light use |

Free-allowance numbers come from public summaries of Google's pricing pages. Confirm on https://cloud.google.com/run/pricing, https://cloud.google.com/build/pricing and https://cloud.google.com/secret-manager/pricing.

#### ⚠ The Vector Search endpoint

A Vector Search index is searched through an **endpoint** that keeps one or more machines running. You pay by the hour while the index is **deployed**, whether or not anyone uses it.

- A small `e2-standard-2` node is reported at roughly **$0.077 per hour (about $56 per month per node)** on third-party price guides. This is not an official figure. Check https://cloud.google.com/vertex-ai/pricing.
- The deployment command in `.github/workflows/deploy.yml` does **not** set a machine type or replica count. Google's documentation says that when replica counts are not set they default to **2**. The default machine type is not documented on the pages checked. **Your real hourly cost may therefore be higher than the single-node figure.**
- At $0.077/hour per node, two nodes would use about $3.70 per day. A larger machine type costs more.

**What to do:**
1. Before deploying, create a **budget alert** (steps below).
2. After the first deployment, open **Billing → Reports** the next day and check the daily cost.
3. When you finish a work session, **undeploy and delete** the index and endpoint. See [13 · Cleanup](#chapter-13). Re-creating them takes 30–45 minutes, so plan to do your cloud work in one sitting.

#### Create a budget alert (do this first)

1. In the Cloud Console open **Billing → Budgets & alerts**.
2. **Create budget**. Name it `meridian-budget`.
3. Scope: your project. Amount: for example **$20**.
4. Alert thresholds: 50 %, 90 %, 100 %. Keep email notifications on.

A budget alert **notifies** you. It does **not stop** spending. You must delete resources yourself.

### 4. GitHub account (paths B and C)

Used to create the cloud resources and deploy the app automatically. Create a free account at https://github.com. GitHub Actions is free for public repositories and has a monthly free allowance for private ones.

### 5. Summary

| Path | Accounts | Money |
|---|---|---|
| A | Google account, Gemini API key | Free |
| B | + Google Cloud (trial) + GitHub | Uses trial credit. Dominated by Vector Search hours |
| C | Same as B | Same cost as B, plus a public URL. Cloud Run is mostly free at low traffic |


---

<a id="chapter-03"></a>

## 03 · Code structure — how the project is organised and why

### 1. The folder layout

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

### 2. Why not one big file?

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

### 3. How the pieces depend on each other

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

### 4. What each file does

#### `backend/api/`
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

#### `backend/rag/`
| File | Purpose |
|---|---|
| `llm.py` | `get_llm()` returns the Gemini chat model. `extract_text()` turns Gemini's reply into plain text |
| `embeddings.py` | `get_embeddings()` returns the Vertex AI embedding model (`text-embedding-005`, 768 dimensions) |
| `vector_store.py` | `get_vector_store()` connects to your Vector Search index and endpoint |
| `data_ingestion.py` | `split_into_chunks()`, `ingest_pdf()`, `ingest_data_from_gcs()` |
| `retrieval.py` | `build_retriever()` (three strategies) and `ask_question()` |

#### `backend/agent/`
| File | Purpose |
|---|---|
| `tools.py` | `check_sanctions_list`, `get_vendor_credit_score`, `calculate_cross_border_tax`, `validate_fx_hedge`, `categorize_expense` |
| `prompts.py` | One instruction text per agent, plus the CFO summary template |
| `agents.py` | `ProcurementSupervisor`: creates the three agents with `create_agent`, runs them one after another, then asks the model for the CFO memo |

#### `backend/config/` and `backend/logger/`
| File | Purpose |
|---|---|
| `settings.py` | One `Settings` object with every setting and its default |
| `custom_logger.py` | JSON log lines to the console and a file; uploads the file to Cloud Storage when the server stops |

#### `backend/tests/`
Eight automated checks that run without Google Cloud: the health and status routes, an unknown `/api/...` URL returning 404, the question route and audit route with the AI replaced by a stub, non-PDF rejection, PDF chunking, and loading the four sample PDFs. Run them with `pytest backend/tests`.

### 5. Configuration in one place

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

### 6. Which parts need which accounts?

| Part | Gemini key | Google Cloud |
|---|:---:|:---:|
| `/api/health`, `/api/status` | – | – |
| `/api/agent/audit` | ✔ | – |
| `/api/rag/ask`, `/api/rag/upload`, `/api/rag/ingest-gcs` | ✔ | ✔ (Vertex AI, Vector Search, Storage) |

This is why path A in [00](#chapter-00) works with only a Gemini key.

### 7. Where to read next

1. [04 · Architecture](#chapter-04): the big picture and request flows
2. [06 · Run it locally](#chapter-06): run the code
3. [07](#chapter-07), [08](#chapter-08), [09](#chapter-09): the code, one package at a time


---

<a id="chapter-04"></a>

## 04 · Architecture

### 1. The big picture

```
 ┌────────────────────────────────────────────────────────────────────────────┐
 │ Your browser                                                               │
 │   React app: Document Upload · RAG Q&A · Audit · System Status             │
 └───────────────▲────────────────────────────────────────────────────────────┘
                 │ HTTPS, JSON
 ┌───────────────┴────────────────────────────────────────────────────────────┐
 │ Google Cloud Run (one container)                                           │
 │   FastAPI backend  +  the built React files                                │
 │   ┌─────────────────────────┐   ┌─────────────────────────────────────┐    │
 │   │ RAG: rag/*              │   │ Agents: agent/*                     │    │
 │   │ chunk → embed → search  │   │ Risk · Tax · Control → CFO memo     │    │
 │   └──────┬───────────┬──────┘   └──────────────────┬──────────────────┘    │
 └──────────┼───────────┼─────────────────────────────┼───────────────────────┘
            │           │                             │
   Vertex AI embeddings │                             │
   (text-embedding-005) │                             │
            │   Vertex AI Vector Search          Gemini API (API key)
            │   (index + endpoint)               gemini-3.8-flash
            │           │
        Cloud Storage bucket: PDFs + logs        Secret Manager: Gemini key
```

Supporting systems: **GitHub Actions** builds and deploys; **Artifact Registry** stores the container image; **Cloud Build** builds it; **IAM** controls access.

### 2. The layers

| Layer | Technology | Where |
|---|---|---|
| User interface | React, TypeScript, Vite, Tailwind CSS, shadcn/ui | `frontend/` |
| Web API | FastAPI, Uvicorn, Pydantic | `backend/api/` |
| AI orchestration | LangChain (`create_agent`, retrieval chains) | `backend/rag/`, `backend/agent/` |
| Chat model | Gemini via Gemini API (API key) | `rag/llm.py` |
| Embeddings and vector database | Vertex AI (Google Cloud credentials) | `rag/embeddings.py`, `rag/vector_store.py` |
| File storage | Cloud Storage | `rag/data_ingestion.py`, `endpoints.py` |
| Hosting | Cloud Run | `Dockerfile`, `deploy.yml` |
| Secrets | Secret Manager | `deploy.yml` |
| Automation | GitHub Actions | `.github/workflows/deploy.yml` |

#### Two ways of signing in to Google

The project uses both:

| Used for | How it authenticates | Setting |
|---|---|---|
| Gemini chat (`rag/llm.py`) | **API key** | `GOOGLE_API_KEY` |
| Embeddings, Vector Search, Cloud Storage | **Google Cloud credentials** (a service account, or your own login) | `GCP_SERVICE_ACCOUNT_PATH` or `gcloud auth application-default login` |

### 3. Request flows

#### 3.1 Uploading a document

```
Browser ──POST /api/rag/upload (PDF)──► endpoints.upload_documents
   1. save the file temporarily
   2. copy it to Cloud Storage  gs://<bucket>/uploads/<name>.pdf
   3. data_ingestion.ingest_pdf:
        PyPDFLoader → pages
        RecursiveCharacterTextSplitter (1000 characters, 100 overlap) → chunks
        embeddings.embed → one 768-number vector per chunk
        vector_store.add_documents → stored in Vector Search
   4. return {filename, status, pages, chunks}
```

#### 3.2 Asking a question

```
Browser ──POST /api/rag/ask {query, retriever_type}──► endpoints.rag_query
   retrieval.ask_question:
     1. retriever finds the closest chunks to the question (by meaning)
     2. a prompt is filled:  "Use this context … Context: <chunks> … Question: <query>"
     3. Gemini writes the answer from that context
   ◄── {answer}
```

Three retrieval strategies are available (the radio buttons in the UI):

| Strategy | What it does |
|---|---|
| `similarity` (Normal) | Top 3 closest chunks |
| `multiquery` | Gemini rewrites the question several ways and merges the results |
| `contextual` | Fetches 10 chunks, then Gemini trims each to the relevant part |

#### 3.3 Running an audit

```
Browser ──POST /api/agent/audit {request_text}──► endpoints.run_audit
   ProcurementSupervisor.run_audit:
     1. Risk agent    → tools: check_sanctions_list, get_vendor_credit_score
     2. Tax agent     → tools: calculate_cross_border_tax, validate_fx_hedge
     3. Control agent → tools: categorize_expense
     4. CFO step      → one model call that reads the three reports
   ◄── {risk_result, tax_result, control_result, cfo_memo}
```

The CFO prompt applies fixed rules based on keywords in the reports:

| If any report contains … | Final decision |
|---|---|
| `RED ALERT` | REJECTED |
| `FX ALERT` or `HOLD FOR TREASURY AUDIT` | CONDITIONAL HOLD |
| only `APPROVED` / `SUCCESS` | APPROVED TO PAY |

#### 3.4 Deploying

```
git push to main (or "Run workflow")
  └► GitHub Actions
       1. sign in to Google Cloud with the service-account key
       2. enable the Google APIs
       3. create the Cloud Storage bucket
       4. create the Vector Search index and endpoint, deploy the index (30–45 min the first time)
       5. store the Gemini key in Secret Manager
       6. Cloud Build builds the Docker image
       7. Cloud Run runs the image and gets a public URL
```

### 4. Google Cloud services used and why

| Service | What it does here | Why it was chosen |
|---|---|---|
| **Cloud Run** | Runs the container; starts on demand and scales to zero | No server to manage; you pay for use |
| **Vertex AI Vector Search** | Stores embeddings and finds the nearest ones quickly | Managed, scales, integrates with LangChain |
| **Vertex AI embeddings** | Turns text into vectors | Same platform as the vector database |
| **Cloud Storage** | Keeps uploaded PDFs, logs, and the staging data for the index | Cheap, durable file storage |
| **Secret Manager** | Holds the Gemini key; Cloud Run reads it at start | Keys stay out of code and images |
| **Artifact Registry** | Stores Docker images | Required place for images on Google Cloud |
| **Cloud Build** | Builds the image without Docker on your machine | Runs in the cloud from the workflow |
| **IAM / service accounts** | Controls who can do what | Gives the GitHub robot and Cloud Run only the access they need |
| **Cloud Logging** | Shows the application's log lines | Debugging a running service |

Alternatives to each service are listed in [15 · Alternatives and next steps](#chapter-15).

### 5. Important design decisions

| Decision | Reason |
|---|---|
| One container serves both frontend and API | One URL, no CORS problems in production, simpler deployment |
| The embedding model must give **768** numbers | The index is created with 768 dimensions. The same model must be used when storing and searching |
| Chat uses an API key, embeddings use Google Cloud credentials | Shows both authentication styles; the key is kept in Secret Manager in production |
| Models and connections are created on first use | The app starts and the health check works before the cloud is configured |
| Agents are built with LangChain's `create_agent` | It runs on LangGraph internally, so the project contains no graph code to maintain |
| Log files are uploaded to Cloud Storage on shutdown | Cloud Run's local disk disappears when the container stops |


---

<a id="chapter-05"></a>

## 05 · Google Cloud setup (paths B and C)

You will create a Google Cloud project, a robot account for GitHub, and let a GitHub workflow create everything else. Read [02](#chapter-02) first and create your budget alert.

Total time: about 30 minutes of work plus 30–45 minutes of waiting.

### Step 1 · Create a project

A **project** is the container for all your Google Cloud resources and billing.

1. Open https://console.cloud.google.com/ and sign in.
2. Click the project selector at the top → **New project**.
3. Name it, for example `meridian-ai`. Note the **Project ID** shown under the name (for example `meridian-ai-123456`). It must be globally unique, and you cannot change it later. You will use the ID, not the name.
4. Click **Create** and select the new project.

### Step 2 · Link billing

Cloud Run and Vertex AI do not work without a billing account linked to the project. The free trial credit is applied through this billing account.

1. Open **Billing** in the console menu.
2. Link a billing account to your project. If this is your first time, the free-trial sign-up is offered here.
3. Create the budget alert described in [02](#chapter-02) if you have not already.

### Step 3 · Install and sign in to the Google Cloud CLI

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud config list
```

Replace `YOUR_PROJECT_ID` with the Project ID from step 1. `gcloud config list` should show your project.

### Step 4 · Create the deployer service account

A **service account** is an identity for a program instead of a person. GitHub will use this one to build and deploy on your behalf.

```bash
export PROJECT_ID="YOUR_PROJECT_ID"

## 1. Create the account
gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer" \
  --project=$PROJECT_ID

## 2. Give it permission to create resources
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/editor"

## 3. Give it permission to manage access settings
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.projectIamAdmin"

## 4. Create a key file
gcloud iam service-accounts keys create github-deployer-key.json \
  --iam-account=github-deployer@${PROJECT_ID}.iam.gserviceaccount.com
```

On Windows PowerShell, replace `export PROJECT_ID="..."` with `$env:PROJECT_ID="..."` and `$PROJECT_ID` with `$env:PROJECT_ID`.

> **Security notes**
> - `github-deployer-key.json` is a powerful credential. **Never commit it**, email it, or paste it anywhere except the GitHub secret in step 6. Delete the local copy after you have added it to GitHub.
> - The `editor` and `projectIamAdmin` roles are broad. They keep this tutorial simple. A production project would give a deployer only the specific roles it needs, and would use *Workload Identity Federation* so that no key file exists at all ([15](#chapter-15)).
> - If the key is ever exposed, delete it: Console → IAM & Admin → Service accounts → `github-deployer` → Keys → delete.

### Step 5 · Get your copy of the code on GitHub

The deployment workflow runs in **your own** GitHub repository.

1. On the project's GitHub page choose **Fork** (or create a new repository and push the code to it).
2. Open the **Actions** tab of your fork. If GitHub shows a notice that workflows are disabled on forks, enable them.

### Step 6 · Add three GitHub secrets

In your repository: **Settings → Secrets and variables → Actions → New repository secret**.

| Secret name | Value |
|---|---|
| `GCP_PROJECT_ID` | Your Project ID, e.g. `meridian-ai-123456` |
| `GCP_CREDENTIALS_JSON` | The **entire contents** of `github-deployer-key.json`, including the braces |
| `GOOGLE_API_KEY` | Your Gemini API key from AI Studio |

### Step 7 · Run the deployment workflow

1. Open **Actions → Deploy to GCP Cloud Run → Run workflow** (choose your branch).
   The workflow also starts automatically on every push to `main`.
2. The workflow performs these stages (each is a step you can expand in the log):

   | Stage | What happens |
   |---|---|
   | Authenticate | Signs in with the service-account key |
   | Enable APIs | Switches on the Google APIs the project needs, then waits 90 seconds |
   | Storage | Creates the bucket `<project-id>-vector-staging` |
   | Vector Search | Creates a small starter file, an index, an endpoint, and deploys the index to the endpoint. **The first run takes 30–45 minutes** |
   | Secrets | Stores your Gemini key in Secret Manager and lets Cloud Run read it |
   | Build | Cloud Build builds the Docker image |
   | Deploy | Cloud Run starts the service and gives it a public URL |
   | Public access | Allows anyone with the URL to open it |

3. Wait until the run shows a green check. Later runs take a few minutes because the index already exists.

### Step 8 · Collect the values you need locally

You need three things from the run.

**The Vector Search index and endpoint IDs.** Either read them from the workflow log (step *Provision Vector Search Index & Endpoint*, lines starting `Created Index:`, `Index already exists:`, `Created Endpoint:` or `Endpoint already exists:`) or ask Google Cloud:

```bash
gcloud ai indexes list --region=us-central1
gcloud ai index-endpoints list --region=us-central1
```

Copy the ID shown for `financial-docs-production` (index) and `financial-docs-endpoint` (endpoint). Either the plain number or the full `projects/…/indexes/…` path works in `.env`.

**The public URL.** In the *Deploy to Cloud Run* step log, find `Service URL: https://…run.app`.

**The bucket name.** `<project-id>-vector-staging`.

### Step 9 · What now exists in your project

Check in the console that you can see them:

| Resource | Where to look |
|---|---|
| Bucket `<project-id>-vector-staging` | Cloud Storage → Buckets |
| Index and endpoint | Vertex AI → Vector Search |
| Secret `GOOGLE_API_KEY` | Security → Secret Manager |
| Image | Artifact Registry |
| Service `meridian-ai-cloud-run` | Cloud Run |

> **Cost reminder:** the deployed Vector Search index is billing by the hour right now. See the warning in [02](#chapter-02) and the cleanup steps in [13](#chapter-13).

### Next

[06 · Run it locally](#chapter-06), using the IDs you just collected.


---

<a id="chapter-06"></a>

## 06 · Run the project on your computer

Two stages. **Stage 1** needs only a Gemini API key and gives you the audit feature. **Stage 2** adds document Q&A and needs the cloud resources from [05](#chapter-05).

All commands are run from the **project root folder** (the folder that contains `backend/`, `frontend/` and `README.md`). This matters: settings are read from the `.env` file in the folder you run from.

### Stage 0 · Get the code and install packages

```bash
git clone https://github.com/mayank953/Meridian-AI.git
cd Meridian-AI
git checkout course-prep          # the learner-ready branch; skip if it has been merged to main

python3.12 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
```

If you forked the repository in step 5 of doc 05, clone your fork instead.

Check that the automated tests pass. They need no accounts:

```bash
pytest backend/tests
```

Expected: `8 passed`.

### Stage 1 · Audit only (Gemini key only)

1. Create your settings file:
   ```bash
   cp .env.example .env              # Windows: copy .env.example .env
   ```
2. Open `.env` and set at least:
   ```
   GOOGLE_API_KEY=your-gemini-api-key
   ```
   The other values can stay as they are for now.
3. Start the backend:
   ```bash
   uvicorn api.main:app --app-dir backend --reload --port 8080
   ```
   Wait for `Application startup complete`.
4. Open http://localhost:8080/docs. This is the automatically generated API page.
5. Check it is alive: expand `GET /api/health` → **Try it out** → **Execute**. You should get `{"status": "ok"}`.
6. Run an audit: expand `POST /api/agent/audit` → **Try it out** and use this body:
   ```json
   {
     "request_text": "Purchase Request - Aldermoor Industries Global Procurement:\n- Vendor: Takumi Controls Europe B.V. (Netherlands)\n- Item: Industrial PLC Controllers + HMI Panels (Qty: 200)\n- Total Cost: 480,000 EUR\n- Origin: JP (Japan)\n- Destination: DE (Aldermoor Industries, Hamburg, Germany)\n- FX Rate quoted: 1 EUR = 163.5 JPY"
   }
   ```
   Click **Execute**. The audit makes several model calls, so it takes a while. Expect from several seconds to a minute or more.
7. The response has four parts: `risk_result`, `tax_result`, `control_result`, `cfo_memo`.

**What you should see:** each report follows the exact format defined in `backend/agent/prompts.py`. The wording differs from run to run because the model writes it, but the structure stays the same. The vendor in the example is fictional and unknown to the model, so expect a cautious risk assessment.

**Try a second request** with the exchange rate changed to `1 EUR = 190 JPY`. The tax report should flag a difference from the market rate of more than 5 % (`FX ALERT`), and the CFO memo should then say **CONDITIONAL HOLD**.

#### Add the user interface

Open a **second terminal** (keep the backend running):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 and use the **Audit** tab. The page sends its requests directly to `http://localhost:8080`.

### Stage 2 · Document Q&A (needs the cloud resources)

1. **Sign in to Google Cloud for your code.** Choose one:

   *Option 1, your own login (no key file):*
   ```bash
   gcloud auth application-default login
   gcloud auth application-default set-quota-project YOUR_PROJECT_ID
   ```
   *Option 2, the service-account key:* put the JSON file in a folder named `credentials/` and set `GCP_SERVICE_ACCOUNT_PATH=./credentials/service-account.json` in `.env`. The `credentials/` folder is ignored by Git.

2. **Fill in `.env`:**
   ```
   ENVIRONMENT=local
   GCP_PROJECT_ID=YOUR_PROJECT_ID
   GCP_REGION=us-central1
   GOOGLE_API_KEY=your-gemini-api-key
   GCS_BUCKET_NAME=YOUR_PROJECT_ID-vector-staging
   GCS_PREFIX=uploads/
   VECTOR_SEARCH_INDEX_ID=<from doc 05, step 8>
   VECTOR_SEARCH_INDEX_ENDPOINT_ID=<from doc 05, step 8>
   ```
3. Restart the backend (stop with `Ctrl+C`, start again).
4. Open http://localhost:8080/api/status. The project, region, bucket and IDs should show your values.
5. Upload the sample documents in the **Document Upload** tab, or call `POST /api/rag/upload` in `/docs`. The four PDFs are in `course/sample_docs/`. Each upload reports `pages` and `chunks`.
6. Ask questions in the **RAG Q&A** tab. A short wait after uploading may be needed before new chunks become searchable.

| Question | Answer found in the sample documents |
|---|---|
| What is Aldermoor Industries total revenue in FY2024? | EUR 2.84 billion |
| What are the standard payment terms for servo motor suppliers? | Net-45 (for vendors with a credit score of 75 or higher) |
| What EU customs duty applies to PLC controllers imported from Japan? | 2.2 % |
| What is the IFRS depreciation schedule for filling line equipment? | 10 years, straight line |

7. Ask something that is not in the documents, for example "Who won the 2018 World Cup?". The answer should say it does not know. The prompt tells the model to answer only from the retrieved context.
8. Try the three retrieval options (Normal, Multi-Query, Contextual Compression) and compare answers and speed.

To recreate the sample PDFs: `python course/sample_docs/generate_sample_docs.py`.

### Stage 3 · Run it in Docker (optional)

```bash
docker build -t meridian-ai .

docker run -p 8080:8080 \
  --env-file .env \
  -e GOOGLE_APPLICATION_CREDENTIALS=/creds/service-account.json \
  -v "$(pwd)/credentials:/creds:ro" \
  meridian-ai
```

Open http://localhost:8080. One container now serves the user interface and the API. The image contains no `.env` and no credentials; you supply them when you run it.

### Common problems

| Message or symptom | See |
|---|---|
| `ModuleNotFoundError: No module named 'api'` | Run from the project root with `--app-dir backend` |
| Settings seem empty | `.env` is read from the folder you run from |
| `index_id is required for api_version='v1'` | Set `VECTOR_SEARCH_INDEX_ID` and the endpoint ID |
| `403` from Cloud Storage or Vertex AI | [14 · Troubleshooting](#chapter-14) |
| Port 8080 already in use | Stop the other program or use `--port 8081` |


---

<a id="chapter-07"></a>

## 07 · The web API (`backend/api/`)

The API is the part of the program that a browser (or any other program) can talk to over HTTP. It is built with **FastAPI** and run by **Uvicorn**.

### Concepts

| Term | Meaning |
|---|---|
| **Endpoint / route** | A URL plus an HTTP method, e.g. `POST /api/rag/ask` |
| **Request / response** | What the caller sends and what it gets back, here as JSON |
| **Pydantic model** | A Python class that describes the expected shape of data and checks it automatically |
| **Router** | A group of related routes |
| **CORS** | A browser rule about which websites may call your API |
| **Uvicorn** | The server program that runs the FastAPI app |

### A minimal FastAPI app

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/hello")
def hello():
    return {"message": "hello"}
```

Run it with `uvicorn file_name:app --reload`, then open `http://localhost:8000/hello` and `http://localhost:8000/docs`. Meridian's API follows the same pattern, with more routes.

### `schemas.py` — the shapes of data

```python
class AuditRequest(BaseModel):
    request_text: str

class AuditResponse(BaseModel):
    risk_result: str
    tax_result: str
    control_result: str
    cfo_memo: str

class QueryRequest(BaseModel):
    query: str
    retriever_type: str = "similarity"

class QueryResponse(BaseModel):
    answer: str
```

If a caller sends a body without `query`, FastAPI rejects it with status **422** and names the missing field. You do not write that check yourself. The same classes produce the documentation at `/docs`.

### `endpoints.py` — the routes

Routers group the URLs:

```python
health_router = APIRouter(prefix="/api", tags=["Health"])
status_router = APIRouter(prefix="/api", tags=["Status"])
agent_router  = APIRouter(prefix="/api/agent", tags=["Agent"])
rag_router    = APIRouter(prefix="/api/rag", tags=["RAG"])
```

Each route is short. It validates input (through the schema), calls one function from `rag/` or `agent/`, and returns the result. The question route:

```python
@rag_router.post("/ask", response_model=QueryResponse)
def rag_query(payload: QueryRequest):
    try:
        return QueryResponse(answer=ask_question(payload.query, payload.retriever_type))
    except Exception as e:
        log.error("RAG query failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

When something goes wrong the route returns status 500 and the real error text in `detail`. The front end shows this message, and so do the troubleshooting tips in [14](#chapter-14).

#### Upload is `async`; the others are not

`POST /api/rag/upload` is declared `async def` because it must `await` the uploaded file. Embedding a document is slow, blocking work, so it is handed to a worker thread:

```python
summary = await run_in_threadpool(ingest_pdf, local_path, f"upload://{upload.filename}")
```

This keeps the server responsive to other requests, such as the health check, while a large PDF is processed.

#### The audit route builds its supervisor on first use

```python
@lru_cache(maxsize=1)
def get_supervisor() -> ProcurementSupervisor:
    return ProcurementSupervisor()
```

`lru_cache` makes the function run once and remember the result. The agents are created at the first audit request, not when the server starts.

### `main.py` — putting it together

`main.py` creates the `FastAPI` app, adds the CORS middleware, registers the four routers and, if the folder `frontend/dist` exists (inside Docker and Cloud Run), serves the built React application:

- `/assets/...` is served as static files.
- Any other path returns the file if it exists, otherwise `index.html`, so the React app can handle its own pages.
- Unknown URLs that start with `/api/` return a 404 error instead of the web page.
- A path check makes sure requests cannot read files outside the `dist` folder.

A `lifespan` function runs when the server stops and uploads the log file to Cloud Storage.

CORS is set to allow all origins (`allow_origins=["*"]`). That is convenient for learning. For a real product, list only your own domain(s).

### `config/settings.py` — settings in one place

```python
class Settings(BaseSettings):
    llm_model_name: str = Field("gemini-3.8-flash", validation_alias="VERTEX_LLM_MODEL_NAME")
    embedding_model_name: str = Field("text-embedding-005", validation_alias="VERTEX_EMBEDDING_MODEL_NAME")
    ...
    model_config = SettingsConfigDict(env_file=".env", ...)
```

`pydantic-settings` reads environment variables and the `.env` file and turns them into typed attributes (`settings.GCP_PROJECT`, …). The rest of the code imports `settings`; no other file reads `.env`.

### Try it yourself

1. Start the backend. In `/docs`, send `POST /api/rag/ask` with the body `{}`. Read the 422 response.
2. Open `/api/status`. Change `GCP_REGION` in `.env`, restart, and open it again.
3. In `endpoints.py` add a route `GET /api/ping` that returns the current time. Reload `/docs` to see it appear.


---

<a id="chapter-08"></a>

## 08 · Document question answering — the RAG pipeline (`backend/rag/`)

**RAG** (Retrieval-Augmented Generation) lets a language model answer from *your* documents, which it has never seen in training.

```
Preparing (once per document)                  Asking (every question)
PDF → pages → chunks → embeddings → store      question → embedding → closest chunks
                                                          → prompt (chunks + question) → Gemini → answer
```

### Concepts

| Term | Meaning |
|---|---|
| **Chunk** | A short piece of a document (here about 1000 characters). Small pieces make search precise |
| **Overlap** | Consecutive chunks share some text (100 characters) so a sentence is not cut in half |
| **Embedding** | A list of numbers (here 768) that represents the *meaning* of a text. Texts with similar meaning have similar numbers |
| **Vector database** | Storage that can quickly find the stored vectors closest to a given vector |
| **Index** | In Vertex AI Vector Search: the stored vectors and the structure used to search them |
| **Endpoint** | The running service that answers searches against a deployed index. It bills by the hour |
| **Retriever** | The LangChain component that returns the best chunks for a question |

### `llm.py` — the chat model

```python
@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.llm_model_name,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=settings.llm_temperature,
    )
```

- It uses the **Gemini API key**, not Google Cloud credentials.
- `lru_cache` creates the model once and reuses it. Nothing is created at import time.
- `extract_text()` in the same file handles Gemini replies that arrive as a list of content blocks instead of plain text.

### `embeddings.py` — text to numbers

```python
@lru_cache(maxsize=1)
def get_embeddings() -> VertexAIEmbeddings:
    return VertexAIEmbeddings(model_name=settings.embedding_model_name)
```

- Uses Vertex AI and your **Google Cloud credentials**.
- `text-embedding-005` produces **768** numbers per text.
- The index was created with 768 dimensions (see `index_metadata.json` and the workflow). Documents and questions must use **the same** embedding model. If you change the model, create a new index.

Check it yourself (from the project root):

```bash
PYTHONPATH=backend python -c "from rag.embeddings import get_embeddings; print(len(get_embeddings().embed_query('servo motor')))"
```

Expected output: `768`.

### `vector_store.py` — the database connection

```python
@lru_cache(maxsize=1)
def get_vector_store() -> VectorSearchVectorStore:
    aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_REGION)
    return VectorSearchVectorStore.from_components(
        project_id=settings.GCP_PROJECT,
        region=settings.GCP_REGION,
        embedding=get_embeddings(),
        index_id=settings.vector_search_index_id,
        endpoint_id=settings.vector_search_index_endpoint_id,
        gcs_bucket_name=settings.GCS_BUCKET_NAME,
        stream_update=True,
    )
```

- `stream_update=True` lets new documents become searchable within a short time. Without it, updates are applied in batches.
- The bucket is used for staging data when adding documents.
- If the index ID is empty you get `index_id is required for api_version='v1'`.

### `data_ingestion.py` — getting documents in

```python
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

def split_into_chunks(pages):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(pages)

def ingest_pdf(local_path, source):
    pages = PyPDFLoader(local_path).load()
    for page in pages:
        page.metadata["source"] = source
    chunks = split_into_chunks(pages)
    if chunks:
        get_vector_store().add_documents(chunks)
    return {"pages": len(pages), "chunks": len(chunks)}
```

Step by step: load the PDF into pages → mark each page with where it came from → split into chunks → embed and store. `add_documents` calls the embedding model for you.

Two routes use `ingest_pdf`:

| Route | Source of the PDF |
|---|---|
| `POST /api/rag/upload` | Files uploaded from the browser |
| `POST /api/rag/ingest-gcs` | PDFs already in the Cloud Storage bucket (`ingest_data_from_gcs`) |

PDFs that contain only scanned images have no text to extract; the upload route reports them as skipped.

### `retrieval.py` — answering

```python
def ask_question(query, retriever_type="similarity") -> str:
    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM_PROMPT), ("human", "{input}")])
    question_answer_chain = create_stuff_documents_chain(get_llm(), prompt)
    rag_chain = create_retrieval_chain(build_retriever(retriever_type), question_answer_chain)
    response = rag_chain.invoke({"input": query})
    return response["answer"]
```

Two chains:

1. `create_stuff_documents_chain` puts ("stuffs") the retrieved chunks into the prompt where `{context}` appears, then calls the model.
2. `create_retrieval_chain` runs the retriever first, then the first chain.

The system prompt tells the model to answer only from the context and say it does not know otherwise:

```
Use the following pieces of retrieved context to answer the question.
If you don't know the answer based on the context, say that you don't know.
```

#### Retrieval strategies

`build_retriever` returns one of three retrievers:

| Name | Behaviour | Trade-off |
|---|---|---|
| `similarity` | Closest 3 chunks | Fastest, cheapest |
| `multiquery` | Gemini writes several versions of the question; results are merged | Finds more, uses extra model calls |
| `contextual` | Fetch 10 chunks, then Gemini shortens each to the relevant sentences | Cleaner context, slowest |

#### A note on package names

`create_retrieval_chain` and the retrievers come from **`langchain-classic`** (imports start with `langchain_classic`). The agent code uses the current `langchain` package (`from langchain.agents import create_agent`). Both are in `requirements.txt`. Online examples mix old and new import paths, so check which package an import comes from.

### Try it yourself

1. Change `CHUNK_SIZE` to 300 in `data_ingestion.py`, upload a PDF again, and compare the answers.
2. Ask a question using each retriever type and note the response time.
3. Ask a question whose answer is not in your documents.
4. Read `index_metadata.json` and find `"dimensions": 768`.


---

<a id="chapter-09"></a>

## 09 · The audit agents (`backend/agent/`)

A RAG pipeline **answers questions**. An **agent** **does work**: it decides which tools to call, reads the results, and continues until it can give an answer.

### Concepts

| Term | Meaning |
|---|---|
| **Tool** | A Python function the model is allowed to call. The model reads its name, arguments and docstring to decide when to use it |
| **System prompt** | The standing instructions for an agent: role, responsibilities, how to decide, and exactly how to format the answer |
| **Agent** | A model + tools + a system prompt, running in a loop: think → call a tool → read the result → think again → answer |
| **Supervisor** | Ordinary Python code that runs several agents and combines their results |

### The five tools — `tools.py`

Each tool is a function marked with `@tool` from `langchain_core.tools`:

| Tool | Used by | What it does | Data source |
|---|---|---|---|
| `check_sanctions_list(vendor_name)` | Risk | Screens a vendor name against well-known sanctions lists | The model's general knowledge |
| `get_vendor_credit_score(vendor_name)` | Risk | Returns a score from 0–100 and a risk level (unknown vendors get 45) | The model's general knowledge |
| `calculate_cross_border_tax(amount, origin, destination)` | Tax | VAT/GST, import duty, total landed cost | The model's general knowledge |
| `validate_fx_hedge(currency_pair, rate_used)` | Tax | Compares the quoted exchange rate with the market rate; flags a difference above 5 % | **Live data** from `api.frankfurter.dev`; falls back to the model if it is unreachable |
| `categorize_expense(amount, item_description)` | Control | CapEx or OpEx, depreciation period, approval flags | The model's general knowledge |

> Four of the five tools ask the language model instead of calling real databases. That is a simplification for teaching. A real system would call a sanctions-screening service, a credit bureau, a tax engine, and so on.

How a tool is defined:

```python
@tool
def categorize_expense(amount: float, item_description: str) -> str:
    """Determines if the expense is Capital Expenditure (CapEx) or Operational (OpEx) using accounting standards."""
    ...
```

The docstring is part of the tool's description. The model uses it to decide when to call the tool, so write it clearly.

Each tool handles failure on its own. If the model call fails, it returns a message such as `SYSTEM WARNING: ... Manual review required.` rather than crashing the audit. Shared helpers: `_ask_llm()` (calls the model, catches errors) and `extract_text()` (normalises the reply).

### The prompts — `prompts.py`

There are four prompts. Each of the three agent prompts follows the same four parts:

1. **Role**: who the agent is
2. **Responsibilities**: what it is accountable for
3. **Decision framework**: which tool to call first, what thresholds to apply
4. **Output format**: an exact template for the answer

Example (shortened) from the risk prompt:

```
DECISION FRAMEWORK:
1. Run `check_sanctions_list` first — this is a hard blocker. A RED ALERT means immediate rejection.
2. Run `get_vendor_credit_score` next. Score ≥ 75 → LOW RISK ... Score < 50 → HIGH RISK ...

OUTPUT FORMAT — always respond in this exact structure:
SANCTIONS CHECK: [CLEARED / RED ALERT — reason]
CREDIT SCORE: [score] → [LOW / MODERATE / HIGH] RISK
...
```

A fixed output format makes the next step reliable. The CFO prompt looks for these exact words in the reports:

| Word | Comes from | Effect |
|---|---|---|
| `RED ALERT` | sanctions tool / risk prompt | Final decision: REJECTED |
| `FX ALERT` | exchange-rate tool | Final decision: CONDITIONAL HOLD |
| `HOLD FOR TREASURY AUDIT` | tax prompt | Final decision: CONDITIONAL HOLD |

If you rename one of these words, rename it everywhere.

All company details in the prompts (Aldermoor Industries, Hamburg, thresholds such as €250,000 and €1,000,000) are fictional.

### The supervisor — `agents.py`

Creating an agent takes one call:

```python
from langchain.agents import create_agent

def create_specialized_agent(tools, system_prompt):
    return create_agent(model=get_llm(), tools=tools, system_prompt=system_prompt)
```

The supervisor creates three agents, each with its own tools and prompt:

```python
self.risk_agent    = create_specialized_agent([check_sanctions_list, get_vendor_credit_score], RISK_AGENT_PROMPT)
self.tax_agent     = create_specialized_agent([calculate_cross_border_tax, validate_fx_hedge], TAX_AGENT_PROMPT)
self.control_agent = create_specialized_agent([categorize_expense], CONTROL_AGENT_PROMPT)
```

`run_audit()` runs them one after another and then asks the model for the CFO memo:

```python
risk_result    = self._invoke_agent(self.risk_agent, request)
tax_result     = self._invoke_agent(self.tax_agent, request)
control_result = self._invoke_agent(self.control_agent, request)

synthesis_prompt = SYNTHESIS_PROMPT_TEMPLATE.format(risk_result=..., tax_result=..., control_result=...)
cfo_memo = extract_text(self.llm.invoke(synthesis_prompt).content)
```

Calling an agent means passing it a message list and reading the last message:

```python
result = agent.invoke({"messages": [{"role": "user", "content": request}]})
text = extract_text(result["messages"][-1].content)
```

Each phase is written to the log, so you can follow an audit in the terminal.

The agents run **sequentially**. They could run in parallel because they do not depend on each other. Sequential code is easier to read and debug.

#### LangChain and LangGraph

`create_agent` is LangChain's standard way to build an agent. Internally it runs on **LangGraph**, which is why `langgraph` is listed in `requirements.txt` and appears in log output. This project does not write any LangGraph code. LangGraph itself is worth learning when you need loops, branches or shared state that a simple agent cannot express ([15](#chapter-15)).

#### Run the supervisor without the web server

From the `backend/` folder, with `GOOGLE_API_KEY` exported in your terminal (this run does not read `.env`, because `.env` is in the project root):

```bash
cd backend
GOOGLE_API_KEY=your-key python -m agent.agents
```

It audits a built-in sample request and prints the CFO memo.

### Things to know about agent output

- The model writes the text, so wording changes from run to run. The structure (headings and key words) should stay stable.
- Setting `LLM_TEMPERATURE=0` (the default) makes answers more repeatable. If a model repeats itself or loops, try `1.0`.
- A model can be wrong. Real audits keep a human in the loop.

### Try it yourself

1. Add a sixth tool, for example `check_delivery_risk(country: str)`, and give it to the control agent.
2. Change a threshold in `RISK_AGENT_PROMPT` (for example the 75 for "low risk") and run the same request again.
3. Submit a request with an exchange rate far from the market rate and read the CFO memo.
4. Remove the output-format section from one prompt. Compare the result and the CFO memo.


---

<a id="chapter-10"></a>

## 10 · The user interface (`frontend/`)

The interface is a **React** application written in **TypeScript**, built with **Vite**, styled with **Tailwind CSS** and **shadcn/ui** components. You do not need to know React to use or understand the rest of the project. This page shows how the interface connects to the backend.

### Files that matter

| File | Role |
|---|---|
| `src/lib/api.ts` | **All calls to the backend** are in this one file |
| `src/pages/Index.tsx` | Page layout and the tab navigation |
| `src/components/DocumentUploadTab.tsx` | Upload PDFs; button to import PDFs already in the bucket |
| `src/components/RagQATab.tsx` | Ask questions; choose the retrieval strategy |
| `src/components/AuditTab.tsx` | Enter a purchase request; shows the three reports and the memo |
| `src/components/SystemStatusTab.tsx` | Shows `/api/status` |
| `src/components/ui/` | Reusable buttons, cards and inputs (generated by shadcn/ui) |

### `api.ts`

```ts
const BASE_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? "http://localhost:8080" : "");
```

- While developing (`npm run dev`), the page calls the backend at `http://localhost:8080`.
- In production (the built files served by FastAPI), `BASE_URL` is empty, so calls go to the same address that served the page.
- Set `VITE_API_URL` if your backend runs somewhere else.

One small helper makes every call and turns errors into messages:

```ts
async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, options);
  if (!res.ok) {
    const body = await res.json().catch(() => ({}));
    throw new Error(body.detail || `HTTP ${res.status}`);
  }
  return res.json();
}
```

Then one function per endpoint, for example:

```ts
export async function askQuestion(query: string, retrieverType = "similarity") {
  return request<{ answer: string }>("/api/rag/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ query, retriever_type: retrieverType }),
  });
}
```

| UI action | Function | Endpoint |
|---|---|---|
| Upload | `uploadDocuments` | `POST /api/rag/upload` |
| Import from bucket | `triggerGcsIngestion` | `POST /api/rag/ingest-gcs` |
| Ask | `askQuestion` | `POST /api/rag/ask` |
| Run audit | `runAudit` | `POST /api/agent/audit` |
| Status | `getSystemStatus` | `GET /api/status` |

### Run and build

```bash
cd frontend
npm install
npm run dev        # development server on http://localhost:3000
npm run build      # creates frontend/dist (what the Docker image serves)
```

In your browser's developer tools, open the **Network** tab and click a button in the app to see the exact request and response for each action.


---

<a id="chapter-11"></a>

## 11 · Docker and Cloud Run

### Concepts

| Term | Meaning |
|---|---|
| **Image** | A packaged, read-only snapshot of an application and everything it needs |
| **Container** | A running copy of an image |
| **Dockerfile** | The recipe for building an image |
| **Multi-stage build** | A Dockerfile with several stages; only the last stage ends up in the final image |
| **Artifact Registry** | Google Cloud's storage for images |
| **Cloud Build** | Builds images in Google Cloud |
| **Cloud Run** | Runs containers on request, scaling from zero to many |

### The Dockerfile

The `Dockerfile` has two stages.

**Stage 1 — build the user interface (Node.js)**
```dockerfile
FROM node:20-alpine AS frontend-builder
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN if [ -f package-lock.json ]; then npm ci; else npm install; fi
COPY frontend/ ./
RUN npm run build
```
This installs the Node packages and creates the optimised website in `frontend/dist`.

**Stage 2 — the application (Python)**
```dockerfile
FROM python:3.12-slim AS backend-builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY --from=frontend-builder /app/frontend/dist /app/frontend/dist
EXPOSE 8080
CMD uvicorn api.main:app --app-dir backend --host 0.0.0.0 --port ${PORT:-8080}
```

Reading it line by line:

| Line | Meaning |
|---|---|
| `COPY requirements.txt` then `pip install` before copying the code | Docker caches each step. Package installation is slow, so it comes first and is only repeated when `requirements.txt` changes |
| `COPY --from=frontend-builder …` | Takes only the finished website from stage 1. Node.js itself does not enter the final image, which keeps it smaller |
| `--host 0.0.0.0` | Listen on all network interfaces inside the container |
| `--port ${PORT:-8080}` | Cloud Run tells the app which port to use through the `PORT` variable; default is 8080 |

`main.py` finds `frontend/dist` next to the backend and serves it, so **one container is the whole application**.

#### What is *not* in the image

`.dockerignore` excludes `.env`, `credentials/`, `.git/`, logs and `node_modules`. Secrets are supplied when the container runs, never baked into the image:

```bash
docker run -p 8080:8080 \
  --env-file .env \
  -e GOOGLE_APPLICATION_CREDENTIALS=/creds/service-account.json \
  -v "$(pwd)/credentials:/creds:ro" \
  meridian-ai
```

### Cloud Run

The workflow builds the image with Cloud Build and deploys it:

```bash
gcloud builds submit --tag <image> .
gcloud run deploy meridian-ai-cloud-run \
  --image <image> --region us-central1 --platform managed \
  --allow-unauthenticated --port 8080 --max-instances 3 \
  --set-env-vars="ENVIRONMENT=production,GCP_PROJECT_ID=...,..." \
  --update-secrets="GOOGLE_API_KEY=GOOGLE_API_KEY:latest"
```

| Option | Meaning |
|---|---|
| `--allow-unauthenticated` | Anyone with the URL can open the app |
| `--max-instances 3` | Never run more than three copies, which limits cost if someone floods the URL |
| `--set-env-vars` | Plain settings (project, region, bucket, model names, index IDs) |
| `--update-secrets` | Injects `GOOGLE_API_KEY` from Secret Manager as an environment variable |

Behaviour to know:

- **Scale to zero.** With no traffic no instance runs. The first request after a quiet period is slower (a *cold start*).
- **Temporary disk.** Files written inside the container disappear when it stops. That is why uploads are also stored in Cloud Storage and logs are uploaded on shutdown.
- **Identity.** The running service uses the project's default compute service account to reach Vertex AI, Cloud Storage and Secret Manager.

> **Public URL warning.** The deployed app has no sign-in. Anyone who finds the URL can upload files and run audits that use your Gemini quota. Delete the service when you are done ([13](#chapter-13)). Do not upload confidential documents.

### Image registry note

The workflow uses an image name of the form `gcr.io/<project>/…`. Google's older *Container Registry* has been shut down; `gcr.io` addresses now work only through Artifact Registry repositories. If the build or push step fails with a permission or "repository does not exist" error, see the GitHub Actions entry in [14 · Troubleshooting](#chapter-14).


---

<a id="chapter-12"></a>

## 12 · Automated deployment with GitHub Actions

**CI/CD** means *continuous integration / continuous delivery*: every time you push code, a machine builds it and (optionally) deploys it, the same way each time. In this project the workflow file is `.github/workflows/deploy.yml`.

### When it runs

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

- Automatically on every push to the `main` branch.
- Manually from **Actions → Deploy to GCP Cloud Run → Run workflow** (`workflow_dispatch`).

> Pushes to other branches do **not** deploy. Do your experiments on a branch and merge to `main` when you want to deploy.

### Settings at the top

```yaml
env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  REGION: us-central1
  SERVICE_NAME: meridian-ai-cloud-run
  IMAGE_NAME: gcr.io/${{ secrets.GCP_PROJECT_ID }}/meridian-ai-cloud-run
  VECTOR_BUCKET: gs://${{ secrets.GCP_PROJECT_ID }}-vector-staging
  INDEX_NAME: financial-docs-production
  ENDPOINT_NAME: financial-docs-endpoint
```

`${{ secrets.NAME }}` reads a GitHub secret (see [05](#chapter-05)). The region is fixed to `us-central1`; if you change it, also change `GCP_REGION` in your `.env`.

### The steps

| # | Step | What it does |
|---|---|---|
| 1 | Checkout | Downloads your code onto the GitHub runner |
| 2 | Authenticate | Signs in to Google Cloud with `GCP_CREDENTIALS_JSON` |
| 3 | Set up Cloud SDK | Installs `gcloud` on the runner |
| 4 | Enable APIs | `gcloud services enable …` for Vertex AI, Cloud Run, Secret Manager, Storage, Artifact Registry, Cloud Build, Logging, Monitoring, Trace, IAM, Resource Manager, BigQuery and Generative Language; waits 90 s |
| 5 | Buckets | Creates `gs://<project>-vector-staging` if it does not exist (no public access) |
| 6 | Initial embeddings file | `generate_json.py` writes a single random 768-number vector; it is copied to the bucket so the index can be created with at least one item |
| 7 | Vector Search | Creates the **index** (768 dimensions, streaming updates), the **endpoint**, and **deploys** the index. Each part is skipped if it already exists. Then removes the dummy vector. Slow the first time |
| 8 | Secrets | Creates the secret `GOOGLE_API_KEY`, adds your key as a new version, and lets Cloud Run's service account read **that secret** |
| 9 | Build | `gcloud builds submit` builds and stores the image |
| 10 | Deploy | `gcloud run deploy` with environment variables, the secret and `--max-instances 3` |
| 11 | Public access | Allows anyone to invoke the service and prints the access policy |

Notes:

- The workflow is **idempotent**: a second run reuses what exists, so it finishes in minutes.
- The index and endpoint IDs are passed to Cloud Run as `VECTOR_SEARCH_INDEX_ID` and `VECTOR_SEARCH_INDEX_ENDPOINT_ID`.
- The Gemini key is read inside the shell step through an environment variable, so its value is not written into the command text.
- BigQuery's API is enabled but not used by the application.
- The deployed Vector Search index starts billing as soon as it is deployed. See [02](#chapter-02).

### Reading a run

1. Open **Actions** and click the run.
2. Click the job *Provision & Deploy*. Each step can be expanded.
3. A red cross marks the failed step; the last lines of its log show the error. Common causes are in [14 · Troubleshooting](#chapter-14).
4. Re-run with **Re-run failed jobs**. Because of the idempotent design, re-running is safe.

### Security points

| Topic | Detail |
|---|---|
| Secrets | GitHub encrypts them and hides their values in logs. Never print them or put them in code |
| The JSON key | It is a long-lived credential. A more secure alternative is **Workload Identity Federation**, where GitHub proves its identity to Google Cloud without any stored key ([15](#chapter-15)) |
| Broad roles | `editor` and `projectIamAdmin` are convenient for learning. Production deployers get narrower roles |
| Public service | `allUsers` can invoke the service. Add sign-in before putting real data in |


---

<a id="chapter-13"></a>

## 13 · Cleanup — stop all charges

Do this at the end of every cloud session. Deployed Vector Search keeps billing even when nobody uses the app.

### What costs money while it exists

| Resource | Stops billing when you … |
|---|---|
| Vector Search **deployed index** on an endpoint | **Undeploy** it |
| Vector Search endpoint and index | Delete them (undeploy first) |
| Cloud Run service | Delete it (idle cost is zero, but delete anyway) |
| Cloud Storage bucket | Empty and delete it (tiny cost) |
| Artifact Registry images | Delete the repository or images (tiny cost) |

### Option 1 · Remove only the expensive part

```bash
export REGION=us-central1

## 1. Find the IDs
gcloud ai index-endpoints list --region=$REGION
gcloud ai indexes list --region=$REGION

## 2. Undeploy the index from the endpoint (this stops the hourly charge)
gcloud ai index-endpoints undeploy-index ENDPOINT_ID \
  --deployed-index-id=deployed_financial_docs --region=$REGION

## 3. Delete the endpoint and the index
gcloud ai index-endpoints delete ENDPOINT_ID --region=$REGION
gcloud ai indexes delete INDEX_ID --region=$REGION
```

When you start again, run the workflow; it re-creates the index and endpoint (30–45 minutes) and gives you new IDs for `.env`.

### Option 2 · Remove the Cloud Run service

```bash
gcloud run services delete meridian-ai-cloud-run --region=us-central1
```

### Option 3 · Delete everything (safest)

Deleting the project removes every resource in it and stops all charges. Google keeps a deleted project recoverable for 30 days.

```bash
gcloud projects delete YOUR_PROJECT_ID
```

### Also clean up credentials

- Delete the service-account key if you no longer need it: Console → IAM & Admin → Service accounts → `github-deployer` → Keys.
- Delete the local `github-deployer-key.json`.
- Remove the GitHub secrets if you are finished (Settings → Secrets and variables → Actions).
- If your Gemini API key was ever exposed, delete it at https://aistudio.google.com/apikey and create a new one.

### Check that nothing is still running

1. Console → **Vertex AI → Vector Search → Index endpoints**: no deployed indexes.
2. Console → **Cloud Run**: no services.
3. Console → **Billing → Reports**: cost per day drops to about zero the next day.
4. Your budget alert from [02](#chapter-02) remains as a safety net.


---

<a id="chapter-14"></a>

## 14 · Troubleshooting

Find the section for the part that is failing. Each entry gives the **symptom** (the message or behaviour), the **cause**, and the **fix**. Most API errors appear in the `detail` field of the response and in the terminal where the backend is running.

**First checks for almost any problem**

1. Are you in the project root folder? (`.env` is read from the folder you run from.)
2. Is the virtual environment active (`(.venv)` in your prompt) and `pip install -r requirements.txt` done?
3. Does `.env` contain your Gemini key and, for cloud features, project, bucket and index IDs? Compare with `.env.example`.
4. Read the last lines of the terminal output. The real error is usually there.

---

### Google Cloud and billing

**`403 ... does not have storage.objects.create access` (or any 403 from Cloud Storage/Vertex)**
Cause: your local credentials belong to a different Google account or service account than you think. Fix: check `gcloud auth list` and `gcloud config get account`; for the app, set `GCP_SERVICE_ACCOUNT_PATH` in `.env` to your service-account JSON (the app exports it as `GOOGLE_APPLICATION_CREDENTIALS`). Grant the account `Storage Object Admin` on the bucket if needed.

**`SERVICE_DISABLED` / "API has not been used in project … before or it is disabled"**
Cause: the API is not enabled. Fix: `gcloud services enable aiplatform.googleapis.com` (or re-run the workflow, which enables all of them). Wait a minute or two.

**"Billing account … is not enabled" / pipeline fails silently**
Cause: project has no billing account. Fix: Console → Billing → link an account.

**`Your default credentials were not found` / `DefaultCredentialsError`**
Cause: no Application Default Credentials. Fix: either `gcloud auth application-default login` or point `GOOGLE_APPLICATION_CREDENTIALS` at the service-account JSON.

**Quota project warnings**
Fix: `gcloud auth application-default set-quota-project <project-id>`.

**Wrong project is being used**
Fix: `gcloud config set project <project-id>` and check `GCP_PROJECT_ID` in `.env`.

**Unexpected bill**
Cause: the Vector Search endpoint keeps a node running 24/7. Fix: see [vector-search.md](#vector-search) (teardown) and set a budget alert.

**"Project is not allowed to use …" / repeated rate-limit or quota errors on a free-trial account**
Cause: free-trial accounts have restricted access and fixed quotas for some Vertex AI services (embeddings run on Vertex AI here; the Gemini chat key from AI Studio is separate). Fix: in Billing, activate the full (paid) account. Remaining trial credit is still applied first; only usage beyond it is charged. Then retry.

**Free-trial credit "disappeared" or resources were deleted**
Cause: the trial ends after 90 days or when the $300 is used. After a 30-day grace period trial resources are permanently deleted unless you upgrade. Fix: upgrade before that, or re-create resources in a new project.

---

### Running the backend (FastAPI)

**`ModuleNotFoundError: No module named 'api'`**
Cause: started from the wrong folder. Fix: from the **project root** run `uvicorn api.main:app --app-dir backend --reload --port 8080`.

**Settings are empty / `.env` not picked up**
Cause: `.env` is read from the *current folder*. Fix: run from the project root, where `.env` lives.

**`422 Unprocessable Entity`**
Cause: the request body does not match the Pydantic model (e.g. `query` missing). Fix: compare with the schema in `/docs`; the response body says which field is wrong.

**Browser: "blocked by CORS policy"**
Cause: frontend and backend on different origins. The backend allows all origins for the demo. Fix: check the backend is running on port 8080 and that `VITE_API_URL` is not pointing elsewhere.

**`Address already in use` (port 8080)**
Fix: `lsof -i :8080` then stop that process, or use `--port 8081` (and set `VITE_API_URL=http://localhost:8081`).

**`/api/rag/ask` returns 500 with a long message**
The `detail` field contains the real error; look it up in [langchain.md](#models-langchain-and-agents) or [vector-search.md](#vector-search).

**Frontend shows blank page on the Docker/Cloud Run URL**
Cause: `frontend/dist` was not built into the image. Fix: rebuild the image; check the first Docker stage ran `npm run build`.

---

### Models, LangChain and agents

**`index_id is required for api_version='v1'`**
Cause: `VECTOR_SEARCH_INDEX_ID` / `VECTOR_SEARCH_INDEX_ENDPOINT_ID` are empty. Fix: copy them from the GitHub Actions log (*Provision Vector Search* step) into `.env`.

**`404 models/<name> is not found` / "no longer available to new users"**
Cause: the model was retired or is not available to your key. Fix: set `VERTEX_LLM_MODEL_NAME` to a current model from https://ai.google.dev/gemini-api/docs/models (this project uses `gemini-3.8-flash`). `gemini-2.5-pro` is closed to new users and retires 16 Oct 2026.

**`API key not valid` / 400 from Gemini**
Fix: create a key at https://aistudio.google.com/apikey; no spaces or newlines in `.env`.

**`ImportError: cannot import name 'create_agent'`**
Cause: old `langchain` installed. Fix: `pip install -r requirements.txt` (needs `langchain==1.2.11`).

**`ModuleNotFoundError: langchain_classic`**
Fix: `pip install langchain-classic==1.0.2`. `create_retrieval_chain` moved there in LangChain 1.x.

**Agent answers instantly without using tools / loops forever**
Cause: tool docstrings unclear, or model temperature. Fix: improve the tool docstring; try `LLM_TEMPERATURE=1.0` (Gemini 3 default) or a different model.

**Tool results contain `LLM_ERROR`**
Cause: the tool's own model call failed (key, quota, model name). The agent output will say "Manual review required". Fix as above.

**`validate_fx_hedge` always uses the LLM fallback**
Cause: the Frankfurter API (`api.frankfurter.dev`) is unreachable from your network. The tool is built to fall back.

**Audit answers differ each run**
Normal: LLM output varies. The key words (`RED ALERT`, `FX ALERT`, `HOLD FOR TREASURY AUDIT`) should be stable.

---

### Vector Search

**Index creation/deployment takes 30–45 minutes the first time.** Normal. Start it hours before class.

**Searches return nothing right after uploading**
Cause: streaming updates take a short time to become searchable. Fix: wait ~30–60 seconds and ask again.

**Dimension mismatch error when upserting**
Cause: the embedding model does not output 768 dimensions (the index is created with 768). Fix: use `text-embedding-005` (default). Changing the model means creating a new index.

**`deployed index not found` / endpoint errors**
Cause: the index is not deployed to the endpoint yet. Check: Console → Vertex AI → Vector Search → Index endpoints.

**Same document uploaded twice → duplicate answers**
Expected: every upload adds chunks again. For class, upload each PDF once.

#### Teardown (stops the hourly charge)
```bash
REGION=us-central1
## 1. find ids
gcloud ai index-endpoints list --region=$REGION
gcloud ai indexes list --region=$REGION
## 2. undeploy the index from the endpoint (this is what stops the billing)
gcloud ai index-endpoints undeploy-index <ENDPOINT_ID> \
  --deployed-index-id=deployed_financial_docs --region=$REGION
## 3. delete endpoint and index
gcloud ai index-endpoints delete <ENDPOINT_ID> --region=$REGION
gcloud ai indexes delete <INDEX_ID> --region=$REGION
```
Also delete the Cloud Run service and the bucket if you are done with the project.

#### Alternatives
Vector Search 2.0 (collection-based, no separate endpoint step, hybrid search), Postgres + pgvector, Pinecone, Chroma, Vertex AI RAG Engine.

---

### Docker and Cloud Run

**Container starts but every request fails with empty settings**
Cause: the image deliberately contains no `.env` or credentials. Fix for local Docker:
```bash
docker run -p 8080:8080 --env-file .env \
  -e GOOGLE_APPLICATION_CREDENTIALS=/creds/service-account.json \
  -v "$(pwd)/credentials:/creds:ro" meridian-ai
```
On Cloud Run the environment variables and secret are set by the deploy step.

**Cloud Run: "container failed to start and listen on the port"**
Cause: app not listening on `$PORT` (8080) or crashed at start. Fix: read the revision logs (Cloud Run → Logs). The Dockerfile uses `--port ${PORT:-8080}`.

**Docker build fails at `npm ci`**
Cause: lockfile out of sync or no network. Fix: `cd frontend && npm install`, commit `package-lock.json`.

**Python packages fail to build**
Fix: keep `build-essential` in the Dockerfile's apt step.

**Cloud Run URL returns 403 "Forbidden"**
Cause: public access (`allUsers` → `run.invoker`) not applied. The last workflow step grants it.

**First request is slow**
Cause: scale-to-zero cold start. Fine for class; mention `--min-instances` as a paid option.

---

### GitHub Actions deployment

**Auth step fails: "invalid JSON" / "credentials_json"**
Cause: `GCP_CREDENTIALS_JSON` must be the **entire** contents of the key file, including braces. Fix: re-copy the file; no extra quotes.

**`GOOGLE_API_KEY` secret empty → app fails at runtime**
Fix: add it under Settings → Secrets and variables → Actions. The workflow strips whitespace and prints only the key length.

**Image build/push fails for `gcr.io/...` (permission denied / repository does not exist)**
Cause: Google Container Registry is shut down; `gcr.io` addresses only work when backed by an Artifact Registry repository, which can need creating first. **Not yet verified by a real deploy in this project.** Fix options: (a) create the `gcr.io` repository in Artifact Registry (Console → Artifact Registry → Create repository → format Docker, multi-region `us`, name `gcr.io`), or (b) change `IMAGE_NAME` in `deploy.yml` to `us-central1-docker.pkg.dev/<project>/<repo>/meridian-ai-cloud-run` and create that repository with `gcloud artifacts repositories create`.

**"Index creation in progress" loop times out**
Cause: first-time index creation is slow. Fix: re-run the workflow; it skips what already exists.

**Run takes 40+ minutes**
Normal on the first run (vector index + deployment). Later runs are minutes.

**Cloud Run deploy OK but app errors on every call**
Check the printed `INDEX_ID`/`ENDPOINT_ID`; read Cloud Run logs; check `VERTEX_LLM_MODEL_NAME` is a current model.

**Pushes to `main` redeploy everything**
By design (`on: push: main`). While teaching, work on a branch; use *Run workflow* manually.

#### Security notes
- A stored JSON key is a long-lived secret; the safer modern option is **Workload Identity Federation** (no key stored).
- `Editor` + `IAM Admin` is broad; fine for a classroom, not for production.
- `--allow-unauthenticated` makes the app public; `--max-instances 3` limits the damage if someone abuses it.

---


---

<a id="chapter-15"></a>

## 15 · Alternatives and next steps

The project makes one choice per layer. This page lists common alternatives so you can see what else exists and why you might pick it.

### Alternatives by layer

| Layer | This project | Alternatives | When to consider them |
|---|---|---|---|
| Cloud provider | Google Cloud | AWS, Microsoft Azure | Your company already uses them. Concepts map across: project ≈ account/subscription, service account ≈ IAM role, Cloud Storage ≈ S3/Blob Storage, Cloud Run ≈ App Runner / Container Apps |
| Web framework | FastAPI | Flask, Django, Node.js/Express | Flask is simpler, Django is full-stack |
| Chat model | Gemini | Claude, OpenAI GPT, open-source models (Ollama, Vertex Model Garden) | Cost, privacy, quality, or data-residency needs |
| Embeddings | Vertex AI `text-embedding-005` | Gemini embedding models, OpenAI embeddings, open-source (Sentence Transformers) | Different languages or dimensions (a new index is needed if dimensions change) |
| Vector database | Vertex AI Vector Search (index + endpoint) | **Vector Search 2.0** (collections, no separate endpoint step, hybrid search), PostgreSQL + pgvector, Pinecone, Chroma, Vertex AI RAG Engine | Lower hourly cost, simpler setup, or an existing database |
| Retrieval | Top-k similarity, multi-query, contextual compression | MMR (diversity), hybrid keyword + vector search, re-ranking | Better accuracy on large document sets |
| Agents | LangChain `create_agent` | **LangGraph** (explicit graphs), Google Agent Development Kit, CrewAI, AutoGen, Vertex AI Agent Engine | Loops, branches, human approval steps, shared state |
| Hosting | Cloud Run | App Engine, GKE (Kubernetes), a virtual machine, Render, Fly.io | More control, or an existing platform |
| Secrets | Secret Manager | HashiCorp Vault, environment files in the host | Multi-cloud setups |
| CI/CD | GitHub Actions | Cloud Build triggers, GitLab CI, Terraform for the infrastructure | Infrastructure as code, enterprise pipelines |
| Cloud sign-in from CI | Stored service-account key | **Workload Identity Federation** (no stored key) | Always preferred for production |

### Ideas to extend the project

| Idea | What you would learn |
|---|---|
| Add sign-in to the API (API keys, OAuth, or Identity-Aware Proxy) | Securing a public service |
| Show **sources** (file and page) next to each answer | The `source` metadata is already stored with each chunk |
| Evaluate answer quality with a test set of questions | Measuring RAG |
| Stream the answer word by word | Server-sent events |
| Run the three agents in parallel | Faster audits |
| Replace a simulated tool with a real data source | Real tool integration |
| Move the agent flow to explicit LangGraph | Graph state, branches, loops |
| Add a database for audit history | Persistence |
| Migrate to Vector Search 2.0 | Comparing designs and costs |
| Add automated tests in the GitHub workflow | Real CI |

### Keeping the project current

| Item | Where to check |
|---|---|
| Gemini model names and retirement dates | https://ai.google.dev/gemini-api/docs/models |
| Embedding model lifecycle (`text-embedding-005` is listed to retire on 1 April 2027) | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions |
| LangChain / LangGraph releases | https://docs.langchain.com |
| Pinned Python packages | `requirements.txt` |

### Where to go from here

1. Read the code in the order of documents 07 → 08 → 09.
2. Make one of the changes in the table above.
3. Look at the glossary ([16](#chapter-16)) for any word you want defined.


---

<a id="chapter-16"></a>

## 16 · Glossary

| Term | Meaning |
|---|---|
| **LLM** | A model that predicts text. Smart, but only knows what it was trained on. |
| **RAG** | Retrieval-Augmented Generation: find relevant pages first, then let the LLM answer from them. |
| **Embedding** | A list of numbers (here 768) that places a piece of text on a "map of meaning". Similar meaning → nearby. |
| **Chunk** | A small piece of a document (here ~1000 characters) that is embedded and searched. |
| **Vector database** | Storage that finds the nearest vectors quickly. Here: Vertex AI Vector Search. |
| **Index / Endpoint** | The index holds the vectors; the endpoint is the running service that answers searches (billed hourly). |
| **Retriever** | The component that fetches chunks for a question. |
| **Tool** | A Python function the model may call (a "hand"). |
| **Agent** | An LLM that decides which tools to call, in a loop, to finish a task. |
| **Supervisor** | Code that runs several agents and combines their results (the "CFO"). |
| **Prompt** | The instructions given to the model (the "job description"). |
| **FastAPI** | A Python framework for building web APIs. |
| **Pydantic** | Library that checks data matches a defined shape. |
| **Uvicorn** | The server that runs a FastAPI app. |
| **GCP project** | The container for all your Google Cloud resources and billing. |
| **API (Google)** | A Google service you must switch on per project. |
| **IAM / role** | Who may do what. A role is a bundle of permissions. |
| **Service account** | A non-human identity (a robot's badge). |
| **ADC** | Application Default Credentials: how Google libraries find your credentials automatically. |
| **Cloud Storage bucket** | A cloud folder for files. |
| **Secret Manager** | A locker for keys and passwords. |
| **Docker image / container** | A packaged app / a running copy of it. |
| **Artifact Registry** | Where Docker images are stored on GCP. |
| **Cloud Build** | Builds images in the cloud. |
| **Cloud Run** | Runs a container; scales to zero when idle. |
| **CI/CD** | Automatically testing and deploying on every code push. |
| **GitHub Actions** | GitHub's CI/CD system (`.github/workflows/`). |
| **Workload Identity Federation** | Lets GitHub authenticate to GCP with no stored key. |
