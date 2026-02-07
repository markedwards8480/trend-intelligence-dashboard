from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.database import get_db
from app.models.models import TrendItem, TrendMetricsHistory
from app.schemas.schemas import (
    TrendItemCreate,
    TrendItemResponse,
    TrendItemList,
    TrendMetricsResponse,
)
from app.services.ai_service import AIService
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/api/trends", tags=["trends"])


@router.post("/submit", response_model=TrendItemResponse)
async def submit_trend(
    trend_create: TrendItemCreate,
    db: Session = Depends(get_db),
):
    """
    Submit a new trend URL.

    Runs AI analysis on the URL, stores it in the database,
    and returns the analyzed trend item.
    """
    # Check if URL already exists
    existing = db.query(TrendItem).filter(TrendItem.url == trend_create.url).first()
    if existing:
        raise HTTPException(status_code=400, detail="URL already submitted")

    # Run AI analysis
    platform = trend_create.get_platform()
    analysis = await AIService.analyze_trend(
        trend_create.url, platform
    )

    # Create trend item
    trend_item = TrendItem(
        url=trend_create.url,
        source_platform=platform,
        submitted_by=trend_create.submitted_by,
        image_url=trend_create.image_url,
        category=analysis.get("category"),
        subcategory=analysis.get("subcategory"),
        colors=analysis.get("colors"),
        patterns=analysis.get("patterns"),
        style_tags=analysis.get("style_tags"),
        price_point=analysis.get("price_point"),
        ai_analysis_text=analysis.get("narrative"),
        # Initial engagement estimates from analysis
        likes=analysis.get("engagement_estimate", 0) // 4,
        comments=analysis.get("engagement_estimate", 0) // 10,
        shares=analysis.get("engagement_estimate", 0) // 20,
        views=analysis.get("engagement_estimate", 0),
        engagement_rate=0.0,
        status="active",
    )

    # Calculate initial scores
    trend_item = ScoringService.update_trend_scores(trend_item)

    # Save to database
    db.add(trend_item)
    db.commit()
    db.refresh(trend_item)

    # Record initial metrics
    metrics = TrendMetricsHistory(
        trend_item_id=trend_item.id,
        likes=trend_item.likes,
        comments=trend_item.comments,
        shares=trend_item.shares,
        views=trend_item.views,
        trend_score=trend_item.trend_score,
    )
    db.add(metrics)
    db.commit()

    return trend_item


@router.get("/daily", response_model=TrendItemList)
async def get_daily_trends(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    source_platform: Optional[str] = None,
    platform: Optional[str] = None,  # Alias accepted from frontend
    sort_by: str = Query("trend_score"),
    db: Session = Depends(get_db),
):
    """
    Get trending items with optional filtering and sorting.

    Parameters:
    - limit: Max items to return (1-100)
    - offset: Pagination offset
    - category: Filter by category
    - source_platform/platform: Filter by source platform
    - sort_by: Sort by trend_score/score (default), velocity_score, or submitted_at
    """
    query = db.query(TrendItem).filter(TrendItem.status == "active")

    # Apply filters (accept both field names)
    plat = source_platform or platform
    if category:
        query = query.filter(TrendItem.category == category)
    if plat:
        query = query.filter(TrendItem.source_platform == plat)

    # Apply sorting (accept aliases from frontend)
    if sort_by == "velocity_score":
        query = query.order_by(desc(TrendItem.velocity_score))
    elif sort_by in ("submitted_at", "newest"):
        query = query.order_by(desc(TrendItem.submitted_at))
    else:  # Default: trend_score (also accepts "score", "trend_score")
        query = query.order_by(desc(TrendItem.trend_score))

    # Get total count
    total = query.count()

    # Apply pagination
    items = query.limit(limit).offset(offset).all()

    return TrendItemList(
        items=items,
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/{trend_id}", response_model=TrendItemResponse)
async def get_trend(
    trend_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific trend by ID."""
    trend = db.query(TrendItem).filter(TrendItem.id == trend_id).first()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")
    return trend


@router.post("/{trend_id}/analyze", response_model=TrendItemResponse)
async def reanalyze_trend(
    trend_id: int,
    db: Session = Depends(get_db),
):
    """Re-run AI analysis on a specific trend."""
    trend = db.query(TrendItem).filter(TrendItem.id == trend_id).first()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    # Run AI analysis again
    analysis = await AIService.analyze_trend(trend.url, trend.source_platform)

    # Update fields
    trend.category = analysis.get("category")
    trend.subcategory = analysis.get("subcategory")
    trend.colors = analysis.get("colors")
    trend.patterns = analysis.get("patterns")
    trend.style_tags = analysis.get("style_tags")
    trend.price_point = analysis.get("price_point")
    trend.ai_analysis_text = analysis.get("narrative")

    # Recalculate scores
    trend = ScoringService.update_trend_scores(trend)

    db.commit()
    db.refresh(trend)
    return trend


@router.get("/metrics/{trend_id}", response_model=List[TrendMetricsResponse])
async def get_trend_metrics(
    trend_id: int,
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    """
    Get time-series metrics data for a trend.

    Parameters:
    - trend_id: The trend item ID
    - hours: Number of hours of history to retrieve (1-720)
    """
    # Verify trend exists
    trend = db.query(TrendItem).filter(TrendItem.id == trend_id).first()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    # Get metrics within time window
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    metrics = (
        db.query(TrendMetricsHistory)
        .filter(
            and_(
                TrendMetricsHistory.trend_item_id == trend_id,
                TrendMetricsHistory.recorded_at >= cutoff,
            )
        )
        .order_by(TrendMetricsHistory.recorded_at)
        .all()
    )

    return metrics
