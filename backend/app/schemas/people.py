"""Pydantic schemas for People database."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# --- Person ---

class PersonPlatformCreate(BaseModel):
    platform: str  # instagram, tiktok, twitter, pinterest, youtube
    handle: str
    profile_url: Optional[str] = None
    follower_count: int = 0
    is_verified: bool = False


class PersonCreate(BaseModel):
    name: str
    type: str  # celebrity, influencer, brand, editor, stylist, media
    tier: Optional[str] = None
    bio: Optional[str] = None
    primary_region: Optional[str] = None
    secondary_regions: Optional[List[str]] = None
    demographics: Optional[List[str]] = None
    style_tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    scrape_frequency: str = "daily"
    priority: int = 5
    notes: Optional[str] = None
    platforms: List[PersonPlatformCreate] = []


class PersonBulkCreate(BaseModel):
    people: List[PersonCreate]


class PersonPlatformResponse(BaseModel):
    id: int
    person_id: int
    platform: str
    handle: str
    profile_url: Optional[str]
    follower_count: int
    engagement_rate: float
    is_verified: bool
    scrape_enabled: bool
    last_checked: Optional[datetime]

    class Config:
        from_attributes = True


class PersonResponse(BaseModel):
    id: int
    name: str
    type: str
    tier: Optional[str]
    bio: Optional[str]
    primary_region: Optional[str]
    secondary_regions: Optional[List[str]]
    demographics: Optional[List[str]]
    style_tags: Optional[List[str]]
    categories: Optional[List[str]]
    follower_count_total: int
    avg_engagement_rate: float
    relevance_score: float
    active: bool
    scrape_frequency: str
    priority: int
    added_at: datetime
    last_scraped_at: Optional[datetime]
    notes: Optional[str]
    platforms: List[PersonPlatformResponse] = []

    class Config:
        from_attributes = True


class PersonUpdate(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    tier: Optional[str] = None
    bio: Optional[str] = None
    primary_region: Optional[str] = None
    demographics: Optional[List[str]] = None
    style_tags: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    active: Optional[bool] = None
    scrape_frequency: Optional[str] = None
    priority: Optional[int] = None
    relevance_score: Optional[float] = None
    notes: Optional[str] = None


class PersonStats(BaseModel):
    total_people: int
    by_type: dict
    by_region: dict
    by_tier: dict
    total_platforms: int
    active_count: int


# --- Scraped Posts ---

class ScrapedPostResponse(BaseModel):
    id: int
    person_id: int
    platform: str
    post_url: str
    image_urls: Optional[List[str]]
    caption: Optional[str]
    hashtags: Optional[List[str]]
    likes: int
    comments: int
    shares: int
    views: int
    analyzed: bool
    category: Optional[str]
    colors: Optional[List[str]]
    style_tags: Optional[List[str]]
    ai_narrative: Optional[str]
    posted_at: Optional[datetime]
    scraped_at: datetime

    class Config:
        from_attributes = True
