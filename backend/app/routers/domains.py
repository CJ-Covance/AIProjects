from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Domain, Project, Source, WebPage
from app.schemas import DomainCreate, DomainOut, DomainUpdate

router = APIRouter(prefix="/api/domains", tags=["domains"])


def _domain_out(domain: Domain, db: Session) -> DomainOut:
    projects = db.query(Project).filter(Project.domain_id == domain.id).all()
    project_ids = [p.id for p in projects]
    page_count = 0
    if project_ids:
        page_count = db.query(WebPage).filter(WebPage.project_id.in_(project_ids)).count()
    return DomainOut(
        id=domain.id,
        source_id=domain.source_id,
        name=domain.name,
        description=domain.description,
        created_at=domain.created_at,
        updated_at=domain.updated_at,
        project_count=len(projects),
        page_count=page_count,
    )


@router.get("", response_model=list[DomainOut])
def list_domains(source_id: str | None = Query(None), db: Session = Depends(get_db)):
    query = db.query(Domain)
    if source_id:
        query = query.filter(Domain.source_id == source_id)
    domains = query.order_by(Domain.name).all()
    return [_domain_out(d, db) for d in domains]


@router.get("/{domain_id}", response_model=DomainOut)
def get_domain(domain_id: str, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    return _domain_out(domain, db)


@router.post("", response_model=DomainOut, status_code=201)
def create_domain(payload: DomainCreate, db: Session = Depends(get_db)):
    source = db.query(Source).filter(Source.id == payload.source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    domain = Domain(
        source_id=payload.source_id,
        name=payload.name,
        description=payload.description,
    )
    db.add(domain)
    db.commit()
    db.refresh(domain)
    return _domain_out(domain, db)


@router.put("/{domain_id}", response_model=DomainOut)
def update_domain(domain_id: str, payload: DomainUpdate, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    if payload.name is not None:
        domain.name = payload.name
    if payload.description is not None:
        domain.description = payload.description
    db.commit()
    db.refresh(domain)
    return _domain_out(domain, db)


@router.delete("/{domain_id}", status_code=204)
def delete_domain(domain_id: str, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    db.delete(domain)
    db.commit()
