"""
RAG Agent — Handles document-based Q&A.

Responsibilities:
  1. Retrieve relevant context from ChromaDB.
  2. Build an augmented prompt with the retrieved context.
  3. Call the local LLM and return an answer with source citations.
  4. Gracefully fall back to general LLM answering if no documents exist.
"""

import os
from openai import OpenAI

try:
    from ..rag.retriever import retrieve_as_context, retrieve
except (ImportError, ValueError):
    from rag.retriever import retrieve_as_context, retrieve

try:
    from ..config import get_llm_base_url, get_llm_api_key, get_llm_model
except (ImportError, ValueError):
    from config import get_llm_base_url, get_llm_api_key, get_llm_model

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=get_llm_base_url(),
            api_key=get_llm_api_key(),
        )
    return _client


def run_rag_agent(
    query: str,
    collection_name: str = "geetagpt",
    top_k: int = 5,
    history: list = None,
) -> dict:
    """
    Answer a question using retrieved document context.
    Falls back gracefully if collection is empty or retrieval encounters an issue.
    """
    context = ""
    raw_results = []

    # Step 1: Safely retrieve context
    try:
        raw_results = retrieve(query, collection_name=collection_name, top_k=top_k)
        if raw_results:
            context = retrieve_as_context(query, collection_name=collection_name, top_k=top_k)
    except Exception as e:
        context = ""
        raw_results = []

    client = _get_client()

    # Step 2: Build appropriate prompt based on whether documents were found
    if raw_results and context.strip():
        system_prompt = (
            "You are GeetaGPT, an intelligent assistant for Geeta University. "
            "Answer the user's question based on the provided document context below. "
            "Cite the source document and page/row where available. "
            "Maintain context from recent conversation turns.\n\n"
            f"### Retrieved Context:\n{context}"
        )
    else:
        system_prompt = (
            "You are GeetaGPT, an intelligent assistant for Geeta University. "
            "Note: No matching document was found in the uploaded knowledge base for this query. "
            "Answer the user's question clearly and helpfully using your general knowledge and conversation context, "
            "and gently let them know they can upload relevant documents if they want answers specific to a particular file."
        )

    # Step 3: Call LLM with history
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(
        model=get_llm_model(),
        messages=messages,
        temperature=0.4,
        max_tokens=1024,
    )

    answer = response.choices[0].message.content

    # Collect unique sources
    sources = list({
        doc.metadata.get("source", "unknown")
        for doc, _ in raw_results
        if hasattr(doc, "metadata")
    })

    return {
        "answer": answer,
        "sources": sources,
        "agent": "rag_agent",
        "context_chunks": len(raw_results),
    }
