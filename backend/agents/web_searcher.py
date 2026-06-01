from backend.tools.google_search import GoogleSearchTool
from backend.tools.web_scraper import WebScraperTool


class WebSearcherAgent:
    def __init__(self):
        self.search_tool = GoogleSearchTool()
        self.scraper_tool = WebScraperTool()

    def search(self, query: str, num_results: int = 10) -> list[dict]:
        return self.search_tool.search(query, num_results)

    def search_and_scrape(self, query: str, num_results: int = 5) -> list[dict]:
        results = self.search_tool.search(query, num_results)
        enriched = []
        for r in results:
            content = self.scraper_tool.scrape(r["url"])
            enriched.append({**r, "content": content.get("content", "")})
        return enriched

    def generate_queries(self, topic: str, depth: str = "medium") -> list[str]:
        depth_map = {"shallow": 2, "medium": 4, "deep": 8}
        n = depth_map.get(depth, 4)

        base_queries = [topic]
        perspectives = [
            f"latest developments in {topic}",
            f"{topic} challenges and solutions",
            f"{topic} future trends",
            f"{topic} analysis and review",
            f"{topic} research papers",
            f"{topic} industry applications",
            f"{topic} case studies",
            f"{topic} expert opinions",
        ]
        base_queries.extend(perspectives[:n - 1])
        return base_queries[:n]
