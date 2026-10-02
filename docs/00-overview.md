# 00 · Overview — what you will build

**Meridian AI** is a web application that helps a company check a purchase before paying for it. It has two features:

1. **Document Q&A (RAG).** You upload PDFs (policies, contracts, reports). You ask questions in plain English and get answers based on those documents.
2. **Procurement audit (agents).** You paste a purchase request. Three specialist AI agents review it, then a "CFO" step writes one summary memo:

   | Agent | Checks |
   |---|---|
   | Risk & Compliance | Is the vendor on a sanctions list? How financially safe is the vendor? |
   | Tax & Treasury | What VAT and import duty apply? Is the quoted exchange rate reasonable? |
   | Financial Control | Is it a capital or an operating expense? Who must approve it? |

The company in the examples, **Aldermoor Industries**, is **fictional**. Its documents are made-up teaching data.

> The audit tools ask an AI model from its general knowledge (only the exchange-rate check uses a live data source). This project teaches the architecture. It is **not** a real compliance system.

## What you will learn

| Topic | Where it appears |
|---|---|
| Building a web API with **FastAPI** | `backend/api/` |
| **RAG**: PDF → chunks → embeddings → vector database → answers | `backend/rag/` |
| **Agents** with LangChain: tools, prompts, a supervisor | `backend/agent/` |
| **Google Cloud**: projects, IAM, Cloud Storage, Vertex AI, Cloud Run, Secret Manager | [05](05-google-cloud-setup.md), [11](11-docker-and-cloud-run.md) |
| **Docker** packaging | `Dockerfile` |
| **CI/CD** with GitHub Actions | `.github/workflows/deploy.yml` |
| Organising a project into modules, configuration and tests | [03](03-code-structure.md) |

## What the finished app looks like

Four screens (tabs):

| Tab | What you do |
|---|---|
| **Document Upload** | Upload PDFs so they can be searched |
| **RAG Q&A** | Ask questions about the uploaded documents |
| **Audit** | Run the multi-agent audit on a purchase request |
| **System Status** | See configuration and health |

## Three ways to use this repository

| Path | You need | You get |
|---|---|---|
| **A. Audit only, on your computer** | Gemini API key | The audit feature. Quickest start (about 20 minutes). |
| **B. Everything on your computer** | A + Google Cloud project + GitHub account | Audit **and** document Q&A. The cloud resources (vector database, storage) are created once by the GitHub workflow, then you run the app locally against them |
| **C. Deployed on the internet** | B | The same app on a public Cloud Run URL (the workflow in B already deploys it) |

Read the documents in order: the numbers in the file names are the suggested reading order.
