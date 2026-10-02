# FastAPI

**`ModuleNotFoundError: No module named 'api'`**
Cause: started from the wrong folder. Fix: from the **project root** run `uvicorn api.main:app --app-dir backend --reload --port 8080`.

**Settings are empty / `.env` not picked up**
Cause: `.env` is read from the *current folder*. Fix: run from the project root, where `.env` lives.

**`422 Unprocessable Entity`**
Cause: the request body does not match the Pydantic model (e.g. `query` missing). Fix: compare with the schema in `/docs`; the response body says which field is wrong.

**Browser: "blocked by CORS policy"**
Cause: frontend and backend on different origins. The backend allows all origins for the demo. Fix: check the backend is running on port 8080 and that `VITE_API_URL` is not pointing elsewhere.

**`Address already in use` (port 8080)**
Fix: `lsof -i :8080` then stop that process, or use `--port 8081` (and set `VITE_API_URL=http://localhost:8081`).

**`/api/rag/ask` returns 500 with a long message**
The `detail` field contains the real error; look it up in [langchain.md](langchain.md) or [vector-search.md](vector-search.md).

**Frontend shows blank page on the Docker/Cloud Run URL**
Cause: `frontend/dist` was not built into the image. Fix: rebuild the image; check the first Docker stage ran `npm run build`.
