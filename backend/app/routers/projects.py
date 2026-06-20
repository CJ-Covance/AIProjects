from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Domain, Project, Source, WebPage
from app.schemas import (
    FileUploadResponse,
    FolderSyncResponse,
    ProjectCreate,
    ProjectOut,
    ProjectUpdate,
)
from app.services.folder_sync import save_uploaded_file, sync_project_folder
from app.services.folders import ensure_hierarchy_folders, get_hierarchy_labels, resolve_project_path

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _project_out(project: Project, db: Session) -> ProjectOut:
    page_count = db.query(WebPage).filter(WebPage.project_id == project.id).count()
    resolved = resolve_project_path(db, project.id)
    return ProjectOut(
        id=project.id,
        domain_id=project.domain_id,
        name=project.name,
        description=project.description,
        folder_path=project.folder_path,
        created_at=project.created_at,
        updated_at=project.updated_at,
        page_count=page_count,
        resolved_folder_path=str(resolved) if resolved else None,
    )


@router.get("", response_model=List[ProjectOut])
def list_projects(domain_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(Project)
    if domain_id:
        query = query.filter(Project.domain_id == domain_id)
    projects = query.order_by(Project.name).all()
    return [_project_out(p, db) for p in projects]


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _project_out(project, db)


@router.post("", response_model=ProjectOut, status_code=201)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    domain = db.query(Domain).filter(Domain.id == payload.domain_id).first()
    if not domain:
        raise HTTPException(status_code=404, detail="Domain not found")
    project = Project(
        domain_id=payload.domain_id,
        name=payload.name,
        description=payload.description,
        folder_path=payload.folder_path,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    source = db.query(Source).filter(Source.id == domain.source_id).first()
    if source:
        try:
            ensure_hierarchy_folders(db, source, domain, project)
        except ValueError:
            pass
    return _project_out(project, db)


@router.put("/{project_id}", response_model=ProjectOut)
def update_project(project_id: str, payload: ProjectUpdate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.folder_path is not None:
        project.folder_path = payload.folder_path
    db.commit()
    db.refresh(project)
    source, domain, _ = get_hierarchy_labels(db, project_id)
    if source and domain:
        try:
            ensure_hierarchy_folders(db, source, domain, project)
        except ValueError:
            pass
    return _project_out(project, db)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()


@router.post("/{project_id}/sync-folder", response_model=FolderSyncResponse)
def sync_folder(project_id: str, db: Session = Depends(get_db)):
    try:
        result = sync_project_folder(db, project_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return FolderSyncResponse(**result)


@router.post("/{project_id}/upload", response_model=FileUploadResponse)
async def upload_file(
    project_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    content = await file.read()
    if not content:
        raise HTTPException(status_code=400, detail="Empty file")
    try:
        result = save_uploaded_file(db, project_id, file.filename or "upload.txt", content)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return FileUploadResponse(**result)
