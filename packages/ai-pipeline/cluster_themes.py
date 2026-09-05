import os
import numpy as np
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv(dotenv_path="../../apps/api/.env")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

EMBEDDING_MODEL = "models/gemini-embedding-001"

# How similar two themes must be (0 to 1) to count as "the same feature."
# Higher = stricter (fewer, more precise merges). Lower = looser (more merges,
# risk of grouping unrelated things together). 0.80 is a reasonable starting point.
SIMILARITY_THRESHOLD = 0.80


def get_embedding(text: str) -> np.ndarray:
    """Convert a piece of text into a vector (list of numbers) representing its meaning."""
    result = genai.embed_content(model=EMBEDDING_MODEL, content=text)
    return np.array(result["embedding"])


def cosine_similarity(vec_a: np.ndarray, vec_b: np.ndarray) -> float:
    """
    Measures how similar two vectors are, from -1 (opposite) to 1 (identical).
    This is the standard way to compare embeddings.
    """
    return np.dot(vec_a, vec_b) / (np.linalg.norm(vec_a) * np.linalg.norm(vec_b))


def cluster_themes(themes: list[dict]) -> list[dict]:
    """
    Groups semantically similar themes together across multiple documents.

    Uses a simple GREEDY clustering approach (not a heavy ML library like
    scikit-learn's KMeans) — deliberately simple because:
    1. We don't know the number of clusters in advance (KMeans needs that)
    2. At MVP scale (dozens, not millions, of themes), greedy is fast enough
    3. It's easy to explain and debug — important while this is still new code

    How it works: go through each theme one at a time. Compare it to every
    existing cluster's "representative" theme. If similar enough, merge in.
    If not similar to anything existing, start a new cluster.

    Each cluster also tracks the similarity score of every member that joined
    it, so we can report a confidence value (average similarity) once the
    cluster is finalized — this feeds the `clusters.confidence` column.
    """
    clusters = []  # each cluster: {"representative_text", "embedding", "members", "similarity_scores"}

    for theme in themes:
        theme_text = theme["theme"]
        embedding = get_embedding(theme_text)

        best_cluster = None
        best_score = 0.0

        for cluster in clusters:
            score = cosine_similarity(embedding, cluster["embedding"])
            if score > best_score:
                best_score = score
                best_cluster = cluster

        if best_cluster and best_score >= SIMILARITY_THRESHOLD:
            best_cluster["members"].append(theme)
            best_cluster["similarity_scores"].append(best_score)
        else:
            clusters.append({
                "representative_text": theme_text,
                "embedding": embedding,
                "members": [theme],
                # the seed theme defines the cluster, so it's treated as a
                # perfect match to itself for the purposes of confidence
                "similarity_scores": [1.0],
            })

    # Build a clean summary for each cluster, ready for scoring/display later
    summarized = []
    for cluster in clusters:
        members = cluster["members"]
        source_ids = list(set(m["source_id"] for m in members))

        # NumPy's cosine_similarity() returns np.float64 values, not native
        # Python floats. SQLAlchemy/psycopg2 can't bind np.float64 directly
        # into a SQL query — it silently stringifies it as "np.float64(...)",
        # which Postgres then tries (and fails) to parse. Casting to float()
        # here converts it to a plain Python float before it ever reaches
        # the database layer.
        confidence = float(round(
            sum(cluster["similarity_scores"]) / len(cluster["similarity_scores"]), 4
        ))

        summarized.append({
            "cluster_theme": cluster["representative_text"],
            "mention_count": len(members),
            "source_count": len(source_ids),
            "source_ids": source_ids,
            "confidence": confidence,
            "evidence": [
                {
                    "theme_text": m["theme"],
                    "quote": m["evidence_quote"],
                    "source_id": m["source_id"],
                    "sentiment": m.get("sentiment", "neutral"),
                }
                for m in members
            ],
        })

    return summarized


if __name__ == "__main__":
    # Simulating output that would come from extract_themes_from_documents()
    sample_themes = [
        {"theme": "Dark mode support", "evidence_quote": "I really wish the app had dark mode.", "source_id": "interview_01", "sentiment": "negative"},
        {"theme": "Dark mode request", "evidence_quote": "Please add dark mode!! My eyes hurt using this app at night.", "source_id": "feedback_ticket_045", "sentiment": "negative"},
        {"theme": "CSV export reliability", "evidence_quote": "every time I try to export my data to CSV, it takes forever and sometimes just fails silently.", "source_id": "interview_01", "sentiment": "negative"},
        {"theme": "Search performance", "evidence_quote": "the search feature is way too slow when I have a lot of items.", "source_id": "feedback_ticket_045", "sentiment": "negative"},
    ]

    clusters = cluster_themes(sample_themes)

    for c in clusters:
        print(f"\nCLUSTER: {c['cluster_theme']}  (confidence: {c['confidence']})")
        print(f"  Mentioned {c['mention_count']} time(s) across {c['source_count']} source(s): {c['source_ids']}")
        for e in c["evidence"]:
            print(f"    - [{e['source_id']}] \"{e['theme_text']}\" — \"{e['quote']}\"")