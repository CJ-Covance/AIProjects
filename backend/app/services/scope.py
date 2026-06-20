from __future__ import annotations

from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Chunk, Domain, Project, Source, WebPage


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
) -> int:
    query = db.query(Chunk)
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
    """Re-index any pages in scope that have content but no embedding chunks."""
    from app.services.indexer import index_web_page

    pages = get_pages_in_scope(db, source_id, domain_id, project_id)
    reindexed = 0
    failed: List[str] = []
    already_indexed = 0

    for page in pages:
        if not page.content or not page.content.strip():
            continue
        chunk_count = db.query(Chunk).filter(Chunk.web_page_id == page.id).count()
        if chunk_count > 0:
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
    }
