# Fixed sentiment weights — how urgent each sentiment type is treated as a signal.
# Negative feedback (pain points) weighted highest since it's the strongest
# signal for "this needs fixing." This is intentionally FIXED, not user-configurable,
# per the PRD decision to avoid premature flexibility before the rubric is validated.
SENTIMENT_WEIGHTS = {
    "negative": 1.0,
    "neutral": 0.6,
    "positive": 0.4,
}


def score_cluster(cluster: dict) -> float:
    """
    Computes a single priority score for a cluster of similar themes.

    score = mention_count * source_count * avg_sentiment_weight

    - mention_count: raw frequency signal
    - source_count: rewards patterns seen across MULTIPLE sources, not just
      repeated within one document (this is what makes it "evidence-backed"
      rather than just "loud")
    - avg_sentiment_weight: how urgent the feedback tone is, on average,
      across all mentions in this cluster
    """
    mention_count = cluster["mention_count"]
    source_count = cluster["source_count"]

    sentiments = [e.get("sentiment", "neutral") for e in cluster.get("evidence", [])]
    if not sentiments:
        avg_sentiment_weight = SENTIMENT_WEIGHTS["neutral"]
    else:
        avg_sentiment_weight = sum(
            SENTIMENT_WEIGHTS.get(s, SENTIMENT_WEIGHTS["neutral"]) for s in sentiments
        ) / len(sentiments)

    return round(mention_count * source_count * avg_sentiment_weight, 2)


def rank_clusters(clusters: list[dict]) -> list[dict]:
    """
    Takes clusters (from cluster_themes.py) and returns them sorted by
    priority score, highest first — this is the actual ranked feature
    list a PM would look at.
    """
    for cluster in clusters:
        cluster["priority_score"] = score_cluster(cluster)

    return sorted(clusters, key=lambda c: c["priority_score"], reverse=True)


if __name__ == "__main__":
    # Simulating output from cluster_themes.py, with sentiment added to evidence
    sample_clusters = [
        {
            "cluster_theme": "Dark mode support",
            "mention_count": 2,
            "source_count": 2,
            "evidence": [
                {"quote": "I really wish the app had dark mode.", "source_id": "interview_01", "sentiment": "negative"},
                {"quote": "Please add dark mode!! My eyes hurt using this app at night.", "source_id": "feedback_ticket_045", "sentiment": "negative"},
            ],
        },
        {
            "cluster_theme": "CSV export reliability",
            "mention_count": 1,
            "source_count": 1,
            "evidence": [
                {"quote": "every time I try to export my data to CSV, it takes forever and sometimes just fails silently.", "source_id": "interview_01", "sentiment": "negative"},
            ],
        },
        {
            "cluster_theme": "Search performance",
            "mention_count": 1,
            "source_count": 1,
            "evidence": [
                {"quote": "the search feature is way too slow when I have a lot of items.", "source_id": "feedback_ticket_045", "sentiment": "negative"},
            ],
        },
    ]

    ranked = rank_clusters(sample_clusters)

    print("RANKED FEATURE LIST\n")
    for i, cluster in enumerate(ranked, start=1):
        print(f"{i}. {cluster['cluster_theme']}  —  score: {cluster['priority_score']}")
        print(f"   Mentioned {cluster['mention_count']}x across {cluster['source_count']} source(s)")