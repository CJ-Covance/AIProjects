from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Chunk, Domain, Project, Source, WebPage
from app.schemas import SourceCreate, SourceOut, SourceUpdate
from app.services.folders import ensure_folder, knowledge_root, resolve_source_path

router = APIRouter(prefix="/api/sources", tags=["sources"])


def _source_out(source: Source, db: Session) -> SourceOut:
    domains = db.query(Domain).filter(Domain.source_id == source.id).all()
    domain_ids = [d.id for d in domains]
    page_count = 0
    if domain_ids:
        projects = db.query(Project).filter(Project.domain_id.in_(domain_ids)).all()
        project_ids = [p.id for p in projects]
        if project_ids:
            page_count = db.query(WebPage).filter(WebPage.project_id.in_(project_ids)).count()
    resolved = resolve_source_path(db, source.id)
    return SourceOut(
        id=source.id,
        name=source.name,
        description=source.description,
        folder_path=source.folder_path,
        created_at=source.created_at,
        updated_at=source.updated_at,
        domain_count=len(domains),
        page_count=page_count,
        resolved_folder_path=str(resolved) if resolved else None,
    )


@router.get("", response_model=List[SourceOut])
def list_sources(db: Session = Depends(get_db)):
    sources = db.query(Source).order_by(Source.name).all()
    return [_source_out(s, db) for s in sources]


@router.get("/{source_id}", response_model=SourceOut)
def get_source(source_id: str, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return _source_out(source, db)


@router.post("", response_model=SourceOut, status_code=201)
def create_source(payload: SourceCreate, db: Session = Depends(get_db)):
    source = Source(
        name=payload.name,
        description=payload.description,
        folder_path=payload.folder_path,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    path = resolve_source_path(db, source.id)
    if path:
        ensure_folder(path)
    ensure_folder(knowledge_root())
    return _source_out(source, db)


@router.put("/{source_id}", response_model=SourceOut)
def update_source(source_id: str, payload: SourceUpdate, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    if payload.name is not None:
        source.name = payload.name
    if payload.description is not None:
        source.description = payload.description
    if payload.folder_path is not None:
        source.folder_path = payload.folder_path
    db.commit()
    db.refresh(source)
    path = resolve_source_path(db, source.id)
    if path:
        ensure_folder(path)
    return _source_out(source, db)


@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: str, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    db.delete(source)
    db.commit()
