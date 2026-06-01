import re
from typing import Optional


class DocumentParserTool:
    def parse_text(self, text: str) -> dict:
        if not text:
            return {"title": "", "sections": [], "word_count": 0, "paragraphs": []}

        lines = text.split("\n")
        title = lines[0].strip() if lines else ""
        if title.startswith("#"):
            title = title.lstrip("#").strip()

        paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        sections = self._extract_sections(text)

        return {
            "title": title,
            "sections": sections,
            "word_count": len(text.split()),
            "paragraphs": paragraphs,
        }

    def _extract_sections(self, text: str) -> list[dict]:
        sections = []
        lines = text.split("\n")
        current_heading = "Introduction"
        current_content = []

        for line in lines:
            stripped = line.strip()
            if re.match(r"^#{1,3}\s", stripped):
                if current_content:
                    sections.append({
                        "heading": current_heading,
                        "content": "\n".join(current_content).strip(),
                    })
                current_heading = re.sub(r"^#+\s*", "", stripped)
                current_content = []
            else:
                current_content.append(stripped)

        if current_content:
            sections.append({
                "heading": current_heading,
                "content": "\n".join(current_content).strip(),
            })

        return sections

    def extract_emails(self, text: str) -> list[str]:
        return re.findall(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", text)

    def extract_urls(self, text: str) -> list[str]:
        return re.findall(r"https?://[^\s<>\"']+", text)

    def count_keywords(self, text: str, keywords: list[str]) -> dict[str, int]:
        text_lower = text.lower()
        return {kw: text_lower.count(kw.lower()) for kw in keywords}
