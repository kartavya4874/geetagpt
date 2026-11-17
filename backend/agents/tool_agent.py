"""
Tool Agent — Handles real-time queries using external tools (web search, etc.).

Responsibilities:
  1. Decide which tool to call based on the query.
  2. Execute the tool.
  3. Summarize the results using the LLM.
"""

import os
import json
from openai import OpenAI
try:
    from ..tools.web_search import web_search
except (ImportError, ValueError):
    from tools.web_search import web_search

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


# Tool definitions for function calling
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "web_search",
            "description": "Search the internet for real-time information, current events, news, or facts.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (default: 5)",
                        "default": 5,
                    },
                },
                "required": ["query"],
            },
        },
    }
]


def _execute_tool(name: str, args: dict) -> str:
    if name == "web_search":
        return web_search(
            query=args["query"],
            max_results=args.get("max_results", 5)
        )
    return f"Unknown tool: {name}"


def run_tool_agent(query: str, history: list = None) -> dict:
    """
    Answer a query using external tools (web search), with academic guardrail and LLM summarization.
    """
    client = _get_client()

    # Step 1: Execute web search (with Academic Guardrail pre-check)
    tool_result = web_search(query)

    # Step 2: If guardrail blocked the search, return refusal explanation immediately
    if "Academic Guardrail Alert" in tool_result:
        return {
            "answer": tool_result,
            "tool_used": "academic_guardrail",
            "tool_query": query,
            "agent": "tool_agent",
        }

    # Step 3: Summarize search results with LLM
    system_prompt = (
        "You are GeetaGPT, the official academic AI assistant for Geeta University. "
        "A live web search was performed for the user's question. "
        "Summarize the information below clearly, accurately, and informatively for an academic setting. "
        "Cite the sources or URLs provided in the results where appropriate."
    )

    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({
        "role": "user",
        "content": f"User Question: {query}\n\nSearch Results:\n{tool_result}"
    })

    try:
        response = client.chat.completions.create(
            model=get_llm_model(),
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        answer = response.choices[0].message.content or tool_result
    except Exception as e:
        answer = f"**Search Results Retrieved:**\n\n{tool_result}"

    return {
        "answer": answer,
        "tool_used": "web_search",
        "tool_query": query,
        "agent": "tool_agent",
    }

