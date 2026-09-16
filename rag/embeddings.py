"""Carga del modelo de embeddings y codificación de texto."""

from functools import lru_cache

import numpy as np
from sentence_transformers import SentenceTransformer

import config


@lru_cache(maxsize=1)
def get_model() -> SentenceTransformer:
    """Carga (una sola vez) el modelo de embeddings configurado."""
    return SentenceTransformer(config.EMBEDDING_MODEL_NAME)


def encode(texts: list[str], show_progress: bool = False) -> np.ndarray:
    """Codifica una lista de textos como vectores normalizados (para similitud coseno)."""
    model = get_model()
    embeddings = model.encode(
        texts,
        show_progress_bar=show_progress,
        convert_to_numpy=True,
        normalize_embeddings=True,
    )
    return embeddings.astype(np.float32)
