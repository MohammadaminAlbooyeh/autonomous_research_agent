from typing import Optional
from sqlalchemy.orm import Session
from backend.models.report import Report
from backend.models.database import SessionLocal


class ReportService:
    def get_report(self, report_id: str) -> Optional[Report]:
        db = SessionLocal()
        try:
            return db.query(Report).filter(Report.id == report_id).first()
        finally:
            db.close()

    def get_report_by_task(self, task_id: str) -> Optional[Report]:
        db = SessionLocal()
        try:
            return db.query(Report).filter(Report.task_id == task_id).first()
        finally:
            db.close()

    def export_report(self, report_id: str, format: str = "markdown") -> Optional[str]:
        report = self.get_report(report_id)
        if not report:
            return None

        if format == "markdown":
            return self._to_markdown(report)
        elif format == "text":
            return self._to_text(report)
        return self._to_markdown(report)

    def _to_markdown(self, report: Report) -> str:
        lines = [f"# {report.title}", "", "## Executive Summary", "", report.executive_summary, ""]
        for section in (report.sections or []):
            heading = section.get("heading", "Section")
            content = section.get("content", "")
            lines.append(f"## {heading}")
            lines.append("")
            lines.append(content)
            lines.append("")

        if report.citations:
            lines.append("## References")
            lines.append("")
            for c in report.citations:
                lines.append(f"- {c}")
            lines.append("")

        return "\n".join(lines)

    def _to_text(self, report: Report) -> str:
        lines = [report.title, "=" * len(report.title), "", "EXECUTIVE SUMMARY", report.executive_summary, ""]
        for section in (report.sections or []):
            heading = section.get("heading", "Section")
            content = section.get("content", "")
            lines.append(heading.upper())
            lines.append("-" * len(heading))
            lines.append(content)
            lines.append("")

        if report.citations:
            lines.append("REFERENCES")
            for c in report.citations:
                lines.append(f"  {c}")

        return "\n".join(lines)
