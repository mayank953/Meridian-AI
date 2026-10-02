# Teaching Guide — Meridian AI

How to teach this project live and record it from the same script. The audience is assumed to know **LangChain basics only**. Everything else (Google Cloud, FastAPI, vector search, agents in production, Docker, CI/CD) is explained when it first appears.

Companion files: [PRE_CLASS_CHECKLIST.md](PRE_CLASS_CHECKLIST.md) · [COVERAGE_MATRIX.md](COVERAGE_MATRIX.md) · [CHANGES.md](CHANGES.md) · [GLOSSARY.md](GLOSSARY.md) · [troubleshooting/](troubleshooting/) · [reading/](reading/) · [sample_docs/](sample_docs/)

---

## 1. The teaching method (apply to every session)

1. **Why → What → How.** Open with a problem the learner can feel. Introduce the concept as the relief. Only then show code.
2. **One mental model per topic**, named out loud, and **called back by name** in later sessions.
3. **Analogy before code.** One sentence, drawn on a whiteboard/Excalidraw, before any file is opened.
4. **Recap and bridge.** Start every session with "Last time… Today… Here is how today grows out of last time." End by previewing the next session.
5. **Honest peer voice.** Say what costs money, what can fail, and what you would do differently. Admit mistakes on camera.
6. **Concept first, but always end on something that visibly works** (a request, a response, a page, a log line).

## 2. The one story that holds the whole course together

> **Aldermoor Industries** (fictional) buys parts from suppliers all over the world. Before paying a supplier, someone must check the paperwork: *Is the supplier on a sanctions list? What tax and duty applies? Is it an asset or an expense? And what does our own policy say?*
> Today that takes people days. **Meridian AI is the office that does it in seconds.**

Draw the office once in session 0 and keep it on screen. Every session lights up one part of it:

| Part of the office | Technology | Mental model (say it out loud) |
|---|---|---|
| The building and utilities | **Google Cloud** | "Rent a building, switch on the utilities, hand out staff badges." |
| The front desk | **FastAPI** | "A front desk: takes a form, checks it is filled in, sends it to the right department." |
| The library and librarian | **RAG + Vector Search** | "A librarian who finds pages by *meaning*, not by keyword." |
| The audit team | **LangChain agents** | "A brain that has been given hands (tools), working from a job description (prompt)." |
| The locker and badge system | **Secret Manager + IAM** | "Keys live in a locker. Staff get badges, never copies of keys." |
| The delivery truck | **GitHub Actions + Cloud Run** | "Push your code, a truck builds it and drives it to a shop that opens only when a customer walks in." |

**Callback you will use many times:** *"An LLM alone is a brilliant new hire on day one — smart, but they have never seen your company's files and they cannot pick up the phone."* Files = RAG. Phone = tools.

## 3. Course map (about 5 h 35 min of content)

| # | Session | Min | The problem the learner feels | Files used |
|---|---|---|---|---|
| 0 | Welcome and the big picture | 15 | "What am I going to build and why should I care?" | `Supporting Documents/architecture_diagram.png` |
| 1 | LLM → RAG → agent: why one is not enough | 20 | "Ask ChatGPT about our own policy — it makes something up." | none (slides + live prompt) |
| 2 | Google Cloud from scratch | 35 | "Where does this even run? I have never used GCP." | `deploy.yml` (preview), console |
| 3 | FastAPI: the front desk | 30 | "My Python works in a notebook. How does anyone else use it?" | `api/main.py`, `api/schemas.py`, `api/endpoints.py`, `config/settings.py` |
| 4 | The model layer: Gemini and embeddings | 25 | "How do I call Gemini, and what is an embedding really?" | `rag/llm.py`, `rag/embeddings.py` |
| 5 | RAG: ingest, store, retrieve | 45 | "The model has never read our PDFs." | `rag/data_ingestion.py`, `rag/vector_store.py`, `rag/retrieval.py` |
| 6 | Agents: three specialists and a CFO | 50 | "RAG answers questions, but nothing *does* the checking." | `agent/tools.py`, `agent/prompts.py`, `agent/agents.py` |
| 7 | Wiring it together and running locally | 25 | "I have the pieces. Does it actually work end to end?" | `frontend/src/lib/api.ts`, tabs |
| 8 | Containers and Cloud Run | 30 | "It works on my laptop — nobody else can use it." | `Dockerfile` |
| 9 | Secrets, IAM and CI/CD | 35 | "I do not want to deploy by hand — or leak my API key." | `.github/workflows/deploy.yml` |
| 10 | Operating it: logs, cost, teardown | 15 | "What do I do when it breaks — and how do I not get a surprise bill?" | `logger/custom_logger.py` |
| 11 | Wrap-up and where to go next | 10 | "What now?" | none |

