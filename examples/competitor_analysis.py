"""
Example: Perform competitor analysis using the autonomous research agent.
"""
from backend.agents.research_agent import ResearchAgent
from backend.tools.citation_manager import CitationManagerTool


def main():
    agent = ResearchAgent()
    citation_tool = CitationManagerTool()

    companies = ["OpenAI", "Google DeepMind", "Anthropic"]

    print("=" * 60)
    print("COMPETITOR ANALYSIS: AI Companies")
    print("=" * 60)

    all_reports = []

    for company in companies:
        print(f"\n--- Analyzing: {company} ---")
        result = agent.execute(f"{company} latest developments 2025", depth="shallow")

        all_reports.append({
            "company": company,
            "sources": len(result["sources"]),
            "findings": result["findings"][:3],
            "report": result["report"],
        })

        print(f"  Sources found: {len(result['sources'])}")
        print(f"  Key findings: {len(result['findings'])}")

    print("\n" + "=" * 60)
    print("COMPARISON SUMMARY")
    print("=" * 60)
    for r in all_reports:
        print(f"\n{r['company']}:")
        print(f"  Sources: {r['sources']}")
        print(f"  Top findings:")
        for f in r["findings"]:
            print(f"    - {f.get('claim', 'N/A')[:80]}")

    combined_citations = []
    for r in all_reports:
        for c in r["report"].get("citations", []):
            if c not in combined_citations:
                combined_citations.append(c)

    print(f"\nTotal unique citations: {len(combined_citations)}")
    for c in combined_citations[:5]:
        print(f"  - {c[:80]}...")


if __name__ == "__main__":
    main()
