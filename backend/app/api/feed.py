"""API routes for the Posts Feed and Trend Analysis."""

import logging
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.models.database import get_db
from app.services.trend_analysis import TrendAnalysisEngine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/feed", tags=["feed"])


@router.get("/posts")
async def get_posts_feed(
    platform: Optional[str] = None,
    person_id: Optional[int] = None,
    person_type: Optional[str] = None,
    days: int = Query(30, ge=1, le=365),
    sort_by: str = Query("engagement", regex="^(engagement|recent|views)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """Get a feed of scraped posts with filtering and sorting."""
    engine = TrendAnalysisEngine(db)
    return engine.get_posts_feed(
        platform=platform,
        person_id=person_id,
        person_type=person_type,
        days=days,
        sort_by=sort_by,
        limit=limit,
        offset=offset,
    )


@router.get("/stats")
async def get_feed_stats(
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db),
):
    """Get summary stats for the feed."""
    engine = TrendAnalysisEngine(db)
    return engine.get_feed_stats(days=days)


@router.get("/trends")
async def get_trend_analysis(
    days: int = Query(7, ge=1, le=90),
    min_mentions: int = Query(2, ge=1, le=20),
    db: Session = Depends(get_db),
):
    """
    Run trend analysis on recent scraped posts.
    Returns trending hashtags, styles, categories, colors,
    cross-person convergence, and AI insights.
    """
    engine = TrendAnalysisEngine(db)
    return engine.analyze_recent_posts(days=days, min_mentions=min_mentions)