**Live delivery:** add two 10-minute breaks (after 4 and after 7). **Recording:** each session becomes one video (target 20–50 min), except session 6 which may be split at the supervisor.

---

## 4. Session scripts

Each script has: **Bridge**, **Why**, **What (mental model + analogy)**, **How (demo)**, **You try**, **Alternatives (60 s)**, **If it goes wrong**.

### Session 0 — Welcome and the big picture (15 min)
- **Why:** open with the finished app. Upload a PDF, ask a question, press *Run audit*, watch four sections fill in. "By the end of today you will have built and deployed this, and you will understand every line."
- **What:** draw the office (section 2). Show `architecture_diagram.png` and name each box using the office words, not the technology names.
- **How:** explain the rules of the course: concept first, then code; every session ends with something that works; cost warning (Vector Search endpoint bills per hour — we will switch it off at the end).
- **Say honestly:** "Aldermoor is fictional. The audit tools ask an LLM from memory — this is a teaching demo, not a real compliance system."

### Session 1 — LLM → RAG → agent (20 min)
- **Bridge:** "You already know LangChain. Today you will see why LangChain alone is not a product."
- **Why (live):** ask Gemini in AI Studio: *"What are Aldermoor Industries' payment terms for servo motor suppliers?"* It invents an answer or says it does not know. Then ask it to *"check whether this supplier is on a sanctions list and email the CFO"* — it can only talk.
- **What:** "brilliant new hire on day one." RAG = give them the files. Agent = give them a phone and a checklist.
- **How:** draw the pipeline `question → retrieve pages → prompt → answer` and the loop `think → use a tool → look at result → think`.
- **You try:** learners write one question RAG would answer and one task that needs an agent.

### Session 2 — Google Cloud from scratch (35 min)
- **Bridge:** "To run the office, we need a building."
- **Why:** show a laptop-only demo failing for a colleague: "Run this? You need Python, a key, a database…"
- **What:** *project = building you rent; APIs = utilities you switch on; service account = a staff badge for a robot; bucket = a filing cabinet.*
- **How (console + terminal):**
  1. Create a project, link billing, **create a budget alert first** (say why).
  2. `gcloud auth login`, `gcloud config set project <id>`.
  3. Enable APIs and explain each of the 13 in `deploy.yml` in one line (Vertex AI, Cloud Run, Secret Manager, Storage, Artifact Registry, Cloud Build…). Point out `bigquery.googleapis.com` is enabled but unused.
  4. Create the `github-deployer` service account. Explain Editor + IAM Admin is *convenient for a class, too broad for production* (full least-privilege story in session 9).
  5. Create a bucket in the console. Upload a file. Delete it.
- **You try:** create a project and a $10 budget alert.
- **Alternatives:** AWS (S3, IAM, App Runner), Azure (Blob, Entra ID, Container Apps). Same ideas, different names.
- **If it goes wrong:** see [troubleshooting/google-cloud.md](troubleshooting/google-cloud.md).

### Session 3 — FastAPI: the front desk (30 min)
- **Bridge:** "We have a building. Now we need a front desk so people can send us work."
- **Why:** a function in a notebook cannot be called by a browser, a phone or a colleague.
- **What:** *front desk: takes a form, checks it is filled in (Pydantic), sends it to the right department, hands back the answer.*
- **How:**
  1. In a scratch file, write a 6-line FastAPI app. Run with `uvicorn`. Open `/docs` and click *Try it out*.
  2. Open `api/schemas.py`: `AuditRequest`, `QueryRequest`. Send a bad request on purpose — show the automatic 422 error.
  3. Open `api/endpoints.py` top to bottom using the docstring map. Show how thin the routes are: *validate → call logic → return JSON*.
  4. `config/settings.py`: values come from `.env`; show `.env.example`.
  5. `api/main.py`: routers, CORS, serving the React build.
