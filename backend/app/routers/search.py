from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Domain, Project, Source, WebPage
from app.schemas import HierarchyNode, SearchRequest, SearchResponse
from app.services.folders import resolve_domain_path, resolve_project_path, resolve_source_path
from app.services.rag import generate_answer

router = APIRouter(tags=["search"])


@router.post("/api/search", response_model=SearchResponse)
def search(payload: SearchRequest, db: Session = Depends(get_db)):
    return generate_answer(
        db,
        question=payload.question,
        source_id=payload.source_id,
        domain_id=payload.domain_id,
        project_id=payload.project_id,
    )


@router.get("/api/hierarchy", response_model=List[HierarchyNode])
def get_hierarchy(db: Session = Depends(get_db)):
    sources = db.query(Source).order_by(Source.name).all()
    result: List[HierarchyNode] = []
    for source in sources:
        source_resolved = resolve_source_path(db, source.id)
        source_node = HierarchyNode(
            id=source.id,
            name=source.name,
            type="source",
            description=source.description,
            folder_path=source.folder_path,
            resolved_folder_path=str(source_resolved) if source_resolved else None,
            children=[],
        )
        domains = db.query(Domain).filter(Domain.source_id == source.id).order_by(Domain.name).all()
        for domain in domains:
            domain_page_count = 0
            domain_resolved = resolve_domain_path(db, domain.id)
            domain_node = HierarchyNode(
                id=domain.id,
                name=domain.name,
                type="domain",
                description=domain.description,
                folder_path=domain.folder_path,
                resolved_folder_path=str(domain_resolved) if domain_resolved else None,
                children=[],
            )
            projects = (
                db.query(Project).filter(Project.domain_id == domain.id).order_by(Project.name).all()
            )
            for project in projects:
                page_count = db.query(WebPage).filter(WebPage.project_id == project.id).count()
                domain_page_count += page_count
                project_resolved = resolve_project_path(db, project.id)
                project_node = HierarchyNode(
                    id=project.id,
                    name=project.name,
                    type="project",
                    description=project.description,
                    folder_path=project.folder_path,
                    resolved_folder_path=str(project_resolved) if project_resolved else None,
                    page_count=page_count,
                    children=[],
                )
                domain_node.children.append(project_node)
            domain_node.page_count = domain_page_count
            source_node.children.append(domain_node)
        source_page_count = sum(d.page_count for d in source_node.children)
        source_node.page_count = source_page_count
        result.append(source_node)
    return result
