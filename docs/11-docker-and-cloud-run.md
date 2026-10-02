# 11 · Docker and Cloud Run

## Concepts

| Term | Meaning |
|---|---|
| **Image** | A packaged, read-only snapshot of an application and everything it needs |
| **Container** | A running copy of an image |
| **Dockerfile** | The recipe for building an image |
| **Multi-stage build** | A Dockerfile with several stages; only the last stage ends up in the final image |
| **Artifact Registry** | Google Cloud's storage for images |
| **Cloud Build** | Builds images in Google Cloud |
| **Cloud Run** | Runs containers on request, scaling from zero to many |

## The Dockerfile

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

### What is *not* in the image

`.dockerignore` excludes `.env`, `credentials/`, `.git/`, logs and `node_modules`. Secrets are supplied when the container runs, never baked into the image:

```bash
docker run -p 8080:8080 \
  --env-file .env \
  -e GOOGLE_APPLICATION_CREDENTIALS=/creds/service-account.json \
  -v "$(pwd)/credentials:/creds:ro" \
  meridian-ai
```

## Cloud Run

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

> **Public URL warning.** The deployed app has no sign-in. Anyone who finds the URL can upload files and run audits that use your Gemini quota. Delete the service when you are done ([13](13-cleanup.md)). Do not upload confidential documents.

## Image registry note

The workflow uses an image name of the form `gcr.io/<project>/…`. Google's older *Container Registry* has been shut down; `gcr.io` addresses now work only through Artifact Registry repositories. If the build or push step fails with a permission or "repository does not exist" error, see the GitHub Actions entry in [14 · Troubleshooting](14-troubleshooting.md).
