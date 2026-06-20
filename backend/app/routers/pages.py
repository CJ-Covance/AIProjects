from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project, WebPage
from app.schemas import WebPageCreate, WebPageOut, WebPageUpdate
from app.services.activity_log import log_activity, log_exception
from app.services.folders import resolve_project_path
from app.services.indexer import delete_web_page_chunks, index_web_page
from app.services.page_files import save_page_to_disk

router = APIRouter(prefix="/api/pages", tags=["pages"])


def _page_out(
    page: WebPage,
    db: Session,
    disk_path: Optional[str] = None,
    index_warning: Optional[str] = None,
) -> WebPageOut:
    chunk_count = len(page.chunks) if page.chunks else 0
    return WebPageOut(
        id=page.id,
        project_id=page.project_id,
        title=page.title,
        content=page.content,
        url=page.url,
        source_file_path=page.source_file_path,
        disk_path=disk_path,
        index_warning=index_warning,
        created_at=page.created_at,
        updated_at=page.updated_at,
        chunk_count=chunk_count,
    )


def _persist_page(
    db: Session,
    page: WebPage,
    save_to_disk: bool,
    activity_label: str,
) -> WebPageOut:
    disk_path: Optional[str] = None
    index_warning: Optional[str] = None

    if save_to_disk:
        try:
            abs_path, rel_path = save_page_to_disk(db, page)
            disk_path = abs_path
            db.commit()
            db.refresh(page)
            log_activity(
                "INFO",
                activity_label,
                f"Saved page content to disk: {abs_path}",
                page="Manage",
                endpoint="/api/pages",
                entity_type="web_page",
                entity_id=page.id,
                details={"disk_path": abs_path, "relative_path": rel_path},
                db=db,
            )
        except Exception as exc:
            log_exception(
                activity_label,
                exc,
                page="Manage",
                endpoint="/api/pages",
                entity_type="web_page",
                entity_id=page.id,
                details={"action": "save_to_disk"},
                db=db,
            )
            index_warning = f"Could not save to disk: {exc}"

    try:
        index_web_page(db, page)
        log_activity(
            "INFO",
            activity_label,
            "Page indexed successfully",
            page="Manage",
            endpoint="/api/pages",
            entity_type="web_page",
            entity_id=page.id,
            db=db,
        )
    except Exception as exc:
        log_exception(
            f"{activity_label} indexing",
            exc,
            page="Manage",
            endpoint="/api/pages",
            entity_type="web_page",
            entity_id=page.id,
            db=db,
        )
        warning = f"Page saved but indexing failed: {exc}"
        index_warning = f"{index_warning}; {warning}" if index_warning else warning

    db.refresh(page)
    return _page_out(page, db, disk_path=disk_path, index_warning=index_warning)


@router.get("", response_model=List[WebPageOut])
def list_pages(project_id: Optional[str] = Query(None), db: Session = Depends(get_db)):
    query = db.query(WebPage)
    if project_id:
        query = query.filter(WebPage.project_id == project_id)
    pages = query.order_by(WebPage.title).all()
    return [_page_out(p, db) for p in pages]


@router.get("/{page_id}", response_model=WebPageOut)
def get_page(page_id: str, db: Session = Depends(get_db)):
    page = db.query(WebPage).filter(WebPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Web page not found")
    return _page_out(page, db)


@router.post("", response_model=WebPageOut, status_code=201)
def create_page(payload: WebPageCreate, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == payload.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    folder = resolve_project_path(db, payload.project_id)
    log_activity(
        "INFO",
        "Create web page",
        f"Creating page '{payload.title}' for project {project.name}",
        page="Manage",
        endpoint="/api/pages",
        entity_type="project",
        entity_id=payload.project_id,
        details={
            "title": payload.title,
            "project_folder": str(folder) if folder else None,
            "save_to_disk": payload.save_to_disk,
        },
        db=db,
    )

    page = WebPage(
        project_id=payload.project_id,
        title=payload.title,
        content=payload.content,
        url=payload.url,
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    return _persist_page(db, page, payload.save_to_disk, "Create web page")


@router.put("/{page_id}", response_model=WebPageOut)
def update_page(page_id: str, payload: WebPageUpdate, db: Session = Depends(get_db)):
    page = db.query(WebPage).filter(WebPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Web page not found")
    if payload.title is not None:
        page.title = payload.title
    if payload.content is not None:
        page.content = payload.content
    if payload.url is not None:
        page.url = payload.url
    db.commit()
    db.refresh(page)
    return _persist_page(db, page, payload.save_to_disk, "Update web page")


@router.delete("/{page_id}", status_code=204)
def delete_page(page_id: str, db: Session = Depends(get_db)):
    page = db.query(WebPage).filter(WebPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Web page not found")
    delete_web_page_chunks(db, page_id)
    db.delete(page)
    db.commit()
    log_activity(
        "INFO",
        "Delete web page",
        f"Deleted page '{page.title}'",
        page="Manage",
        endpoint=f"/api/pages/{page_id}",
        entity_type="web_page",
        entity_id=page_id,
        db=db,
    )
