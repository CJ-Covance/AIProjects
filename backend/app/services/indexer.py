from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Chunk, Domain, Project, Source, WebPage
from app.services.embeddings import serialize_embedding
from app.services.llm_provider import embed_texts as provider_embed_texts


def chunk_text(
    text: str, chunk_size: Optional[int] = None, overlap: Optional[int] = None
) -> List[str]:
    size = chunk_size or settings.chunk_size
    step = size - (overlap or settings.chunk_overlap)
    if not text.strip():
        return []
    chunks: List[str] = []
    start = 0
    while start < len(text):
        end = start + size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start += step
    return chunks


def index_web_page(db: Session, web_page: WebPage) -> int:
    """Chunk, embed, and store vectors for a web page. Returns chunk count."""
    db.query(Chunk).filter(Chunk.web_page_id == web_page.id).delete()

    project = db.query(Project).filter(Project.id == web_page.project_id).first()
    if not project:
        return 0
    domain = db.query(Domain).filter(Domain.id == project.domain_id).first()
    if not domain:
        return 0
    source = db.query(Source).filter(Source.id == domain.source_id).first()
    if not source:
        return 0

    text_chunks = chunk_text(web_page.content)
    if not text_chunks:
        db.commit()
        return 0

    embeddings, provider = provider_embed_texts(text_chunks)
    for idx, (chunk_text_content, embedding) in enumerate(zip(text_chunks, embeddings)):
        db.add(
            Chunk(
                web_page_id=web_page.id,
                chunk_index=idx,
                content=chunk_text_content,
                embedding=serialize_embedding(embedding),
                embedding_provider=provider,
                source_id=source.id,
                domain_id=domain.id,
                project_id=project.id,
            )
        )
    db.commit()
    return len(text_chunks)


def delete_web_page_chunks(db: Session, web_page_id: str) -> None:
    db.query(Chunk).filter(Chunk.web_page_id == web_page_id).delete()
    db.commit()


def reindex_all(db: Session) -> Dict[str, int]:
    pages = db.query(WebPage).all()
    total_chunks = 0
    for page in pages:
        total_chunks += index_web_page(db, page)
    return {"pages_indexed": len(pages), "chunks_created": total_chunks}
