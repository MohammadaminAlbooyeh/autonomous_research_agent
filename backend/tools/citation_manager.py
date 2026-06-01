from datetime import datetime


class CitationManagerTool:
    def __init__(self, default_style: str = "apa"):
        self.default_style = default_style

    def format_citation(self, url: str, title: str = "", author: str = "", date: str = "", style: str = "") -> str:
        style = style or self.default_style
        title = title or "Untitled"
        today = datetime.now().strftime("%Y-%m-%d")

        if style == "apa":
            return self._apa(url, title, author, date, today)
        elif style == "mla":
            return self._mla(url, title, author, date, today)
        elif style == "chicago":
            return self._chicago(url, title, author, date, today)
        return self._apa(url, title, author, date, today)

    def _apa(self, url: str, title: str, author: str, date: str, today: str) -> str:
        author_part = f"{author}. " if author else ""
        date_part = f"({date}). " if date else "(n.d.). "
        return f"{author_part}{title}. {date_part}Retrieved {today}, from {url}"

    def _mla(self, url: str, title: str, author: str, date: str, today: str) -> str:
        author_part = f"{author}. " if author else ""
        return f'{author_part}"{title}." {date}. Web. {today}. &lt;{url}&gt;.'

    def _chicago(self, url: str, title: str, author: str, date: str, today: str) -> str:
        author_part = f"{author}. " if author else ""
        date_part = f". {date}" if date else ""
        return f'{author_part}"{title}"{date_part}. Accessed {today}. {url}.'

    def format_citations(self, sources: list[dict], style: str = "apa") -> list[str]:
        return [self.format_citation(s.get("url", ""), s.get("title", ""), s.get("author", ""), s.get("date", ""), style) for s in sources]
