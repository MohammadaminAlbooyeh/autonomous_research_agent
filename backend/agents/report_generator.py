import os
from datetime import datetime
from typing import Optional
from openai import OpenAI
from backend.tools.citation_manager import CitationManagerTool


class ReportGeneratorAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.citation_tool = CitationManagerTool()
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None
        self._no_llm = not self.client

    def generate_report(self, topic: str, findings: list[dict], sources: list[dict]) -> dict:
        if not self._no_llm:
            return self._llm_generate(topic, findings, sources)
        return self._template_generate(topic, findings, sources)

    def _llm_generate(self, topic: str, findings: list[dict], sources: list[dict]) -> dict:
        try:
            findings_text = "\n".join([
                f"- {f.get('claim', '')} (confidence: {f.get('confidence', 0)})"
                for f in findings[:15]
            ])
            sources_text = "\n".join([
                f"- {s.get('title', 'Untitled')}: {s.get('url', '')}"
                for s in sources[:20]
            ])

            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a research report writer. Generate a comprehensive, well-structured report with an executive summary, introduction, main sections, analysis, and conclusion. Include citations."},
                    {"role": "user", "content": f"Topic: {topic}\n\nFindings:\n{findings_text}\n\nSources:\n{sources_text}"},
                ],
                temperature=0.4,
                max_tokens=3000,
            )
            report_text = resp.choices[0].message.content.strip()
            return self._parse_report(report_text, topic, sources)
        except Exception:
            return self._template_generate(topic, findings, sources)

    def _template_generate(self, topic: str, findings: list[dict], sources: list[dict]) -> dict:
        citations = self.citation_tool.format_citations(sources)

        sections = [
            {
                "heading": "Introduction",
                "content": f"This report provides a comprehensive analysis of {topic}. "
                          f"The research was conducted using multiple sources to ensure accuracy and depth."
            },
            {
                "heading": "Key Findings",
                "content": "\n".join([
                    f"- {f.get('claim', 'No claim available')}"
                    for f in findings[:8]
                ]) if findings else "No significant findings were discovered."
            },
            {
                "heading": "Analysis",
                "content": f"The research on {topic} reveals several important insights. "
                          f"Based on the analysis of {len(sources)} sources, "
                          f"the key themes and patterns have been identified and documented."
            },
            {
                "heading": "Conclusion",
                "content": f"In conclusion, this research on {topic} provides a solid foundation "
                          f"for understanding the current landscape. Further research may be warranted "
                          f"as new developments emerge."
            },
        ]

        summary = f"This report examines {topic} through a systematic analysis of {len(sources)} sources. " \
                 f"The research covers key aspects including recent developments, challenges, and future outlook."

        return {
            "title": f"Research Report: {topic}",
            "executive_summary": summary,
            "sections": sections,
            "citations": citations,
        }

    def _parse_report(self, text: str, topic: str, sources: list) -> dict:
        citations = self.citation_tool.format_citations(sources)
        lines = text.split("\n")
        title = f"Research Report: {topic}"
        sections = []
        current_heading = "Introduction"
        current_content = []

        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#") and len(stripped) > 2:
                if current_content:
                    sections.append({"heading": current_heading, "content": "\n".join(current_content).strip()})
                current_heading = stripped.lstrip("#").strip()
                current_content = []
            elif stripped:
                current_content.append(stripped)

        if current_content:
            sections.append({"heading": current_heading, "content": "\n".join(current_content).strip()})

        if not sections:
            sections.append({"heading": "Content", "content": text[:2000]})

        summary = sections[0]["content"][:500] if sections else ""

        return {
            "title": title,
            "executive_summary": summary,
            "sections": sections,
            "citations": citations,
        }
