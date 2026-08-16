from sqlalchemy import (
    Column, Integer, Text, Float, String,
    ForeignKey, TIMESTAMP, Computed, func
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from db.base import Base


class FeedbackSource(Base):
    __tablename__ = "feedback_sources"

    id = Column(Integer, primary_key=True)
    source_type = Column(String, nullable=False)   # "interview" | "feedback" | "analytics"
    raw_text = Column(Text, nullable=False)
    meta = Column(JSONB, nullable=True)             # filename, upload timestamp, original format
    created_at = Column(TIMESTAMP, server_default=func.now())

    themes = relationship("Theme", back_populates="source", cascade="all, delete-orphan")


class Theme(Base):
    __tablename__ = "themes"

    id = Column(Integer, primary_key=True)
    source_id = Column(Integer, ForeignKey("feedback_sources.id", ondelete="CASCADE"), nullable=False)
    theme_text = Column(Text, nullable=False)        # the extracted theme
    verified_quote = Column(Text, nullable=True)     # guardrail-verified substring
    sentiment = Column(String, nullable=False)       # "positive" | "negative" | "neutral"
    llm_raw_response = Column(JSONB, nullable=True)  # full LLM payload, for audit/debug
    created_at = Column(TIMESTAMP, server_default=func.now())

    source = relationship("FeedbackSource", back_populates="themes")
    clusters = relationship("ThemeCluster", back_populates="theme", cascade="all, delete-orphan")


class Cluster(Base):
    __tablename__ = "clusters"

    id = Column(Integer, primary_key=True)
    label = Column(Text, nullable=False)             # representative text for the cluster
    confidence = Column(Float, nullable=False)       # avg cosine similarity within cluster
    created_at = Column(TIMESTAMP, server_default=func.now())

    themes = relationship("ThemeCluster", back_populates="cluster", cascade="all, delete-orphan")
    score = relationship("FeatureScore", back_populates="cluster", uselist=False, cascade="all, delete-orphan")


class ThemeCluster(Base):
    __tablename__ = "theme_clusters"

    id = Column(Integer, primary_key=True)
    theme_id = Column(Integer, ForeignKey("themes.id", ondelete="CASCADE"), nullable=False)
    cluster_id = Column(Integer, ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False)
    similarity_score = Column(Float, nullable=True)  # this theme's cosine similarity to the cluster

    theme = relationship("Theme", back_populates="clusters")
    cluster = relationship("Cluster", back_populates="themes")


class FeatureScore(Base):
    __tablename__ = "feature_scores"

    id = Column(Integer, primary_key=True)
    cluster_id = Column(Integer, ForeignKey("clusters.id", ondelete="CASCADE"), nullable=False, unique=True)
    frequency = Column(Integer, nullable=False)
    source_diversity = Column(Integer, nullable=False)
    sentiment_weight = Column(Float, nullable=False)
    rice_score = Column(
        Float,
        Computed("frequency * source_diversity * sentiment_weight", persisted=True)
    )
    created_at = Column(TIMESTAMP, server_default=func.now())

    cluster = relationship("Cluster", back_populates="score")