from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Project, WebPage
from app.schemas import WebPageCreate, WebPageOut, WebPageUpdate
from app.services.indexer import delete_web_page_chunks, index_web_page

router = APIRouter(prefix="/api/pages", tags=["pages"])


def _page_out(page: WebPage, db: Session) -> WebPageOut:
    chunk_count = len(page.chunks) if page.chunks else 0
    return WebPageOut(
        id=page.id,
        project_id=page.project_id,
        title=page.title,
        content=page.content,
        url=page.url,
        created_at=page.created_at,
        updated_at=page.updated_at,
        chunk_count=chunk_count,
    )


@router.get("", response_model=list[WebPageOut])
def list_pages(project_id: str | None = Query(None), db: Session = Depends(get_db)):
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
    page = WebPage(
        project_id=payload.project_id,
        title=payload.title,
        content=payload.content,
        url=payload.url,
    )
    db.add(page)
    db.commit()
    db.refresh(page)
    try:
        index_web_page(db, page)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    db.refresh(page)
    return _page_out(page, db)


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
    try:
        index_web_page(db, page)
    except ValueError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    db.refresh(page)
    return _page_out(page, db)


@router.delete("/{page_id}", status_code=204)
def delete_page(page_id: str, db: Session = Depends(get_db)):
    page = db.query(WebPage).filter(WebPage.id == page_id).first()
    if not page:
        raise HTTPException(status_code=404, detail="Web page not found")
    delete_web_page_chunks(db, page_id)
    db.delete(page)
    db.commit()
