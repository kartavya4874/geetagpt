"""
RAG Pipeline — Retriever
Performs similarity search against ChromaDB and returns top-k documents.
"""

from typing import List, Tuple
try:
    from langchain_core.documents import Document
except ImportError:
    class Document:
        def __init__(self, page_content: str, metadata: dict = None):
            self.page_content = page_content
            self.metadata = metadata or {}
try:
    from .embedder import get_vector_store
except (ImportError, ValueError):
    from rag.embedder import get_vector_store


def retrieve(
    query: str,
    collection_name: str = "geetagpt",
    top_k: int = 5,
    score_threshold: float = -0.5,
) -> List[Tuple[Document, float]]:
    """
    Retrieve the most relevant document chunks for a query.

    Args:
        query: The user's question.
        collection_name: ChromaDB collection to search.
        top_k: Number of results to return.
        score_threshold: Minimum similarity score (default -0.5 to avoid dropping negative distance scores).

    Returns:
        List of (Document, score) tuples sorted by relevance.
    """
    store = get_vector_store(collection_name)
    try:
        results = store.similarity_search_with_relevance_scores(query, k=top_k)
        filtered = [(doc, score) for doc, score in results if score >= score_threshold]
        if filtered:
            return filtered
    except Exception:
        pass

    # Fallback to standard similarity search without strict score cutoff
    docs = store.similarity_search(query, k=top_k)
    return [(doc, 1.0) for doc in docs]


def retrieve_as_context(
    query: str,
    collection_name: str = "geetagpt",
    top_k: int = 5,
) -> str:
    """
    Retrieve and format documents as a plain-text context block for LLM prompting.
    """
    results = retrieve(query, collection_name=collection_name, top_k=top_k)
    if not results:
        return "No relevant documents found in the knowledge base."

    context_parts = []
    for i, (doc, score) in enumerate(results, 1):
        source = doc.metadata.get("source", "unknown")
        page = doc.metadata.get("page", "")
        page_str = f" (page {page})" if page else ""
        context_parts.append(
            f"[{i}] Source: {source}{page_str} | Relevance: {score:.2f}\n{doc.page_content}"
        )
    return "\n\n---\n\n".join(context_parts)

