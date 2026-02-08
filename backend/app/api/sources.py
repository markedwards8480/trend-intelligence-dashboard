from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from datetime import datetime
from typing import List, Optional

from app.models.database import get_db
from app.models.models import MonitoringTarget, TrendItem
from app.schemas.schemas import (
    SourceCreate,
    SourceResponse,
    SourceUpdate,
    SourceSuggestion,
    SourceBulkCreateRequest,
    SourceBulkResponse,
    SourceBulkImportResult,
    SocialDiscoveryResponse,
    BrandSocialDiscovery,
    SocialAccount,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/sources", tags=["sources"])


def _to_source_response(target: MonitoringTarget) -> dict:
    """Convert a MonitoringTarget (type=source) to SourceResponse-compatible dict."""
    return {
        "id": target.id,
        "url": target.source_url or target.value,
        "platform": target.platform,
        "name": target.source_name or target.value,
        "target_demographics": target.target_demographics or [],
        "frequency": target.frequency or "manual",
        "active": target.active,
        "trend_count": target.trend_count or 0,
        "last_scraped_at": target.last_scraped_at,
        "added_by": target.added_by,
        "added_at": target.added_at,
    }


@router.post("", response_model=SourceResponse)
async def add_source(
    source: SourceCreate,
    db: Session = Depends(get_db),
):
    """Add a new watched source (ecommerce site or social media account)."""
    # Check for duplicate
    existing = db.query(MonitoringTarget).filter(
        MonitoringTarget.type == "source",
        MonitoringTarget.source_url == source.url,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Source already exists")

    target = MonitoringTarget(
        type="source",
        value=source.name,
        platform=source.platform,
        active=True,
        added_by="Mark Edwards",
        source_url=source.url,
        source_name=source.name,
        target_demographics=source.target_demographics,
        frequency=source.frequency,
        trend_count=0,
    )

    db.add(target)
    db.commit()
    db.refresh(target)

    return _to_source_response(target)


@router.get("", response_model=List[SourceResponse])
async def list_sources(
    platform: Optional[str] = None,
    demographic: Optional[str] = None,
    active: Optional[bool] = None,
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List all watched sources with optional filtering."""
    query = db.query(MonitoringTarget).filter(MonitoringTarget.type == "source")

    if platform:
        query = query.filter(MonitoringTarget.platform == platform)
    if active is not None:
        query = query.filter(MonitoringTarget.active == active)

    query = query.order_by(desc(MonitoringTarget.added_at))
    targets = query.limit(limit).offset(offset).all()

    # Filter by demographic in Python (JSON field)
    results = []
    for t in targets:
        if demographic:
            demos = t.target_demographics or []
            if demographic not in demos:
                continue
        results.append(_to_source_response(t))

    return results


@router.post("/bulk", response_model=SourceBulkResponse)
async def bulk_import_sources(
    request: SourceBulkCreateRequest,
    db: Session = Depends(get_db),
):
    """Bulk import sources from a list. Skips duplicates gracefully."""
    succeeded = 0
    failed = []

    for source in request.sources:
        try:
            # Check for duplicate
            existing = db.query(MonitoringTarget).filter(
                MonitoringTarget.type == "source",
                MonitoringTarget.source_url == source.url,
            ).first()

            if existing:
                failed.append(SourceBulkImportResult(
                    name=source.name,
                    url=source.url,
                    reason="Source already exists",
                ))
                continue

            # Validate URL format
            if not source.url.startswith(('http://', 'https://')):
                failed.append(SourceBulkImportResult(
                    name=source.name,
                    url=source.url,
                    reason="Invalid URL format (must start with http:// or https://)",
                ))
                continue

            # Create source
            target = MonitoringTarget(
                type="source",
                value=source.name,
                platform=source.platform,
                active=True,
                added_by="Mark Edwards",
                source_url=source.url,
                source_name=source.name,
                target_demographics=source.target_demographics,
                frequency=source.frequency,
                trend_count=0,
            )
            db.add(target)
            db.commit()
            succeeded += 1

        except Exception as e:
            db.rollback()
            failed.append(SourceBulkImportResult(
                name=source.name,
                url=source.url,
                reason=str(e)[:100],
            ))

    return SourceBulkResponse(succeeded=succeeded, failed=failed)


@router.get("/discover-social-debug")
async def discover_social_debug(db: Session = Depends(get_db)):
    """Debug endpoint to test AI connectivity."""
    from app.config import settings
    ecommerce = db.query(MonitoringTarget).filter(
        MonitoringTarget.type == "source",
        MonitoringTarget.platform == "ecommerce",
        MonitoringTarget.active == True,
    ).all()
    return {
        "mock_ai": settings.USE_MOCK_AI,
        "has_api_key": bool(settings.CLAUDE_API_KEY),
        "api_key_prefix": settings.CLAUDE_API_KEY[:15] + "..." if settings.CLAUDE_API_KEY else "none",
        "ecommerce_count": len(ecommerce),
        "first_brands": [s.source_name for s in ecommerce[:3]],
    }


@router.post("/discover-social", response_model=SocialDiscoveryResponse)
async def discover_social_accounts(
    db: Session = Depends(get_db),
):
    """AI-powered discovery of social media accounts for existing ecommerce brands."""
    # Get all active ecommerce sources
    ecommerce = db.query(MonitoringTarget).filter(
        MonitoringTarget.type == "source",
        MonitoringTarget.platform == "ecommerce",
        MonitoringTarget.active == True,
    ).all()

    if not ecommerce:
        raise HTTPException(status_code=400, detail="No ecommerce sources found. Add some first.")

    brands = [
        {"name": s.source_name, "url": s.source_url}
        for s in ecommerce
    ]

    try:
        results = await AIService.discover_social_accounts(brands)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI discovery failed: {str(e)}")

    # Transform raw AI results into typed response
    brand_discoveries = []
    total_accounts = 0
    total_influencers = 0

    for item in results:
        accounts = [
            SocialAccount(**a) for a in item.get("accounts", [])
        ]
        influencers = [
            SocialAccount(
                platform=inf.get("platform", ""),
                handle=inf.get("handle", ""),
                url=inf.get("url", ""),
                name=inf.get("name", ""),
                type="influencer",
                description=inf.get("description", ""),
                estimated_followers=inf.get("estimated_followers", ""),
            )
            for inf in item.get("related_influencers", [])
        ]

        total_accounts += len(accounts)
        total_influencers += len(influencers)

        brand_discoveries.append(BrandSocialDiscovery(
            brand=item.get("brand", ""),
            accounts=accounts,
            related_influencers=influencers,
            hashtags=item.get("hashtags", []),
        ))

    return SocialDiscoveryResponse(
        brands=brand_discoveries,
        total_accounts=total_accounts,
        total_influencers=total_influencers,
    )


@router.post("/suggestions", response_model=List[SourceSuggestion])
async def suggest_sources(
    db: Session = Depends(get_db),
):
    """AI-powered suggestions for new sources based on existing watched sources."""
    # Get existing sources
    existing = db.query(MonitoringTarget).filter(
        MonitoringTarget.type == "source",
        MonitoringTarget.active == True,
    ).all()

    existing_sources = [
        {"name": s.source_name, "url": s.source_url, "platform": s.platform}
        for s in existing
    ]

    suggestions = await AIService.suggest_sources(existing_sources)
    return suggestions


# ============ Parameterized routes MUST come AFTER all named routes ============

@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: int,
    db: Session = Depends(get_db),
):
    """Get a specific source by ID."""
    target = db.query(MonitoringTarget).filter(
        MonitoringTarget.id == source_id,
        MonitoringTarget.type == "source",
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Source not found")
    return _to_source_response(target)


@router.put("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: int,
    update: SourceUpdate,
    db: Session = Depends(get_db),
):
    """Update a source's settings."""
    target = db.query(MonitoringTarget).filter(
        MonitoringTarget.id == source_id,
        MonitoringTarget.type == "source",
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Source not found")

    if update.active is not None:
        target.active = update.active
    if update.name is not None:
        target.source_name = update.name
        target.value = update.name
    if update.target_demographics is not None:
        target.target_demographics = update.target_demographics
    if update.frequency is not None:
        target.frequency = update.frequency

    db.commit()
    db.refresh(target)
    return _to_source_response(target)


@router.delete("/{source_id}")
async def delete_source(
    source_id: int,
    db: Session = Depends(get_db),
):
    """Delete a watched source."""
    target = db.query(MonitoringTarget).filter(
        MonitoringTarget.id == source_id,
        MonitoringTarget.type == "source",
    ).first()
    if not target:
        raise HTTPException(status_code=404, detail="Source not found")

    db.delete(target)
    db.commit()
    return {"message": f"Source '{target.source_name}' deleted"}


@router.post("/{source_id}/analyze")
async def analyze_from_source(
    source_id: int,
    url: str = Query(..., description="URL of the item to analyze from this source"),
    db: Session = Depends(get_db),
):
    """Submit and analyze a specific URL from a watched source."""
    source = db.query(MonitoringTarget).filter(
        MonitoringTarget.id == source_id,
        MonitoringTarget.type == "source",
    ).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    existing = db.query(TrendItem).filter(TrendItem.url == url).first()
    if existing:
        raise HTTPException(status_code=400, detail="URL already analyzed")

    from app.services.scoring_service import ScoringService
    from app.models.models import TrendMetricsHistory

    analysis = await AIService.analyze_trend(url, source.platform)

    demographic = analysis.get("demographic")
    if not demographic and source.target_demographics:
        demographic = source.target_demographics[0]

    trend_item = TrendItem(
        url=url,
        source_platform=source.platform,
        submitted_by="Mark Edwards",
        source_id=source.id,
        demographic=demographic,
        category=analysis.get("category"),
        subcategory=analysis.get("subcategory"),
        colors=analysis.get("colors"),
        patterns=analysis.get("patterns"),
        style_tags=analysis.get("style_tags"),
        fabrications=analysis.get("fabrications"),
        price_point=analysis.get("price_point"),
        ai_analysis_text=analysis.get("narrative"),
        likes=analysis.get("engagement_estimate", 0) // 4,
        comments=analysis.get("engagement_estimate", 0) // 10,
        shares=analysis.get("engagement_estimate", 0) // 20,
        views=analysis.get("engagement_estimate", 0),
        engagement_rate=0.0,
        status="active",
    )

    trend_item = ScoringService.update_trend_scores(trend_item)
    db.add(trend_item)

    source.trend_count = (source.trend_count or 0) + 1
    source.last_scraped_at = datetime.utcnow()

    db.commit()
    db.refresh(trend_item)

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
