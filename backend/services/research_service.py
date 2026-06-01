from datetime import datetime, timezone
from sqlalchemy.orm import Session, joinedload
from backend.models.research_task import ResearchTask, Source, Finding
from backend.models.report import Report
from backend.models.database import SessionLocal
from backend.agents.research_agent import ResearchAgent
from backend.services.cache_service import CacheService


class ResearchService:
    def __init__(self):
        self.agent = ResearchAgent()
        self.cache = CacheService()

    def create_task(self, topic: str, depth: str = "medium") -> ResearchTask:
        db = SessionLocal()
        try:
            task = ResearchTask(topic=topic, depth=depth, status="pending")
            db.add(task)
            db.commit()
            db.refresh(task)

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

            except Exception as e:
                task.status = "failed"
                task.error = str(e)
                db.commit()

            db.refresh(task)
            return task
        finally:
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
