from __future__ import annotations

import re
from typing import List, Optional, Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Chunk, Domain, Project, Source, WebPage
from app.schemas import Citation, SearchResponse
from app.services.activity_log import log_exception
from app.services.embeddings import cosine_similarity, deserialize_embedding
from app.services.folder_sync import sync_scope_from_disk
from app.services.llm_provider import (
    embed_query,
    generate_chat,
    get_embedding_provider_name,
    is_ai_configured,
)
from app.services.scope import count_chunks_in_scope, ensure_indexed_for_scope, get_pages_in_scope

SYSTEM_PROMPT = """You are Atlas, an enterprise knowledge assistant. Your role is to answer questions using ONLY the provided context passages from the organization's knowledge base.

STRICT RULES:
1. Answer ONLY using information explicitly stated in the provided context passages.
2. Do NOT use any external knowledge, assumptions, or information not in the passages.
3. Cite every substantive claim using inline citation markers like [1], [2], etc. matching the passage numbers.
4. If the context does not contain enough information to answer the question, respond clearly: "I could not find sufficient information in the knowledge base to answer this question." Do NOT guess or fabricate.
5. If sources contain conflicting information, note the conflict and cite both sources.
6. Write in clear, formal English. Consolidate information from multiple passages into a coherent answer.
7. Keep answers concise but complete."""

SSL_HELP = (
    " If you see SSL/certificate errors on Windows, run: pip install certifi "
    "and restart the backend. For development only, you may set OPENAI_SSL_VERIFY=false in backend/.env."
)

SIMILARITY_THRESHOLD = 0.15
_STOP_WORDS = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "but",
        "in",
        "on",
        "at",
        "to",
        "for",
        "of",
        "with",
        "by",
        "from",
        "is",
        "are",
        "was",
        "were",
        "be",
        "been",
        "being",
        "have",
        "has",
        "had",
        "do",
        "does",
        "did",
        "will",
        "would",
        "could",
        "should",
        "may",
        "might",
        "what",
        "which",
        "who",
        "whom",
        "this",
        "that",
        "these",
        "those",
        "how",
        "when",
        "where",
        "why",
        "vs",
        "versus",
    }
)


def _error_response(
    message: str,
    folder_paths: Optional[List[str]] = None,
    files_synced: int = 0,
    pages_in_scope: int = 0,
    chunks_indexed: int = 0,
    index_warnings: Optional[List[str]] = None,
) -> SearchResponse:
    return SearchResponse(
        answer=message,
        citations=[],
        confidence="none",
        found_relevant=False,
        folder_paths=folder_paths or [],
        files_synced=files_synced,
        pages_in_scope=pages_in_scope,
        chunks_indexed=chunks_indexed,
        index_warnings=index_warnings or [],
    )


def _build_filters(
    source_id: Optional[str], domain_id: Optional[str], project_id: Optional[str]
):
    filters = []
    if project_id:
        filters.append(Chunk.project_id == project_id)
    elif domain_id:
        filters.append(Chunk.domain_id == domain_id)
    elif source_id:
        filters.append(Chunk.source_id == source_id)
    return filters


def _chunk_query(
    db: Session,
    source_id: Optional[str],
    domain_id: Optional[str],
    project_id: Optional[str],
    *,
    current_provider_only: bool = True,
):
    query = db.query(Chunk)
    if current_provider_only:
        query = query.filter(Chunk.embedding_provider == get_embedding_provider_name())
    for f in _build_filters(source_id, domain_id, project_id):
        query = query.filter(f)
    return query


def _question_terms(question: str) -> List[str]:
    terms = re.findall(r"[a-z0-9]+", question.lower())
    return [t for t in terms if len(t) >= 2 and t not in _STOP_WORDS]


def _load_chunk_context(
    db: Session, chunk: Chunk
) -> Optional[Tuple[Chunk, WebPage, Project, Domain, Source]]:
    page = db.query(WebPage).filter(WebPage.id == chunk.web_page_id).first()
    if not page:
        return None
    project = db.query(Project).filter(Project.id == chunk.project_id).first()
    domain = db.query(Domain).filter(Domain.id == chunk.domain_id).first()
    source = db.query(Source).filter(Source.id == chunk.source_id).first()
    if project and domain and source:
        return chunk, page, project, domain, source
    return None


