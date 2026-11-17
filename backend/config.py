"""
Configuration loader for GeetaGPT.
Loads .env from root directory and backend directory,
supporting VLLM_*, LLM_*, OPENAI_*, and other variations.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from project root and from backend dir
ROOT_DIR = Path(__file__).resolve().parent.parent
BACKEND_DIR = Path(__file__).resolve().parent

load_dotenv(dotenv_path=ROOT_DIR / ".env", override=True)
load_dotenv(dotenv_path=BACKEND_DIR / ".env", override=False)


def get_llm_base_url() -> str:
    """Return the configured local LLM base URL."""
    url = (
        os.getenv("VLLM_BASE_URL")
        or os.getenv("LLM_BASE_URL")
        or os.getenv("OPENAI_BASE_URL")
        or os.getenv("LOCAL_LLM_URL")
        or os.getenv("LLM_URL")
        or os.getenv("BASE_URL")
        or os.getenv("URL")
        or "http://127.0.0.1:8000/v1"
    )
    url = url.strip()
    if url.endswith("/"):
        url = url[:-1]
    # Automatically upgrade remote domain URLs from http:// to https://
    # to avoid 301 redirect converting POST to GET (which causes 405 Method Not Allowed)
    if url.startswith("http://") and not any(h in url for h in ["localhost", "127.0.0.1", "0.0.0.0"]):
        url = "https://" + url[len("http://"):]
    return url


def get_llm_api_key() -> str:
    """Return the API key (or 'none' for local models)."""
    return (
        os.getenv("VLLM_API_KEY")
        or os.getenv("LLM_API_KEY")
        or os.getenv("OPENAI_API_KEY")
        or os.getenv("API_KEY")
        or "none"
    )


def get_llm_model() -> str:
    """Return the configured model name."""
    return (
        os.getenv("VLLM_MODEL")
        or os.getenv("LLM_MODEL")
        or os.getenv("MODEL")
        or os.getenv("MODEL_NAME")
        or os.getenv("OPENAI_MODEL")
        or "default"
    )


def get_embedding_model() -> str:
    """Return the embedding model name."""
    return (
        os.getenv("VLLM_EMBEDDING_MODEL")
        or os.getenv("EMBEDDING_MODEL")
        or os.getenv("EMBED_MODEL")
        or get_llm_model()
    )
