from __future__ import annotations

import json
from typing import List

import numpy as np

from app.services.llm_provider import embed_texts as provider_embed_texts


def embed_texts(texts: List[str]) -> List[List[float]]:
    vectors, _ = provider_embed_texts(texts)
    return vectors


def serialize_embedding(vector: List[float]) -> str:
    return json.dumps(vector)


def deserialize_embedding(data: str) -> np.ndarray:
    return np.array(json.loads(data), dtype=np.float32)


def cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    return matrix_norm @ query_norm
