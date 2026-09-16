"""Búsqueda semántica sobre el índice: similitud coseno + top-k."""

import time
from dataclasses import dataclass

import numpy as np

import config
from rag.embeddings import encode
from rag.index import Chunk, load_index


@dataclass
class SearchResult:
    """Un fragmento recuperado junto con su puntuación de similitud."""

    chunk: Chunk
    score: float


def search(query: str, top_k: int = config.TOP_K) -> tuple[list[SearchResult], float]:
    """Devuelve los `top_k` fragmentos más similares a `query` y el tiempo empleado."""
    start = time.perf_counter()
    embeddings, chunks = load_index()
    query_embedding = encode([query])[0]

    scores = embeddings @ query_embedding
    k = min(top_k, len(chunks))
    top_indices = np.argsort(scores)[::-1][:k]

    results = [SearchResult(chunk=chunks[i], score=float(scores[i])) for i in top_indices]
    elapsed = time.perf_counter() - start
    return results, elapsed
