# 02 · Accounts, the $300 credit and costs

> Prices and free-tier limits change. The numbers below were checked in October 2026. Always confirm on the linked official pages before relying on them.

## 1. Gemini API key (Google AI Studio)

The chat model (`gemini-3.8-flash`) is called with an **API key**. It does not use your Google Cloud billing.

1. Open https://aistudio.google.com/apikey and sign in with your Google account.
2. Choose **Create API key**. Copy it.
3. Keep it secret. Treat it like a password. Never commit it to Git or paste it into screenshots.

| Fact | Detail |
|---|---|
| Free tier | Yes. For `gemini-3.8-flash`, the free tier is "free of charge" for input and output, subject to rate limits. |
| Privacy on the free tier | Google states that free-tier content may be **used to improve its products**. Do not send confidential data. Use only the fictional sample documents. |
| Paid tier | Prices per 1 million tokens: input $0.75, output $3.75 through 31 Dec 2026. From 1 Jan 2027: input $1.50, output $7.50. Paid-tier data is not used to improve products. |
| Rate limits | https://ai.google.dev/gemini-api/docs/rate-limits |
| Model list and retirements | https://ai.google.dev/gemini-api/docs/models |

Models are retired regularly. The project's earlier default, `gemini-2.5-pro`, stops working in October 2026. The model name is a setting (`VERTEX_LLM_MODEL_NAME`), so you can change it without touching code.

## 2. Google Cloud account and the $300 free trial

Google Cloud is needed for the vector database (Vertex AI Vector Search), file storage, and hosting (Cloud Run). Path A does not need it.

### How the free trial works

| Question | Answer (from Google's Free Trial documentation) |
|---|---|
| How much credit? | **$300** of "Welcome credit" |
| For how long? | **90 days** (about three months) from sign-up |
| Who qualifies? | **New customers only**: you have never been a paying Google Cloud, Google Maps Platform or Firebase customer and have not used the trial before |
| Is a card needed? | **Yes.** A valid payment method is required. The authorisation is "a hold, not an actual charge." |
| Do I get charged automatically? | **No.** You are billed only if you manually upgrade to a paid account |
| What if the 90 days or $300 run out first? | The trial ends. After that there is a **30-day grace period**, then free-trial resources are **permanently deleted** unless you upgrade |
| If I upgrade? | You are billed for usage **not covered by the remaining credit**, and for products that are not part of the free trial |

Source: https://docs.cloud.google.com/free/docs/free-cloud-features

The credit is a **balance in dollars**. Every Google Cloud service you use subtracts from it. The 90-day limit and the $300 limit apply together: the trial ends at whichever comes first.

### Trial limitations to know

Google lists these limits for free-trial accounts:

- No GPUs on virtual machines
- No Google Cloud Marketplace
- No quota increase requests
- No Windows Server VMs
- Certain generative AI services are restricted

Some users also report that Vertex AI model requests on trial accounts are throttled hard, with fixed rate limits. In this project the **chat model uses your AI Studio key**, so it is unaffected. **Embeddings use Vertex AI**, so they are the part that could hit a trial limit. If you see a message such as *"Project is not allowed to use …"* or repeated rate-limit errors during document upload, see [14 · Troubleshooting](14-troubleshooting.md). The usual remedy is to **activate the full (paid) account** in Billing. Your remaining credit still applies first. Only usage beyond it is charged.

### Create the account

1. Go to https://cloud.google.com/free and choose **Get started for free**.
2. Sign in, accept the terms, add your payment method.
3. Create a project (done in [05](05-google-cloud-setup.md)).

## 3. Where the money goes

| Service | How it is billed | Expected cost for this project |
|---|---|---|
| **Vertex AI Vector Search** | **Per hour, for as long as an index is deployed to an endpoint, even with zero traffic** | **The main cost.** See the warning below |
| **Cloud Run** | Per use (CPU time, memory, requests). Scales to zero when idle | Usually inside the monthly free allowance for light use (about 2 million requests, 180,000 vCPU-seconds, 360,000 GiB-seconds per month) |
| **Cloud Build** | Per build minute | A monthly free allowance exists (reported as 2,500 minutes) |
| **Cloud Storage** | Per GB stored | A few cents or less for sample PDFs and logs |
| **Artifact Registry** | Per GB of stored images | Small |
| **Secret Manager** | Per active secret version and per access | Small (6 active versions free per month) |
| **Vertex AI embeddings** | Per characters embedded | Small for a few documents |
| **Gemini API chat** | Free tier, or per token on the paid tier | Free tier for light use |

Free-allowance numbers come from public summaries of Google's pricing pages. Confirm on https://cloud.google.com/run/pricing, https://cloud.google.com/build/pricing and https://cloud.google.com/secret-manager/pricing.

### ⚠ The Vector Search endpoint

A Vector Search index is searched through an **endpoint** that keeps one or more machines running. You pay by the hour while the index is **deployed**, whether or not anyone uses it.

- A small `e2-standard-2` node is reported at roughly **$0.077 per hour (about $56 per month per node)** on third-party price guides. This is not an official figure. Check https://cloud.google.com/vertex-ai/pricing.
- The deployment command in `.github/workflows/deploy.yml` does **not** set a machine type or replica count. Google's documentation says that when replica counts are not set they default to **2**. The default machine type is not documented on the pages checked. **Your real hourly cost may therefore be higher than the single-node figure.**
- At $0.077/hour per node, two nodes would use about $3.70 per day. A larger machine type costs more.

**What to do:**
1. Before deploying, create a **budget alert** (steps below).
2. After the first deployment, open **Billing → Reports** the next day and check the daily cost.
3. When you finish a work session, **undeploy and delete** the index and endpoint. See [13 · Cleanup](13-cleanup.md). Re-creating them takes 30–45 minutes, so plan to do your cloud work in one sitting.

### Create a budget alert (do this first)

1. In the Cloud Console open **Billing → Budgets & alerts**.
2. **Create budget**. Name it `meridian-budget`.
3. Scope: your project. Amount: for example **$20**.
4. Alert thresholds: 50 %, 90 %, 100 %. Keep email notifications on.

A budget alert **notifies** you. It does **not stop** spending. You must delete resources yourself.

## 4. GitHub account (paths B and C)

Used to create the cloud resources and deploy the app automatically. Create a free account at https://github.com. GitHub Actions is free for public repositories and has a monthly free allowance for private ones.

## 5. Summary

| Path | Accounts | Money |
|---|---|---|
| A | Google account, Gemini API key | Free |
| B | + Google Cloud (trial) + GitHub | Uses trial credit. Dominated by Vector Search hours |
| C | Same as B | Same cost as B, plus a public URL. Cloud Run is mostly free at low traffic |
