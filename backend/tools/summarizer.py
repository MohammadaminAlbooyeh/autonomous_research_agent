import os
from typing import Optional
from openai import OpenAI


class SummarizerTool:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def summarize(self, text: str, max_sentences: int = 5) -> str:
        if not text.strip():
            return ""

        if self.client:
            return self._llm_summarize(text, max_sentences)
        return self._extractive_summarize(text, max_sentences)

    def _llm_summarize(self, text: str, max_sentences: int) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": f"Summarize the following text in at most {max_sentences} sentences. Be concise and factual."},
                    {"role": "user", "content": text[:8000]},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            return resp.choices[0].message.content.strip()
        except Exception:
            return self._extractive_summarize(text, max_sentences)

    def _extractive_summarize(self, text: str, max_sentences: int) -> str:
        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip()]
        if not sentences:
            return text[:500]

        scored = []
        for s in sentences:
            score = len(s.split())
            if any(kw in s.lower() for kw in ["key", "important", "significant", "result", "conclusion", "finding"]):
                score *= 1.5
            scored.append((score, s))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = [s for _, s in scored[:max_sentences]]
        return ". ".join(top) + "." if top else sentences[0]

    def extract_key_points(self, text: str, max_points: int = 5) -> list[str]:
        if self.client:
            try:
                resp = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": f"Extract {max_points} key points from the text. Return as a numbered list."},
                        {"role": "user", "content": text[:8000]},
                    ],
                    temperature=0.3,
                    max_tokens=500,
                )
                content = resp.choices[0].message.content.strip()
                points = [p.strip() for p in content.split("\n") if p.strip()]
                return [p.lstrip("0123456789.)- ") for p in points if any(c.isdigit() for c in p[:3]) or not any(c.isdigit() for c in p[:3])][:max_points]
            except Exception:
                pass

        sentences = [s.strip() for s in text.replace("\n", " ").split(".") if s.strip() and len(s.strip()) > 30]
        return sentences[:max_points]
