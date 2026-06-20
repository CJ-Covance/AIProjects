from __future__ import annotations

from typing import List, Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import ActivityLog
from app.schemas import ActivityLogOut, LogsResponse
from app.services.page_files import read_log_file_tail

router = APIRouter(tags=["logs"])


def _fetch_logs(
    db: Session,
    level: Optional[str],
    page: Optional[str],
    limit: int,
    offset: int,
) -> LogsResponse:
    query = db.query(ActivityLog).order_by(ActivityLog.created_at.desc())
    if level:
        query = query.filter(ActivityLog.level == level.upper())
    if page:
        query = query.filter(ActivityLog.page == page)

    total = query.count()
    logs: List[ActivityLog] = query.offset(offset).limit(limit).all()
    return LogsResponse(
        logs=[ActivityLogOut.model_validate(log) for log in logs],
        total=total,
        file_tail=read_log_file_tail(150),
    )


@router.get("/api/logs", response_model=LogsResponse)
@router.get("/api/log", response_model=LogsResponse)
def list_logs(
    level: Optional[str] = Query(None, description="Filter by level: INFO, WARNING, ERROR"),
    page: Optional[str] = Query(None, description="Filter by UI page name"),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return _fetch_logs(db, level, page, limit, offset)


@router.delete("/api/logs", status_code=204)
@router.delete("/api/log", status_code=204)
def clear_logs(db: Session = Depends(get_db)):
    db.query(ActivityLog).delete()
    db.commit()
