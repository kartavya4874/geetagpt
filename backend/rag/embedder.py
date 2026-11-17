"""
RAG Pipeline — Embedder & ChromaDB Vector Store Manager
Uses Chroma's built-in local embedding model (all-MiniLM-L6-v2)
so no external /embeddings API endpoint is required!
"""

import os
from typing import List
from pathlib import Path

try:
    from langchain_core.documents import Document
except ImportError:
    class Document:
        def __init__(self, page_content: str, metadata: dict = None):
            self.page_content = page_content
            self.metadata = metadata or {}

try:
    from langchain_chroma import Chroma
except ImportError:
    Chroma = None

try:
    import chromadb.utils.embedding_functions as ef
    _default_ef = ef.DefaultEmbeddingFunction()
except Exception:
    _default_ef = None

CHROMA_PERSIST_DIR = os.path.join(os.path.dirname(__file__), "../../chroma_db")


class LocalChromaEmbeddings:
    """
    Local embedding generator using Chroma's built-in ONNX model.
    Runs locally on CPU, completely free, fast, and does NOT require
    the remote LLM/vLLM server to have an /embeddings endpoint.
    """
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        if _default_ef is not None:
            return _default_ef(texts)
        # Fallback hash vectors in rare case onnx is unavailable
        return [[float(hash(w) % 1000) for w in t.split()[:64]] for t in texts]

    def embed_query(self, text: str) -> List[float]:
        return self.embed_documents([text])[0]


_embeddings_instance = None


def get_embeddings():
    """Return local embedding function."""
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = LocalChromaEmbeddings()
    return _embeddings_instance


def get_vector_store(collection_name: str = "geetagpt"):
    """Return (or create) a persistent ChromaDB vector store."""
    if Chroma is None:
        raise RuntimeError("langchain-chroma is not installed. Run: pip install langchain-chroma chromadb")
    Path(CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
    return Chroma(
        collection_name=collection_name,
        embedding_function=get_embeddings(),
        persist_directory=CHROMA_PERSIST_DIR,
    )


def add_documents(documents: List[Document], collection_name: str = "geetagpt") -> int:
    """
    Embed and store documents in ChromaDB using local embeddings.

    Returns:
        Number of chunks added.
    """
    store = get_vector_store(collection_name)
    store.add_documents(documents)
    return len(documents)


def list_collections() -> List[str]:
    """List all ChromaDB collections (document sets)."""
    try:
        import chromadb
        Path(CHROMA_PERSIST_DIR).mkdir(parents=True, exist_ok=True)
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        cols = [col.name for col in client.list_collections()]
        return cols if cols else ["geetagpt"]
    except Exception:
        return ["geetagpt"]


def delete_collection(collection_name: str) -> bool:
    """Delete a ChromaDB collection."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
        client.delete_collection(collection_name)
        return True
    except Exception:
        return False
