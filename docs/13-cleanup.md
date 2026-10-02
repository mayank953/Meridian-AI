# 13 · Cleanup — stop all charges

Do this at the end of every cloud session. Deployed Vector Search keeps billing even when nobody uses the app.

## What costs money while it exists

| Resource | Stops billing when you … |
|---|---|
| Vector Search **deployed index** on an endpoint | **Undeploy** it |
| Vector Search endpoint and index | Delete them (undeploy first) |
| Cloud Run service | Delete it (idle cost is zero, but delete anyway) |
| Cloud Storage bucket | Empty and delete it (tiny cost) |
| Artifact Registry images | Delete the repository or images (tiny cost) |

## Option 1 · Remove only the expensive part

```bash
export REGION=us-central1

# 1. Find the IDs
gcloud ai index-endpoints list --region=$REGION
gcloud ai indexes list --region=$REGION

# 2. Undeploy the index from the endpoint (this stops the hourly charge)
gcloud ai index-endpoints undeploy-index ENDPOINT_ID \
  --deployed-index-id=deployed_financial_docs --region=$REGION

# 3. Delete the endpoint and the index
gcloud ai index-endpoints delete ENDPOINT_ID --region=$REGION
gcloud ai indexes delete INDEX_ID --region=$REGION
```

When you start again, run the workflow; it re-creates the index and endpoint (30–45 minutes) and gives you new IDs for `.env`.

## Option 2 · Remove the Cloud Run service

```bash
gcloud run services delete meridian-ai-cloud-run --region=us-central1
```

## Option 3 · Delete everything (safest)

Deleting the project removes every resource in it and stops all charges. Google keeps a deleted project recoverable for 30 days.

```bash
gcloud projects delete YOUR_PROJECT_ID
```

## Also clean up credentials

- Delete the service-account key if you no longer need it: Console → IAM & Admin → Service accounts → `github-deployer` → Keys.
- Delete the local `github-deployer-key.json`.
- Remove the GitHub secrets if you are finished (Settings → Secrets and variables → Actions).
- If your Gemini API key was ever exposed, delete it at https://aistudio.google.com/apikey and create a new one.

## Check that nothing is still running

1. Console → **Vertex AI → Vector Search → Index endpoints**: no deployed indexes.
2. Console → **Cloud Run**: no services.
3. Console → **Billing → Reports**: cost per day drops to about zero the next day.
4. Your budget alert from [02](02-accounts-credits-costs.md) remains as a safety net.
