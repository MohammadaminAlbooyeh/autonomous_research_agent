"""
Example: Research current technology trends using the autonomous research agent.
"""
from backend.agents.research_agent import ResearchAgent


def main():
    agent = ResearchAgent()

    topics = [
        "Large Language Models in 2025",
        "Quantum Computing Breakthroughs",
        "Autonomous Vehicles Progress",
    ]

    for topic in topics:
        print(f"\n{'='*60}")
        print(f"RESEARCHING: {topic}")
        print(f"{'='*60}")

        result = agent.execute(topic, depth="shallow")

        print(f"\nQueries used: {len(result['queries'])}")
        print(f"Sources found: {len(result['sources'])}")
        print(f"Findings: {len(result['findings'])}")

        report = result["report"]
        print(f"\nReport Title: {report['title']}")
        print(f"Executive Summary: {report['executive_summary'][:200]}...")
        print(f"Sections: {len(report['sections'])}")
        print(f"Citations: {len(report['citations'])}")


if __name__ == "__main__":
    main()
