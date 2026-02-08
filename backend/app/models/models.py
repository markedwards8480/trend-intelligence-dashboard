from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, ForeignKey, JSON, Numeric, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base
from datetime import datetime


class TrendItem(Base):
    """Main table for tracking individual trend items."""
    __tablename__ = "trend_items"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String(2048), unique=True, nullable=False, index=True)
    source_platform = Column(String(50), nullable=False, index=True)  # instagram, tiktok, pinterest, etc.
    image_url = Column(String(2048), nullable=True)
    submitted_by = Column(String(255), nullable=False)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())

    # Trend classification
    category = Column(String(100), nullable=True, index=True)  # e.g., "midi dress", "crop top"
    subcategory = Column(String(100), nullable=True)
    colors = Column(JSON, nullable=True)  # ["navy blue", "white"]
    patterns = Column(JSON, nullable=True)  # ["plaid", "striped"]
    style_tags = Column(JSON, nullable=True)  # ["cottagecore", "y2k", "quiet luxury"]
    price_point = Column(String(50), nullable=True)  # "budget", "mid", "luxury"

    # Engagement metrics
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # Scoring
    trend_score = Column(Float, default=0.0, index=True)
    velocity_score = Column(Float, default=0.0, index=True)
    cross_platform_score = Column(Float, default=0.0)

    # Metadata
    scraped_at = Column(DateTime(timezone=True), nullable=True)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    status = Column(String(20), default="active", index=True)  # active, archived, flagged

    # AI Analysis
    ai_analysis_text = Column(Text, nullable=True)  # Narrative analysis from Claude

    # Demographics & Fabrication (Phase 2 expansion)
    demographic = Column(String(50), nullable=True, index=True)  # junior_girls, young_women, contemporary, kids
    fabrications = Column(JSON, nullable=True)  # ["cotton", "polyester blend", "silk"]
    source_id = Column(Integer, ForeignKey("monitoring_targets.id", ondelete="SET NULL"), nullable=True, index=True)

    # Relationships
    metrics_history = relationship("TrendMetricsHistory", back_populates="trend_item", cascade="all, delete-orphan")
    source = relationship("MonitoringTarget", foreign_keys=[source_id])

    __table_args__ = (
        Index("idx_trend_items_score_date", "trend_score", "submitted_at"),
        Index("idx_trend_items_velocity_date", "velocity_score", "submitted_at"),
        Index("idx_trend_items_category_status", "category", "status"),
        Index("idx_trend_items_demographic", "demographic", "status"),
    )


class TrendMetricsHistory(Base):
    """Historical tracking of trend metrics over time for trend analysis."""
    __tablename__ = "trend_metrics_history"

    id = Column(Integer, primary_key=True, index=True)
    trend_item_id = Column(Integer, ForeignKey("trend_items.id", ondelete="CASCADE"), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Snapshot of metrics at this time
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    trend_score = Column(Float, default=0.0)

    # Relationships
    trend_item = relationship("TrendItem", back_populates="metrics_history")

    __table_args__ = (
        Index("idx_metrics_history_date", "trend_item_id", "recorded_at"),
    )


class MoodBoard(Base):
    """Curated collections of trend items."""
    __tablename__ = "mood_boards"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Categorization
    category = Column(String(100), nullable=True, index=True)  # e.g., "spring 2024", "festival wear"

    # Items in this mood board (trend_item IDs)
    items = Column(JSON, nullable=True, default=[])  # [1, 2, 3, ...]

    __table_args__ = (
        Index("idx_mood_boards_created", "created_by", "created_at"),
    )


class TrendingHashtag(Base):
    """Track trending hashtags across platforms."""
    __tablename__ = "trending_hashtags"

    id = Column(Integer, primary_key=True, index=True)
    hashtag = Column(String(255), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)  # instagram, tiktok, etc.

    # Metrics
    mention_count = Column(Integer, default=0)
    growth_rate = Column(Float, default=0.0)  # percentage change

    # Timeline
    first_seen = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        UniqueConstraint("hashtag", "platform", name="uq_hashtag_platform"),
        Index("idx_hashtags_growth", "growth_rate", "last_updated"),
    )


class MonitoringTarget(Base):
    """Configuration for monitoring specific trends, hashtags, accounts, or sources."""
    __tablename__ = "monitoring_targets"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)  # hashtag, account, keyword, color, style, source
    value = Column(String(255), nullable=False)  # The actual value to monitor
    platform = Column(String(50), nullable=False, index=True)  # instagram, tiktok, pinterest, all

    # Status
    active = Column(Boolean, default=True, index=True)
    added_by = Column(String(255), nullable=False)
    added_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # Source-specific fields (for type="source")
    source_url = Column(String(2048), nullable=True)  # Full URL of ecommerce site or account
    source_name = Column(String(255), nullable=True)  # Display name like "SHEIN", "Zara US"
    target_demographics = Column(JSON, nullable=True)  # ["junior_girls", "young_women"]
    frequency = Column(String(50), default="manual")  # daily, weekly, manual
    trend_count = Column(Integer, default=0)  # Number of trends surfaced from this source
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_monitoring_active_platform", "active", "platform"),
        Index("idx_monitoring_type_value", "type", "value"),
    )


class Recommendation(Base):
    """AI-generated recommendations for new sources, influencers, or trends."""
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(50), nullable=False, index=True)  # source, influencer, trend
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    url = Column(String(2048), nullable=False)
    platform = Column(String(50), nullable=False)
    reason = Column(Text, nullable=True)  # Why AI suggested this
    confidence_score = Column(Float, default=0.5)

    # Status
    status = Column(String(20), default="pending", index=True)  # pending, accepted, rejected, dismissed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    responded_at = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("idx_recommendations_status", "status", "created_at"),
    )


class UserFeedback(Base):
    """User feedback on trends, sources, and recommendations for learning."""
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    entity_type = Column(String(50), nullable=False, index=True)  # trend, source, recommendation
    entity_id = Column(Integer, nullable=False, index=True)
    feedback_type = Column(String(20), nullable=False)  # thumbs_up, thumbs_down, saved, dismissed
    context = Column(Text, nullable=True)  # Optional note
    recorded_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    __table_args__ = (
        Index("idx_feedback_entity", "entity_type", "entity_id"),
        UniqueConstraint("entity_type", "entity_id", "feedback_type", name="uq_feedback_entity"),
    )
