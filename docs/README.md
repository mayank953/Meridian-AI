# Meridian AI — Learner Guide

Welcome. These documents explain the Meridian AI project step by step: what it does, what you need, how the code is organised, how to run it on your computer, and how to deploy it to Google Cloud.

Read them in order. You can also open any one on its own.

| # | Document | What you will find |
|---|---|---|
| 00 | [Overview](00-overview.md) | What you will build; three ways to use the repository |
| 01 | [Requirements](01-requirements.md) | Knowledge, accounts, software, time |
| 02 | [Accounts, credits and costs](02-accounts-credits-costs.md) | Gemini API key, Google Cloud account, how the **$300 / 90-day** free trial works, what costs money, budget alerts |
| 03 | [Code structure](03-code-structure.md) | Folder layout, **why the code is split into modules**, what each file does, configuration |
| 04 | [Architecture](04-architecture.md) | Diagrams, request flows, Google Cloud services and why each is used |
| 05 | [Google Cloud setup](05-google-cloud-setup.md) | Project, billing, service account, GitHub secrets, first deployment |
| 06 | [Run it on your computer](06-run-locally.md) | Audit-only start, document Q&A, tests, Docker |
| 07 | [The web API](07-backend-api.md) | FastAPI, schemas, routes, settings |
| 08 | [Document Q&A (RAG)](08-rag-pipeline.md) | Chunks, embeddings, Vector Search, retrieval |
| 09 | [The audit agents](09-agents.md) | Tools, prompts, `create_agent`, supervisor |
| 10 | [The user interface](10-frontend.md) | How the React app talks to the backend |
| 11 | [Docker and Cloud Run](11-docker-and-cloud-run.md) | Containers and hosting |
| 12 | [GitHub Actions deployment](12-cicd-github-actions.md) | The automated pipeline, step by step |
| 13 | [Cleanup](13-cleanup.md) | Stop all charges |
| 14 | [Troubleshooting](14-troubleshooting.md) | Symptoms, causes and fixes |
| 15 | [Alternatives and next steps](15-alternatives-and-next-steps.md) | Other tools and project ideas |
| 16 | [Glossary](16-glossary.md) | Plain-English definitions |

Everything in one file: [MERIDIAN_AI_COMPLETE_GUIDE.md](MERIDIAN_AI_COMPLETE_GUIDE.md) (generated from the documents above with `python docs/build_complete_guide.py`).

## Quick start (about 20 minutes, no Google Cloud needed)

```bash
git clone https://github.com/mayank953/Meridian-AI.git
cd Meridian-AI
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements-dev.txt
cp .env.example .env            # then put your Gemini API key in .env
uvicorn api.main:app --app-dir backend --reload --port 8080
```

Open http://localhost:8080/docs and try the audit endpoint. Full steps: [06](06-run-locally.md).

## Important

- **Aldermoor Industries is fictional.** The sample documents contain made-up data.
- **Cloud features cost money after your free credit.** Read [02](02-accounts-credits-costs.md) and [13](13-cleanup.md) before creating cloud resources.
- **Never commit keys.** `.env` and `credentials/` are ignored by Git; keep it that way.
