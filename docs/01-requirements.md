# 01 · Requirements

Check this list before you start. Details for accounts and costs are in [02 · Accounts, credits and costs](02-accounts-credits-costs.md).

## Knowledge you need

| You should know | Level |
|---|---|
| Python | Comfortable with functions, classes, packages, virtual environments |
| **LangChain basics** | Prompts, chat models, chains, what a tool is |
| Command line | Run commands, change directories, set environment variables |
| Git | Clone a repository |

You do **not** need prior experience with Google Cloud, FastAPI, vector databases, Docker, or CI/CD. They are explained in these documents.

## Accounts you need

| Account | Needed for | Cost | Required for path |
|---|---|---|---|
| **Google account** (Gmail or Workspace) | Everything Google | Free | A, B, C |
| **Gemini API key** from Google AI Studio | The chat model (answers and agents) | Free tier available | A, B, C |
| **Google Cloud account** with billing enabled | Vector database, storage, Cloud Run | $300 free credit for new customers (see 02) | B, C |
| **GitHub account** | Creates the cloud resources and deploys the app (GitHub Actions) | Free | B, C |

A **credit or debit card is required** to create a Google Cloud account, even for the free trial. Google places a temporary authorisation hold to verify it. It is not a charge.

## Software you need

| Tool | Version | Used for | Check with |
|---|---|---|---|
| **Python** | 3.12 | Backend | `python3 --version` |
| **Node.js** and npm | 20 or newer | Frontend | `node --version` |
| **Git** | any recent | Getting the code | `git --version` |
| **Google Cloud CLI** (`gcloud`) | recent | Cloud setup (paths B, C) | `gcloud --version` |
| **Docker Desktop** | recent | Optional, container run | `docker --version` |
| A code editor | e.g. VS Code | Reading and editing | — |
| A web browser | any | The app and Google Cloud console | — |

Install links:
- Python: https://www.python.org/downloads/
- Node.js: https://nodejs.org/
- Google Cloud CLI: https://cloud.google.com/sdk/docs/install
- Docker: https://docs.docker.com/get-docker/

**Windows users:** the commands in these documents use macOS/Linux syntax. Use **WSL 2** (Windows Subsystem for Linux) for the smoothest experience, or use the Windows variants shown where they differ.

## Computer and network

| Item | Minimum |
|---|---|
| RAM | 8 GB |
| Free disk space | 3 GB (Python packages, Node packages, Docker image) |
| Internet | Required (Google APIs, package downloads) |

## Time you should plan

| Task | Time |
|---|---|
| Path A (audit only, local) | about 20–30 minutes |
| Google Cloud setup | about 30–45 minutes |
| First cloud deployment (mostly waiting for the vector index) | **30–45 minutes**, unattended |
| Reading the code walkthroughs | 2–3 hours |

## Before you continue

- [ ] I have a Google account.
- [ ] I can create a Gemini API key (see 02).
- [ ] I have Python 3.12, Node.js 20+, and Git installed.
- [ ] For paths B and C: I have a payment card for Google Cloud verification, and I have read the cost warnings in 02.
- [ ] For paths B and C: I have a GitHub account.
