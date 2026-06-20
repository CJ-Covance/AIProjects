from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.models import Domain, Project, Source, WebPage
from app.services.file_reader import list_supported_files, read_file_content
from app.services.folders import (
    ensure_hierarchy_folders,
    get_hierarchy_labels,
    resolve_domain_path,
    resolve_project_path,
    resolve_scope_paths,
    resolve_source_path,
)
from app.services.indexer import index_web_page


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _sync_file(db: Session, project: Project, file_path: Path, project_folder: Path) -> str:
    relative_path = str(file_path.relative_to(project_folder))
    title = file_path.stem
    try:
        content = read_file_content(file_path)
    except ValueError as exc:
        return f"skipped:{file_path.name}:{exc}"

    if not content.strip():
        return f"skipped:{file_path.name}:empty"

    page = (
        db.query(WebPage)
        .filter(
            WebPage.project_id == project.id,
            WebPage.source_file_path == relative_path,
        )
        .first()
    )
    mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)

    if page:
        page.title = title
        page.content = content
        page.url = f"file://{file_path.as_posix()}"
        page.updated_at = _utcnow()
        action = "updated"
    else:
        page = WebPage(
            project_id=project.id,
            title=title,
            content=content,
            url=f"file://{file_path.as_posix()}",
            source_file_path=relative_path,
        )
        db.add(page)
        action = "created"

    db.commit()
    db.refresh(page)
    try:
        index_web_page(db, page)
    except Exception as exc:
        return f"indexed_failed:{file_path.name}:{exc}"
    return action


def sync_project_folder(db: Session, project_id: str) -> Dict[str, object]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    source, domain, _ = get_hierarchy_labels(db, project_id)
    if source and domain:
        ensure_hierarchy_folders(db, source, domain, project)

    folder = resolve_project_path(db, project_id)
    if folder is None:
        return {
            "project_id": project_id,
            "folder_path": None,
            "files_found": 0,
            "results": [],
            "message": "No folder path configured for this project",
        }

    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)

    files = list_supported_files(folder)
    results = []
    for file_path in files:
        results.append(_sync_file(db, project, file_path, folder))

    return {
        "project_id": project_id,
        "folder_path": str(folder),
        "files_found": len(files),
        "results": results,
        "message": f"Synced {len(files)} file(s) from disk",
    }


def sync_scope_from_disk(
    db: Session,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Dict[str, object]:
    paths = resolve_scope_paths(db, source_id, domain_id, project_id)
    summary: Dict[str, object] = {
        "folder_paths": [str(p) for p in paths],
        "projects_synced": 0,
        "files_found": 0,
        "details": [],
    }

    project_ids: List[str] = []
    if project_id:
        project_ids = [project_id]
    elif domain_id:
        project_ids = [
            p.id for p in db.query(Project).filter(Project.domain_id == domain_id).all()
        ]
    elif source_id:
        domain_ids = [
            d.id for d in db.query(Domain).filter(Domain.source_id == source_id).all()
        ]
        if domain_ids:
            project_ids = [
                p.id
                for p in db.query(Project).filter(Project.domain_id.in_(domain_ids)).all()
            ]

    for pid in project_ids:
        result = sync_project_folder(db, pid)
        summary["details"].append(result)
        summary["projects_synced"] = int(summary["projects_synced"]) + 1
        summary["files_found"] = int(summary["files_found"]) + int(result["files_found"])

    return summary


def save_uploaded_file(
    db: Session, project_id: str, filename: str, file_bytes: bytes
) -> Dict[str, object]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    source, domain, _ = get_hierarchy_labels(db, project_id)
    if not source or not domain:
        raise ValueError("Project hierarchy incomplete")

    folder = ensure_hierarchy_folders(db, source, domain, project)
    safe_name = Path(filename).name
    if not safe_name:
        raise ValueError("Invalid filename")

    suffix = Path(safe_name).suffix.lower()
    from app.services.file_reader import SUPPORTED_EXTENSIONS

    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    target = folder / safe_name
    target.write_bytes(file_bytes)
    result = _sync_file(db, project, target, folder)
    return {
        "project_id": project_id,
        "folder_path": str(folder),
        "filename": safe_name,
        "result": result,
    }
