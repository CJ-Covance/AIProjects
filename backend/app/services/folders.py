from __future__ import annotations

import re
from pathlib import Path
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.config import BACKEND_DIR, settings
from app.models import Domain, Project, Source


def slugify(name: str) -> str:
    cleaned = re.sub(r"[^\w\s-]", "", name, flags=re.UNICODE).strip()
    cleaned = re.sub(r"[\s_]+", "_", cleaned)
    return cleaned or "unnamed"


def _segment(folder_path: Optional[str], name: str) -> str:
    if folder_path and folder_path.strip():
        return folder_path.strip().strip("/\\")
    return slugify(name)


def knowledge_root() -> Path:
    root = Path(settings.knowledge_base_root)
    if not root.is_absolute():
        root = BACKEND_DIR / root
    return root.resolve()


def resolve_source_path(db: Session, source_id: str) -> Optional[Path]:
    source = db.query(Source).filter(Source.id == source_id).first()
    if not source:
        return None
    return knowledge_root() / _segment(source.folder_path, source.name)


def resolve_domain_path(db: Session, domain_id: str) -> Optional[Path]:
    domain = db.query(Domain).filter(Domain.id == domain_id).first()
    if not domain:
        return None
    source_path = resolve_source_path(db, domain.source_id)
    if not source_path:
        return None
    return source_path / _segment(domain.folder_path, domain.name)


def resolve_project_path(db: Session, project_id: str) -> Optional[Path]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None
    domain_path = resolve_domain_path(db, project.domain_id)
    if not domain_path:
        return None
    return domain_path / _segment(project.folder_path, project.name)


def resolve_scope_paths(
    db: Session,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> List[Path]:
    if project_id:
        path = resolve_project_path(db, project_id)
        return [path] if path else []
    if domain_id:
        domain_path = resolve_domain_path(db, domain_id)
        if not domain_path:
            return []
        projects = db.query(Project).filter(Project.domain_id == domain_id).all()
        if projects:
            return [
                domain_path / _segment(p.folder_path, p.name)
                for p in projects
            ]
        return [domain_path]
    if source_id:
        source_path = resolve_source_path(db, source_id)
        if not source_path:
            return []
        return [source_path]
    return []


def ensure_folder(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def ensure_hierarchy_folders(db: Session, source: Source, domain: Domain, project: Project) -> Path:
    project_path = resolve_project_path(db, project.id)
    if project_path is None:
        raise ValueError("Could not resolve project folder path")
    return ensure_folder(project_path)


def get_hierarchy_labels(
    db: Session, project_id: str
) -> Tuple[Optional[Source], Optional[Domain], Optional[Project]]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        return None, None, None
    domain = db.query(Domain).filter(Domain.id == project.domain_id).first()
    if not domain:
        return None, None, project
    source = db.query(Source).filter(Source.id == domain.source_id).first()
    return source, domain, project
