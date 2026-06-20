from __future__ import annotations

import json
import logging
import traceback
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.config import BACKEND_DIR
from app.database import SessionLocal
from app.models import ActivityLog

LOG_DIR = BACKEND_DIR / "logs"
LOG_FILE = LOG_DIR / "atlas.log"

_file_logger: Optional[logging.Logger] = None


def _get_file_logger() -> logging.Logger:
    global _file_logger
    if _file_logger is not None:
        return _file_logger
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("atlas")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
        handler.setFormatter(
            logging.Formatter("%(asctime)s | %(levelname)s | %(message)s")
        )
        logger.addHandler(handler)
    _file_logger = logger
    return logger


def log_activity(
    level: str,
    activity: str,
    message: str,
    *,
    page: Optional[str] = None,
    endpoint: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    error_trace: Optional[str] = None,
    db: Optional[Session] = None,
) -> ActivityLog:
    """Persist an activity log entry to the database and atlas.log file."""
    owns_session = db is None
    session = db or SessionLocal()
    try:
        entry = ActivityLog(
            id=str(uuid.uuid4()),
            level=level.upper(),
            activity=activity,
            page=page,
            message=message,
            endpoint=endpoint,
            entity_type=entity_type,
            entity_id=entity_id,
            details=json.dumps(details or {}, default=str),
            error_trace=error_trace,
            created_at=datetime.now(timezone.utc),
        )
        session.add(entry)
        session.commit()
        session.refresh(entry)

        log_line = f"{activity} | {page or '-'} | {endpoint or '-'} | {message}"
        if details:
            log_line += f" | {json.dumps(details, default=str)}"
        logger = _get_file_logger()
        if level.upper() == "ERROR":
            logger.error(log_line)
            if error_trace:
                logger.error(error_trace)
        elif level.upper() == "WARNING":
            logger.warning(log_line)
        else:
            logger.info(log_line)
        return entry
    except Exception:
        session.rollback()
        raise
    finally:
        if owns_session:
            session.close()


def log_exception(
    activity: str,
    exc: BaseException,
    *,
    page: Optional[str] = None,
    endpoint: Optional[str] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[str] = None,
    details: Optional[Dict[str, Any]] = None,
    db: Optional[Session] = None,
) -> ActivityLog:
    return log_activity(
        "ERROR",
        activity,
        str(exc),
        page=page,
        endpoint=endpoint,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        error_trace=traceback.format_exc(),
        db=db,
    )
