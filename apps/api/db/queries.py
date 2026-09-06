from sqlalchemy import func, cast, Date
from sqlalchemy.orm import Session
from db.models import FeedbackSource, Theme, Cluster, FeatureScore


def get_dashboard_stats(db: Session) -> dict:
    """
    Aggregates everything Command Center needs into one payload:
    - top-line counts (sources, features, themes, avg confidence)
    - a day-by-day sentiment trend (for the chart)
    - a top-5 ranked feature preview (for the list)
    """
    total_sources = db.query(FeedbackSource).count()
    total_features = db.query(Cluster).count()
    total_themes = db.query(Theme).count()

    avg_confidence = db.query(func.avg(Cluster.confidence)).scalar()
    avg_confidence = round(float(avg_confidence), 2) if avg_confidence is not None else 0.0

    # Sentiment trend: count of themes per day, split by sentiment.
    # Grouped in SQL rather than Python since Postgres does this far more
    # efficiently than pulling every row and counting client-side.
    sentiment_rows = (
        db.query(
            cast(Theme.created_at, Date).label("date"),
            Theme.sentiment,
            func.count(Theme.id).label("count"),
        )
        .group_by("date", Theme.sentiment)
        .order_by("date")
        .all()
    )

    # Reshape from flat rows into one entry per date, e.g.:
    # {"date": "2026-09-05", "positive": 1, "negative": 3, "neutral": 0}
    trend_by_date: dict[str, dict] = {}
    for row in sentiment_rows:
        date_str = row.date.isoformat()
        if date_str not in trend_by_date:
            trend_by_date[date_str] = {"date": date_str, "positive": 0, "negative": 0, "neutral": 0}
        trend_by_date[date_str][row.sentiment] = row.count

    sentiment_trend = sorted(trend_by_date.values(), key=lambda r: r["date"])

    # Top 5 features by RICE score, for the preview list.
    top_features = (
        db.query(Cluster.label, FeatureScore.rice_score)
        .join(FeatureScore, FeatureScore.cluster_id == Cluster.id)
        .order_by(FeatureScore.rice_score.desc())
        .limit(5)
        .all()
    )

    top_features_list = [
        {"label": label, "rice_score": round(float(score), 2) if score is not None else 0.0}
        for label, score in top_features
    ]

    return {
        "total_sources": total_sources,
        "total_features": total_features,
        "total_themes": total_themes,
        "avg_confidence": avg_confidence,
        "sentiment_trend": sentiment_trend,
        "top_features": top_features_list,
    }