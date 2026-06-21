from __future__ import annotations

from typing import List, Optional, Tuple

import certifi
import httpx
from openai import APIStatusError, OpenAI, RateLimitError

from app.config import settings

_openai_client: Optional[OpenAI] = None
_google_client = None

PROVIDER_OPENAI = "openai"
PROVIDER_GOOGLE = "google"


def _build_http_client() -> httpx.Client:
    verify = certifi.where()
    if not settings.openai_ssl_verify:
        verify = False
    return httpx.Client(verify=verify, timeout=120.0)


def get_openai_client() -> Optional[OpenAI]:
    global _openai_client
    if not settings.openai_api_key:
        return None
    if _openai_client is None:
        _openai_client = OpenAI(
            api_key=settings.openai_api_key,
            http_client=_build_http_client(),
        )
    return _openai_client


def reset_clients() -> None:
    global _openai_client, _google_client
    _openai_client = None
    _google_client = None


def is_openai_configured() -> bool:
    return bool(settings.openai_api_key)


def is_google_configured() -> bool:
    return bool(settings.google_api_key)


def is_ai_configured() -> bool:
    mode = settings.llm_provider.lower()
    if mode == PROVIDER_OPENAI:
        return is_openai_configured()
    if mode == PROVIDER_GOOGLE:
        return is_google_configured()
    return is_openai_configured() or is_google_configured()


def resolve_provider_order() -> List[str]:
    mode = settings.llm_provider.lower().strip()
    if mode == PROVIDER_GOOGLE:
        return [PROVIDER_GOOGLE]
    if mode == PROVIDER_OPENAI:
        return [PROVIDER_OPENAI]
    return [PROVIDER_OPENAI, PROVIDER_GOOGLE]


def get_embedding_provider_name() -> str:
    """Preferred provider for explicit openai/google modes and new indexing."""
    mode = settings.llm_provider.lower().strip()
    if mode == PROVIDER_GOOGLE:
        return PROVIDER_GOOGLE
    if mode == PROVIDER_OPENAI:
        return PROVIDER_OPENAI
    for provider in resolve_provider_order():
        if provider == PROVIDER_OPENAI and is_openai_configured():
            return PROVIDER_OPENAI
        if provider == PROVIDER_GOOGLE and is_google_configured():
            return PROVIDER_GOOGLE
    if is_google_configured():
        return PROVIDER_GOOGLE
    if is_openai_configured():
        return PROVIDER_OPENAI
    return PROVIDER_OPENAI


def is_quota_or_rate_error(exc: Exception) -> bool:
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, APIStatusError) and exc.status_code == 429:
        return True
    msg = str(exc).lower()
    return (
        "429" in msg
        or "quota" in msg
        or "insufficient_quota" in msg
        or "rate limit" in msg
        or "resource exhausted" in msg
        or "exceeded your current" in msg
    )


def _get_google_client():
    global _google_client
    if _google_client is None:
        from google import genai

        _google_client = genai.Client(api_key=settings.google_api_key)
    return _google_client


def _embed_openai(texts: List[str]) -> List[List[float]]:
    client = get_openai_client()
    if not client:
        raise ValueError("OPENAI_API_KEY is not configured.")
    response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
    return [item.embedding for item in response.data]


def _embed_google(texts: List[str], task_type: str = "RETRIEVAL_DOCUMENT") -> List[List[float]]:
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is not configured.")

    from google.genai import types

    client = _get_google_client()
    model = settings.google_embedding_model

    result = client.models.embed_content(
        model=model,
        contents=texts,
        config=types.EmbedContentConfig(task_type=task_type),
    )
    return [embedding.values for embedding in result.embeddings]


def _embed_with_provider(
    texts: List[str], provider: str, *, for_query: bool = False
) -> List[List[float]]:
    if provider == PROVIDER_OPENAI:
        return _embed_openai(texts)
    task_type = "RETRIEVAL_QUERY" if for_query else "RETRIEVAL_DOCUMENT"
    return _embed_google(texts, task_type=task_type)


def embed_texts(texts: List[str]) -> Tuple[List[List[float]], str]:
    """Embed texts using configured provider order. Returns (vectors, provider_used)."""
    if not texts:
        return [], get_embedding_provider_name()

    errors: List[str] = []
    order = resolve_provider_order()
    auto_mode = settings.llm_provider.lower().strip() == "auto"

    for provider in order:
        if provider == PROVIDER_OPENAI and not is_openai_configured():
            continue
        if provider == PROVIDER_GOOGLE and not is_google_configured():
            continue
        try:
            return _embed_with_provider(texts, provider), provider
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
            if auto_mode and is_quota_or_rate_error(exc):
                continue
            if not auto_mode:
                raise
            continue

    hint = (
        "Set OPENAI_API_KEY and/or GOOGLE_API_KEY in backend/.env. "
        "If OpenAI quota is exhausted, set LLM_PROVIDER=google. "
        "Use LLM_PROVIDER=auto to fall back to Google on OpenAI quota errors."
    )
    detail = "; ".join(errors) if errors else "No provider keys configured."
    raise ValueError(f"Embedding failed. {detail} {hint}")


def embed_query(text: str) -> Tuple[List[float], str]:
    """Embed a search query, with auto fallback. Returns (vector, provider_used)."""
    errors: List[str] = []
    order = resolve_provider_order()
    auto_mode = settings.llm_provider.lower().strip() == "auto"

    for provider in order:
        if provider == PROVIDER_OPENAI and not is_openai_configured():
            continue
        if provider == PROVIDER_GOOGLE and not is_google_configured():
            continue
        try:
            vectors = _embed_with_provider([text], provider, for_query=True)
            return vectors[0], provider
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
            if auto_mode and is_quota_or_rate_error(exc):
                continue
            if not auto_mode:
                raise
            continue

    detail = "; ".join(errors) if errors else "No provider keys configured."
    raise ValueError(f"Query embedding failed. {detail}")


def _chat_openai(system_prompt: str, user_prompt: str) -> str:
    client = get_openai_client()
    if not client:
        raise ValueError("OPENAI_API_KEY is not configured.")
    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
    return response.choices[0].message.content or ""


def _chat_google(system_prompt: str, user_prompt: str) -> str:
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is not configured.")

    from google.genai import types

    client = _get_google_client()
    response = client.models.generate_content(
        model=settings.google_chat_model,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=system_prompt,
            temperature=0.1,
        ),
    )
    return response.text or ""


def generate_chat(system_prompt: str, user_prompt: str) -> Tuple[str, str]:
    """Generate chat completion. Returns (answer, provider_used)."""
    errors: List[str] = []
    order = resolve_provider_order()
    auto_mode = settings.llm_provider.lower().strip() == "auto"

    for provider in order:
        if provider == PROVIDER_OPENAI and not is_openai_configured():
            continue
        if provider == PROVIDER_GOOGLE and not is_google_configured():
            continue
        try:
            if provider == PROVIDER_OPENAI:
                return _chat_openai(system_prompt, user_prompt), PROVIDER_OPENAI
            return _chat_google(system_prompt, user_prompt), PROVIDER_GOOGLE
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
            if auto_mode and is_quota_or_rate_error(exc):
                continue
            if not auto_mode:
                raise
            continue

    hint = (
        "Set OPENAI_API_KEY and/or GOOGLE_API_KEY in backend/.env. "
        "If OpenAI quota is exhausted, set LLM_PROVIDER=google."
    )
    detail = "; ".join(errors) if errors else "No provider keys configured."
    raise ValueError(f"Chat generation failed. {detail} {hint}")
