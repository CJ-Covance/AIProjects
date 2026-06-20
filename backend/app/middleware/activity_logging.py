from __future__ import annotations

import time
from typing import Callable

from fastapi import HTTPException, Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.services.activity_log import log_activity, log_exception


class ActivityLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        if request.url.path.startswith("/api/logs") or request.url.path.startswith("/api/log"):
            return await call_next(request)

        start = time.time()
        page = request.headers.get("X-Atlas-Page", "")
        method = request.method
        path = request.url.path

        try:
            response = await call_next(request)
            duration_ms = int((time.time() - start) * 1000)
            level = "INFO" if response.status_code < 400 else "WARNING"
            log_activity(
                level,
                f"{method} {path}",
                f"HTTP {response.status_code} ({duration_ms}ms)",
                page=page or None,
                endpoint=path,
                details={
                    "method": method,
                    "status_code": response.status_code,
                    "duration_ms": duration_ms,
                },
            )
            return response
        except HTTPException as exc:
            log_activity(
                "WARNING",
                f"{method} {path}",
                str(exc.detail),
                page=page or None,
                endpoint=path,
                details={"status_code": exc.status_code},
            )
            raise
        except Exception as exc:
            log_exception(
                f"{method} {path}",
                exc,
                page=page or None,
                endpoint=path,
                details={"method": method},
            )
            return JSONResponse(
                status_code=500,
                content={"detail": str(exc)},
            )


def register_exception_handlers(app) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        if isinstance(exc, HTTPException):
            raise exc
        page = request.headers.get("X-Atlas-Page", "")
        log_exception(
            "Unhandled exception",
            exc,
            page=page or None,
            endpoint=request.url.path,
            details={"method": request.method},
        )
        return JSONResponse(
            status_code=500,
            content={"detail": str(exc)},
        )
