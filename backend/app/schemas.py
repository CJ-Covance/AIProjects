from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class SourceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    folder_path: Optional[str] = Field(None, max_length=500)


class SourceCreate(SourceBase):
    pass


class SourceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    folder_path: Optional[str] = Field(None, max_length=500)


class SourceOut(SourceBase):
    id: str
    created_at: datetime
    updated_at: datetime
    domain_count: int = 0
    page_count: int = 0
    resolved_folder_path: Optional[str] = None

    model_config = {"from_attributes": True}


class DomainBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    folder_path: Optional[str] = Field(None, max_length=500)


class DomainCreate(DomainBase):
    source_id: str


class DomainUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    folder_path: Optional[str] = Field(None, max_length=500)


class DomainOut(DomainBase):
    id: str
    source_id: str
    created_at: datetime
    updated_at: datetime
    project_count: int = 0
    page_count: int = 0
    resolved_folder_path: Optional[str] = None

    model_config = {"from_attributes": True}


class ProjectBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    folder_path: Optional[str] = Field(None, max_length=500)


class ProjectCreate(ProjectBase):
    domain_id: str


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    folder_path: Optional[str] = Field(None, max_length=500)


class ProjectOut(ProjectBase):
    id: str
    domain_id: str
    created_at: datetime
    updated_at: datetime
    page_count: int = 0
    resolved_folder_path: Optional[str] = None

    model_config = {"from_attributes": True}


class WebPageBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    content: str = ""
    url: Optional[str] = None


class WebPageCreate(WebPageBase):
    project_id: str


class WebPageUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=500)
    content: Optional[str] = None
    url: Optional[str] = None


class WebPageOut(WebPageBase):
    id: str
    project_id: str
    source_file_path: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    chunk_count: int = 0

    model_config = {"from_attributes": True}


class HierarchyNode(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None
    page_count: int = 0
    folder_path: Optional[str] = None
    resolved_folder_path: Optional[str] = None
    children: List["HierarchyNode"] = []


class SearchRequest(BaseModel):
    question: str = Field(..., min_length=1)
    source_id: Optional[str] = None
    domain_id: Optional[str] = None
    project_id: Optional[str] = None


class Citation(BaseModel):
    index: int
    web_page_id: str
    title: str
    url: Optional[str]
    snippet: str
    source_name: str
    domain_name: str
    project_name: str
    updated_at: datetime


class SearchResponse(BaseModel):
    answer: str
    citations: List[Citation]
    confidence: str
    found_relevant: bool
    folder_paths: List[str] = []
    files_synced: int = 0


class FolderSyncResponse(BaseModel):
    project_id: str
    folder_path: Optional[str]
    files_found: int
    results: List[str]
    message: str


class FileUploadResponse(BaseModel):
    project_id: str
    folder_path: str
    filename: str
    result: str


class ScopeSyncSummary(BaseModel):
    folder_paths: List[str]
    projects_synced: int
    files_found: int
    details: List[Dict[str, object]]
