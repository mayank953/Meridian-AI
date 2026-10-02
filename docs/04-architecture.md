# 04 · Architecture

## 1. The big picture

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

## 2. The layers

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

### Two ways of signing in to Google

The project uses both:

| Used for | How it authenticates | Setting |
|---|---|---|
| Gemini chat (`rag/llm.py`) | **API key** | `GOOGLE_API_KEY` |
| Embeddings, Vector Search, Cloud Storage | **Google Cloud credentials** (a service account, or your own login) | `GCP_SERVICE_ACCOUNT_PATH` or `gcloud auth application-default login` |

## 3. Request flows

### 3.1 Uploading a document

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

### 3.2 Asking a question

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

### 3.3 Running an audit

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

### 3.4 Deploying

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

## 4. Google Cloud services used and why

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

Alternatives to each service are listed in [15 · Alternatives and next steps](15-alternatives-and-next-steps.md).

## 5. Important design decisions

| Decision | Reason |
|---|---|
| One container serves both frontend and API | One URL, no CORS problems in production, simpler deployment |
| The embedding model must give **768** numbers | The index is created with 768 dimensions. The same model must be used when storing and searching |
| Chat uses an API key, embeddings use Google Cloud credentials | Shows both authentication styles; the key is kept in Secret Manager in production |
| Models and connections are created on first use | The app starts and the health check works before the cloud is configured |
| Agents are built with LangChain's `create_agent` | It runs on LangGraph internally, so the project contains no graph code to maintain |
| Log files are uploaded to Cloud Storage on shutdown | Cloud Run's local disk disappears when the container stops |
