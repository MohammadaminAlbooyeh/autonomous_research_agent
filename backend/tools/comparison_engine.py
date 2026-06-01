from collections import Counter
from difflib import SequenceMatcher


class ComparisonEngineTool:
    def compare_sources(self, sources: list[dict]) -> dict:
        if not sources:
            return {"agreements": [], "disagreements": [], "unique_insights": [], "overlap_score": 0.0}

        contents = [s.get("content", "") for s in sources if s.get("content")]
        if not contents:
            return {"agreements": [], "disagreements": [], "unique_insights": [], "overlap_score": 0.0}

        overlap_score = self._compute_overlap(contents)
        key_phrases = self._extract_common_phrases(contents)
        unique_points = self._find_unique_points(sources)

        return {
            "agreements": key_phrases[:5],
            "disagreements": [],
            "unique_insights": unique_points,
            "overlap_score": round(overlap_score, 2),
        }

    def _compute_overlap(self, contents: list[str]) -> float:
        if len(contents) < 2:
            return 0.0

        words_list = [set(c.lower().split()) for c in contents]
        common = words_list[0]
        for ws in words_list[1:]:
            common = common & ws

        all_words = set()
        for ws in words_list:
            all_words = all_words | ws

        if not all_words:
            return 0.0
        return len(common) / len(all_words)

    def _extract_common_phrases(self, contents: list[str], phrase_len: int = 3) -> list[str]:
        phrases = []
        for content in contents:
            words = content.lower().split()
            for i in range(len(words) - phrase_len + 1):
                phrases.append(" ".join(words[i:i + phrase_len]))

        counter = Counter(phrases)
        common = [p for p, count in counter.most_common(20) if count >= len(contents) * 0.5]
        return common[:10]

    def _find_unique_points(self, sources: list[dict]) -> list[str]:
        unique = []
        for i, src in enumerate(sources):
            content = src.get("content", "")
            if not content:
                continue
            sentences = [s.strip() for s in content.replace("\n", " ").split(".") if s.strip() and len(s.strip()) > 40]
            other_contents = [s.get("content", "") for j, s in enumerate(sources) if j != i and s.get("content")]

            for sent in sentences[:5]:
                if not other_contents:
                    unique.append(sent)
                    break
                is_unique = True
                for oc in other_contents:
                    if sent.lower() in oc.lower():
                        is_unique = False
                        break
                if is_unique:
                    unique.append(sent)
                    break
        return unique[:5]

    def compute_similarity(self, text1: str, text2: str) -> float:
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
