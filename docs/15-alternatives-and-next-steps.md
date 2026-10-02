# 15 · Alternatives and next steps

The project makes one choice per layer. This page lists common alternatives so you can see what else exists and why you might pick it.

## Alternatives by layer

| Layer | This project | Alternatives | When to consider them |
|---|---|---|---|
| Cloud provider | Google Cloud | AWS, Microsoft Azure | Your company already uses them. Concepts map across: project ≈ account/subscription, service account ≈ IAM role, Cloud Storage ≈ S3/Blob Storage, Cloud Run ≈ App Runner / Container Apps |
| Web framework | FastAPI | Flask, Django, Node.js/Express | Flask is simpler, Django is full-stack |
| Chat model | Gemini | Claude, OpenAI GPT, open-source models (Ollama, Vertex Model Garden) | Cost, privacy, quality, or data-residency needs |
| Embeddings | Vertex AI `text-embedding-005` | Gemini embedding models, OpenAI embeddings, open-source (Sentence Transformers) | Different languages or dimensions (a new index is needed if dimensions change) |
| Vector database | Vertex AI Vector Search (index + endpoint) | **Vector Search 2.0** (collections, no separate endpoint step, hybrid search), PostgreSQL + pgvector, Pinecone, Chroma, Vertex AI RAG Engine | Lower hourly cost, simpler setup, or an existing database |
| Retrieval | Top-k similarity, multi-query, contextual compression | MMR (diversity), hybrid keyword + vector search, re-ranking | Better accuracy on large document sets |
| Agents | LangChain `create_agent` | **LangGraph** (explicit graphs), Google Agent Development Kit, CrewAI, AutoGen, Vertex AI Agent Engine | Loops, branches, human approval steps, shared state |
| Hosting | Cloud Run | App Engine, GKE (Kubernetes), a virtual machine, Render, Fly.io | More control, or an existing platform |
| Secrets | Secret Manager | HashiCorp Vault, environment files in the host | Multi-cloud setups |
| CI/CD | GitHub Actions | Cloud Build triggers, GitLab CI, Terraform for the infrastructure | Infrastructure as code, enterprise pipelines |
| Cloud sign-in from CI | Stored service-account key | **Workload Identity Federation** (no stored key) | Always preferred for production |

## Ideas to extend the project

| Idea | What you would learn |
|---|---|
| Add sign-in to the API (API keys, OAuth, or Identity-Aware Proxy) | Securing a public service |
| Show **sources** (file and page) next to each answer | The `source` metadata is already stored with each chunk |
| Evaluate answer quality with a test set of questions | Measuring RAG |
| Stream the answer word by word | Server-sent events |
| Run the three agents in parallel | Faster audits |
| Replace a simulated tool with a real data source | Real tool integration |
| Move the agent flow to explicit LangGraph | Graph state, branches, loops |
| Add a database for audit history | Persistence |
| Migrate to Vector Search 2.0 | Comparing designs and costs |
| Add automated tests in the GitHub workflow | Real CI |

## Keeping the project current

| Item | Where to check |
|---|---|
| Gemini model names and retirement dates | https://ai.google.dev/gemini-api/docs/models |
| Embedding model lifecycle (`text-embedding-005` is listed to retire on 1 April 2027) | https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/model-versions |
| LangChain / LangGraph releases | https://docs.langchain.com |
| Pinned Python packages | `requirements.txt` |

## Where to go from here

1. Read the code in the order of documents 07 → 08 → 09.
2. Make one of the changes in the table above.
3. Look at the glossary ([16](16-glossary.md)) for any word you want defined.
