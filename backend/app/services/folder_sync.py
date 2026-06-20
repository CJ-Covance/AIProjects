from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from sqlalchemy.orm import Session

from app.models import Domain, Project, Source, WebPage
from app.services.file_reader import SUPPORTED_EXTENSIONS, list_supported_files, read_file_content
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


def list_files_shallow(folder: Path) -> List[Path]:
    """Files directly in folder (not subfolders) — for source/domain root files."""
    if not folder.exists() or not folder.is_dir():
        return []
    return sorted(
        [
            p
            for p in folder.iterdir()
            if p.is_file() and p.suffix.lower() in SUPPORTED_EXTENSIONS
        ]
    )


def _sync_file(db: Session, project: Project, file_path: Path, storage_key: str) -> str:
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
            WebPage.source_file_path == storage_key,
        )
        .first()
    )

    if page:
        page.title = title
        page.content = content
        page.url = f"file:///{file_path.resolve().as_posix()}"
        page.updated_at = _utcnow()
        action = "updated"
    else:
        page = WebPage(
            project_id=project.id,
            title=title,
            content=content,
            url=f"file:///{file_path.resolve().as_posix()}",
            source_file_path=storage_key,
        )
        db.add(page)
        action = "created"

    db.commit()
    db.refresh(page)
    try:
        count = index_web_page(db, page)
        if count == 0:
            return f"indexed_empty:{file_path.name}"
        return action
    except Exception as exc:
        return f"indexed_failed:{file_path.name}:{exc}"


def _sync_folder(
    db: Session, project_id: str, folder: Path, recursive: bool = True
) -> Dict[str, object]:
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise ValueError("Project not found")

    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)

    if recursive:
        files = list_supported_files(folder)
        results = []
        for file_path in files:
            try:
                key = str(file_path.relative_to(folder))
            except ValueError:
                key = f"@external/{file_path.name}"
            results.append(_sync_file(db, project, file_path, key))
    else:
        files = list_files_shallow(folder)
        results = []
        for file_path in files:
            key = f"@root/{folder.name}/{file_path.name}"
            results.append(_sync_file(db, project, file_path, key))

    return {
        "project_id": project_id,
        "folder_path": str(folder.resolve()),
        "files_found": len(files),
        "results": results,
        "recursive": recursive,
    }


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

    result = _sync_folder(db, project_id, folder, recursive=True)
    result["message"] = f"Synced {result['files_found']} file(s) from disk"
    return result


def _collect_sync_targets(
    db: Session,
    source_id: Optional[str],
    domain_id: Optional[str],
    project_id: Optional[str],
) -> List[Tuple[str, Path, bool]]:
    """Return (project_id, folder_path, recursive) tuples to scan."""
    targets: List[Tuple[str, Path, bool]] = []

    if project_id:
        folder = resolve_project_path(db, project_id)
        if folder:
            targets.append((project_id, folder, True))
        return targets

    if domain_id:
        projects = db.query(Project).filter(Project.domain_id == domain_id).all()
        for project in projects:
            folder = resolve_project_path(db, project.id)
            if folder:
                targets.append((project.id, folder, True))
        domain_path = resolve_domain_path(db, domain_id)
        if domain_path and projects:
            targets.append((projects[0].id, domain_path, False))
        return targets

    if source_id:
        projects = (
            db.query(Project)
            .join(Domain, Project.domain_id == Domain.id)
            .filter(Domain.source_id == source_id)
            .all()
        )
        for project in projects:
            folder = resolve_project_path(db, project.id)
            if folder:
                targets.append((project.id, folder, True))
        source_path = resolve_source_path(db, source_id)
        if source_path and projects:
            # Files placed directly in source folder (e.g. knowledge_base/Cancer/*.txt)
            targets.append((projects[0].id, source_path, False))
        return targets

    return targets


def sync_scope_from_disk(
    db: Session,
    source_id: Optional[str] = None,
    domain_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Dict[str, object]:
    paths = resolve_scope_paths(db, source_id, domain_id, project_id)
    targets = _collect_sync_targets(db, source_id, domain_id, project_id)

    summary: Dict[str, object] = {
        "folder_paths": [str(p) for p in paths],
        "projects_synced": 0,
        "files_found": 0,
        "details": [],
    }

    seen: set[Tuple[str, str, bool]] = set()
    for pid, folder, recursive in targets:
        key = (pid, str(folder.resolve()), recursive)
        if key in seen:
            continue
        seen.add(key)
        result = _sync_folder(db, pid, folder, recursive=recursive)
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
    if suffix not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type. Supported: {', '.join(sorted(SUPPORTED_EXTENSIONS))}"
        )

    target = folder / safe_name
    target.write_bytes(file_bytes)
    key = str(target.relative_to(folder))
    result = _sync_file(db, project, target, key)
    return {
        "project_id": project_id,
        "folder_path": str(folder.resolve()),
        "filename": safe_name,
        "result": result,
    }