- **Talk about:** `def` vs `async def` — upload is `async` because it awaits file reads; the slow embedding work is pushed to a worker thread with `run_in_threadpool`.
- **You try:** add a `GET /api/ping` that returns the server time.
- **Alternatives:** Flask (simpler, no validation), Django (full-stack), Node/Express.
- **If it goes wrong:** [troubleshooting/fastapi.md](troubleshooting/fastapi.md).

### Session 4 — The model layer (25 min)
- **Bridge:** "The front desk can take a request. Who actually answers?"
- **Why:** you need a model to write answers and a way to compare *meaning*.
- **What:** **two doors into Google.** *Door 1: the API-key door (Gemini chat — `rag/llm.py`). Door 2: the staff-badge door (Vertex AI embeddings — `rag/embeddings.py`, uses your service account).* **Embedding = GPS coordinates for meaning**: sentences about the same thing land close together.
- **How:**
  1. From the project root, start Python with `PYTHONPATH=backend python`, then: `from rag.llm import get_llm; get_llm().invoke("Say hello")`.
  2. `get_embeddings().embed_query("servo motor")` → print `len(...)` → **768**. Say why 768 matters (the index was created with 768 dimensions; the same model must be used for indexing and searching).
  3. Show `@lru_cache` and why nothing connects at import (the app can start before GCP is ready).
- **Say honestly:** models are retired often. `gemini-2.5-pro` stops on 16 Oct 2026; this project uses `gemini-3.8-flash`. The model name is a setting, not hard-coded.
- **Alternatives:** OpenAI, Claude, open-source via Vertex Model Garden/Ollama.

### Session 5 — RAG: ingest, store, retrieve (45 min)
- **Bridge:** "We have a brain and a way to measure meaning. It still has never read our files."
- **Why:** repeat the failing question from session 1.
- **What:**
  - **Chunking = cutting pages into index cards**, with a little overlap so no sentence is cut in half (1000 characters, 100 overlap).
  - **Vector Search = a card catalogue organised by meaning.** *Index = the catalogue. Endpoint = the reading room that is open to visitors.* (And it bills by the hour while open.)
- **How:**
  1. `data_ingestion.py`: read top to bottom: `PyPDFLoader → split → embed → add_documents`.
  2. Upload the four PDFs from `course/sample_docs/` in the UI. Show the response (`pages`, `chunks`).
  3. `retrieval.py`: the two chains. Draw `retriever → prompt(context + question) → Gemini`.
  4. Ask the four example questions. **Expected answers:** revenue FY2024 = €2.84 billion; servo-motor suppliers = Net-45 (if score ≥ 75); PLC duty from Japan = 2.2 %; filling-line depreciation = 10 years straight-line.
  5. Switch retriever: *Normal*, *Multi-Query*, *Contextual Compression*. Show the speed/quality trade-off.
  6. Ask something not in the documents → "I don't know". Praise that behaviour.
- **Talk about:** `langchain_classic` vs new LangChain 1.x. `create_retrieval_chain` lives in `langchain-classic`; agents use the new `create_agent`. Search results online will mix both — explain once.
- **You try:** change `CHUNK_SIZE` to 300, re-upload, ask again. What changed?
- **Alternatives:** Vector Search 2.0 (collection-based, no separate endpoint), pgvector, Pinecone, Chroma, Vertex RAG Engine.
- **If it goes wrong:** [troubleshooting/vector-search.md](troubleshooting/vector-search.md).

### Session 6 — Agents: three specialists and a CFO (50 min)
- **Bridge:** "RAG answers questions. Now we need someone who *does the checking*." Call back: **brain with no hands** → here come the hands.
- **Why:** run the audit prompt against the plain LLM (no tools): it guesses the tax rate and never checks the FX rate.
- **What:**
  - **Tool = a hand** (`@tool` function with a clear docstring — the model reads it to decide when to use it).
  - **Prompt = the job description** (role, responsibilities, decision framework, output format — point at the four parts in `prompts.py`).
  - **Agent = brain + hands + job description, in a loop.**
  - **Supervisor = the CFO** who reads three reports and writes one memo.
