from sqlalchemy.orm import Session
from db.models import FeedbackSource, Theme, Cluster, ThemeCluster, FeatureScore


def persist_analysis(db: Session, documents: list[dict], ranked_clusters: list[dict]) -> None:
    """
    Persists one full /analyze run into the database.

    documents: [{"id": "interview_01", "text": "...", "source_type": "interview"}, ...]
    ranked_clusters: the output of run_pipeline() — see cluster_themes.py / score_themes.py

    Walks the pipeline output and inserts, in dependency order:
    feedback_sources -> clusters -> themes -> theme_clusters -> feature_scores
    """
    # Step 1: insert feedback sources, build a map from the pipeline's string id
    # (e.g. "interview_01") to the real database integer id, so we can correctly
    # link themes back to their source below.
    source_id_map: dict[str, int] = {}

    for doc in documents:
        source = FeedbackSource(
            source_type=doc["source_type"],
            raw_text=doc["text"],
        )
        db.add(source)
        db.flush()  # assigns source.id immediately, without committing the transaction yet
        source_id_map[doc["id"]] = source.id

    # Step 2: for each ranked cluster, insert the cluster itself, its member
    # themes, the links between them, and its RICE score inputs.
    for cluster_data in ranked_clusters:
        cluster = Cluster(
            label=cluster_data["cluster_theme"],
            # Defensive cast: cluster_themes.py computes confidence from NumPy
            # cosine similarity, which produces np.float64 values. SQLAlchemy/
            # psycopg2 can't bind those directly into a query — casting to a
            # native Python float here guards against that even if the
            # pipeline's own cast is ever removed or missed upstream.
            confidence=float(cluster_data["confidence"]),
        )
        db.add(cluster)
        db.flush()

        for evidence in cluster_data["evidence"]:
            theme = Theme(
                source_id=source_id_map[evidence["source_id"]],
                theme_text=evidence["theme_text"],
                verified_quote=evidence["quote"],
                sentiment=evidence["sentiment"],
            )
            db.add(theme)
            db.flush()

            db.add(ThemeCluster(theme_id=theme.id, cluster_id=cluster.id))

        db.add(FeatureScore(
            cluster_id=cluster.id,
            frequency=cluster_data["mention_count"],
            source_diversity=cluster_data["source_count"],
            sentiment_weight=float(cluster_data["sentiment_weight"]),
        ))

    db.commit()