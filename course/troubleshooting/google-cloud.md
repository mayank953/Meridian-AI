# Google Cloud

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
Cause: the Vector Search endpoint keeps a node running 24/7. Fix: see [vector-search.md](vector-search.md) (teardown) and set a budget alert.
