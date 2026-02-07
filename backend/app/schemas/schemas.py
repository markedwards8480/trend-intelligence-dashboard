from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Dict, Any
from datetime import datetime


# ============ Trend Item Schemas ============

class TrendItemCreate(BaseModel):
    """Schema for creating a new trend item."""
    url: str
    source_platform: Optional[str] = None
    platform: Optional[str] = None  # Alias accepted from frontend
    submitted_by: str = "Mark Edwards"
    image_url: Optional[str] = None

    def get_platform(self) -> str:
        """Get platform from either field name."""
        return self.source_platform or self.platform or "Other"


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

    # Frontend-compatible aliases
    @property
    def platform(self) -> str:
        return self.source_platform

    @property
    def engagement_count(self) -> int:
        return self.likes + self.comments + self.shares

    @property
    def ai_analysis(self) -> Optional[str]:
        return self.ai_analysis_text

    @property
    def created_at(self) -> datetime:
        return self.submitted_at

    @property
    def updated_at(self) -> datetime:
        return self.last_updated

    class Config:
        from_attributes = True

    def model_dump(self, **kwargs):
        d = super().model_dump(**kwargs)
        d['platform'] = self.source_platform
        d['engagement_count'] = (d.get('likes', 0) or 0) + (d.get('comments', 0) or 0) + (d.get('shares', 0) or 0)
        d['ai_analysis'] = d.get('ai_analysis_text')
        d['created_at'] = d.get('submitted_at')
        d['updated_at'] = d.get('last_updated')
        return d


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
