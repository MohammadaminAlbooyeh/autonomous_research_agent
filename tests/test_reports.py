import unittest
from datetime import datetime, timezone
from backend.models.database import init_db, Base, engine
from backend.models.research_task import ResearchTask, Source, Finding
from backend.models.report import Report
from backend.services.report_service import ReportService
from backend.services.database_service import DatabaseService

init_db()


class TestReportModel(unittest.TestCase):
    def test_report_creation(self):
        report = Report(
            task_id="test-task",
            title="Test Report",
            executive_summary="Summary here",
            sections=[{"heading": "Intro", "content": "Content"}],
            citations=["Citation 1"],
        )
        self.assertEqual(report.title, "Test Report")
        self.assertEqual(len(report.sections), 1)
        self.assertEqual(len(report.citations), 1)

    def test_report_defaults(self):
        from backend.models.database import SessionLocal
        db = SessionLocal()
        report = Report(task_id="test-task")
        db.add(report)
        db.flush()
        self.assertIsNotNone(report.id)
        self.assertEqual(report.title, "")
        self.assertEqual(report.sections, [])
        db.rollback()
        db.close()


class TestResearchTaskModel(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        Base.metadata.create_all(bind=engine)

    def test_task_creation(self):
        task = ResearchTask(topic="AI Research", depth="deep")
        self.assertEqual(task.topic, "AI Research")
        self.assertEqual(task.depth, "deep")

    def test_source_creation(self):
        source = Source(task_id="test", url="https://example.com", title="Example")
        self.assertEqual(source.url, "https://example.com")

    def test_finding_creation(self):
        finding = Finding(task_id="test", claim="AI is important", confidence=0.95)
        self.assertEqual(finding.claim, "AI is important")
        self.assertEqual(finding.confidence, 0.95)


class TestReportService(unittest.TestCase):
    def setUp(self):
        self.service = ReportService()

    def test_get_nonexistent_report(self):
        report = self.service.get_report("nonexistent")
        self.assertIsNone(report)

    def test_export_markdown_format(self):
        report = Report(
            task_id="test",
            title="Test Report",
            executive_summary="Summary",
            sections=[{"heading": "Section 1", "content": "Content 1"}],
            citations=["Ref 1"],
        )
        from backend.models.database import SessionLocal
        db = SessionLocal()
        try:
            db.add(report)
            db.commit()
            markdown = self.service._to_markdown(report)
            self.assertIn("# Test Report", markdown)
            self.assertIn("## Executive Summary", markdown)
            self.assertIn("## References", markdown)
            db.delete(report)
            db.commit()
        finally:
            db.close()

    def test_export_text_format(self):
        report = Report(
            task_id="test",
            title="Test Report",
            executive_summary="Summary",
            sections=[{"heading": "Section 1", "content": "Content 1"}],
            citations=["Ref 1"],
        )
        text = self.service._to_text(report)
        self.assertIn("TEST REPORT", text.upper())


class TestDatabaseService(unittest.TestCase):
    def setUp(self):
        self.service = DatabaseService()

    def test_get_statistics(self):
        stats = self.service.get_statistics()
        self.assertIn("total_tasks", stats)
        self.assertIn("completed_tasks", stats)
        self.assertIn("total_sources", stats)
        self.assertIn("total_findings", stats)


if __name__ == "__main__":
    unittest.main()
