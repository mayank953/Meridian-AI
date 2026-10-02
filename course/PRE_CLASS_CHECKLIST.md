# Pre-class checklist (instructor)

Do this the day before. The first cloud deploy takes **30–45 minutes**, so never start it during class.

## 1. Accounts and keys (you provide; never commit them)
- [ ] GCP project created, **billing linked**, **budget alert set** (e.g. $10).
- [ ] Gemini API key from https://aistudio.google.com/apikey
- [ ] Service account `github-deployer` + JSON key (see README, step 2). Store in `credentials/service-account.json` (git-ignored).
- [ ] `cp .env.example .env` and fill it in. `.env` and `credentials/` are git-ignored and excluded from the Docker image.

## 2. Local dry run (15 min)
```bash
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
pytest backend/tests                       # 8 passed, no cloud needed
```
- [ ] Run these two from the project root (where `.env` is). Model check (this proves your key and the model name work):
```bash
PYTHONPATH=backend python -c "from rag.llm import get_llm; print(get_llm().invoke('Say hello in five words').content)"
```
- [ ] Embedding check (must print 768):
```bash
PYTHONPATH=backend python -c "from rag.embeddings import get_embeddings; print(len(get_embeddings().embed_query('servo motor')))"
```
- [ ] Frontend: `cd frontend && npm ci && npm run build`

## 3. Cloud dry run (start 2+ hours before class)
- [ ] Add GitHub secrets `GCP_PROJECT_ID`, `GCP_CREDENTIALS_JSON`, `GOOGLE_API_KEY`.
- [ ] Run the workflow (Actions → *Deploy to GCP Cloud Run* → *Run workflow*).
- [ ] Copy `INDEX_ID` and `ENDPOINT_ID` from the *Provision Vector Search* step log into `.env`.
- [ ] Open the Cloud Run URL, upload the four PDFs from `course/sample_docs/`, ask the four questions below.

## 4. Expected answers (use these to confirm everything works)
| Question | Expected answer |
|---|---|
| What is Aldermoor Industries total revenue in FY2024? | EUR 2.84 billion |
| What are the standard payment terms for servo motor suppliers? | Net-45 (credit score ≥ 75) |
| What EU customs duty applies to PLC controllers imported from Japan? | 2.2 % |
| What is the IFRS depreciation schedule for filling line equipment? | 10 years, straight-line |

Audit demo: use the default request, then change the FX line to `1 EUR = 190 JPY`. The second should trigger `FX ALERT` and a **CONDITIONAL HOLD** memo. (LLM output varies; the key words should be stable.)

## 5. Day-of
- [ ] Browser tabs: GCP console, GitHub Actions, the app, `/docs`, AI Studio.
- [ ] Terminal font large; `.env` and `credentials/` **not** visible on screen.
- [ ] Budget alert visible and the teardown commands ready ([troubleshooting/vector-search.md](troubleshooting/vector-search.md)).
- [ ] After class: **undeploy and delete the Vector Search index/endpoint.** It bills by the hour.

## 6. Things that change — re-check before every new cohort
- Gemini model names/retirements: https://ai.google.dev/gemini-api/docs/models
- `text-embedding-005` retires **1 Apr 2027**.
- LangChain/LangGraph versions (pinned in `requirements.txt`).
