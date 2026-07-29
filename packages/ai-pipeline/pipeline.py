"""
The full AI/ML pipeline, chained together:
documents -> extract themes -> verify (guardrail) -> cluster -> rank

This is the single entry point the API (and eventually the frontend) calls.
Each step was built and tested independently — this file just wires them
together in sequence.
"""

from extract_themes import extract_themes_from_documents
from cluster_themes import cluster_themes
from score_themes import rank_clusters


def run_pipeline(documents: list[dict]) -> list[dict]:
    """
    documents: [{"id": "doc1", "text": "..."}, ...]
    returns: a ranked list of feature clusters, each with evidence and a priority score
    """
    print(f"Step 1/3: Extracting themes from {len(documents)} document(s)...")
    themes = extract_themes_from_documents(documents)
    print(f"  -> {len(themes)} verified theme(s) extracted")

    print("Step 2/3: Clustering similar themes...")
    clusters = cluster_themes(themes)
    print(f"  -> {len(clusters)} distinct cluster(s) formed")

    print("Step 3/3: Scoring and ranking...")
    ranked = rank_clusters(clusters)
    print("  -> Done")

    return ranked


if __name__ == "__main__":
    sample_documents = [
        {
            "id": "interview_01",
            "text": """
            I really wish the app had dark mode. Also, every time I try to export my data
            to CSV, it takes forever and sometimes just fails silently. The onboarding
            flow was actually pretty smooth though, no complaints there.
            """
        },
        {
            "id": "feedback_ticket_045",
            "text": """
            Please add dark mode!! My eyes hurt using this app at night.
            Also the search feature is way too slow when I have a lot of items.
            """
        },
    ]

    import json
    result = run_pipeline(sample_documents)
    print("\n--- FINAL RANKED OUTPUT ---")
    print(json.dumps(result, indent=2))