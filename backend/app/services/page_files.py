from __future__ import annotations


from pathlib import Path
from typing import Optional, Tuple

from sqlalchemy.orm import Session

from app.models import WebPage
from app.services.folders import ensure_folder, resolve_project_path, slugify


def page_filename(title: str, extension: str = ".md") -> str:
    base = slugify(title) or "page"
    return f"{base}{extension}"


def save_page_to_disk(db: Session, page: WebPage) -> Tuple[Optional[str], Optional[str]]:
    """
    Write page content to the project folder on disk.
    Returns (absolute_path, relative_path) or (None, None) on failure.
    """
    folder = resolve_project_path(db, page.project_id)
    if folder is None:
        return None, None

    ensure_folder(folder)
    filename = page_filename(page.title)
    target = folder / filename

    # Avoid overwriting unrelated files when title changes
    if page.source_file_path:
        existing = folder / page.source_file_path
        if existing.exists() and existing.is_file():
            target = existing
            filename = existing.name

    target.write_text(page.content or "", encoding="utf-8")
    relative = str(target.relative_to(folder))
    page.source_file_path = relative
    page.url = f"file:///{target.as_posix()}"
    return str(target.resolve()), relative


def read_log_file_tail(max_lines: int = 200) -> str:
    from app.services.activity_log import LOG_FILE

    if not LOG_FILE.exists():
        return ""
    lines = LOG_FILE.read_text(encoding="utf-8", errors="ignore").splitlines()
    return "\n".join(lines[-max_lines:])
