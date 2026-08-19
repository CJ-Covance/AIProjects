from fastapi import APIRouter, Query

from app.config import settings
from app.schemas import (
    JiraIssueCreate,
    JiraIssueOut,
    JiraIssueType,
    JiraPriority,
    JiraProject,
    JiraStatusResponse,
)
from app.services.jira import jira_client

router = APIRouter(prefix="/api/jira", tags=["jira"])


@router.get("/status", response_model=JiraStatusResponse)
async def jira_status():
    status = await jira_client.get_status()
    return JiraStatusResponse(**status)


@router.get("/projects", response_model=list[JiraProject])
async def list_jira_projects():
    projects = await jira_client.list_projects()
    return [JiraProject(**p) for p in projects]


@router.get("/issue-types", response_model=list[JiraIssueType])
async def list_jira_issue_types(project_key: str = Query(..., min_length=1)):
    issue_types = await jira_client.list_issue_types(project_key)
    return [JiraIssueType(**it) for it in issue_types]


@router.get("/priorities", response_model=list[JiraPriority])
async def list_jira_priorities():
    priorities = await jira_client.list_priorities()
    return [JiraPriority(**p) for p in priorities]


@router.post("/issues", response_model=JiraIssueOut, status_code=201)
async def create_jira_issue(payload: JiraIssueCreate):
    project_key = payload.project_key or settings.jira_default_project_key
    if not project_key:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail="Project key is required")

    result = await jira_client.create_issue(
        project_key=project_key,
        summary=payload.summary,
        description=payload.description,
        issue_type=payload.issue_type,
        priority=payload.priority,
        labels=payload.labels or None,
    )
    return JiraIssueOut(**result)
