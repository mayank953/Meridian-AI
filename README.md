<p align="center">
  <h1 align="center">Meridian AI Audit</h1>
  <p align="center">
    <strong>Multi-Agent Procurement Audit & RAG Document Intelligence Platform</strong>
  </p>
  <p align="center">
    Built with FastAPI · React · LangChain · Gemini · Vertex AI · Cloud Run
  </p>
</p>

> **Teaching or learning with this project?** Start with [`course/`](course/README.md): session-by-session teaching guide, pre-class checklist, sample documents and troubleshooting.

---

## Architecture

<p align="center">
  <img src="Supporting Documents/architecture_diagram.png" alt="Meridian AI Architecture" width="100%"/>
</p>

| Layer | Components | Technologies |
|---|---|---|
| **Client** | React Frontend | Vite, TypeScript, Tailwind CSS, Shadcn UI |
| **Compute** | FastAPI Backend on GCP Cloud Run | Uvicorn, CORS, Static File Serving |
| **AI Agents** | Multi-agent Procurement Audit, RAG Pipeline | LangChain (`create_agent`), Gemini 3.8 Flash |
| **Data & AI** | Gemini LLMs, Vertex AI Vector Search, Cloud Storage | Embeddings, GCS Buckets |
| **Security** | Secret Manager | Runtime API Key Injection |
| **CI/CD** | GitHub Actions → Cloud Build → Artifact Registry → Cloud Run | Automated Provisioning & Deployment |

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Deploying to GCP (From Scratch)](#deploying-to-a-brand-new-gcp-project-from-scratch)
  - [Step 1: Create Project & Enable Billing](#step-1-create-the-project-and-enable-billing)
  - [Step 2: Create a Service Account](#step-2-create-a-powerful-service-account)
  - [Step 3: Configure GitHub Secrets](#step-3-configure-github-secrets)
  - [Step 4: Trigger the Pipeline](#step-4-trigger-the-pipeline)
  - [Step 5: Sync Local Environment](#step-5-sync-local-environment)
- [Local Development](#local-development)
  - [1. Backend Setup](#1-backend-setup)
  - [2. Frontend Setup](#2-frontend-setup)
- [Running with Docker](#running-with-docker)
- [How the Code Fits Together](#how-the-code-fits-together)
- [Running the Tests](#running-the-tests)
- [Environment Variables](#environment-variables)

---

## Prerequisites

- **Python** 3.12
- **Node.js** 20+
- **Google Cloud SDK** (`gcloud` CLI) — [Install Guide](https://cloud.google.com/sdk/docs/install)
- **Docker** (optional, for containerised local runs)
- A **GCP project** with billing enabled
- A **Google API Key** for Gemini access

---

## Project Structure

```
Meridian-AI/
├── backend/
│   ├── api/            # FastAPI app, endpoints, and middleware
│   ├── agent/          # LangChain multi-agent procurement audit (agents, tools, prompts)
│   ├── rag/            # RAG pipeline — document indexing & QA
│   ├── config/         # Pydantic settings and app configuration
│   ├── tests/          # Smoke tests (run without Google Cloud)
│   └── logger/         # Structured logging with GCS flush support
├── frontend/
│   ├── src/
│   │   ├── components/ # Shadcn UI and custom React components
│   │   ├── pages/      # Application pages (RAG Q&A, Procurement Audit)
│   │   └── hooks/      # Custom React hooks
│   └── package.json
├── .github/
│   └── workflows/
│       └── deploy.yml  # CI/CD — full GCP provisioning & Cloud Run deploy
├── credentials/        # Local service account keys (git-ignored)
├── Dockerfile          # Multi-stage build (Node + Python)
├── requirements.txt    # Python dependencies (pinned)
├── requirements-dev.txt# + test tools
├── .env.example        # Template for your local .env
└── .env                # Your local environment variables (git-ignored)
```

---

## Deploying to a Brand New GCP Project (From Scratch)

> If you are moving this codebase to an entirely new GCP project where **nothing** has been configured, follow these exact manual steps **once**. After this initial setup, the GitHub Action will fully manage the project for you.

### Step 1: Create the Project and Enable Billing

1. Go to the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a **new project** (e.g., `meridian-ai-prod`).
3. Link an **active Billing Account** to the project.

> [!IMPORTANT]
> Cloud Run and Vertex AI **require active billing** to function. The deployment pipeline will fail silently without it.

### Step 2: Create a Powerful Service Account

The GitHub Action acts as a **"robot administrator"**. It needs permission to enable APIs, create storage buckets, provision vector indexes, and deploy services.

Open Google Cloud Shell (or your local terminal authenticated to your account) and run:

```bash
# Set your active project
export PROJECT_ID="meridian-ai-prod"
gcloud config set project $PROJECT_ID

# Create the GitHub Deployer service account
gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer" \
  --project=$PROJECT_ID

# Grant the "Editor" role so it can build infrastructure
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/editor"

# Grant IAM Admin role so it can manage service-level permissions
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.projectIamAdmin"

# Generate the JSON key file
gcloud iam service-accounts keys create github-deployer-key.json \
  --iam-account=github-deployer@${PROJECT_ID}.iam.gserviceaccount.com
```

> [!CAUTION]
> The `github-deployer-key.json` file contains highly privileged credentials.
> **Never commit this file to version control.** Store it securely and delete the local copy after adding it to GitHub Secrets.

### Step 3: Configure GitHub Secrets

Navigate to your GitHub repository → **Settings** → **Secrets and variables** → **Actions** → **New repository secret**.

Add the following three secrets:

| Secret Name | Value |
|---|---|
| `GCP_PROJECT_ID` | Your new project ID (e.g., `meridian-ai-prod`) |
| `GCP_CREDENTIALS_JSON` | The **entire contents** of `github-deployer-key.json` |
| `GOOGLE_API_KEY` | Your Gemini API key |

### Step 4: Trigger the Pipeline

Push your code to the `main` branch (or manually trigger the workflow via the **Actions** tab).

```bash
git add .
git commit -m <Commit Message>
git push
```

The GitHub Action (`.github/workflows/deploy.yml`) will now automatically:

1. ✅ **Enable** all necessary GCP APIs natively.
2. ✅ **Provision** the Cloud Storage buckets.
3. ✅ **Create** the Vertex AI Vector Search Index & Endpoint *(expect ~30+ min on first run)*.
4. ✅ **Inject** your `GOOGLE_API_KEY` into GCP Secret Manager.
5. ✅ **Build** the Docker image and push to Artifact Registry.
6. ✅ **Deploy** the Cloud Run service with public access.

> [!NOTE]
> The very first deployment can take **30–45 minutes** due to Vector Search index creation. Subsequent deployments typically complete in **3–5 minutes**.

Once complete, the Action logs will print your live Cloud Run URL. **Your application is now fully automated and live!** 🚀

### Step 5: Sync Local Environment

To run the project locally, you must sync it against your newly provisioned GCP infrastructure:

1. **Service Account Credentials:** Move the `github-deployer-key.json` file downloaded in Step 2 into the `credentials/` folder and rename it to `service-account.json`. Your local `.env` and `README` startup commands will now automatically use this file.
2. **Vector Search IDs:** In your GitHub Actions run, expand the **Provision Vector Search Index & Endpoint** step in the logs. Look at the very bottom of that step's output to find your newly generated `INDEX_ID` and `ENDPOINT_ID`.
3. **Update `.env`:** Copy those IDs into your local `.env` file as `VECTOR_SEARCH_INDEX_ID` and `VECTOR_SEARCH_INDEX_ENDPOINT_ID`. Also ensure `GCP_PROJECT_ID` and `GCS_BUCKET_NAME` match your new project.

---

## Local Development

Now that GCP is provisioned and your local credentials/ `.env` are set up, you can run the project locally.

### 1. Backend Setup

```bash
# Clone the repository
git clone https://github.com/<your-org>/Meridian-AI.git
cd Meridian-AI

# Create your local settings file, then fill in the values
cp .env.example .env

# Create and activate a virtual environment
python3.12 -m venv .venv
# Windows
.venv\Scripts\activate
# macOS / Linux
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Set GCP credentials for local development
# Windows (cmd)
set GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json
# Windows (PowerShell)
$env:GOOGLE_APPLICATION_CREDENTIALS="./credentials/service-account.json"
# macOS / Linux
export GOOGLE_APPLICATION_CREDENTIALS=./credentials/service-account.json

# (Optional) Set your quota project
gcloud auth application-default set-quota-project <your-gcp-project-id>

# Start the backend dev server (run this from the project root, where .env lives)
uvicorn api.main:app --app-dir backend --reload --port 8080
```

The API will be available at **http://localhost:8080**. Interactive docs at **http://localhost:8080/docs**.

### 2. Frontend Setup

```bash
# In a new terminal, navigate to the frontend directory
cd frontend

# Install dependencies
npm install

# Start the Vite dev server
npm run dev
```

The frontend will be available at **http://localhost:5173** (default Vite port) and talks directly to the backend at `http://localhost:8080` (see `frontend/src/lib/api.ts`).

---

## Running with Docker

Build and run the unified container that serves both the frontend and backend locally:

```bash
# Build the image
docker build -t meridian-ai .

# Run the container (the image does not contain your .env or credentials, so pass them in)
docker run -p 8080:8080 \
  --env-file .env \
  -e GOOGLE_APPLICATION_CREDENTIALS=/creds/service-account.json \
  -v "$(pwd)/credentials:/creds:ro" \
  meridian-ai
```

The application will be accessible at **http://localhost:8080**.

---

## How the Code Fits Together

Every user action follows the same path: **browser → FastAPI route → LangChain logic → Google Cloud**.

| You click… | Frontend (`frontend/src`) | Route (`backend/api/endpoints.py`) | Logic | Google Cloud |
|---|---|---|---|---|
| **Upload PDF** | `DocumentUploadTab` | `POST /api/rag/upload` | `rag/data_ingestion.py` (load → chunk → embed) | Vertex AI embeddings → Vector Search; PDF copy to Cloud Storage |
| **Ask a question** | `RagQATab` | `POST /api/rag/ask` | `rag/retrieval.py` (retrieve → prompt → Gemini) | Vector Search, Gemini API |
| **Run audit** | `AuditTab` | `POST /api/agent/audit` | `agent/agents.py` (3 agents + CFO), `agent/tools.py`, `agent/prompts.py` | Gemini API |
| **System status** | `SystemStatusTab` | `GET /api/status` | `config/settings.py` | none |

Things worth knowing:

- **Two ways to authenticate to Google.** Chat (Gemini) uses an API key (`GOOGLE_API_KEY`). Embeddings and Vector Search use Google Cloud credentials (the service account).
- **Nothing connects to Google Cloud when the server starts.** Models and the vector store are created the first time they are used, so `/api/health` and `/api/status` work even before GCP is configured.
- **The agents use LangChain's `create_agent`.** It runs on LangGraph internally, but this project contains no graph code.
- **Aldermoor Industries is a fictional company** used for the demo data and prompts.

---

## Running the Tests

The tests need no Google Cloud account or API key; everything external is faked.

```bash
pip install -r requirements-dev.txt
pytest backend/tests
```

---

## Environment Variables

Create a `.env` file in the project root. See the table below for required and optional variables:

| Variable | Required | Description |
|---|:---:|---|
| `ENVIRONMENT` | ✅ | `local` or `production` |
| `GCP_PROJECT_ID` | ✅ | Your Google Cloud project ID |
| `GCP_REGION` | ✅ | GCP region (e.g., `us-central1`) |
| `GOOGLE_API_KEY` | ✅ | Gemini API key |
| `GCS_BUCKET_NAME` | ✅ | GCS bucket for vector staging & uploads |
| `GCS_PREFIX` | | Upload path prefix (default: `uploads/`) |
| `GCP_SERVICE_ACCOUNT_PATH` | | Path to local service account JSON |
| `VERTEX_LLM_MODEL_NAME` | | Chat model (default: `gemini-3.8-flash`) |
| `VERTEX_EMBEDDING_MODEL_NAME` | | Embedding model (default: `text-embedding-005`). Must output 768 dimensions to match the Vector Search index. |
| `VECTOR_SEARCH_INDEX_ID` | ✅ | Vertex AI Vector Search index resource ID |
| `VECTOR_SEARCH_INDEX_ENDPOINT_ID` | ✅ | Vertex AI Vector Search endpoint resource ID |

---

## License

This project is proprietary. All rights reserved.
