# 07 · The web API (`backend/api/`)

The API is the part of the program that a browser (or any other program) can talk to over HTTP. It is built with **FastAPI** and run by **Uvicorn**.

## Concepts

| Term | Meaning |
|---|---|
| **Endpoint / route** | A URL plus an HTTP method, e.g. `POST /api/rag/ask` |
| **Request / response** | What the caller sends and what it gets back, here as JSON |
| **Pydantic model** | A Python class that describes the expected shape of data and checks it automatically |
| **Router** | A group of related routes |
| **CORS** | A browser rule about which websites may call your API |
| **Uvicorn** | The server program that runs the FastAPI app |

## A minimal FastAPI app

```python
from fastapi import FastAPI
app = FastAPI()

@app.get("/hello")
def hello():
    return {"message": "hello"}
```

Run it with `uvicorn file_name:app --reload`, then open `http://localhost:8000/hello` and `http://localhost:8000/docs`. Meridian's API follows the same pattern, with more routes.

## `schemas.py` — the shapes of data

```python
class AuditRequest(BaseModel):
    request_text: str

class AuditResponse(BaseModel):
    risk_result: str
    tax_result: str
    control_result: str
    cfo_memo: str

class QueryRequest(BaseModel):
    query: str
    retriever_type: str = "similarity"

class QueryResponse(BaseModel):
    answer: str
```

If a caller sends a body without `query`, FastAPI rejects it with status **422** and names the missing field. You do not write that check yourself. The same classes produce the documentation at `/docs`.

## `endpoints.py` — the routes

Routers group the URLs:

```python
health_router = APIRouter(prefix="/api", tags=["Health"])
status_router = APIRouter(prefix="/api", tags=["Status"])
agent_router  = APIRouter(prefix="/api/agent", tags=["Agent"])
rag_router    = APIRouter(prefix="/api/rag", tags=["RAG"])
```

Each route is short. It validates input (through the schema), calls one function from `rag/` or `agent/`, and returns the result. The question route:

```python
@rag_router.post("/ask", response_model=QueryResponse)
def rag_query(payload: QueryRequest):
    try:
        return QueryResponse(answer=ask_question(payload.query, payload.retriever_type))
    except Exception as e:
        log.error("RAG query failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
```

When something goes wrong the route returns status 500 and the real error text in `detail`. The front end shows this message, and so do the troubleshooting tips in [14](14-troubleshooting.md).

### Upload is `async`; the others are not

`POST /api/rag/upload` is declared `async def` because it must `await` the uploaded file. Embedding a document is slow, blocking work, so it is handed to a worker thread:

```python
summary = await run_in_threadpool(ingest_pdf, local_path, f"upload://{upload.filename}")
```

This keeps the server responsive to other requests, such as the health check, while a large PDF is processed.

### The audit route builds its supervisor on first use

```python
@lru_cache(maxsize=1)
def get_supervisor() -> ProcurementSupervisor:
    return ProcurementSupervisor()
```

`lru_cache` makes the function run once and remember the result. The agents are created at the first audit request, not when the server starts.

## `main.py` — putting it together

`main.py` creates the `FastAPI` app, adds the CORS middleware, registers the four routers and, if the folder `frontend/dist` exists (inside Docker and Cloud Run), serves the built React application:

- `/assets/...` is served as static files.
- Any other path returns the file if it exists, otherwise `index.html`, so the React app can handle its own pages.
- Unknown URLs that start with `/api/` return a 404 error instead of the web page.
- A path check makes sure requests cannot read files outside the `dist` folder.

A `lifespan` function runs when the server stops and uploads the log file to Cloud Storage.

CORS is set to allow all origins (`allow_origins=["*"]`). That is convenient for learning. For a real product, list only your own domain(s).

## `config/settings.py` — settings in one place

```python
class Settings(BaseSettings):
    llm_model_name: str = Field("gemini-3.8-flash", validation_alias="VERTEX_LLM_MODEL_NAME")
    embedding_model_name: str = Field("text-embedding-005", validation_alias="VERTEX_EMBEDDING_MODEL_NAME")
    ...
    model_config = SettingsConfigDict(env_file=".env", ...)
```

`pydantic-settings` reads environment variables and the `.env` file and turns them into typed attributes (`settings.GCP_PROJECT`, …). The rest of the code imports `settings`; no other file reads `.env`.

## Try it yourself

1. Start the backend. In `/docs`, send `POST /api/rag/ask` with the body `{}`. Read the 422 response.
2. Open `/api/status`. Change `GCP_REGION` in `.env`, restart, and open it again.
3. In `endpoints.py` add a route `GET /api/ping` that returns the current time. Reload `/docs` to see it appear.