- **How:**
  1. `tools.py`: walk `check_sanctions_list` (LLM from memory), `validate_fx_hedge` (a *real* web API with an LLM fallback). Say plainly which tools are real and which are simulated.
  2. `prompts.py`: read the Risk prompt aloud. Show that the CFO prompt relies on exact trigger words (`RED ALERT`, `FX ALERT`, `HOLD FOR TREASURY AUDIT`).
  3. `agents.py`: `create_agent(model, tools, system_prompt)`. Three agents, one supervisor, four phases.
  4. Run the audit from the UI with the default request. **What to expect:** the unknown fictional vendor usually gets a mid/low credit score (the tool says unknown → 45) so risk is flagged; show the memo.
  5. Run a second request with `1 EUR = 190 JPY`. **Expected:** `FX ALERT` → CFO memo says **CONDITIONAL HOLD**. This shows the rule chain working.
  6. Open the logs: each phase logged.
- **Talk about:** `create_agent` runs on LangGraph underneath; we write no graph code. Mention explicit LangGraph for loops/branches as the "next step".
- **Say honestly:** results vary run to run; tools simulated by an LLM are for teaching; real systems call real sanctions/credit APIs and keep a human in the loop.
- **You try:** add a sixth tool (e.g. `check_delivery_risk(country)`) and add it to the Control agent.
- **Alternatives:** LangGraph (explicit graphs), Google ADK, CrewAI, AutoGen, Vertex AI Agent Engine.

### Session 7 — Wiring it together and running locally (25 min)
- **Bridge:** "We built every room. Let's walk one form through the whole office."
- **What:** *Follow one form through the office.* Use the table in the README ("How the code fits together").
- **How:**
  1. Terminal 1: `uvicorn api.main:app --app-dir backend --reload --port 8080`. Terminal 2: `cd frontend && npm install && npm run dev`.
  2. Open DevTools → Network. Click *Ask*. Show the request to `/api/rag/ask` and the JSON response.
  3. Open `frontend/src/lib/api.ts` — one small file where the browser meets the backend. Do **not** teach React.
  4. Use `/docs` to call the same endpoint without the UI.
  5. Show `/api/status`.
  6. `pytest backend/tests` — 8 tests, no cloud needed.
- **You try:** upload a PDF, ask a question, run an audit — all through `/docs` only.

### Session 8 — Containers and Cloud Run (30 min)
- **Bridge:** "It works on my laptop. Now let's make it work on every laptop and a server."
- **What:** *container = a shipping container: the same box runs anywhere.* *Cloud Run = a shop that opens only when a customer walks in, and closes when nobody is there.*
- **How:**
  1. `Dockerfile` — two stages: build the React app with Node, then Python image that contains the backend and the built frontend. Explain why multi-stage keeps the image small.
  2. `docker build -t meridian-ai .` then `docker run` with `--env-file` and the credentials mounted (the image contains no secrets, on purpose).
  3. Open `http://localhost:8080` — frontend and API from one container.
  4. Explain Artifact Registry (image storage), Cloud Build (builds the image in the cloud), Cloud Run (runs it), `PORT`, scale to zero, `--max-instances`.
- **Alternatives:** App Engine, GKE, Compute Engine VM, Vercel/Render for the frontend.

### Session 9 — Secrets, IAM and CI/CD (35 min)
- **Bridge:** "Deploying by hand is slow and error-prone. Let's put a truck on a schedule."
- **What:** *keys live in a locker (Secret Manager); staff get badges (IAM roles), never copies of keys.* *CI/CD = an assembly line: push code → build → test → deliver.*
- **How:**
  1. Walk `deploy.yml` phase by phase: enable APIs → bucket → vector index → endpoint → secret → build → deploy → public access.
  2. Why the first run takes 30+ minutes (index creation and deployment). Tell learners you started it earlier.
  3. Add the three GitHub secrets (`GCP_PROJECT_ID`, `GCP_CREDENTIALS_JSON`, `GOOGLE_API_KEY`) — never show the real values.
  4. Security review aloud: JSON key in a secret = long-lived credential (works, but the modern, safer option is **Workload Identity Federation**, no stored key); Editor role is broad; `--allow-unauthenticated` means the URL is public — we capped `--max-instances 3`.
  5. Trigger the workflow from the Actions tab (`workflow_dispatch`).
- **Alternatives:** Cloud Build triggers, Terraform, GitLab CI.
- **If it goes wrong:** [troubleshooting/github-actions.md](troubleshooting/github-actions.md).

