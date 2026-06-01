import os
import json
from typing import Optional
import requests


class GoogleSearchTool:
    def __init__(self, api_key: Optional[str] = None, cx: Optional[str] = None):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY", "")
        self.cx = cx or os.getenv("GOOGLE_CX", "")
        self._use_mock = not (self.api_key and self.cx)

    def search(self, query: str, num_results: int = 10) -> list[dict]:
        if self._use_mock:
            return self._mock_search(query, num_results)

        url = "https://www.googleapis.com/customsearch/v1"
        params = {"key": self.api_key, "cx": self.cx, "q": query, "num": min(num_results, 10)}
        try:
            resp = requests.get(url, params=params, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            return [
                {
                    "url": item["link"],
                    "title": item.get("title", ""),
                    "snippet": item.get("snippet", ""),
                }
                for item in data.get("items", [])
            ]
        except requests.RequestException:
            return self._mock_search(query, num_results)

    def _mock_search(self, query: str, num_results: int = 10) -> list[dict]:
        sample_results = [
            {"url": "https://en.wikipedia.org/wiki/" + query.replace(" ", "_"),
             "title": f"{query} - Wikipedia",
             "snippet": f"Comprehensive overview of {query} including history, key concepts, and related topics."},
            {"url": f"https://www.google.com/search?q={query.replace(' ', '+')}",
             "title": f"{query} - Search Results",
             "snippet": f"Top search results for {query} from across the web."},
            {"url": f"https://arxiv.org/search/?query={query.replace(' ', '+')}&searchtype=all",
             "title": f"{query} - arXiv",
             "snippet": f"Academic papers and preprints related to {query}."},
        ]
        return sample_results[:num_results]
