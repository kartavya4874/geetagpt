"""
Parent Orchestrator Agent with Conversational Memory & Persistence.

Decides whether to route a query to:
  - direct_llm → General conversations, programming, explanations, greetings, normal answering
  - rag_agent  → Questions asking about uploaded documents / university knowledge base
  - tool_agent → Real-time queries, current events, live web lookups
"""

import os
import json
from typing import List, Dict, Any, Optional
from openai import OpenAI

try:
    from .rag_agent import run_rag_agent
    from .tool_agent import run_tool_agent
except (ImportError, ValueError):
    from agents.rag_agent import run_rag_agent
    from agents.tool_agent import run_tool_agent

try:
    from ..config import get_llm_base_url, get_llm_api_key, get_llm_model
    from ..memory import add_message, get_llm_context
except (ImportError, ValueError):
    from config import get_llm_base_url, get_llm_api_key, get_llm_model
    from memory import add_message, get_llm_context

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(
            base_url=get_llm_base_url(),
            api_key=get_llm_api_key(),
        )
    return _client


ROUTING_SYSTEM_PROMPT = """You are the orchestrator of GeetaGPT, the academic AI assistant for Geeta University.

Your job is to route the user's query to one of three agents:

1. **rag_agent** (Knowledge Base & Ingested Documents):
   - Select this for ANY specific factual questions about university subjects, uploaded files, course material, syllabus, handbooks, guidelines, schedules, hardware/project documentation, or departmental policies.
   - If the user is asking about specific data, terms, reports, or institutional information, ALWAYS route to rag_agent.

2. **tool_agent** (Web Search):
   - Select this ONLY when the user asks about real-time events, current news/dates/weather, or explicitly asks to search the web/internet.

3. **direct_llm** (Conversational / General AI):
   - Select this ONLY for greetings, introductions, casual chat, or general programming/math concepts that don't depend on private documents (e.g., "write a quicksort in C++", "hello").

Respond ONLY with a valid JSON object in this format:
{
  "agent": "direct_llm" | "rag_agent" | "tool_agent",
  "reasoning": "brief explanation of why",
  "confidence": 0.0 to 1.0
}"""


def run_direct_agent(query: str, history: Optional[List[Dict[str, str]]] = None) -> dict:
    """
    Direct LLM conversation with conversational memory.
    """
    client = _get_client()
    system_prompt = (
        "You are GeetaGPT, the official academic AI assistant of Geeta University. "
        "Answer the user's questions clearly, accurately, and politely. "
        "Maintain conversation context from previous messages."
    )

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": query})

    response = client.chat.completions.create(
        model=get_llm_model(),
        messages=messages,
        temperature=0.7,
        max_tokens=1024,
    )
    answer = response.choices[0].message.content
    return {
        "answer": answer,
        "agent": "direct_llm",
        "sources": [],
    }


def route_query(query: str, collection_name: str = "geetagpt") -> dict:
    """
    Intelligently route query using heuristic rules, knowledge-base pre-check, and LLM classification.
    """
    client = _get_client()

    lower = query.strip().lower()
    greetings = {"hi", "hello", "hey", "namaste", "good morning", "good evening", "who are you", "what can you do"}
    if lower in greetings:
        return {
            "agent": "direct_llm",
            "reasoning": "Standard greeting",
            "confidence": 0.99,
        }

    # Explicit web search keywords
    web_keywords = ["latest news", "today's weather", "current price", "search web", "google this", "live score"]
    if any(k in lower for k in web_keywords):
        return {
            "agent": "tool_agent",
            "reasoning": "Query explicitly requests real-time or web search information",
            "confidence": 0.95,
        }

    # Explicit document indicator words
    doc_keywords = ["document", "pdf", "docx", "file", "uploaded", "syllabus", "notes", "handbook", "circular", "in the doc", "attached", "according to"]
    if any(k in lower for k in doc_keywords):
        return {
            "agent": "rag_agent",
            "reasoning": "Query explicitly references uploaded documents or files",
            "confidence": 0.95,
        }

    # Pre-check: If ChromaDB has documents and finds a high-confidence match, automatically route to RAG
    try:
        from rag.retriever import retrieve
        matches = retrieve(query, collection_name=collection_name, top_k=1)
        if matches and len(matches) > 0:
            top_doc, top_score = matches[0]
            # Chroma relevance score > 0.2 indicates a strong semantic match with uploaded documents
            if top_score > 0.20:
                return {
                    "agent": "rag_agent",
                    "reasoning": f"Query strongly matched uploaded document: {top_doc.metadata.get('source', 'knowledge base')}",
                    "confidence": float(top_score),
                }
    except Exception:
        pass

    try:
        response = client.chat.completions.create(
            model=get_llm_model(),
            messages=[
                {"role": "system", "content": ROUTING_SYSTEM_PROMPT},
                {"role": "user", "content": f"Query: {query}"},
            ],
            temperature=0.1,
            max_tokens=150,
        )
        content = response.choices[0].message.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        routing = json.loads(content)
        if routing.get("agent") in ["direct_llm", "rag_agent", "tool_agent"]:
            return routing
        return {"agent": "direct_llm", "reasoning": "Defaulted to direct conversation", "confidence": 0.8}

    except Exception as e:
        return {
            "agent": "direct_llm",
            "reasoning": f"Defaulted to direct LLM response ({str(e)})",
            "confidence": 0.8,
        }


def run_parent_agent(
    query: str,
    collection_name: str = "geetagpt",
    top_k: int = 5,
    session_id: str = "default",
) -> dict:
    """
    Main entry point with persistent memory checkpointing.
    """
    # 1. Fetch recent conversation memory
    history = get_llm_context(session_id, max_turns=6)

    # 2. Decide routing
    routing = route_query(query, collection_name=collection_name)
    selected_agent = routing.get("agent", "direct_llm")

    # 3. Execute with memory
    if selected_agent == "rag_agent":
        result = run_rag_agent(query, collection_name=collection_name, top_k=top_k, history=history)
    elif selected_agent == "tool_agent":
        result = run_tool_agent(query, history=history)
    else:
        result = run_direct_agent(query, history=history)

    # 4. Checkpoint into persistent SQLite memory
    add_message(session_id, "user", query)
    ans = result.get("answer") or "I could not generate an answer at this time."
    add_message(
        session_id,
        "assistant",
        ans,
        agent=result.get("agent"),
        sources=result.get("sources", [])
    )

    return {
        **result,
        "routing": {
            "selected_agent": selected_agent,
            "reasoning": routing.get("reasoning", ""),
            "confidence": routing.get("confidence", 1.0),
        },
        "query": query,
        "session_id": session_id,
    }
