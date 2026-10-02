# 12 · Automated deployment with GitHub Actions

**CI/CD** means *continuous integration / continuous delivery*: every time you push code, a machine builds it and (optionally) deploys it, the same way each time. In this project the workflow file is `.github/workflows/deploy.yml`.

## When it runs

```yaml
on:
  push:
    branches: [main]
  workflow_dispatch:
```

- Automatically on every push to the `main` branch.
- Manually from **Actions → Deploy to GCP Cloud Run → Run workflow** (`workflow_dispatch`).

> Pushes to other branches do **not** deploy. Do your experiments on a branch and merge to `main` when you want to deploy.

## Settings at the top

```yaml
env:
  PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
  REGION: us-central1
  SERVICE_NAME: meridian-ai-cloud-run
  IMAGE_NAME: gcr.io/${{ secrets.GCP_PROJECT_ID }}/meridian-ai-cloud-run
  VECTOR_BUCKET: gs://${{ secrets.GCP_PROJECT_ID }}-vector-staging
  INDEX_NAME: financial-docs-production
  ENDPOINT_NAME: financial-docs-endpoint
```

`${{ secrets.NAME }}` reads a GitHub secret (see [05](05-google-cloud-setup.md)). The region is fixed to `us-central1`; if you change it, also change `GCP_REGION` in your `.env`.

## The steps

| # | Step | What it does |
|---|---|---|
| 1 | Checkout | Downloads your code onto the GitHub runner |
| 2 | Authenticate | Signs in to Google Cloud with `GCP_CREDENTIALS_JSON` |
| 3 | Set up Cloud SDK | Installs `gcloud` on the runner |
| 4 | Enable APIs | `gcloud services enable …` for Vertex AI, Cloud Run, Secret Manager, Storage, Artifact Registry, Cloud Build, Logging, Monitoring, Trace, IAM, Resource Manager, BigQuery and Generative Language; waits 90 s |
| 5 | Buckets | Creates `gs://<project>-vector-staging` if it does not exist (no public access) |
| 6 | Initial embeddings file | `generate_json.py` writes a single random 768-number vector; it is copied to the bucket so the index can be created with at least one item |
| 7 | Vector Search | Creates the **index** (768 dimensions, streaming updates), the **endpoint**, and **deploys** the index. Each part is skipped if it already exists. Then removes the dummy vector. Slow the first time |
| 8 | Secrets | Creates the secret `GOOGLE_API_KEY`, adds your key as a new version, and lets Cloud Run's service account read **that secret** |
| 9 | Build | `gcloud builds submit` builds and stores the image |
| 10 | Deploy | `gcloud run deploy` with environment variables, the secret and `--max-instances 3` |
| 11 | Public access | Allows anyone to invoke the service and prints the access policy |

Notes:

- The workflow is **idempotent**: a second run reuses what exists, so it finishes in minutes.
- The index and endpoint IDs are passed to Cloud Run as `VECTOR_SEARCH_INDEX_ID` and `VECTOR_SEARCH_INDEX_ENDPOINT_ID`.
- The Gemini key is read inside the shell step through an environment variable, so its value is not written into the command text.
- BigQuery's API is enabled but not used by the application.
- The deployed Vector Search index starts billing as soon as it is deployed. See [02](02-accounts-credits-costs.md).

## Reading a run

1. Open **Actions** and click the run.
2. Click the job *Provision & Deploy*. Each step can be expanded.
3. A red cross marks the failed step; the last lines of its log show the error. Common causes are in [14 · Troubleshooting](14-troubleshooting.md).
4. Re-run with **Re-run failed jobs**. Because of the idempotent design, re-running is safe.

## Security points

| Topic | Detail |
|---|---|
| Secrets | GitHub encrypts them and hides their values in logs. Never print them or put them in code |
| The JSON key | It is a long-lived credential. A more secure alternative is **Workload Identity Federation**, where GitHub proves its identity to Google Cloud without any stored key ([15](15-alternatives-and-next-steps.md)) |
| Broad roles | `editor` and `projectIamAdmin` are convenient for learning. Production deployers get narrower roles |
| Public service | `allUsers` can invoke the service. Add sign-in before putting real data in |
