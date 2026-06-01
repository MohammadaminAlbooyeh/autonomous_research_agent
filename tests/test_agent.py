import unittest
from backend.agents.web_searcher import WebSearcherAgent
from backend.agents.content_analyzer import ContentAnalyzerAgent
from backend.agents.fact_checker import FactCheckerAgent
from backend.agents.report_generator import ReportGeneratorAgent
from backend.agents.research_agent import ResearchAgent


class TestWebSearcherAgent(unittest.TestCase):
    def setUp(self):
        self.agent = WebSearcherAgent()

    def test_search(self):
        results = self.agent.search("test query")
        self.assertGreater(len(results), 0)

    def test_generate_queries(self):
        queries = self.agent.generate_queries("AI", "shallow")
        self.assertEqual(len(queries), 2)

        queries = self.agent.generate_queries("AI", "deep")
        self.assertEqual(len(queries), 8)


class TestContentAnalyzerAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ContentAnalyzerAgent()

    def test_analyze_empty(self):
        result = self.agent.analyze_sources([])
        self.assertEqual(len(result["source_analyses"]), 0)

    def test_analyze_sources(self):
        sources = [{"url": "https://example.com", "title": "Test", "content": "AI is transforming the world of technology and research."}]
        result = self.agent.analyze_sources(sources)
        self.assertEqual(len(result["source_analyses"]), 1)
        self.assertIn("comparison", result)

    def test_score_relevance(self):
        score = self.agent._score_relevance("AI is about artificial intelligence", "artificial intelligence")
        self.assertGreater(score, 0.0)


class TestFactCheckerAgent(unittest.TestCase):
    def setUp(self):
        self.agent = FactCheckerAgent()

    def test_verify_no_sources(self):
        result = self.agent.verify_claim("test claim", [])
        self.assertEqual(result["verdict"], "unverifiable")

    def test_heuristic_verify(self):
        result = self.agent._heuristic_verify("AI is important", ["AI is very important for future", "AI matters a lot"])
        self.assertIn(result["verdict"], ["supported", "contradicted", "unverifiable"])


class TestReportGeneratorAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ReportGeneratorAgent()

    def test_template_generate(self):
        findings = [{"claim": "AI is growing", "confidence": 0.9}]
        sources = [{"url": "https://example.com", "title": "Test Source"}]
        report = self.agent._template_generate("AI Growth", findings, sources)
        self.assertIn("title", report)
        self.assertIn("sections", report)
        self.assertIn("citations", report)

    def test_generate_report(self):
        findings = [{"claim": "AI is transforming healthcare", "confidence": 0.8}]
        sources = [{"url": "https://example.com", "title": "AI Healthcare"}]
        report = self.agent.generate_report("AI in Healthcare", findings, sources)
        self.assertGreater(len(report["sections"]), 0)


class TestResearchAgent(unittest.TestCase):
    def setUp(self):
        self.agent = ResearchAgent()

    def test_execute(self):
        result = self.agent.execute("test topic", "shallow")
        self.assertIn("topic", result)
        self.assertIn("sources", result)
        self.assertIn("analysis", result)
        self.assertIn("findings", result)
        self.assertIn("report", result)
        self.assertEqual(result["topic"], "test topic")


if __name__ == "__main__":
    unittest.main()
