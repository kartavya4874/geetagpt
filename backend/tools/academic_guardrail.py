"""
Academic Guardrail for GeetaGPT Web Search.
Restricts web search queries strictly to academic, learning, research,
and educational topics for Geeta University students and faculty.
"""

import json
from openai import OpenAI

try:
    from ..config import get_llm_base_url, get_llm_api_key, get_llm_model
except (ImportError, ValueError):
    from config import get_llm_base_url, get_llm_api_key, get_llm_model

# Obvious non-academic patterns for fast-path blocking
NON_ACADEMIC_KEYWORDS = [
    "celebrity gossip", "movie leak", "torrent download", "pirated movie",
    "game cheat", "hack coins", "sports betting", "casino online",
    "dating site", "hookup", "adult video", "xxx", "porn",
    "rumors about", "scandal", "lottery numbers", "free vbucks"
]

# Fast-path allowed academic domains/keywords
ACADEMIC_KEYWORDS = [
    "algorithm", "math", "science", "physics", "chemistry", "biology",
    "history", "literature", "engineering", "programming", "python",
    "java", "database", "sql", "ai", "machine learning", "deep learning",
    "university", "syllabus", "exam", "course", "curriculum", "scholarship",
    "research", "paper", "journal", "definition", "tutorial", "how does",
    "explain", "theory", "formula", "calculus", "geeta university"
]


def check_academic_guardrail(query: str) -> dict:
    """
    Evaluate if a query is acceptable under the academic & learning policy.

    Returns:
        {
            "allowed": bool,
            "reason": str,
            "category": "academic" | "blocked"
        }
    """
    lower = query.lower().strip()

    # Fast-path rejection
    if any(k in lower for k in NON_ACADEMIC_KEYWORDS):
        return {
            "allowed": False,
            "reason": "This query contains non-academic or prohibited entertainment/gambling/adult content.",
            "category": "blocked"
        }

    # Fast-path acceptance for clear academic terms
    if any(k in lower for k in ACADEMIC_KEYWORDS):
        return {
            "allowed": True,
            "reason": "Clear academic/educational topic.",
            "category": "academic"
        }

    # LLM classification for borderline queries
    try:
        client = OpenAI(base_url=get_llm_base_url(), api_key=get_llm_api_key())
        guardrail_prompt = (
            "You are an academic compliance guardrail for Geeta University AI.\n"
            "Determine if the user's web search query is for STUDY, ACADEMIC, RESEARCH, "
            "EDUCATIONAL, TECHNICAL, OR CAREER LEARNING purposes.\n\n"
            "ACCEPTABLE: Mathematics, computer science, literature, engineering, science, "
            "university life, exams, career guidance, current affairs relevant to studies, history, economics.\n"
            "PROHIBITED: Celebrity gossip, entertainment rumors, sports betting, video game cheat codes, "
            "piracy, social media drama, non-educational pop culture.\n\n"
            "Respond ONLY with a JSON object:\n"
            "{\n"
            '  "allowed": true | false,\n'
            '  "reason": "one sentence explanation"\n'
            "}"
        )

        response = client.chat.completions.create(
            model=get_llm_model(),
            messages=[
                {"role": "system", "content": guardrail_prompt},
                {"role": "user", "content": f"Query to evaluate: {query}"}
            ],
            temperature=0.1,
            max_tokens=100
        )
        content = response.choices[0].message.content.strip()

        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].split("```")[0].strip()

        data = json.loads(content)
        return {
            "allowed": bool(data.get("allowed", False)),
            "reason": data.get("reason", "Academic evaluation"),
            "category": "academic" if data.get("allowed", False) else "blocked"
        }
    except Exception:
        # If classifier fails, default to allowing general queries as long as not explicitly in blocklist
        return {
            "allowed": True,
            "reason": "Allowed under fallback educational guidelines",
            "category": "academic"
        }

