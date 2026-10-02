# 14 · Troubleshooting

Find the section for the part that is failing. Each entry gives the **symptom** (the message or behaviour), the **cause**, and the **fix**. Most API errors appear in the `detail` field of the response and in the terminal where the backend is running.

**First checks for almost any problem**

1. Are you in the project root folder? (`.env` is read from the folder you run from.)
2. Is the virtual environment active (`(.venv)` in your prompt) and `pip install -r requirements.txt` done?
3. Does `.env` contain your Gemini key and, for cloud features, project, bucket and index IDs? Compare with `.env.example`.
4. Read the last lines of the terminal output. The real error is usually there.

---

## Google Cloud and billing

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

## Running the backend (FastAPI)

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

## Models, LangChain and agents

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

## Vector Search

**Index creation/deployment takes 30–45 minutes the first time.** Normal. Start it hours before class.

**Searches return nothing right after uploading**
Cause: streaming updates take a short time to become searchable. Fix: wait ~30–60 seconds and ask again.

**Dimension mismatch error when upserting**
Cause: the embedding model does not output 768 dimensions (the index is created with 768). Fix: use `text-embedding-005` (default). Changing the model means creating a new index.

**`deployed index not found` / endpoint errors**
Cause: the index is not deployed to the endpoint yet. Check: Console → Vertex AI → Vector Search → Index endpoints.

**Same document uploaded twice → duplicate answers**
Expected: every upload adds chunks again. For class, upload each PDF once.

### Teardown (stops the hourly charge)
```bash
REGION=us-central1
# 1. find ids
gcloud ai index-endpoints list --region=$REGION
gcloud ai indexes list --region=$REGION
# 2. undeploy the index from the endpoint (this is what stops the billing)
gcloud ai index-endpoints undeploy-index <ENDPOINT_ID> \
  --deployed-index-id=deployed_financial_docs --region=$REGION
# 3. delete endpoint and index
gcloud ai index-endpoints delete <ENDPOINT_ID> --region=$REGION
gcloud ai indexes delete <INDEX_ID> --region=$REGION
```
Also delete the Cloud Run service and the bucket if you are done with the project.

### Alternatives
Vector Search 2.0 (collection-based, no separate endpoint step, hybrid search), Postgres + pgvector, Pinecone, Chroma, Vertex AI RAG Engine.

---

## Docker and Cloud Run

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

## GitHub Actions deployment

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

### Security notes
- A stored JSON key is a long-lived secret; the safer modern option is **Workload Identity Federation** (no key stored).
- `Editor` + `IAM Admin` is broad; fine for a classroom, not for production.
- `--allow-unauthenticated` makes the app public; `--max-instances 3` limits the damage if someone abuses it.

---
