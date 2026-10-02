# Reading material

Put the PDFs and notes you share with learners here, **one folder per technology**, so an issue can be matched to the right material quickly.

```
reading/
├── llm-rag-agents/      # concepts: RAG, agents, prompts
├── google-cloud/        # projects, IAM, Storage, billing
├── fastapi/             # routing, Pydantic, async
├── langchain/           # chains, tools, create_agent
├── vector-search/       # embeddings, Vertex AI Vector Search
├── docker-cloud-run/    # containers, Cloud Run, Artifact Registry
└── github-actions/      # CI/CD, secrets, Workload Identity Federation
```

Rules of thumb:
- Name files `NN-topic.pdf` in the order they are used in class (`01-what-is-rag.pdf`).
- Link each file from the matching session in [../TEACHING_GUIDE.md](../TEACHING_GUIDE.md).
- When a learner hits a problem, add the fix to [../troubleshooting/](../troubleshooting/) under the same technology name.
- Do not put keys, `.env` files or service-account JSON here.
