from __future__ import annotations

import hashlib
import json
from os import getenv
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

OLLAMA_URL = getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

CACHE_DIR = Path(getenv("EMBEDDING_CACHE_DIR", "app/cache/embeddings"))
CACHE_DIR.mkdir(parents=True, exist_ok=True)


def _cache_file(text: str) -> Path:
    """Return the cache file path for a given text."""
    text_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
    return CACHE_DIR / f"{text_hash}.json"


def _load_from_cache(cache_file: Path) -> list[float] | None:
    """Load an embedding from cache if it exists."""
    if not cache_file.exists():
        return None

    with cache_file.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_to_cache(cache_file: Path, embedding: list[float]) -> None:
    """Save an embedding to the cache."""
    with cache_file.open("w", encoding="utf-8") as f:
        json.dump(embedding, f)


def _request_embedding(text: str) -> list[float]:
    """Request an embedding from the local Ollama server."""
    response = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={
            "model": MODEL,
            "input": text,
        },
        timeout=60,
    )

    response.raise_for_status()

    data = response.json()
    return data["embeddings"][0]


def embed(text: str) -> list[float]:
    """
    Return the embedding for a piece of text.

    Cached embeddings are returned immediately.
    Otherwise, an embedding is requested from Ollama,
    cached on disk, and returned.
    """
    cache_file = _cache_file(text)

    embedding = _load_from_cache(cache_file)
    if embedding is not None:
        return embedding

    embedding = _request_embedding(text)

    _save_to_cache(cache_file, embedding)

    return embedding
