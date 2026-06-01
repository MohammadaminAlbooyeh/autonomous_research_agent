import re
from typing import Optional
import requests
from bs4 import BeautifulSoup


class WebScraperTool:
    def __init__(self, user_agent: Optional[str] = None):
        self.user_agent = user_agent or "Mozilla/5.0 (compatible; AutonomousResearchAgent/1.0)"
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.user_agent})

    def scrape(self, url: str, max_chars: int = 10000) -> dict:
        try:
            resp = self.session.get(url, timeout=20)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            for tag in soup(["script", "style", "nav", "footer", "header", "aside"]):
                tag.decompose()

            title = soup.title.string.strip() if soup.title and soup.title.string else ""

            body = soup.find("body")
            text = body.get_text(separator="\n", strip=True) if body else ""

            lines = [line.strip() for line in text.split("\n") if line.strip()]
            cleaned = "\n".join(lines)

            if len(cleaned) > max_chars:
                cleaned = cleaned[:max_chars] + "..."

            return {
                "url": url,
                "title": title,
                "content": cleaned,
                "word_count": len(cleaned.split()),
            }
        except requests.RequestException as e:
            return {"url": url, "title": "", "content": "", "word_count": 0, "error": str(e)}

    def scrape_batch(self, urls: list[str], max_chars: int = 5000) -> list[dict]:
        return [self.scrape(url, max_chars) for url in urls]
