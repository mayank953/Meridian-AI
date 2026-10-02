# 05 · Google Cloud setup (paths B and C)

You will create a Google Cloud project, a robot account for GitHub, and let a GitHub workflow create everything else. Read [02](02-accounts-credits-costs.md) first and create your budget alert.

Total time: about 30 minutes of work plus 30–45 minutes of waiting.

## Step 1 · Create a project

A **project** is the container for all your Google Cloud resources and billing.

1. Open https://console.cloud.google.com/ and sign in.
2. Click the project selector at the top → **New project**.
3. Name it, for example `meridian-ai`. Note the **Project ID** shown under the name (for example `meridian-ai-123456`). It must be globally unique, and you cannot change it later. You will use the ID, not the name.
4. Click **Create** and select the new project.

## Step 2 · Link billing

Cloud Run and Vertex AI do not work without a billing account linked to the project. The free trial credit is applied through this billing account.

1. Open **Billing** in the console menu.
2. Link a billing account to your project. If this is your first time, the free-trial sign-up is offered here.
3. Create the budget alert described in [02](02-accounts-credits-costs.md) if you have not already.

## Step 3 · Install and sign in to the Google Cloud CLI

```bash
gcloud auth login
gcloud config set project YOUR_PROJECT_ID
gcloud config list
```

Replace `YOUR_PROJECT_ID` with the Project ID from step 1. `gcloud config list` should show your project.

## Step 4 · Create the deployer service account

A **service account** is an identity for a program instead of a person. GitHub will use this one to build and deploy on your behalf.

```bash
export PROJECT_ID="YOUR_PROJECT_ID"

# 1. Create the account
gcloud iam service-accounts create github-deployer \
  --display-name="GitHub Actions Deployer" \
  --project=$PROJECT_ID

# 2. Give it permission to create resources
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/editor"

# 3. Give it permission to manage access settings
gcloud projects add-iam-policy-binding $PROJECT_ID \
  --member="serviceAccount:github-deployer@${PROJECT_ID}.iam.gserviceaccount.com" \
  --role="roles/resourcemanager.projectIamAdmin"

# 4. Create a key file
gcloud iam service-accounts keys create github-deployer-key.json \
  --iam-account=github-deployer@${PROJECT_ID}.iam.gserviceaccount.com
```

On Windows PowerShell, replace `export PROJECT_ID="..."` with `$env:PROJECT_ID="..."` and `$PROJECT_ID` with `$env:PROJECT_ID`.

> **Security notes**
> - `github-deployer-key.json` is a powerful credential. **Never commit it**, email it, or paste it anywhere except the GitHub secret in step 6. Delete the local copy after you have added it to GitHub.
> - The `editor` and `projectIamAdmin` roles are broad. They keep this tutorial simple. A production project would give a deployer only the specific roles it needs, and would use *Workload Identity Federation* so that no key file exists at all ([15](15-alternatives-and-next-steps.md)).
> - If the key is ever exposed, delete it: Console → IAM & Admin → Service accounts → `github-deployer` → Keys → delete.

## Step 5 · Get your copy of the code on GitHub

The deployment workflow runs in **your own** GitHub repository.

1. On the project's GitHub page choose **Fork** (or create a new repository and push the code to it).
2. Open the **Actions** tab of your fork. If GitHub shows a notice that workflows are disabled on forks, enable them.

## Step 6 · Add three GitHub secrets

In your repository: **Settings → Secrets and variables → Actions → New repository secret**.

| Secret name | Value |
|---|---|
| `GCP_PROJECT_ID` | Your Project ID, e.g. `meridian-ai-123456` |
| `GCP_CREDENTIALS_JSON` | The **entire contents** of `github-deployer-key.json`, including the braces |
| `GOOGLE_API_KEY` | Your Gemini API key from AI Studio |

## Step 7 · Run the deployment workflow

1. Open **Actions → Deploy to GCP Cloud Run → Run workflow** (choose your branch).
   The workflow also starts automatically on every push to `main`.
2. The workflow performs these stages (each is a step you can expand in the log):

   | Stage | What happens |
   |---|---|
   | Authenticate | Signs in with the service-account key |
   | Enable APIs | Switches on the Google APIs the project needs, then waits 90 seconds |
   | Storage | Creates the bucket `<project-id>-vector-staging` |
   | Vector Search | Creates a small starter file, an index, an endpoint, and deploys the index to the endpoint. **The first run takes 30–45 minutes** |
   | Secrets | Stores your Gemini key in Secret Manager and lets Cloud Run read it |
   | Build | Cloud Build builds the Docker image |
   | Deploy | Cloud Run starts the service and gives it a public URL |
   | Public access | Allows anyone with the URL to open it |

3. Wait until the run shows a green check. Later runs take a few minutes because the index already exists.

## Step 8 · Collect the values you need locally

You need three things from the run.

**The Vector Search index and endpoint IDs.** Either read them from the workflow log (step *Provision Vector Search Index & Endpoint*, lines starting `Created Index:`, `Index already exists:`, `Created Endpoint:` or `Endpoint already exists:`) or ask Google Cloud:

```bash
gcloud ai indexes list --region=us-central1
gcloud ai index-endpoints list --region=us-central1
```

Copy the ID shown for `financial-docs-production` (index) and `financial-docs-endpoint` (endpoint). Either the plain number or the full `projects/…/indexes/…` path works in `.env`.

**The public URL.** In the *Deploy to Cloud Run* step log, find `Service URL: https://…run.app`.

**The bucket name.** `<project-id>-vector-staging`.

## Step 9 · What now exists in your project

Check in the console that you can see them:

| Resource | Where to look |
|---|---|
| Bucket `<project-id>-vector-staging` | Cloud Storage → Buckets |
| Index and endpoint | Vertex AI → Vector Search |
| Secret `GOOGLE_API_KEY` | Security → Secret Manager |
| Image | Artifact Registry |
| Service `meridian-ai-cloud-run` | Cloud Run |

> **Cost reminder:** the deployed Vector Search index is billing by the hour right now. See the warning in [02](02-accounts-credits-costs.md) and the cleanup steps in [13](13-cleanup.md).

## Next

[06 · Run it locally](06-run-locally.md), using the IDs you just collected.
