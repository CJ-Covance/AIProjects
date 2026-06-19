from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Domain, Project, WebPage
from app.schemas import ProjectCreate, ProjectOut, ProjectUpdate

router = APIRouter(prefix="/api/projects", tags=["projects"])


def _project_out(project: Project, db: Session) -> ProjectOut:
    page_count = db.query(WebPage).filter(WebPage.project_id == project.id).count()
    return ProjectOut(
        id=project.id,
        domain_id=project.domain_id,
        name=project.name,
        description=project.description,
        created_at=project.created_at,
        updated_at=project.updated_at,
        page_count=page_count,
    )


@router.get("", response_model=list[ProjectOut])
def list_projects(domain_id: str | None = Query(None), db: Session = Depends(get_db)):
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
    )
    db.add(project)
    db.commit()
    db.refresh(project)
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
    db.commit()
    db.refresh(project)
    return _project_out(project, db)


@router.delete("/{project_id}", status_code=204)
def delete_project(project_id: str, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(project)
    db.commit()
