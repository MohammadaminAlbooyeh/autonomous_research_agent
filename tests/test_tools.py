import unittest
from backend.tools.google_search import GoogleSearchTool
from backend.tools.web_scraper import WebScraperTool
from backend.tools.summarizer import SummarizerTool
from backend.tools.citation_manager import CitationManagerTool
from backend.tools.comparison_engine import ComparisonEngineTool
from backend.tools.document_parser import DocumentParserTool


class TestGoogleSearch(unittest.TestCase):
    def setUp(self):
        self.tool = GoogleSearchTool()

    def test_search_returns_results(self):
        results = self.tool.search("artificial intelligence")
        self.assertGreater(len(results), 0)
        self.assertIn("url", results[0])

    def test_mock_search_format(self):
        results = self.tool._mock_search("test query")
        for r in results:
            self.assertIn("url", r)
            self.assertIn("title", r)
            self.assertIn("snippet", r)


class TestWebScraper(unittest.TestCase):
    def setUp(self):
        self.tool = WebScraperTool()

    def test_scrape_invalid_url(self):
        result = self.tool.scrape("https://invalid.url.xyz")
        self.assertIn("url", result)
        self.assertIn("error", result)


class TestSummarizer(unittest.TestCase):
    def setUp(self):
        self.tool = SummarizerTool()

    def test_summarize_empty(self):
        self.assertEqual(self.tool.summarize(""), "")

    def test_extractive_summarize(self):
        text = "This is the first key sentence about research. This is the second important finding. This is the third significant result. This is the fourth point."
        summary = self.tool._extractive_summarize(text, 2)
        self.assertTrue(len(summary) > 0)

    def test_extract_key_points(self):
        text = "Key finding one is important. Significant result two is crucial. Important conclusion three is notable."
        points = self.tool.extract_key_points(text, 3)
        self.assertLessEqual(len(points), 3)


class TestCitationManager(unittest.TestCase):
    def setUp(self):
        self.tool = CitationManagerTool()

    def test_apa_citation(self):
        citation = self.tool.format_citation("https://example.com", "Test Title", "John Doe", "2024")
        self.assertIn("Test Title", citation)
        self.assertIn("John Doe", citation)
        self.assertIn("2024", citation)

    def test_format_citations_batch(self):
        sources = [{"url": "https://a.com", "title": "A"}, {"url": "https://b.com", "title": "B"}]
        citations = self.tool.format_citations(sources)
        self.assertEqual(len(citations), 2)


class TestComparisonEngine(unittest.TestCase):
    def setUp(self):
        self.tool = ComparisonEngineTool()

    def test_compare_empty(self):
        result = self.tool.compare_sources([])
        self.assertEqual(result["overlap_score"], 0.0)

    def test_compare_sources(self):
        sources = [
            {"content": "AI is transforming healthcare and education."},
            {"content": "AI is transforming healthcare and transportation."},
        ]
        result = self.tool.compare_sources(sources)
        self.assertGreater(result["overlap_score"], 0.0)

    def test_similarity(self):
        sim = self.tool.compute_similarity("hello world", "hello world")
        self.assertAlmostEqual(sim, 1.0)


class TestDocumentParser(unittest.TestCase):
    def setUp(self):
        self.tool = DocumentParserTool()

    def test_parse_empty(self):
        result = self.tool.parse_text("")
        self.assertEqual(result["word_count"], 0)

    def test_parse_text(self):
        text = "# Title\n\nFirst paragraph.\n\n## Section 1\n\nSection content."
        result = self.tool.parse_text(text)
        self.assertGreater(result["word_count"], 0)
        self.assertGreater(len(result["sections"]), 0)

    def test_extract_urls(self):
        text = "Visit https://example.com and http://test.org"
        urls = self.tool.extract_urls(text)
        self.assertEqual(len(urls), 2)

    def test_count_keywords(self):
        result = self.tool.count_keywords("AI and machine learning AI", ["ai", "machine"])
        self.assertEqual(result["ai"], 2)
        self.assertEqual(result["machine"], 1)


if __name__ == "__main__":
    unittest.main()