### Session 10 — Operating it (15 min)
- **What:** *the utility bill.* Logs tell you what happened; the meter tells you what it costs.
- **How:** read the JSON logs in Cloud Logging (filter `severity>=ERROR`); show the log file flushed to the bucket on shutdown; show the billing report; then **tear down**: undeploy the index from the endpoint and delete it (commands in [troubleshooting/vector-search.md](troubleshooting/vector-search.md)).

### Session 11 — Wrap-up (10 min)
- Re-draw the office with every room lit. Name every technology *using the office words first*.
- Next steps: authentication in front of the API, evaluation of answers, streaming responses, Vector Search 2.0, explicit LangGraph, real sanctions/credit APIs.
- Point to `course/reading/` and the troubleshooting folder.

---

## 5. Checkpoints (ask live; use as quiz questions in the recording)

| After session | Question |
|---|---|
| 1 | Which problem does RAG solve, and which does an agent solve? |
| 2 | What is the difference between a service account and an API key? |
| 3 | What happens if the request body does not match the Pydantic model? |
| 4 | Why must the embedding model be the same at indexing time and at query time? |
| 5 | What is the difference between the index and the endpoint, and which one bills by the hour? |
| 6 | Why does the CFO prompt contain exact words like `RED ALERT`? |
| 7 | Which file is the only place the browser talks to the backend? |
| 8 | Why does the Docker image not contain `.env`? |
| 9 | Why is a stored JSON key riskier than Workload Identity Federation? |
| 10 | What is the first thing you do after the course to avoid a surprise bill? |

## 6. Teachability audit — can we teach and cover everything?

**Result: yes, with the gaps below closed.** The sessions above cover every file in `backend/`, `Dockerfile`, `deploy.yml` and the one frontend file that matters (`api.ts`); see [COVERAGE_MATRIX.md](COVERAGE_MATRIX.md).

| Gap found in the original repo | Fix |
|---|---|
| Real company branding and German-only jargon | Fictional Aldermoor Industries, English terms |
| Default model `gemini-2.5-pro` retires 16 Oct 2026 and is closed to new users | Default is `gemini-3.8-flash`; model and temperature are settings |
| GCS ingestion silently indexed only the last PDF and always errored | Fixed, shared code path with upload |
| Duplicate chunking and RAG code in three places | One place each (`rag/`) |
| Everything connected to Google Cloud at import time (could not demo a piece alone) | Lazy creation; `/api/health` and `/api/status` work with no GCP |
| No demo documents; UI example questions had nothing to answer them | Four fictional PDFs in `course/sample_docs/` that answer them |
| Unpinned dependencies | Pinned in `requirements.txt` |
| README errors (no `docker-compose.yml`, wrong env names, "proxy") | Corrected |
| No tests | 8 smoke tests, no cloud needed |

**Still to confirm with real keys (cannot be checked without them):**
1. `gemini-3.8-flash` works with the agent tools through `langchain-google-genai` 4.2.1 (tool calling with Gemini 3 models). If it loops or repeats, set `LLM_TEMPERATURE=1.0` or try `gemini-3.5-flash`.
2. The upload → index → ask loop returns the expected answers in section 5 of session 5.
3. The audit memo shows `CONDITIONAL HOLD` for the 190 JPY request.
4. A full GitHub Actions run on a fresh project, including `gcr.io` image push (Container Registry is shut down; `gcr.io` URLs only work through Artifact Registry repositories — see `troubleshooting/github-actions.md`).
5. `text-embedding-005` is retired on 1 April 2027 — update before the next cohort.

## 7. Recording workflow

1. Run the [PRE_CLASS_CHECKLIST.md](PRE_CLASS_CHECKLIST.md) the day before; start the cloud deploy at least two hours early.
2. Record each session in order from a clean terminal. Keep the office diagram on the second screen.
3. Per session: recap (1 min) → why (3–5 min) → analogy drawing → files + demo → *You try* → checkpoint question → bridge.
4. Never edit out a failure that a learner is likely to hit; keep it and fix it on camera, then link the matching troubleshooting page.
5. Keep reference PDFs in `course/reading/<technology>/` and add new troubleshooting entries to `course/troubleshooting/<technology>.md` whenever a learner reports a problem.
