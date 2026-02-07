from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from collections import Counter
from typing import List, Optional

from app.models.database import get_db
from app.models.models import TrendItem
from app.schemas.schemas import (
    DashboardSummary,
    CategoryStats,
    ColorStats,
    StyleStats,
    FabricationStats,
    TrendLeader,
)

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/summary", response_model=DashboardSummary)
async def get_dashboard_summary(
    days: int = Query(7, ge=1, le=90),
    demographic: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Get aggregated dashboard summary statistics.

    Parameters:
    - days: Number of days to look back for statistics
    - demographic: Filter by demographic (junior_girls, young_women, contemporary, kids)
    """
    cutoff_date = datetime.utcnow() - timedelta(days=days)

    # Base query for active trends within timeframe
    base_query = db.query(TrendItem).filter(
        TrendItem.status == "active",
        TrendItem.submitted_at >= cutoff_date,
    )
    if demographic:
        base_query = base_query.filter(TrendItem.demographic == demographic)

    trends = base_query.all()

    # Calculate total active trends
    total_query = db.query(TrendItem).filter(TrendItem.status == "active")
    if demographic:
        total_query = total_query.filter(TrendItem.demographic == demographic)
    total_active = total_query.count()

    # Calculate new today
    today_cutoff = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    today_query = db.query(TrendItem).filter(
        TrendItem.status == "active",
        TrendItem.submitted_at >= today_cutoff,
    )
    if demographic:
        today_query = today_query.filter(TrendItem.demographic == demographic)
    new_today = today_query.count()

    # Top categories by count
    category_counts = Counter()
    category_scores = {}
    for trend in trends:
        if trend.category:
            category_counts[trend.category] += 1
            if trend.category not in category_scores:
                category_scores[trend.category] = []
            category_scores[trend.category].append(trend.trend_score)

    top_categories = [
        CategoryStats(
            name=category,
            count=count,
            trend_score=sum(category_scores[category]) / len(category_scores[category]),
        )
        for category, count in category_counts.most_common(10)
    ]

    # Trending colors (most common)
    color_counts = Counter()
    for trend in trends:
        if trend.colors:
            for color in trend.colors:
                color_counts[color] += 1

    trending_colors = [
        ColorStats(color=color, count=count)
        for color, count in color_counts.most_common(10)
    ]

    # Trending style tags (most common)
    style_counts = Counter()
    for trend in trends:
        if trend.style_tags:
            for style in trend.style_tags:
                style_counts[style] += 1

    trending_styles = [
        StyleStats(style=style, count=count)
        for style, count in style_counts.most_common(10)
    ]

    # Trending fabrications (most common)
    fab_counts = Counter()
    for trend in trends:
        if trend.fabrications:
            for fab in trend.fabrications:
                fab_counts[fab] += 1

    trending_fabrications = [
        FabricationStats(fabrication=fab, count=count)
        for fab, count in fab_counts.most_common(10)
    ]

    # Velocity leaders (top 5 by velocity_score)
    velocity_leaders = [
        TrendLeader(
            id=trend.id,
            title=trend.url[:50] + "..." if len(trend.url) > 50 else trend.url,
            category=trend.category,
            velocity_score=trend.velocity_score,
            trend_score=trend.trend_score,
        )
        for trend in sorted(trends, key=lambda t: t.velocity_score, reverse=True)[:5]
    ]

    return DashboardSummary(
        top_categories=top_categories,
        trending_colors=trending_colors,
        trending_styles=trending_styles,
        trending_fabrications=trending_fabrications,
        velocity_leaders=velocity_leaders,
        total_active_trends=total_active,
        new_today=new_today,
        demographic_filter=demographic,
        timestamp=datetime.utcnow(),
    )
