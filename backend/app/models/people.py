"""People database — celebrities, influencers, brands, editors, stylists to monitor."""

from sqlalchemy import (
    Column, Integer, String, Text, Float, DateTime, Boolean,
    JSON, Index, UniqueConstraint, ForeignKey,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database import Base


class Person(Base):
    """A tracked individual, brand, or account in the fashion ecosystem."""
    __tablename__ = "people"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False, index=True)
    # types: celebrity, influencer, brand, editor, stylist, media

    tier = Column(String(50), index=True)
    # tiers: a_list, b_list, macro, mid_tier, micro, nano, brand, editorial

    # Metadata
    bio = Column(Text, nullable=True)
    primary_region = Column(String(50), index=True)
    # regions: north_america, europe, asia, australia, global
    secondary_regions = Column(JSON, nullable=True)  # ["europe", "asia"]
    demographics = Column(JSON, nullable=True)  # ["junior_girls", "young_women"]
    style_tags = Column(JSON, nullable=True)  # ["streetwear", "quiet luxury"]
    categories = Column(JSON, nullable=True)  # ["dresses", "athleisure", "accessories"]

    # Aggregate stats
    follower_count_total = Column(Integer, default=0)
    avg_engagement_rate = Column(Float, default=0.0)
    relevance_score = Column(Float, default=50.0)  # 0-100

    # Tracking config
    active = Column(Boolean, default=True, index=True)
    scrape_frequency = Column(String(50), default="daily")  # hourly, daily, weekly
    priority = Column(Integer, default=5)  # 1=highest, 10=lowest

    # Timestamps
    added_at = Column(DateTime(timezone=True), server_default=func.now())
    last_scraped_at = Column(DateTime(timezone=True), nullable=True)
    notes = Column(Text, nullable=True)

    # Relationships
    platforms = relationship("PersonPlatform", back_populates="person", cascade="all, delete-orphan")
    scraped_posts = relationship("ScrapedPost", back_populates="person", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_people_type_tier", "type", "tier"),
        Index("idx_people_region_active", "primary_region", "active"),
        Index("idx_people_relevance", "relevance_score", "active"),
    )


class PersonPlatform(Base):
    """Platform-specific info for a person (their IG, TikTok, X handles, etc.)."""
    __tablename__ = "people_platforms"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=False)  # instagram, tiktok, twitter, pinterest, youtube
    handle = Column(String(255), nullable=False)
    profile_url = Column(Text, nullable=True)
    follower_count = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)
    is_verified = Column(Boolean, default=False)
    last_checked = Column(DateTime(timezone=True), nullable=True)
    last_post_at = Column(DateTime(timezone=True), nullable=True)

    # Scraping config
    scrape_enabled = Column(Boolean, default=True)
    apify_actor_id = Column(String(255), nullable=True)  # Which Apify actor to use

    # Relationships
    person = relationship("Person", back_populates="platforms")

    __table_args__ = (
        UniqueConstraint("person_id", "platform", name="uq_person_platform"),
        Index("idx_platform_handle", "platform", "handle"),
        Index("idx_platform_scrape", "scrape_enabled", "platform"),
    )


class ScrapedPost(Base):
    """A post/content scraped from a tracked person's social media."""
    __tablename__ = "scraped_posts"

    id = Column(Integer, primary_key=True, index=True)
    person_id = Column(Integer, ForeignKey("people.id", ondelete="CASCADE"), nullable=False, index=True)
    platform = Column(String(50), nullable=False, index=True)
    platform_post_id = Column(String(255), nullable=True)  # Native post ID from platform

    # Content
    post_url = Column(Text, nullable=False)
    image_urls = Column(JSON, nullable=True)  # Array of image URLs
    caption = Column(Text, nullable=True)
    hashtags = Column(JSON, nullable=True)  # Extracted hashtags

    # Engagement at time of scrape
    likes = Column(Integer, default=0)
    comments = Column(Integer, default=0)
    shares = Column(Integer, default=0)
    views = Column(Integer, default=0)
    engagement_rate = Column(Float, default=0.0)

    # AI Analysis (populated after scraping)
    analyzed = Column(Boolean, default=False, index=True)
    category = Column(String(100), nullable=True)
    colors = Column(JSON, nullable=True)
    patterns = Column(JSON, nullable=True)
    style_tags = Column(JSON, nullable=True)
    ai_narrative = Column(Text, nullable=True)

    # Converted to trend_item?
    trend_item_id = Column(Integer, ForeignKey("trend_items.id", ondelete="SET NULL"), nullable=True)

    # Timestamps
    posted_at = Column(DateTime(timezone=True), nullable=True)
    scraped_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    person = relationship("Person", back_populates="scraped_posts")

    __table_args__ = (
        UniqueConstraint("platform", "platform_post_id", name="uq_platform_post"),
        Index("idx_scraped_posts_analyzed", "analyzed", "scraped_at"),
        Index("idx_scraped_posts_person_date", "person_id", "scraped_at"),
    )
