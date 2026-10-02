# 16 · Glossary

| Term | Meaning |
|---|---|
| **LLM** | A model that predicts text. Smart, but only knows what it was trained on. |
| **RAG** | Retrieval-Augmented Generation: find relevant pages first, then let the LLM answer from them. |
| **Embedding** | A list of numbers (here 768) that places a piece of text on a "map of meaning". Similar meaning → nearby. |
| **Chunk** | A small piece of a document (here ~1000 characters) that is embedded and searched. |
| **Vector database** | Storage that finds the nearest vectors quickly. Here: Vertex AI Vector Search. |
| **Index / Endpoint** | The index holds the vectors; the endpoint is the running service that answers searches (billed hourly). |
| **Retriever** | The component that fetches chunks for a question. |
| **Tool** | A Python function the model may call (a "hand"). |
| **Agent** | An LLM that decides which tools to call, in a loop, to finish a task. |
| **Supervisor** | Code that runs several agents and combines their results (the "CFO"). |
| **Prompt** | The instructions given to the model (the "job description"). |
| **FastAPI** | A Python framework for building web APIs. |
| **Pydantic** | Library that checks data matches a defined shape. |
| **Uvicorn** | The server that runs a FastAPI app. |
| **GCP project** | The container for all your Google Cloud resources and billing. |
| **API (Google)** | A Google service you must switch on per project. |
| **IAM / role** | Who may do what. A role is a bundle of permissions. |
| **Service account** | A non-human identity (a robot's badge). |
| **ADC** | Application Default Credentials: how Google libraries find your credentials automatically. |
| **Cloud Storage bucket** | A cloud folder for files. |
| **Secret Manager** | A locker for keys and passwords. |
| **Docker image / container** | A packaged app / a running copy of it. |
| **Artifact Registry** | Where Docker images are stored on GCP. |
| **Cloud Build** | Builds images in the cloud. |
| **Cloud Run** | Runs a container; scales to zero when idle. |
| **CI/CD** | Automatically testing and deploying on every code push. |
| **GitHub Actions** | GitHub's CI/CD system (`.github/workflows/`). |
| **Workload Identity Federation** | Lets GitHub authenticate to GCP with no stored key. |
