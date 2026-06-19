from datetime import datetime

from pydantic import BaseModel, Field


class SourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class SourceOut(SourceBase):
    id: str
    created_at: datetime
    updated_at: datetime
    domain_count: int = 0
    page_count: int = 0

    model_config = {"from_attributes": True}


class DomainBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class DomainCreate(DomainBase):
    source_id: str


class DomainUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class DomainOut(DomainBase):
    id: str
    source_id: str
    created_at: datetime
    updated_at: datetime
    project_count: int = 0
    page_count: int = 0

    model_config = {"from_attributes": True}


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: str | None = None


class ProjectCreate(ProjectBase):
    domain_id: str


class ProjectUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    description: str | None = None


class ProjectOut(ProjectBase):
    id: str
    domain_id: str
    created_at: datetime
    updated_at: datetime
    page_count: int = 0

    model_config = {"from_attributes": True}


class WebPageBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = ""
    url: str | None = None


class WebPageCreate(WebPageBase):
    project_id: str


class WebPageUpdate(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=500)
    content: str | None = None
    url: str | None = None


class WebPageOut(WebPageBase):
    id: str
    project_id: str
    created_at: datetime
    updated_at: datetime
    chunk_count: int = 0

    model_config = {"from_attributes": True}


class HierarchyNode(BaseModel):
    id: str
    name: str
    type: str
    description: str | None = None
    page_count: int = 0
    children: list["HierarchyNode"] = []


class SearchRequest(BaseModel):
    question: str = Field(..., min_length=1)
    source_id: str | None = None
    domain_id: str | None = None
    project_id: str | None = None


class Citation(BaseModel):
    index: int
    web_page_id: str
    title: str
    url: str | None
    snippet: str
    source_name: str
    domain_name: str
    project_name: str
    updated_at: datetime


class SearchResponse(BaseModel):
    answer: str
    citations: list[Citation]
    confidence: str
    found_relevant: bool
