from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class ResearchRequest(BaseModel):
    topic: str
    depth: str = "medium"


class ResearchTaskResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    topic: str
    queries: list = []
    depth: str
    status: str
    progress: float = 0.0
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class SourceResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: str
    url: str
    title: str
    content_snippet: str
    relevance_score: float
    accessed_at: datetime


class FindingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    task_id: str
    claim: str
    evidence: str
    confidence: float
    source_urls: list = []


class ReportResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    task_id: str
    title: str
    executive_summary: str
    sections: list = []
    citations: list = []
    generated_at: datetime


class TaskDetailResponse(BaseModel):
    task: ResearchTaskResponse
    sources: list[SourceResponse] = []
    findings: list[FindingResponse] = []
    report: Optional[ReportResponse] = None


class StatisticsResponse(BaseModel):
    total_tasks: int
    completed_tasks: int
    failed_tasks: int
    total_sources: int
    total_findings: int


class UserToken(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str = "bearer"
