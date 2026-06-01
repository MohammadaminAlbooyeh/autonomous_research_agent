"""
Example: Perform market research using the autonomous research agent.
"""
import json
from backend.agents.research_agent import ResearchAgent
from backend.tools.comparison_engine import ComparisonEngineTool


def main():
    agent = ResearchAgent()
    comparator = ComparisonEngineTool()

    topic = "Electric Vehicle Market 2025"
    print(f"Running market research on: {topic}")

    result = agent.execute(topic, depth="medium")

    print(f"\n=== MARKET RESEARCH REPORT ===")
    print(f"Topic: {result['topic']}")
    print(f"Sources Analyzed: {len(result['sources'])}")
    print(f"Key Findings: {len(result['findings'])}")

    print("\n--- Top Findings ---")
    for i, finding in enumerate(result["findings"][:5], 1):
        claim = finding.get("claim", "N/A")[:100]
        confidence = finding.get("confidence", 0)
        verification = finding.get("verification", {})
        verdict = verification.get("verdict", "unknown")
        print(f"{i}. [{verdict}] (confidence: {confidence:.2f}) {claim}...")

    print("\n--- Source Overlap Analysis ---")
    source_texts = [
        {"content": s.get("snippet", "")}
        for s in result["sources"]
        if s.get("snippet")
    ]
    if source_texts:
        comparison = comparator.compare_sources(source_texts)
        print(f"Overlap Score: {comparison['overlap_score']}")
        print(f"Agreements: {len(comparison['agreements'])}")
        print(f"Unique Insights: {len(comparison['unique_insights'])}")

    report = result["report"]
    print(f"\n--- Report Summary ---")
    print(f"Title: {report['title']}")
    print(f"Sections: {[s['heading'] for s in report['sections']]}")
    print(f"Citations: {len(report['citations'])}")

    with open("market_research_output.json", "w") as f:
        json.dump(result, f, indent=2, default=str)
    print("\nFull results saved to market_research_output.json")


if __name__ == "__main__":
    main()
