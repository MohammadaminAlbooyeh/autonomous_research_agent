from concurrent.futures import ThreadPoolExecutor, as_completed
from backend.agents.web_searcher import WebSearcherAgent
from backend.agents.content_analyzer import ContentAnalyzerAgent
from backend.agents.fact_checker import FactCheckerAgent
from backend.agents.report_generator import ReportGeneratorAgent


class ResearchAgent:
    def __init__(self):
        self.web_searcher = WebSearcherAgent()
        self.content_analyzer = ContentAnalyzerAgent()
        self.fact_checker = FactCheckerAgent()
        self.report_generator = ReportGeneratorAgent()

    def execute(self, topic: str, depth: str = "medium") -> dict:
        queries = self.web_searcher.generate_queries(topic, depth)

        all_sources = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = {executor.submit(self.web_searcher.search_and_scrape, q): q for q in queries}
            for future in as_completed(futures):
                try:
                    results = future.result()
                    for r in results:
                        r["query"] = futures[future]
                    all_sources.extend(results)
                except Exception:
                    pass

        analysis = self.content_analyzer.analyze_sources(all_sources)

        findings = []
        for src_analysis in analysis.get("source_analyses", []):
            key_points = src_analysis.get("key_points", [])
            for kp in key_points[:3]:
                findings.append({
                    "claim": kp,
                    "evidence": src_analysis.get("summary", ""),
                    "confidence": src_analysis.get("relevance", 0.0),
                    "source_urls": [src_analysis.get("url", "")],
                })

        source_texts = [s.get("content", "") for s in all_sources if s.get("content")]
        verified_findings = self.fact_checker.verify_findings(findings, source_texts)

        report = self.report_generator.generate_report(topic, verified_findings, all_sources)

        return {
            "topic": topic,
            "depth": depth,
            "queries": queries,
            "sources": [
                {
                    "url": s.get("url", ""),
                    "title": s.get("title", ""),
                    "snippet": s.get("snippet", s.get("content", "")[:200]),
                    "relevance_score": next(
                        (a.get("relevance", 0) for a in analysis.get("source_analyses", []) if a.get("url") == s.get("url")),
                        0.0,
                    ),
                }
                for s in all_sources
            ],
            "analysis": analysis,
            "findings": verified_findings,
            "report": report,
        }
