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
    source_id: Optional[int] = None  # Link to a watched source
    demographic: Optional[str] = None  # junior_girls, young_women, contemporary, kids

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

    # Demographics & Fabrication
    demographic: Optional[str] = None
    fabrications: Optional[List[str]] = None
    source_id: Optional[int] = None

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
        d['demographic'] = d.get('demographic')
        d['fabrications'] = d.get('fabrications')
        d['source_id'] = d.get('source_id')
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


class FabricationStats(BaseModel):
    """Stats for a single fabrication/material."""
    fabrication: str
    count: int


class DashboardSummary(BaseModel):
    """Aggregated dashboard summary statistics."""
    top_categories: List[CategoryStats]
    trending_colors: List[ColorStats]
    trending_styles: List[StyleStats]
    trending_fabrications: List[FabricationStats] = []
    velocity_leaders: List[TrendLeader]
    total_active_trends: int
    new_today: int
    demographic_filter: Optional[str] = None
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


# ============ Source Schemas ============

class SourceCreate(BaseModel):
    """Schema for adding a watched source."""
    url: str
    platform: str  # instagram, tiktok, shein, zara, fashionnova, etc.
    name: str  # Display name
    target_demographics: List[str] = []  # ["junior_girls", "young_women"]
    frequency: str = "manual"  # daily, weekly, manual


class SourceResponse(BaseModel):
    """Schema for source response."""
    id: int
    url: str
    platform: str
    name: str
    target_demographics: Optional[List[str]]
    frequency: str
    active: bool
    trend_count: int
    last_scraped_at: Optional[datetime]
    added_by: str
    added_at: datetime

    class Config:
        from_attributes = True


class SourceUpdate(BaseModel):
    """Schema for updating a source."""
    active: Optional[bool] = None
    name: Optional[str] = None
    target_demographics: Optional[List[str]] = None
    frequency: Optional[str] = None


class SourceSuggestion(BaseModel):
    """AI-suggested source."""
    url: str
    platform: str
    name: str
    reasoning: str
    demographics: List[str] = []


# ============ Bulk Import Schemas ============

class SourceBulkCreateRequest(BaseModel):
    """Request for bulk importing sources."""
    sources: List[SourceCreate]


class SourceBulkImportResult(BaseModel):
    """Result detail for a failed bulk import row."""
    name: str
    url: str
    reason: str


class SourceBulkResponse(BaseModel):
    """Response for bulk import."""
    succeeded: int
    failed: List[SourceBulkImportResult]


# ============ Social Media Discovery Schemas ============

class SocialAccount(BaseModel):
    """A discovered social media account."""
    platform: str
    handle: str
    url: str
    name: str
    type: str = "official"  # official, influencer
    description: str = ""
    estimated_followers: str = ""


class BrandSocialDiscovery(BaseModel):
    """Social media discovery results for a single brand."""
    brand: str
    accounts: List[SocialAccount] = []
    related_influencers: List[SocialAccount] = []
    hashtags: List[str] = []


class SocialDiscoveryResponse(BaseModel):
    """Full response for social media discovery."""
    brands: List[BrandSocialDiscovery]
    total_accounts: int
    total_influencers: int


# ============ Seed Generation Schemas ============

class SeedGenerationResponse(BaseModel):
    """Response for AI seed trend generation."""
    created: int
    skipped: int
    sources_processed: int
    errors: int = 0


# ============ Recommendation & Feedback Schemas ============

class RecommendationResponse(BaseModel):
    """A single AI recommendation."""
    id: int
    type: str  # source, influencer, trend
    title: str
    description: str
    url: str
    platform: str
    reason: str
    confidence_score: float
    status: str  # pending, accepted, rejected, dismissed
    created_at: datetime

    class Config:
        from_attributes = True


class RecommendationFeedback(BaseModel):
    """Feedback on a recommendation."""
    status: str  # accepted, rejected, dismissed


class UserFeedbackCreate(BaseModel):
    """Create feedback on a trend or source."""
    feedback_type: str  # thumbs_up, thumbs_down, saved, dismissed
    context: Optional[str] = None


class FeedbackSummary(BaseModel):
    """Summary of user feedback for AI context."""
    total_thumbs_up: int
    total_thumbs_down: int
    liked_categories: List[str] = []
    disliked_categories: List[str] = []
    liked_sources: List[str] = []


# ============ Trend Insights Schemas ============

class TrendInsightResponse(BaseModel):
    """AI-generated category trend summary."""
    id: int
    category: str
    summary: str
    key_characteristics: Dict[str, Any]
    trending_items_count: int
    avg_trend_score: float
    style_tags_distribution: Dict[str, Any]
    generated_at: datetime

    class Config:
        from_attributes = True


class ThemedLookResponse(BaseModel):
    """AI-generated themed fashion aesthetic."""
    id: int
    theme_name: str
    description: str
    color_palette: List[str]
    key_items: List[Dict[str, Any]]
    style_tags: List[str]
    mood_description: Optional[str]
    demographic_appeal: List[str]
    featured_trend_ids: Optional[List[int]]
    generated_at: datetime

    class Config:
        from_attributes = True


class InsightsResponse(BaseModel):
    """Combined response for insights + themed looks."""
    category_insights: List[TrendInsightResponse]
    themed_looks: List[ThemedLookResponse]
    generated_at: Optional[datetime] = None


class InsightsStatusResponse(BaseModel):
    """Status of insights generation job."""
    status: str  # idle, running, completed, failed
    progress: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    error: Optional[str] = None
