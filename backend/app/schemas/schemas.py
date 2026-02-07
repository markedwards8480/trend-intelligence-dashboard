from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============ Trend Item Schemas ============

class TrendItemCreate(BaseModel):
    """Schema for creating a new trend item."""
    url: str
    source_platform: str
    submitted_by: str
    image_url: Optional[str] = None


class TrendItemResponse(BaseModel):
    """Schema for trend item response with all fields."""
    id: int
    url: str
    source_platform: str
    image_url: Optional[str]
    submitted_by: str
    submitted_at: datetime

    category: Optional[str]
    subcategory: Optional[str]
    colors: Optional[List[str]]
    patterns: Optional[List[str]]
    style_tags: Optional[List[str]]
    price_point: Optional[str]

    likes: int
    comments: int
    shares: int
    views: int
    engagement_rate: float

    trend_score: float
    velocity_score: float
    cross_platform_score: float

    scraped_at: Optional[datetime]
    last_updated: datetime
    status: str
    ai_analysis_text: Optional[str]

    class Config:
        from_attributes = True


class TrendItemList(BaseModel):
    """Schema for listing trend items."""
    items: List[TrendItemResponse]
    total: int
    limit: int
    offset: int


class TrendMetricsResponse(BaseModel):
    """Schema for time-series metrics data."""
    recorded_at: datetime
    likes: int
    comments: int
    shares: int
    views: int
    trend_score: float

    class Config:
        from_attributes = True


# ============ Mood Board Schemas ============

class MoodBoardCreate(BaseModel):
    """Schema for creating a mood board."""
    title: str
    description: Optional[str] = None
    category: Optional[str] = None
    item_ids: List[int] = []
    created_by: str


class MoodBoardResponse(BaseModel):
    """Schema for mood board response."""
    id: int
    title: str
    description: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
    category: Optional[str]
    items: Optional[List[int]]
    trend_items: Optional[List[TrendItemResponse]] = None

    class Config:
        from_attributes = True


class MoodBoardUpdate(BaseModel):
    """Schema for updating a mood board."""
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    items: Optional[List[int]] = None


# ============ Monitoring Target Schemas ============

class MonitoringTargetCreate(BaseModel):
    """Schema for creating a monitoring target."""
    type: str  # hashtag, account, keyword, color, style
    value: str
    platform: str
    added_by: str


class MonitoringTargetResponse(BaseModel):
    """Schema for monitoring target response."""
    id: int
    type: str
    value: str
    platform: str
    active: bool
    added_by: str
    added_at: datetime

    class Config:
        from_attributes = True


class MonitoringTargetUpdate(BaseModel):
    """Schema for updating a monitoring target."""
    active: Optional[bool] = None
    value: Optional[str] = None


# ============ Dashboard Schemas ============

class CategoryStats(BaseModel):
    """Stats for a single category."""
    name: str
    count: int
    trend_score: float


class ColorStats(BaseModel):
    """Stats for a single color."""
    color: str
    count: int


class StyleStats(BaseModel):
    """Stats for a single style tag."""
    style: str
    count: int


class TrendLeader(BaseModel):
    """A trending item leader."""
    id: int
    title: str  # url or display name
    category: Optional[str]
    velocity_score: float
    trend_score: float


class DashboardSummary(BaseModel):
    """Aggregated dashboard summary statistics."""
    top_categories: List[CategoryStats]
    trending_colors: List[ColorStats]
    trending_styles: List[StyleStats]
    velocity_leaders: List[TrendLeader]
    total_active_trends: int
    new_today: int
    timestamp: datetime


# ============ Hashtag Schemas ============

class TrendingHashtagResponse(BaseModel):
    """Response for trending hashtag."""
    id: int
    hashtag: str
    platform: str
    mention_count: int
    growth_rate: float
    first_seen: datetime
    last_updated: datetime

    class Config:
        from_attributes = True
