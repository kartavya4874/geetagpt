"""
Tool Agent — Web Search Tool with Academic Guardrail.
Restricted exclusively to educational, learning, academic, and research topics.
"""

import warnings
import urllib.request
import urllib.parse
import json

# Suppress the duckduckgo_search → ddgs rename deprecation warning
warnings.filterwarnings("ignore", message=".*duckduckgo.search.*", category=RuntimeWarning)
warnings.filterwarnings("ignore", message=".*ddgs.*", category=RuntimeWarning)

from duckduckgo_search import DDGS
from .academic_guardrail import check_academic_guardrail


def search_wikipedia(query: str) -> str:
    """Fetch educational summary from Wikipedia API."""
    try:
        clean_query = query.strip().replace(" ", "_")
        url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(clean_query)}"
        req = urllib.request.Request(url, headers={"User-Agent": "GeetaGPT/1.0 (academic research)"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            title = data.get("title", "")
            extract = data.get("extract", "")
            page_url = data.get("content_urls", {}).get("desktop", {}).get("page", "")
            if extract:
                return f"📖 **Wikipedia: {title}**\n{extract}\nSource: {page_url}"
    except Exception:
        pass
    return ""


def web_search(query: str, max_results: int = 5) -> str:
    """
    Search the web with an active Academic Guardrail.

    Args:
        query: Search query string.
        max_results: Max number of results to return.

    Returns:
        Formatted string of search results or guardrail refusal.
    """
    # ─── 1. Guardrail Evaluation ──────────────────────────────────────────
    guardrail = check_academic_guardrail(query)
    if not guardrail["allowed"]:
        return (
            "🛡️ **Academic Guardrail Alert:**\n\n"
            f"This search request was blocked: *\"{query}\"*\n\n"
            f"**Reason:** {guardrail['reason']}\n\n"
            "GeetaGPT's web search capability is restricted strictly to **study, academic, research, "
            "educational, and career-learning topics** for Geeta University students and faculty. "
            "Please ask a question related to your courses, syllabus, science, coding, or academic projects."
        )

    # ─── 2. Execute Safe Academic Search ──────────────────────────────────
    results_list = []

    # Optional: Check Wikipedia for academic definitions/topics
    wiki_summary = search_wikipedia(query)
    if wiki_summary:
        results_list.append(wiki_summary)

    try:
        with DDGS() as ddgs:
            # Using backend='html' for reliable fetching without rate-limit drops
            raw_results = list(ddgs.text(query, max_results=max_results, backend="html"))

        for i, r in enumerate(raw_results, 1):
            title = r.get("title", "No title")
            body = r.get("body", "")
            href = r.get("href", "")
            results_list.append(f"[{i}] **{title}**\n{body}\nSource: {href}")

    except Exception as e:
        if not results_list:
            return f"Web search could not retrieve results: {str(e)}"

    if not results_list:
        return f"No educational web results found for: {query}"

    return "\n\n".join(results_list)


TOOL_REGISTRY = {
    "web_search": {
        "fn": web_search,
        "description": "Search the internet for study, academic concepts, research, or university information.",
        "parameters": {
            "query": "The educational or academic search query",
            "max_results": "Maximum number of results (default 5)"
        }
    }
}
