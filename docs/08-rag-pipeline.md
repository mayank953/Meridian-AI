# 08 · Document question answering — the RAG pipeline (`backend/rag/`)

**RAG** (Retrieval-Augmented Generation) lets a language model answer from *your* documents, which it has never seen in training.

```
Preparing (once per document)                  Asking (every question)
PDF → pages → chunks → embeddings → store      question → embedding → closest chunks
                                                          → prompt (chunks + question) → Gemini → answer
```

## Concepts

| Term | Meaning |
|---|---|
| **Chunk** | A short piece of a document (here about 1000 characters). Small pieces make search precise |
| **Overlap** | Consecutive chunks share some text (100 characters) so a sentence is not cut in half |
| **Embedding** | A list of numbers (here 768) that represents the *meaning* of a text. Texts with similar meaning have similar numbers |
| **Vector database** | Storage that can quickly find the stored vectors closest to a given vector |
| **Index** | In Vertex AI Vector Search: the stored vectors and the structure used to search them |
| **Endpoint** | The running service that answers searches against a deployed index. It bills by the hour |
| **Retriever** | The LangChain component that returns the best chunks for a question |

## `llm.py` — the chat model

```python
@lru_cache(maxsize=1)
def get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model=settings.llm_model_name,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=settings.llm_temperature,
    )
```

- It uses the **Gemini API key**, not Google Cloud credentials.
- `lru_cache` creates the model once and reuses it. Nothing is created at import time.
- `extract_text()` in the same file handles Gemini replies that arrive as a list of content blocks instead of plain text.

## `embeddings.py` — text to numbers

```python
@lru_cache(maxsize=1)
def get_embeddings() -> VertexAIEmbeddings:
    return VertexAIEmbeddings(model_name=settings.embedding_model_name)
```

- Uses Vertex AI and your **Google Cloud credentials**.
- `text-embedding-005` produces **768** numbers per text.
- The index was created with 768 dimensions (see `index_metadata.json` and the workflow). Documents and questions must use **the same** embedding model. If you change the model, create a new index.

Check it yourself (from the project root):

```bash
PYTHONPATH=backend python -c "from rag.embeddings import get_embeddings; print(len(get_embeddings().embed_query('servo motor')))"
```

Expected output: `768`.

## `vector_store.py` — the database connection

```python
@lru_cache(maxsize=1)
def get_vector_store() -> VectorSearchVectorStore:
    aiplatform.init(project=settings.GCP_PROJECT, location=settings.GCP_REGION)
    return VectorSearchVectorStore.from_components(
        project_id=settings.GCP_PROJECT,
        region=settings.GCP_REGION,
        embedding=get_embeddings(),
        index_id=settings.vector_search_index_id,
        endpoint_id=settings.vector_search_index_endpoint_id,
        gcs_bucket_name=settings.GCS_BUCKET_NAME,
        stream_update=True,
    )
```

- `stream_update=True` lets new documents become searchable within a short time. Without it, updates are applied in batches.
- The bucket is used for staging data when adding documents.
- If the index ID is empty you get `index_id is required for api_version='v1'`.

## `data_ingestion.py` — getting documents in

```python
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 100

def split_into_chunks(pages):
    splitter = RecursiveCharacterTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    return splitter.split_documents(pages)

def ingest_pdf(local_path, source):
    pages = PyPDFLoader(local_path).load()
    for page in pages:
        page.metadata["source"] = source
    chunks = split_into_chunks(pages)
    if chunks:
        get_vector_store().add_documents(chunks)
    return {"pages": len(pages), "chunks": len(chunks)}
```

Step by step: load the PDF into pages → mark each page with where it came from → split into chunks → embed and store. `add_documents` calls the embedding model for you.

Two routes use `ingest_pdf`:

| Route | Source of the PDF |
|---|---|
| `POST /api/rag/upload` | Files uploaded from the browser |
| `POST /api/rag/ingest-gcs` | PDFs already in the Cloud Storage bucket (`ingest_data_from_gcs`) |

PDFs that contain only scanned images have no text to extract; the upload route reports them as skipped.

## `retrieval.py` — answering

```python
def ask_question(query, retriever_type="similarity") -> str:
    prompt = ChatPromptTemplate.from_messages([("system", SYSTEM_PROMPT), ("human", "{input}")])
    question_answer_chain = create_stuff_documents_chain(get_llm(), prompt)
    rag_chain = create_retrieval_chain(build_retriever(retriever_type), question_answer_chain)
    response = rag_chain.invoke({"input": query})
    return response["answer"]
```

Two chains:

1. `create_stuff_documents_chain` puts ("stuffs") the retrieved chunks into the prompt where `{context}` appears, then calls the model.
2. `create_retrieval_chain` runs the retriever first, then the first chain.

The system prompt tells the model to answer only from the context and say it does not know otherwise:

```
Use the following pieces of retrieved context to answer the question.
If you don't know the answer based on the context, say that you don't know.
```

### Retrieval strategies

`build_retriever` returns one of three retrievers:

| Name | Behaviour | Trade-off |
|---|---|---|
| `similarity` | Closest 3 chunks | Fastest, cheapest |
| `multiquery` | Gemini writes several versions of the question; results are merged | Finds more, uses extra model calls |
| `contextual` | Fetch 10 chunks, then Gemini shortens each to the relevant sentences | Cleaner context, slowest |

### A note on package names

`create_retrieval_chain` and the retrievers come from **`langchain-classic`** (imports start with `langchain_classic`). The agent code uses the current `langchain` package (`from langchain.agents import create_agent`). Both are in `requirements.txt`. Online examples mix old and new import paths, so check which package an import comes from.

## Try it yourself

1. Change `CHUNK_SIZE` to 300 in `data_ingestion.py`, upload a PDF again, and compare the answers.
2. Ask a question using each retriever type and note the response time.
3. Ask a question whose answer is not in your documents.
4. Read `index_metadata.json` and find `"dimensions": 768`.
