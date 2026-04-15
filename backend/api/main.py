"""
FastAPI Backend — Procurement Audit & RAG Document Intelligence
===============================================================
Exposes REST endpoints for:
  1. Running multi-agent procurement audits  (agent.py)
  2. Uploading documents into Vertex AI Vector Search  (rag.py)
  3. Querying the RAG pipeline
"""
import os

from api.endpoints import health_router,status_router,agent_router,rag_router

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from logger import _LOGGER_INSTANCE
from config.settings import settings
from logger import GLOBAL_LOGGER as log

# ---------------------------------------------------------------------------
# App Initialisation
# ---------------------------------------------------------------------------
app = FastAPI(
    title= settings.app_name,
    version=settings.app_version,
    description="Multi-agent procurement audit & RAG document intelligence backend.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],            # Tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(health_router)
app.include_router(status_router)
app.include_router(agent_router)
app.include_router(rag_router)


@app.on_event("shutdown")
async def shutdown_event():
    """Flush logs to GCS upon application shutdown (critical for Cloud Run)."""
    
    _LOGGER_INSTANCE.flush_to_gcs()


# ============================================================
# Serve Frontend Static Files (for unified Docker deployment)
# ============================================================

frontend_dist = os.path.join(os.path.dirname(__file__), "../../frontend/dist")

if os.path.exists(frontend_dist):
    # Mount assets so they are served quickly
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    # Catch-all route to serve files or fallback to index.html for React Router
    @app.get("/{catchall:path}")
    def serve_frontend(catchall: str):
        file_path = os.path.join(frontend_dist, catchall.lstrip("/"))
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    
    log.warning("Frontend dist not found — frontend will not be served.", path=frontend_dist)

