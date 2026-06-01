from fastapi import APIRouter, HTTPException, Depends, Request
from slowapi import Limiter
from slowapi.util import get_remote_address
from backend.api.schemas import (
    ResearchRequest,
    ResearchTaskResponse,
    TaskDetailResponse,
    SourceResponse,
    FindingResponse,
    ReportResponse,
    StatisticsResponse,
)
from backend.services.research_service import ResearchService
from backend.services.report_service import ReportService
from backend.services.database_service import DatabaseService
from backend.auth import get_current_user
from backend.logging_config import get_logger

router = APIRouter(prefix="/api/research", tags=["research"])
research_service = ResearchService()
report_service = ReportService()
database_service = DatabaseService()
limiter = Limiter(key_func=get_remote_address)
logger = get_logger(__name__)


@router.post("", response_model=ResearchTaskResponse)
@limiter.limit("5/minute")
def start_research(request: Request, req: ResearchRequest, current_user: str = Depends(get_current_user)):
    logger.info(f"User {current_user} starting research on topic: {req.topic}")
    if not req.topic.strip():
        raise HTTPException(status_code=400, detail="Topic is required")
    if req.depth not in ("shallow", "medium", "deep"):
        raise HTTPException(status_code=400, detail="Depth must be shallow, medium, or deep")
    task = research_service.create_task(req.topic, req.depth)
    logger.info(f"Research task created: {task.id}")
    return ResearchTaskResponse.model_validate(task)


@router.get("", response_model=list[ResearchTaskResponse])
@limiter.limit("10/minute")
def list_research(request: Request, skip: int = 0, limit: int = 50, current_user: str = Depends(get_current_user)):
    logger.info(f"User {current_user} listing research tasks (skip={skip}, limit={limit})")
    tasks = research_service.list_tasks(skip, limit)
    return [ResearchTaskResponse.model_validate(t) for t in tasks]


@router.get("/stats", response_model=StatisticsResponse)
@limiter.limit("10/minute")
def get_statistics(request: Request, current_user: str = Depends(get_current_user)):
    logger.info(f"User {current_user} requesting statistics")
    return database_service.get_statistics()


@router.get("/{task_id}", response_model=TaskDetailResponse)
@limiter.limit("10/minute")
def get_research(request: Request, task_id: str, current_user: str = Depends(get_current_user)):
    logger.info(f"User {current_user} retrieving research task: {task_id}")
    task = research_service.get_task(task_id)
    if not task:
        logger.warning(f"Research task not found: {task_id}")
        raise HTTPException(status_code=404, detail="Research task not found")

    sources = [SourceResponse.model_validate(s) for s in task.sources]
    findings = [FindingResponse.model_validate(f) for f in task.findings]
    report = ReportResponse.model_validate(task.report) if task.report else None

    return TaskDetailResponse(
        task=ResearchTaskResponse.model_validate(task),
        sources=sources,
        findings=findings,
        report=report,
    )


@router.delete("/{task_id}")
@limiter.limit("5/minute")
def delete_research(request: Request, task_id: str, current_user: str = Depends(get_current_user)):
    logger.info(f"User {current_user} deleting research task: {task_id}")
    deleted = research_service.delete_task(task_id)
    if not deleted:
        logger.warning(f"Research task not found for deletion: {task_id}")
        raise HTTPException(status_code=404, detail="Research task not found")
    logger.info(f"Research task deleted: {task_id}")
    return {"message": "Research task deleted"}


@router.get("/{task_id}/report", response_model=ReportResponse)
@limiter.limit("10/minute")
def get_report(request: Request, task_id: str, current_user: str = Depends(get_current_user)):
    logger.info(f"User {current_user} retrieving report for task: {task_id}")
    report = report_service.get_report_by_task(task_id)
    if not report:
        logger.warning(f"Report not found for task: {task_id}")
        raise HTTPException(status_code=404, detail="Report not found")
    return ReportResponse.model_validate(report)


@router.get("/{task_id}/report/export")
@limiter.limit("5/minute")
def export_report(request: Request, task_id: str, format: str = "markdown", current_user: str = Depends(get_current_user)):
    logger.info(f"User {current_user} exporting report for task {task_id} in {format} format")
    report = report_service.get_report_by_task(task_id)
    if not report:
        logger.warning(f"Report not found for export: {task_id}")
        raise HTTPException(status_code=404, detail="Report not found")
    content = report_service.export_report(report.id, format)
    if not content:
        logger.warning(f"Unsupported export format: {format}")
        raise HTTPException(status_code=400, detail="Unsupported format")
    logger.info(f"Report exported successfully for task: {task_id}")
    return {"content": content, "format": format}
