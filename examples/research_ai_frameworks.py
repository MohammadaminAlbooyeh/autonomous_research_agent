"""
Example: Research AI frameworks using the autonomous research agent via the API.
"""
import requests
import time
import json

API_BASE = "http://localhost:8000/api/research"


def run_research(topic, depth="medium"):
    print(f"Starting research: '{topic}' (depth: {depth})")

    resp = requests.post(API_BASE, json={"topic": topic, "depth": depth})
    resp.raise_for_status()
    task = resp.json()
    task_id = task["id"]
    print(f"Task ID: {task_id}")

    while True:
        resp = requests.get(f"{API_BASE}/{task_id}")
        resp.raise_for_status()
        data = resp.json()
        status = data["task"]["status"]
        print(f"  Status: {status}")
        if status in ("completed", "failed"):
            break
        time.sleep(2)

    if status == "failed":
        print(f"Research failed: {data['task'].get('error', 'Unknown error')}")
        return None

    return data


def main():
    topics = [
        "PyTorch vs TensorFlow comparison 2025",
        "LangChain framework capabilities",
    ]

    for topic in topics:
        result = run_research(topic, "shallow")
        if result:
            report = result.get("report")
            if report:
                print(f"\n=== Report: {report['title']} ===")
                print(f"Sections: {len(report.get('sections', []))}")
                print(f"Citations: {len(report.get('citations', []))}")
                print(f"Sources: {len(result.get('sources', []))}")
            print("-" * 40)

    print("\nDone! Use the API or frontend to view full reports.")


if __name__ == "__main__":
    main()
