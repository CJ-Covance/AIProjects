from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.config import settings
from app.models import Chunk, Domain, Project, Source, WebPage
from app.services.llm_provider import get_embedding_provider_name


def _page_needs_reindex(db: Session, page: WebPage) -> bool:
    chunks = db.query(Chunk).filter(Chunk.web_page_id == page.id).all()
    if not chunks:
        return True
    if any(chunk.embedding_provider is None for chunk in chunks):
        return True

    # In auto mode, any successfully indexed provider is acceptable.
    if settings.llm_provider.lower().strip() == "auto":
        return False

    target_provider = get_embedding_provider_name()
    return any(chunk.embedding_provider != target_provider for chunk in chunks)


def get_pages_in_scope(
    db: Session,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> List[WebPage]:
    query = db.query(WebPage)
    if project_id:
        return query.filter(WebPage.project_id == project_id).all()
    if domain_id:
        project_ids = [
            p.id for p in db.query(Project).filter(Project.domain_id == domain_id).all()
        ]
        if not project_ids:
            return []
        return query.filter(WebPage.project_id.in_(project_ids)).all()
    if source_id:
        domain_ids = [
            d.id for d in db.query(Domain).filter(Domain.source_id == source_id).all()
        ]
        if not domain_ids:
            return []
        project_ids = [
            p.id for p in db.query(Project).filter(Project.domain_id.in_(domain_ids)).all()
        ]
        if not project_ids:
            return []
        return query.filter(WebPage.project_id.in_(project_ids)).all()
    return query.all()


def count_chunks_in_scope(
    db: Session,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
    embedding_provider: Optional[str] = None,
) -> int:
    provider = embedding_provider
    if provider is None and settings.llm_provider.lower().strip() != "auto":
        provider = get_embedding_provider_name()

    query = db.query(Chunk)
    if provider:
        query = query.filter(Chunk.embedding_provider == provider)
    else:
        query = query.filter(Chunk.embedding_provider.isnot(None))
    if project_id:
        query = query.filter(Chunk.project_id == project_id)
    elif domain_id:
        query = query.filter(Chunk.domain_id == domain_id)
    elif source_id:
        query = query.filter(Chunk.source_id == source_id)
    return query.count()


def ensure_indexed_for_scope(
    db: Session,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Dict[str, object]:
    """Re-index pages in scope that are missing chunks or were embedded with another provider."""
    from app.services.indexer import index_web_page

    pages = get_pages_in_scope(db, source_id, domain_id, project_id)
    current_provider = get_embedding_provider_name()
    reindexed = 0
    failed: List[str] = []
    already_indexed = 0

    for page in pages:
        if not page.content or not page.content.strip():
            continue
        if not _page_needs_reindex(db, page):
            already_indexed += 1
            continue
        try:
            created = index_web_page(db, page)
            if created > 0:
                reindexed += 1
            else:
                failed.append(f"{page.title}: no chunks produced")
        except Exception as exc:
            failed.append(f"{page.title}: {exc}")

    return {
        "pages_in_scope": len(pages),
        "already_indexed": already_indexed,
        "reindexed": reindexed,
        "failed": failed,
        "embedding_provider": current_provider,
    }
