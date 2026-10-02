# What changed from the original repo (branch `course-prep`)

Use this if you or a learner compare with the original `main` or older material.

## Behaviour fixes
- **GCS ingestion** (`/api/rag/ingest-gcs`): previously indexed only the last PDF and always returned an error; now indexes every PDF and returns totals.
- **Embeddings were computed twice** during GCS ingestion (a debug block); removed.
- **`ask_question()`** never returned the answer; now it does and the API uses it.
- **Embedding model**: the deploy set `gemini-embedding-2-preview` but the code used `text-embedding-005`, and the status page showed the wrong one. Now one setting (`VERTEX_EMBEDDING_MODEL_NAME`, default `text-embedding-005`, 768 dimensions) is used everywhere.
- **Gemini content blocks**: the CFO memo and tools now handle list-style model replies (previously only agents did).
- **Default chat model** changed from `gemini-2.5-pro` (retires 16 Oct 2026 / closed to new users) to `gemini-3.8-flash`. Temperature is now `LLM_TEMPERATURE`.
- **Unknown `/api/...` URLs** return 404 instead of the React page; static-file serving can no longer escape the `dist` folder.

## Structure (easier to teach)
- One place per idea: chunking and RAG chain live only in `backend/rag/`; routes in `endpoints.py` are thin.
- Models, embeddings, vector store and agents are created on first use (`@lru_cache`), not at import. The API starts and `/api/health` + `/api/status` work with no cloud setup.
- `/api/status` no longer reaches into private vector-store internals; it reports configured IDs.
- `vector_store` (module variable) became `get_vector_store()`.
- FastAPI `lifespan` replaces deprecated `on_event`; timezone-aware timestamps.
- Header comments in each module explain the flow.

## Rebrand
- Krones AG / Mitsubishi / Neutraubling → **Aldermoor Industries** (fictional, Hamburg), vendor **Takumi Controls Europe B.V.** German terms (Kompetenzregelung, Prüfungsvermerk, …) replaced with English. Verdict wording is now `APPROVED TO PAY` / `CONDITIONAL HOLD` / `REJECTED`.
- Product name in the UI is **Meridian AI**.

## Repo hygiene
- Dependencies pinned (`requirements.txt`); `requirements-dev.txt` for tests; `.env.example`.
- 8 smoke tests (`pytest backend/tests`) that need no cloud.
- Dockerfile uses Python 3.12 (matches README).
- Workflow: secret passed via env var, secret-level IAM binding, `--max-instances 3`, embedding model aligned.
- README corrected (no `docker-compose.yml`, correct env names, no "proxy" claim) and extended.

## Not changed on purpose
- `gcr.io` image name in `deploy.yml` (needs a real deploy to validate; see `troubleshooting/github-actions.md`).
- Service-account JSON key auth (taught as the simple path; Workload Identity Federation is explained as the upgrade).
- `allow_origins=["*"]` CORS (explained as demo-only).
