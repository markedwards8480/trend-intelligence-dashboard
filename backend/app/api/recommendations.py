from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime
from typing import List, Optional

from app.models.database import get_db
from app.models.models import Recommendation, UserFeedback, TrendItem, MonitoringTarget
from app.schemas.schemas import (
    RecommendationResponse,
    RecommendationFeedback,
    UserFeedbackCreate,
    FeedbackSummary,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


@router.get("", response_model=List[RecommendationResponse])
async def get_recommendations(
    status: Optional[str] = Query(None),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """Get recommendations, optionally filtered by status."""
    query = db.query(Recommendation)
    if status:
        query = query.filter(Recommendation.status == status)
    else:
        # Default: show pending
        query = query.filter(Recommendation.status == "pending")
    query = query.order_by(desc(Recommendation.confidence_score))
    return query.limit(limit).all()


@router.post("/generate")
async def generate_recommendations(
    db: Session = Depends(get_db),
):
    """
    Ask AI to generate new source/influencer recommendations
    based on current sources and past feedback.
    """
    # Gather existing sources for context
    sources = db.query(MonitoringTarget).filter(
        MonitoringTarget.type == "source",
        MonitoringTarget.active == True,
    ).all()

    source_names = [s.source_name or s.value for s in sources]

    # Gather feedback history
    recent_feedback = db.query(UserFeedback).order_by(
        desc(UserFeedback.recorded_at)
    ).limit(50).all()

    # Build feedback summary
    liked_entities = []
    disliked_entities = []
    for fb in recent_feedback:
        label = f"{fb.entity_type}:{fb.entity_id}"
        if fb.feedback_type == "thumbs_up":
            liked_entities.append(label)
        elif fb.feedback_type == "thumbs_down":
            disliked_entities.append(label)

    # Get previously rejected recommendations to avoid re-suggesting
    rejected = db.query(Recommendation).filter(
        Recommendation.status.in_(["rejected", "dismissed"])
    ).all()
    rejected_urls = [r.url for r in rejected]

    # Ask AI for recommendations
    try:
        results = await AIService.generate_recommendations(
            existing_sources=source_names,
            liked=liked_entities[:20],
            disliked=disliked_entities[:20],
            rejected_urls=rejected_urls[:50],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation generation failed: {str(e)}")

    created = 0
    for item in results:
        url = item.get("url", "")
        if not url:
            continue

        # Skip if already recommended
        existing = db.query(Recommendation).filter(Recommendation.url == url).first()
        if existing:
            continue

        rec = Recommendation(
            type=item.get("type", "source"),
            title=item.get("title", ""),
            description=item.get("description", ""),
            url=url,
            platform=item.get("platform", "ecommerce"),
            reason=item.get("reason", ""),
            confidence_score=item.get("confidence_score", 0.5),
            status="pending",
        )
        db.add(rec)
        created += 1

    db.commit()
    return {"created": created, "total_suggestions": len(results)}


@router.post("/{recommendation_id}/feedback")
async def respond_to_recommendation(
    recommendation_id: int,
    feedback: RecommendationFeedback,
    db: Session = Depends(get_db),
):
    """Accept, reject, or dismiss a recommendation."""
    rec = db.query(Recommendation).filter(Recommendation.id == recommendation_id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    rec.status = feedback.status
    rec.responded_at = datetime.utcnow()

    # If accepted, auto-add as a source
    if feedback.status == "accepted":
        existing_source = db.query(MonitoringTarget).filter(
            MonitoringTarget.source_url == rec.url
        ).first()
        if not existing_source:
            new_source = MonitoringTarget(
                type="source",
                value=rec.title,
                platform=rec.platform,
                active=True,
                added_by="AI Recommendation",
                source_url=rec.url,
                source_name=rec.title,
                target_demographics=[],
                frequency="manual",
            )
            db.add(new_source)

    # Record as feedback for learning
    fb = UserFeedback(
        entity_type="recommendation",
        entity_id=recommendation_id,
        feedback_type="thumbs_up" if feedback.status == "accepted" else "thumbs_down",
    )
    # Use merge to handle unique constraint
    existing_fb = db.query(UserFeedback).filter(
        UserFeedback.entity_type == "recommendation",
        UserFeedback.entity_id == recommendation_id,
    ).first()
    if existing_fb:
        existing_fb.feedback_type = fb.feedback_type
        existing_fb.recorded_at = datetime.utcnow()
    else:
        db.add(fb)

    db.commit()
    return {"status": rec.status, "recommendation_id": rec.id}


# ---- Trend feedback endpoints (thumbs up/down on trends) ----

@router.post("/trends/{trend_id}/feedback")
async def submit_trend_feedback(
    trend_id: int,
    feedback: UserFeedbackCreate,
    db: Session = Depends(get_db),
):
    """Submit thumbs up/down feedback on a trend item."""
    trend = db.query(TrendItem).filter(TrendItem.id == trend_id).first()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

    # Upsert feedback
    existing = db.query(UserFeedback).filter(
        UserFeedback.entity_type == "trend",
        UserFeedback.entity_id == trend_id,
    ).first()

    if existing:
        existing.feedback_type = feedback.feedback_type
        existing.context = feedback.context
        existing.recorded_at = datetime.utcnow()
    else:
        fb = UserFeedback(
            entity_type="trend",
            entity_id=trend_id,
            feedback_type=feedback.feedback_type,
            context=feedback.context,
        )
        db.add(fb)

    db.commit()
    return {"status": "recorded", "trend_id": trend_id, "feedback": feedback.feedback_type}


@router.get("/feedback/summary", response_model=FeedbackSummary)
async def get_feedback_summary(
    db: Session = Depends(get_db),
):
    """Get aggregated feedback stats."""
    total_up = db.query(UserFeedback).filter(UserFeedback.feedback_type == "thumbs_up").count()
    total_down = db.query(UserFeedback).filter(UserFeedback.feedback_type == "thumbs_down").count()

    # Get liked categories (from trend feedback)
    liked_trend_ids = db.query(UserFeedback.entity_id).filter(
        UserFeedback.entity_type == "trend",
        UserFeedback.feedback_type == "thumbs_up",
    ).all()
    liked_ids = [r[0] for r in liked_trend_ids]

    liked_categories = []
    disliked_categories = []
    liked_sources = []

    if liked_ids:
        cats = db.query(TrendItem.category).filter(
            TrendItem.id.in_(liked_ids),
            TrendItem.category.isnot(None),
        ).distinct().all()
        liked_categories = [c[0] for c in cats]

    disliked_trend_ids = db.query(UserFeedback.entity_id).filter(
        UserFeedback.entity_type == "trend",
        UserFeedback.feedback_type == "thumbs_down",
    ).all()
    disliked_ids = [r[0] for r in disliked_trend_ids]
    if disliked_ids:
        cats = db.query(TrendItem.category).filter(
            TrendItem.id.in_(disliked_ids),
            TrendItem.category.isnot(None),
        ).distinct().all()
        disliked_categories = [c[0] for c in cats]

    # Liked sources
    liked_source_recs = db.query(Recommendation.title).filter(
        Recommendation.status == "accepted"
    ).all()
    liked_sources = [r[0] for r in liked_source_recs]

    return FeedbackSummary(
        total_thumbs_up=total_up,
        total_thumbs_down=total_down,
        liked_categories=liked_categories,
        disliked_categories=disliked_categories,
        liked_sources=liked_sources,
    )
