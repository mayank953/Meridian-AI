# 06 · Run the project on your computer

Two stages. **Stage 1** needs only a Gemini API key and gives you the audit feature. **Stage 2** adds document Q&A and needs the cloud resources from [05](05-google-cloud-setup.md).

All commands are run from the **project root folder** (the folder that contains `backend/`, `frontend/` and `README.md`). This matters: settings are read from the `.env` file in the folder you run from.

## Stage 0 · Get the code and install packages

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

## Stage 1 · Audit only (Gemini key only)

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

### Add the user interface

Open a **second terminal** (keep the backend running):

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:3000 and use the **Audit** tab. The page sends its requests directly to `http://localhost:8080`.

## Stage 2 · Document Q&A (needs the cloud resources)

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

## Stage 3 · Run it in Docker (optional)

```bash
docker build -t meridian-ai .

docker run -p 8080:8080 \
  --env-file .env \
  -e GOOGLE_APPLICATION_CREDENTIALS=/creds/service-account.json \
  -v "$(pwd)/credentials:/creds:ro" \
  meridian-ai
```

Open http://localhost:8080. One container now serves the user interface and the API. The image contains no `.env` and no credentials; you supply them when you run it.

## Common problems

| Message or symptom | See |
|---|---|
| `ModuleNotFoundError: No module named 'api'` | Run from the project root with `--app-dir backend` |
| Settings seem empty | `.env` is read from the folder you run from |
| `index_id is required for api_version='v1'` | Set `VECTOR_SEARCH_INDEX_ID` and the endpoint ID |
| `403` from Cloud Storage or Vertex AI | [14 · Troubleshooting](14-troubleshooting.md) |
| Port 8080 already in use | Stop the other program or use `--port 8081` |
