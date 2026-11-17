"""
GeetaGPT — FastAPI Backend
Main application entry point.
"""

import os
import sys
import shutil
import tempfile
from pathlib import Path
from typing import Optional

# Support running from root directory or from inside the backend directory
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

load_dotenv()

try:
    from backend.config import get_llm_base_url, get_llm_model
    from backend.memory import get_history, clear_history
except ImportError:
    from config import get_llm_base_url, get_llm_model
    from memory import get_history, clear_history

try:
    from backend.agents.parent_agent import run_parent_agent
    from backend.rag.loader import load_document
    from backend.rag.chunker import chunk_documents
    from backend.rag.embedder import add_documents, list_collections, delete_collection
except ImportError:
    from agents.parent_agent import run_parent_agent
    from rag.loader import load_document
    from rag.chunker import chunk_documents
    from rag.embedder import add_documents, list_collections, delete_collection

# ─── App Setup ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="GeetaGPT API",
    description="Multi-Agent RAG System for Geeta University",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # tighten in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Request / Response Models ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str
    collection_name: Optional[str] = "geetagpt"
    top_k: Optional[int] = 5
    session_id: Optional[str] = "default"


class ChatResponse(BaseModel):
    answer: str
    agent: str
    routing: dict
    query: str
    session_id: Optional[str] = "default"
    sources: Optional[list] = None
    tool_used: Optional[str] = None
    tool_query: Optional[str] = None
    context_chunks: Optional[int] = None


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"message": "GeetaGPT API is running 🎓", "status": "ok"}


@app.on_event("startup")
def on_startup():
    print("=" * 60)
    print("🎓 GeetaGPT Backend Started")
    print(f"📡 Configured LLM Base URL : {get_llm_base_url()}")
    print(f"🤖 Configured LLM Model    : {get_llm_model()}")
    print("=" * 60)


@app.get("/health")
def health():
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint. Routes query through the Parent Orchestrator Agent.
    """
    if not request.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    try:
        result = run_parent_agent(
            query=request.query,
            collection_name=request.collection_name,
            top_k=request.top_k,
            session_id=request.session_id or "default",
        )
        return result
    except Exception as e:
        import traceback
        import openai
        traceback.print_exc()
        if isinstance(e, openai.APIConnectionError):
            llm_url = get_llm_base_url()
            raise HTTPException(
                status_code=503,
                detail=f"Cannot connect to local LLM server at '{llm_url}'. Please ensure your local LLM (e.g. Ollama, LM Studio, vLLM) is started and listening."
            )
        raise HTTPException(status_code=500, detail=f"{type(e).__name__}: {str(e)}")


@app.get("/history/{session_id}")
def get_chat_history(session_id: str):
    """Retrieve full persistent conversation history for a session."""
    try:
        messages = get_history(session_id)
        return {"session_id": session_id, "messages": messages}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/history/{session_id}")
def delete_chat_history(session_id: str):
    """Clear conversation history for a session (Start New Chat)."""
    try:
        clear_history(session_id)
        return {"status": "cleared", "session_id": session_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    collection_name: str = Form(default="geetagpt"),
    chunk_size: int = Form(default=1000),
    chunk_overlap: int = Form(default=200),
):
    """
    Upload and ingest a document into the RAG knowledge base.
    Supports: PDF, TXT, DOCX, CSV, MD
    """
    allowed_extensions = {".pdf", ".txt", ".docx", ".csv", ".md", ".markdown"}
    ext = Path(file.filename).suffix.lower()

    if ext not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed: {', '.join(allowed_extensions)}"
        )

    # Save to temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        # Load → Chunk → Embed
        docs = load_document(tmp_path)
        chunks = chunk_documents(docs, chunk_size=chunk_size, chunk_overlap=chunk_overlap)

        # Tag with original filename
        for chunk in chunks:
            chunk.metadata["source"] = file.filename

        num_added = add_documents(chunks, collection_name=collection_name)

        return {
            "status": "success",
            "filename": file.filename,
            "pages_loaded": len(docs),
            "chunks_created": num_added,
            "collection": collection_name,
        }
    finally:
        os.unlink(tmp_path)


@app.get("/collections")
def get_collections():
    """List all available document collections."""
    try:
        cols = list_collections()
        return {"collections": cols}
    except Exception as e:
        return {"collections": [], "error": str(e)}


@app.delete("/collections/{collection_name}")
def remove_collection(collection_name: str):
    """Delete a document collection from ChromaDB."""
    try:
        delete_collection(collection_name)
        return {"status": "deleted", "collection": collection_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