def keyword_retrieve_chunks(
    db: Session,
    question: str,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
    top_k: Optional[int] = None,
) -> List[Tuple[Chunk, float, WebPage, Project, Domain, Source]]:
    """Fallback retrieval using keyword overlap when embeddings are unavailable or weak."""
    k = top_k or settings.top_k_chunks
    terms = _question_terms(question)
    if not terms:
        return []

    query = _chunk_query(
        db, source_id, domain_id, project_id, current_provider_only=False
    )
    chunks = query.all()
    if not chunks:
        return []

    scored: List[Tuple[Chunk, float]] = []
    for chunk in chunks:
        content_lower = chunk.content.lower()
        hits = sum(1 for term in terms if term in content_lower)
        if hits == 0:
            continue
        # Favor chunks that match more query terms and longer overlap.
        score = hits / len(terms)
        scored.append((chunk, score))

    scored.sort(key=lambda item: item[1], reverse=True)
    results: List[Tuple[Chunk, float, WebPage, Project, Domain, Source]] = []
    for chunk, score in scored[:k]:
        ctx = _load_chunk_context(db, chunk)
        if ctx:
            c, page, project, domain, source = ctx
            results.append((c, score, page, project, domain, source))
    return results


def retrieve_chunks(
    db: Session,
    question: str,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
    top_k: Optional[int] = None,
) -> List[Tuple[Chunk, float, WebPage, Project, Domain, Source]]:
    k = top_k or settings.top_k_chunks
    query = _chunk_query(db, source_id, domain_id, project_id)
    chunks = query.all()
    if not chunks:
        return keyword_retrieve_chunks(db, question, source_id, domain_id, project_id, top_k)

    query_embedding = embed_query(question)
    query_vec = np.array(query_embedding, dtype=np.float32)

    matrix = np.stack([deserialize_embedding(c.embedding) for c in chunks])
    scores = cosine_similarity(query_vec, matrix)

    ranked_indices = np.argsort(scores)[::-1][:k]
    results: List[Tuple[Chunk, float, WebPage, Project, Domain, Source]] = []
    for idx in ranked_indices:
        chunk = chunks[int(idx)]
        score = float(scores[int(idx)])
        if score < SIMILARITY_THRESHOLD:
            continue
        ctx = _load_chunk_context(db, chunk)
        if ctx:
            c, page, project, domain, source = ctx
            results.append((c, score, page, project, domain, source))

    if results:
        return results

    return keyword_retrieve_chunks(db, question, source_id, domain_id, project_id, top_k)


def _empty_scope_message(
    pages_in_scope: int,
    chunks_indexed: int,
    index_warnings: List[str],
) -> str:
    if pages_in_scope == 0:
        return (
            "I could not find sufficient information in the knowledge base to answer this question. "
            "No web pages exist in the selected scope yet. "
            "On the Manage page, create a Domain and Project under your Source, place files in the "
            "source folder (e.g. knowledge_base/Cancer/cancer1.txt), then sync or ask again."
        )

    if chunks_indexed == 0:
        warning_hint = ""
        if index_warnings:
            warning_hint = f" Indexing issues: {'; '.join(index_warnings[:3])}."
        return (
            "I could not find sufficient information in the knowledge base to answer this question. "
            f"Found {pages_in_scope} page(s) in scope but none are indexed for search. "
            "This usually means embedding failed during sync — check the Logs page and "
            "ensure OPENAI_API_KEY and/or GOOGLE_API_KEY is set in backend/.env. "
            "Use LLM_PROVIDER=auto to fall back to Google when OpenAI quota is exceeded."
            f"{warning_hint}"
        )

    return (
        "I could not find sufficient information in the knowledge base to answer this question. "
        f"Searched {chunks_indexed} indexed chunk(s) across {pages_in_scope} page(s) but none "
        "matched your question closely enough. Try rephrasing or broadening your search terms."
    )


