from __future__ import annotations

from typing import List, Optional, Tuple

import certifi
import httpx
from openai import APIStatusError, OpenAI, RateLimitError

from app.config import settings

_openai_client: Optional[OpenAI] = None
_google_configured = False

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
    global _openai_client, _google_configured
    _openai_client = None
    _google_configured = False


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
    """Provider used for new embeddings and vector search."""
    for provider in resolve_provider_order():
        if provider == PROVIDER_OPENAI and is_openai_configured():
            return PROVIDER_OPENAI
        if provider == PROVIDER_GOOGLE and is_google_configured():
            return PROVIDER_GOOGLE
    if is_google_configured():
        return PROVIDER_GOOGLE
    if is_openai_configured():
        return PROVIDER_OPENAI
    return resolve_provider_order()[0]


def is_quota_or_rate_error(exc: Exception) -> bool:
    if isinstance(exc, RateLimitError):
        return True
    if isinstance(exc, APIStatusError) and exc.status_code == 429:
        return True
    msg = str(exc).lower()
    return (
        "429" in msg
        or "quota" in msg
        or "rate limit" in msg
        or "resource exhausted" in msg
        or "exceeded your current" in msg
    )


def _configure_google() -> None:
    global _google_configured
    if _google_configured:
        return
    import google.generativeai as genai

    genai.configure(api_key=settings.google_api_key)
    _google_configured = True


def _embed_openai(texts: List[str]) -> List[List[float]]:
    client = get_openai_client()
    if not client:
        raise ValueError("OPENAI_API_KEY is not configured.")
    response = client.embeddings.create(model=settings.openai_embedding_model, input=texts)
    return [item.embedding for item in response.data]


def _embed_google(texts: List[str]) -> List[List[float]]:
    if not settings.google_api_key:
        raise ValueError("GOOGLE_API_KEY is not configured.")
    _configure_google()
    import google.generativeai as genai

    model_name = settings.google_embedding_model
    if not model_name.startswith("models/"):
        model_name = f"models/{model_name}"

    vectors: List[List[float]] = []
    for text in texts:
        result = genai.embed_content(
            model=model_name,
            content=text,
            task_type="retrieval_document",
        )
        vectors.append(result["embedding"])
    return vectors


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
            if provider == PROVIDER_OPENAI:
                return _embed_openai(texts), PROVIDER_OPENAI
            return _embed_google(texts), PROVIDER_GOOGLE
        except Exception as exc:
            errors.append(f"{provider}: {exc}")
            if auto_mode and is_quota_or_rate_error(exc):
                continue
            if not auto_mode:
                raise
            continue

    hint = (
        "Set OPENAI_API_KEY and/or GOOGLE_API_KEY in backend/.env. "
        "Use LLM_PROVIDER=auto to fall back when one provider hits quota limits."
    )
    detail = "; ".join(errors) if errors else "No provider keys configured."
    raise ValueError(f"Embedding failed. {detail} {hint}")


def embed_query(text: str) -> List[float]:
    """Embed a search query using the active indexed-chunk provider (no cross-provider fallback)."""
    provider = get_embedding_provider_name()
    if provider == PROVIDER_OPENAI:
        if not is_openai_configured():
            raise ValueError("OPENAI_API_KEY is not configured.")
        return _embed_openai([text])[0]
    if not is_google_configured():
        raise ValueError("GOOGLE_API_KEY is not configured.")
    return _embed_google([text])[0]


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
    _configure_google()
    import google.generativeai as genai

    model = genai.GenerativeModel(
        settings.google_chat_model,
        system_instruction=system_prompt,
    )
    response = model.generate_content(
        user_prompt,
        generation_config=genai.types.GenerationConfig(temperature=0.1),
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
        "Use LLM_PROVIDER=auto to fall back when one provider hits quota limits."
    )
    detail = "; ".join(errors) if errors else "No provider keys configured."
    raise ValueError(f"Chat generation failed. {detail} {hint}")
