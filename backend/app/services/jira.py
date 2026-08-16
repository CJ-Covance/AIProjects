"""Jira Cloud REST API client."""

from __future__ import annotations

import httpx
from fastapi import HTTPException

from app.config import settings


class JiraClient:
    def __init__(self) -> None:
        self._base_url = settings.jira_base_url.rstrip("/")
        self._auth = (settings.jira_email, settings.jira_api_token)

    def _require_configured(self) -> None:
        if not settings.jira_configured:
            raise HTTPException(
                status_code=503,
                detail=(
                    "Jira is not configured. Set JIRA_BASE_URL, JIRA_EMAIL, "
                    "and JIRA_API_TOKEN in the backend environment."
                ),
            )

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: dict | None = None,
        params: dict | None = None,
    ) -> dict | list:
        self._require_configured()
        url = f"{self._base_url}{path}"
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.request(
                method,
                url,
                auth=self._auth,
                json=json,
                params=params,
                headers={"Accept": "application/json", "Content-Type": "application/json"},
            )

        if response.status_code >= 400:
            detail = response.text
            try:
                body = response.json()
                if isinstance(body, dict):
                    messages = body.get("errorMessages") or []
                    errors = body.get("errors") or {}
                    if messages:
                        detail = "; ".join(messages)
                    elif errors:
                        detail = "; ".join(f"{k}: {v}" for k, v in errors.items())
            except Exception:
                pass
            raise HTTPException(status_code=response.status_code, detail=detail)

        if response.status_code == 204 or not response.content:
            return {}
        return response.json()

    async def get_status(self) -> dict:
        if not settings.jira_configured:
            return {"configured": False, "connected": False}
        try:
            await self._request("GET", "/rest/api/3/myself")
            return {"configured": True, "connected": True}
        except HTTPException as exc:
            return {"configured": True, "connected": False, "error": str(exc.detail)}

    async def list_projects(self) -> list[dict]:
        data = await self._request(
            "GET",
            "/rest/api/3/project/search",
            params={"maxResults": 50, "orderBy": "name"},
        )
        values = data.get("values", []) if isinstance(data, dict) else []
        return [
            {"id": p["id"], "key": p["key"], "name": p["name"]}
            for p in values
        ]

    async def list_issue_types(self, project_key: str) -> list[dict]:
        data = await self._request(
            "GET",
            "/rest/api/3/issue/createmeta",
            params={
                "projectKeys": project_key,
                "expand": "projects.issuetypes",
            },
        )
        projects = data.get("projects", []) if isinstance(data, dict) else []
        if not projects:
            return []
        issue_types = projects[0].get("issuetypes", [])
        return [
            {"id": it["id"], "name": it["name"], "description": it.get("description")}
            for it in issue_types
        ]

    async def list_priorities(self) -> list[dict]:
        data = await self._request("GET", "/rest/api/3/priority")
        if not isinstance(data, list):
            return []
        return [{"id": p["id"], "name": p["name"]} for p in data]

    @staticmethod
    def _adf_description(text: str) -> dict:
        paragraphs = []
        for block in text.split("\n"):
            if block.strip():
                paragraphs.append(
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": block}],
                    }
                )
        if not paragraphs:
            paragraphs.append(
                {
                    "type": "paragraph",
                    "content": [{"type": "text", "text": ""}],
                }
            )
        return {"type": "doc", "version": 1, "content": paragraphs}

    async def create_issue(
        self,
        *,
        project_key: str,
        summary: str,
        description: str,
        issue_type: str,
        priority: str | None = None,
        labels: list[str] | None = None,
    ) -> dict:
        fields: dict = {
            "project": {"key": project_key},
            "summary": summary,
            "description": self._adf_description(description),
            "issuetype": {"name": issue_type},
        }
        if priority:
            fields["priority"] = {"name": priority}
        if labels:
            fields["labels"] = labels

        result = await self._request(
            "POST",
            "/rest/api/3/issue",
            json={"fields": fields},
        )
        issue_key = result.get("key", "")
        issue_id = result.get("id", "")
        issue_url = f"{self._base_url}/browse/{issue_key}" if issue_key else None
        return {
            "id": issue_id,
            "key": issue_key,
            "url": issue_url,
        }


jira_client = JiraClient()