def generate_answer(
    db: Session,
    question: str,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> SearchResponse:
    folder_paths: List[str] = []
    files_synced = 0
    index_warnings: List[str] = []
    pages_in_scope = 0
    chunks_indexed = 0

    try:
        sync_summary = sync_scope_from_disk(db, source_id, domain_id, project_id)
        folder_paths = [str(p) for p in sync_summary.get("folder_paths", [])]
        files_synced = int(sync_summary.get("files_found", 0))
        for detail in sync_summary.get("details", []):
            if not isinstance(detail, dict):
                continue
            for result in detail.get("results", []):
                result_str = str(result)
                if result_str.startswith("indexed_failed:") or result_str.startswith("indexed_empty:"):
                    index_warnings.append(result_str)
    except Exception as exc:
        log_exception(
            "Search folder sync",
            exc,
            page="Ask",
            endpoint="/api/search",
            db=db,
        )

    try:
        index_result = ensure_indexed_for_scope(db, source_id, domain_id, project_id)
        pages_in_scope = int(index_result.get("pages_in_scope", 0))
        for failure in index_result.get("failed", []):
            index_warnings.append(str(failure))
    except Exception as exc:
        log_exception(
            "Search re-index",
            exc,
            page="Ask",
            endpoint="/api/search",
            db=db,
        )
        index_warnings.append(f"Re-index failed: {exc}")

    pages_in_scope = max(pages_in_scope, len(get_pages_in_scope(db, source_id, domain_id, project_id)))
    chunks_indexed = count_chunks_in_scope(db, source_id, domain_id, project_id)

    try:
        retrieved = retrieve_chunks(db, question, source_id, domain_id, project_id)
    except Exception as exc:
        log_exception(
            "Search retrieval",
            exc,
            page="Ask",
            endpoint="/api/search",
            db=db,
        )
        if chunks_indexed > 0:
            try:
                retrieved = keyword_retrieve_chunks(
                    db, question, source_id, domain_id, project_id
                )
            except Exception as kw_exc:
                log_exception(
                    "Search keyword fallback",
                    kw_exc,
                    page="Ask",
                    endpoint="/api/search",
                    db=db,
                )
                retrieved = []
        else:
            retrieved = []

        if not retrieved:
            msg = (
                f"Search failed while generating embeddings: {exc}. "
                "Set OPENAI_API_KEY and/or GOOGLE_API_KEY in backend/.env. "
                "Use LLM_PROVIDER=auto to fall back when OpenAI quota is exceeded."
                f"{SSL_HELP}"
            )
            return _error_response(
                msg,
                folder_paths,
                files_synced,
                pages_in_scope,
                chunks_indexed,
                index_warnings,
            )

    if not retrieved:
        return _error_response(
            _empty_scope_message(pages_in_scope, chunks_indexed, index_warnings),
            folder_paths,
            files_synced,
            pages_in_scope,
            chunks_indexed,
            index_warnings,
        )

    context_parts: List[str] = []
    citations: List[Citation] = []
    for i, (chunk, score, page, project, domain, source) in enumerate(retrieved, start=1):
        context_parts.append(
            f"[{i}] Title: {page.title}\n"
            f"Source: {source.name} > {domain.name} > {project.name}\n"
            f"Content: {chunk.content}"
        )
        citations.append(
            Citation(
                index=i,
                web_page_id=page.id,
                title=page.title,
                url=page.url,
                snippet=chunk.content[:300] + ("..." if len(chunk.content) > 300 else ""),
                source_name=source.name,
                domain_name=domain.name,
                project_name=project.name,
                updated_at=page.updated_at,
            )
        )

    context = "\n\n".join(context_parts)
    user_prompt = f"""Context passages from the knowledge base:

{context}

Question: {question}

Answer the question using only the context above. Include inline citations [1], [2], etc."""

    if not is_ai_configured():
        return _error_response(
            "No AI provider is configured. Set OPENAI_API_KEY and/or GOOGLE_API_KEY in backend/.env. "
            "Use LLM_PROVIDER=openai, google, or auto.",
            folder_paths,
            files_synced,
            pages_in_scope,
            chunks_indexed,
            index_warnings,
        )

    try:
        answer, _provider_used = generate_chat(SYSTEM_PROMPT, user_prompt)
    except Exception as exc:
        log_exception(
            "Search chat generation",
            exc,
            page="Ask",
            endpoint="/api/search",
            db=db,
        )
        msg = (
            f"Search failed while generating the answer: {exc}. "
            "Set OPENAI_API_KEY and/or GOOGLE_API_KEY in backend/.env. "
            "Use LLM_PROVIDER=auto to fall back when OpenAI quota is exceeded."
            f"{SSL_HELP}"
        )
        return _error_response(
            msg,
            folder_paths,
            files_synced,
            pages_in_scope,
            chunks_indexed,
            index_warnings,
        )

    not_found_phrases = [
        "could not find sufficient information",
        "no sufficient information",
        "not enough information",
        "cannot answer",
        "don't have enough information",
        "do not have enough information",
    ]
    found_relevant = not any(phrase in answer.lower() for phrase in not_found_phrases)

    avg_score = sum(s for _, s, *_ in retrieved) / len(retrieved)
    if avg_score >= 0.7:
        confidence = "high"
    elif avg_score >= 0.5:
        confidence = "medium"
    elif avg_score >= 0.15:
        confidence = "low"
    else:
        confidence = "low"

    if not found_relevant:
        confidence = "none"
        citations = []

    return SearchResponse(
        answer=answer,
        citations=citations if found_relevant else [],
        confidence=confidence,
        found_relevant=found_relevant,
        folder_paths=folder_paths,
        files_synced=files_synced,
        pages_in_scope=pages_in_scope,
        chunks_indexed=chunks_indexed,
        index_warnings=index_warnings,
    )
