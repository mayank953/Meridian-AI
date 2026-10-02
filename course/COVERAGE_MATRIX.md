# Coverage matrix — every file has a home

| File | What it does | Taught in |
|---|---|---|
| `backend/config/settings.py` | Reads configuration from `.env` | Session 3 |
| `backend/api/schemas.py` | Request/response shapes (Pydantic) | Session 3 |
| `backend/api/endpoints.py` | The routes (thin; call the logic) | Sessions 3, 7 |
| `backend/api/main.py` | App, CORS, routers, serves the React build | Session 3 |
| `backend/rag/llm.py` | Gemini chat model (API-key door) | Session 4 |
| `backend/rag/embeddings.py` | Vertex AI embeddings (badge door), 768 dims | Session 4 |
| `backend/rag/data_ingestion.py` | PDF → chunks → vectors | Session 5 |
| `backend/rag/vector_store.py` | Connection to Vertex AI Vector Search | Session 5 |
| `backend/rag/retrieval.py` | Retrieve → prompt → answer; 3 retrieval strategies | Session 5 |
| `backend/agent/tools.py` | The five tools (the hands) | Session 6 |
| `backend/agent/prompts.py` | The job descriptions | Session 6 |
| `backend/agent/agents.py` | Three agents + supervisor | Session 6 |
| `backend/logger/custom_logger.py` | JSON logs, flush to GCS on shutdown | Session 10 |
| `backend/tests/` | Smoke tests without cloud | Session 7 |
| `frontend/src/lib/api.ts` | The only place the browser calls the backend | Session 7 |
| `frontend/src/components/*Tab.tsx` | The four screens (shown, not taught) | Sessions 5–7 |
| `Dockerfile` | Two-stage image: React build + Python | Session 8 |
| `.github/workflows/deploy.yml` | Provision + build + deploy | Sessions 2, 9 |
| `generate_json.py`, `init_embeddings.json`, `index_metadata.json` | Bootstrap vector for index creation (the workflow regenerates them) | Session 9 |
| `.env.example` | Template for local settings | Sessions 3, 7 |
| `course/sample_docs/` | Fictional demo PDFs | Session 5 |

## Concept → where

| Concept | Session | Alternatives to mention |
|---|---|---|
| LLM limits, RAG, agents | 1 | fine-tuning vs RAG |
| GCP project, IAM, service accounts, Storage, APIs | 2 | AWS / Azure |
| REST, FastAPI, Pydantic, CORS, async | 3 | Flask, Django, Express |
| Gemini via API key vs Vertex via credentials | 4 | OpenAI, Claude, Model Garden |
| Embeddings, dimensions | 4 | other embedding models |
| Chunking, overlap | 5 | semantic chunking |
| Vector Search (index vs endpoint), retrievers | 5 | Vector Search 2.0, pgvector, Pinecone, Chroma, RAG Engine |
| Tools, prompts, `create_agent`, supervisor pattern | 6 | LangGraph, ADK, CrewAI, AutoGen, Agent Engine |
| Docker multi-stage | 8 | buildpacks |
| Cloud Run, Artifact Registry, Cloud Build | 8 | GKE, App Engine, VM |
| Secret Manager, least privilege, Workload Identity Federation | 9 | Vault, env files |
| GitHub Actions CI/CD | 9 | Cloud Build triggers, Terraform |
| Logging, cost, teardown | 10 | Cloud Monitoring, budgets |
