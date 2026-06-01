from typing import Optional
from sqlalchemy.orm import Session
from backend.models.database import SessionLocal
from backend.models.research_task import ResearchTask
from backend.models.report import Report
from backend.models.research_task import Source, Finding


class DatabaseService:
    def cleanup_old_tasks(self, days: int = 30):
        from datetime import datetime, timedelta, timezone
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        db = SessionLocal()
        try:
            old = db.query(ResearchTask).filter(ResearchTask.created_at < cutoff).all()
            for task in old:
                db.delete(task)
            db.commit()
            return len(old)
        finally:
            db.close()

    def get_statistics(self) -> dict:
        db = SessionLocal()
        try:
            total_tasks = db.query(ResearchTask).count()
            completed = db.query(ResearchTask).filter(ResearchTask.status == "completed").count()
            failed = db.query(ResearchTask).filter(ResearchTask.status == "failed").count()
            total_sources = db.query(Source).count()
            total_findings = db.query(Finding).count()
            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed,
                "failed_tasks": failed,
                "total_sources": total_sources,
                "total_findings": total_findings,
            }
        finally:
            db.close()
