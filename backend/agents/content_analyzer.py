from backend.tools.summarizer import SummarizerTool
from backend.tools.comparison_engine import ComparisonEngineTool


class ContentAnalyzerAgent:
    def __init__(self):
        self.summarizer = SummarizerTool()
        self.comparison_engine = ComparisonEngineTool()

    def analyze_sources(self, sources: list[dict]) -> dict:
        findings = []
        for src in sources:
            if src.get("content"):
                summary = self.summarizer.summarize(src["content"])
                key_points = self.summarizer.extract_key_points(src["content"])
                findings.append({
                    "url": src.get("url", ""),
                    "title": src.get("title", ""),
                    "summary": summary,
                    "key_points": key_points,
                    "relevance": self._score_relevance(src.get("content", ""), src.get("query", "")),
                })
            else:
                findings.append({
                    "url": src.get("url", ""),
                    "title": src.get("title", ""),
                    "summary": src.get("snippet", ""),
                    "key_points": [],
                    "relevance": 0.0,
                })

        comparison = self.comparison_engine.compare_sources(sources)

        return {
            "source_analyses": findings,
            "comparison": comparison,
        }

    def _score_relevance(self, content: str, query: str) -> float:
        if not content or not query:
            return 0.0
        query_terms = set(query.lower().split())
        content_lower = content.lower()
        matches = sum(1 for term in query_terms if term in content_lower)
        return round(matches / len(query_terms), 2) if query_terms else 0.0
