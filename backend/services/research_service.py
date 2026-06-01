import asyncio
import time
from sqlalchemy.orm import Session, joinedload
from backend.models.research_task import ResearchTask, Source, Finding
from backend.models.report import Report
from backend.models.database import SessionLocal
from backend.agents.research_agent import ResearchAgent
from backend.services.cache_service import CacheService
from backend.analytics import get_analytics
from backend.monitoring import record_research_task, set_active_tasks
from backend.webhooks import get_webhook_manager, WebhookEventType


class ResearchService:
    def __init__(self):
        self.agent = ResearchAgent()
        self.cache = CacheService()

    def create_task(self, topic: str, depth: str = "medium") -> ResearchTask:
        db = SessionLocal()
        analytics = get_analytics()
        started_at = time.time()
        try:
            task = ResearchTask(topic=topic, depth=depth, status="pending")
            db.add(task)
            db.commit()
            db.refresh(task)
            analytics.record_task_started(task.id, "system", topic, depth)
            set_active_tasks(1)
            self._dispatch_webhook_event(WebhookEventType.RESEARCH_STARTED.value, {
                "task_id": task.id,
                "topic": topic,
                "depth": depth,
                "status": "in_progress",
            })

            task.status = "in_progress"
            db.commit()

            try:
                result = self.agent.execute(topic, depth)

                for s in result.get("sources", []):
                    source = Source(
                        task_id=task.id,
                        url=s.get("url", ""),
                        title=s.get("title", ""),
                        content_snippet=s.get("snippet", "")[:500],
                        relevance_score=s.get("relevance_score", 0.0),
                    )
                    db.add(source)

                for f in result.get("findings", []):
                    finding = Finding(
                        task_id=task.id,
                        claim=f.get("claim", ""),
                        evidence=f.get("evidence", "")[:1000],
                        confidence=f.get("confidence", 0.0),
                        source_urls=f.get("source_urls", []),
                    )
                    db.add(finding)

                report_data = result.get("report", {})
                report = Report(
                    task_id=task.id,
                    title=report_data.get("title", f"Report: {topic}"),
                    executive_summary=report_data.get("executive_summary", ""),
                    sections=report_data.get("sections", []),
                    citations=report_data.get("citations", []),
                )
                db.add(report)

                task.status = "completed"
                task.progress = 1.0
                task.queries = result.get("queries", [])
                db.commit()
                duration = time.time() - started_at
                analytics.record_task_completed(task.id, len(result.get("findings", [])), len(result.get("sources", [])))
                record_research_task("completed", duration, len(result.get("sources", [])), len(result.get("findings", [])))
                self._dispatch_webhook_event(WebhookEventType.RESEARCH_COMPLETED.value, {
                    "task_id": task.id,
                    "topic": topic,
                    "status": "completed",
                    "findings_count": len(result.get("findings", [])),
                    "sources_count": len(result.get("sources", [])),
                })

            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                db.commit()
                duration = time.time() - started_at
                analytics.record_task_failed(task.id, str(e))
                record_research_task("failed", duration, 0, 0)
                self._dispatch_webhook_event(WebhookEventType.RESEARCH_FAILED.value, {
                    "task_id": task.id,
                    "topic": topic,
                    "status": "failed",
                    "error": str(e),
                })

            db.refresh(task)
            return task
        finally:
            set_active_tasks(0)
            db.close()

    def get_task(self, task_id: str) -> ResearchTask:
        db = SessionLocal()
        try:
            return (
                db.query(ResearchTask)
                .options(
                    joinedload(ResearchTask.sources),
                    joinedload(ResearchTask.findings),
                    joinedload(ResearchTask.report),
                )
                .filter(ResearchTask.id == task_id)
                .first()
            )
        finally:
            db.close()

    def list_tasks(self, skip: int = 0, limit: int = 50) -> list[ResearchTask]:
        db = SessionLocal()
        try:
            return (
                db.query(ResearchTask)
                .order_by(ResearchTask.created_at.desc())
                .offset(skip)
                .limit(limit)
                .all()
            )
        finally:
            db.close()

    def delete_task(self, task_id: str) -> bool:
        db = SessionLocal()
        try:
            task = db.query(ResearchTask).filter(ResearchTask.id == task_id).first()
            if task:
                db.delete(task)
                db.commit()
                return True
            return False
        finally:
            db.close()

    def _dispatch_webhook_event(self, event_type: str, data: dict) -> None:
        manager = get_webhook_manager()
        try:
            asyncio.run(manager.trigger_event(event_type, data))
        except RuntimeError:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(manager.trigger_event(event_type, data))
            else:
                loop.run_until_complete(manager.trigger_event(event_type, data))
