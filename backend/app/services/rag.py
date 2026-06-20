from __future__ import annotations

from typing import List, Optional, Tuple

import numpy as np
from sqlalchemy.orm import Session

from app.config import settings
from app.models import Chunk, Domain, Project, Source, WebPage
from app.schemas import Citation, SearchResponse
from app.services.embeddings import (
    cosine_similarity,
    deserialize_embedding,
    embed_texts,
    get_openai_client,
)

SYSTEM_PROMPT = """You are Atlas, an enterprise knowledge assistant. Your role is to answer questions using ONLY the provided context passages from the organization's knowledge base.

STRICT RULES:
1. Answer ONLY using information explicitly stated in the provided context passages.
2. Do NOT use any external knowledge, assumptions, or information not in the passages.
3. Cite every substantive claim using inline citation markers like [1], [2], etc. matching the passage numbers.
4. If the context does not contain enough information to answer the question, respond clearly: "I could not find sufficient information in the knowledge base to answer this question." Do NOT guess or fabricate.
5. If sources contain conflicting information, note the conflict and cite both sources.
6. Write in clear, formal English. Consolidate information from multiple passages into a coherent answer.
7. Keep answers concise but complete."""


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


def retrieve_chunks(
    db: Session,
    question: str,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
    top_k: Optional[int] = None,
) -> List[Tuple[Chunk, float, WebPage, Project, Domain, Source]]:
    k = top_k or settings.top_k_chunks
    query = db.query(Chunk)
    for f in _build_filters(source_id, domain_id, project_id):
        query = query.filter(f)
    chunks = query.all()
    if not chunks:
        return []

    query_embedding = embed_texts([question])[0]
    query_vec = np.array(query_embedding, dtype=np.float32)

    matrix = np.stack([deserialize_embedding(c.embedding) for c in chunks])
    scores = cosine_similarity(query_vec, matrix)

    ranked_indices = np.argsort(scores)[::-1][:k]
    results: List[Tuple[Chunk, float, WebPage, Project, Domain, Source]] = []
    for idx in ranked_indices:
        chunk = chunks[int(idx)]
        score = float(scores[int(idx)])
        if score < 0.3:
            continue
        page = db.query(WebPage).filter(WebPage.id == chunk.web_page_id).first()
        if not page:
            continue
        project = db.query(Project).filter(Project.id == chunk.project_id).first()
        domain = db.query(Domain).filter(Domain.id == chunk.domain_id).first()
        source = db.query(Source).filter(Source.id == chunk.source_id).first()
        if project and domain and source:
            results.append((chunk, score, page, project, domain, source))
    return results


def generate_answer(
    db: Session,
    question: str,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> SearchResponse:
    retrieved = retrieve_chunks(db, question, source_id, domain_id, project_id)

    if not retrieved:
        return SearchResponse(
            answer="I could not find sufficient information in the knowledge base to answer this question. No relevant content was found in the selected scope.",
            citations=[],
            confidence="none",
            found_relevant=False,
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

    client = get_openai_client()
    if not client:
        return SearchResponse(
            answer="OpenAI API key is not configured. Please set OPENAI_API_KEY in the backend environment.",
            citations=citations,
            confidence="none",
            found_relevant=False,
        )

    response = client.chat.completions.create(
        model=settings.openai_chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.1,
    )
    answer = response.choices[0].message.content or ""

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
    )
