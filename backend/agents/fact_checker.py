import os
from typing import Optional
from openai import OpenAI


class FactCheckerAgent:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if api_key else None

    def verify_claim(self, claim: str, context_sources: list[str]) -> dict:
        if self.client and context_sources:
            return self._llm_verify(claim, context_sources)
        return self._heuristic_verify(claim, context_sources)

    def _llm_verify(self, claim: str, context_sources: list[str]) -> dict:
        try:
            context = "\n\n".join(context_sources[:5])[:6000]
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a fact-checker. Verify the claim against the provided sources. Respond with a JSON object: {\"verdict\": \"supported|contradicted|unverifiable\", \"confidence\": 0.0-1.0, \"explanation\": \"...\"}"},
                    {"role": "user", "content": f"Claim: {claim}\n\nSources:\n{context}"},
                ],
                temperature=0.2,
                response_format={"type": "json_object"},
            )
            import json
            return json.loads(resp.choices[0].message.content.strip())
        except Exception:
            return self._heuristic_verify(claim, context_sources)

    def _heuristic_verify(self, claim: str, context_sources: list[str]) -> dict:
        if not context_sources:
            return {"verdict": "unverifiable", "confidence": 0.0, "explanation": "No sources provided to verify against."}

        claim_terms = set(claim.lower().split())
        supporting_count = 0

        for src in context_sources:
            src_lower = src.lower()
            matches = sum(1 for term in claim_terms if term in src_lower)
            if matches > len(claim_terms) * 0.3:
                supporting_count += 1

        ratio = supporting_count / len(context_sources)
        if ratio > 0.6:
            return {"verdict": "supported", "confidence": round(ratio, 2), "explanation": f"Claim is supported by {supporting_count} of {len(context_sources)} sources."}
        elif ratio > 0.2:
            return {"verdict": "unverifiable", "confidence": round(ratio, 2), "explanation": f"Claim has partial support from {supporting_count} of {len(context_sources)} sources."}
        else:
            return {"verdict": "contradicted", "confidence": round(1 - ratio, 2), "explanation": f"Claim lacks support across {len(context_sources)} sources."}

    def verify_findings(self, findings: list[dict], source_texts: list[str]) -> list[dict]:
        verified = []
        for finding in findings:
            result = self.verify_claim(finding.get("claim", ""), source_texts)
            verified.append({**finding, "verification": result})
        return verified
