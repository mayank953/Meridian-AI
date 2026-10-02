# Docker and Cloud Run

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
