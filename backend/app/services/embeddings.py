from __future__ import annotations

import json
from typing import List, Optional, Union

import certifi
import httpx
import numpy as np
from openai import OpenAI

from app.config import settings

_client: Optional[OpenAI] = None


def _build_http_client() -> httpx.Client:
    """Use certifi CA bundle — fixes SSL errors on many Windows/corporate setups."""
    verify: Union[bool, str] = certifi.where()
    if not settings.openai_ssl_verify:
        verify = False
    return httpx.Client(verify=verify, timeout=120.0)


def get_openai_client() -> Optional[OpenAI]:
    global _client
    if not settings.openai_api_key:
        return None
    if _client is None:
        _client = OpenAI(
            api_key=settings.openai_api_key,
            http_client=_build_http_client(),
        )
    return _client


def reset_openai_client() -> None:
    """Reset cached client (e.g. after .env change)."""
    global _client
    _client = None


def embed_texts(texts: List[str]) -> List[List[float]]:
    client = get_openai_client()
    if not client:
        raise ValueError(
            "OPENAI_API_KEY is not configured. Set it in backend/.env to enable embeddings."
        )
    response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
    return [item.embedding for item in response.data]


def serialize_embedding(vector: List[float]) -> str:
    return json.dumps(vector)


def deserialize_embedding(data: str) -> np.ndarray:
    return np.array(json.loads(data), dtype=np.float32)


def cosine_similarity(query_vec: np.ndarray, matrix: np.ndarray) -> np.ndarray:
    query_norm = query_vec / (np.linalg.norm(query_vec) + 1e-10)
    matrix_norm = matrix / (np.linalg.norm(matrix, axis=1, keepdims=True) + 1e-10)
    return matrix_norm @ query_norm
