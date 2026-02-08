import threading

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, and_
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.database import get_db, SessionLocal
from app.models.models import TrendItem, TrendMetricsHistory
from app.schemas.schemas import (
    TrendItemCreate,
    TrendItemResponse,
    TrendItemList,
    TrendMetricsResponse,
    SeedGenerationResponse,
)
from app.models.models import MonitoringTarget
from app.services.ai_service import AIService
from app.services.scoring_service import ScoringService

router = APIRouter(prefix="/api/trends", tags=["trends"])

# In-memory seed job status tracker
_seed_status = {
    "running": False,
    "progress": "",
    "created": 0,
    "skipped": 0,
    "errors": 0,
    "total_brands": 0,
    "brands_processed": 0,
    "done": False,
}


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
        source_id=trend_create.source_id,
        demographic=analysis.get("demographic") or trend_create.demographic,
        fabrications=analysis.get("fabrications"),
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
    limit: int = Query(200, ge=1, le=500),
    offset: int = Query(0, ge=0),
    category: Optional[str] = None,
    source_platform: Optional[str] = None,
    platform: Optional[str] = None,  # Alias accepted from frontend
    demographic: Optional[str] = None,
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
    - demographic: Filter by demographic (junior_girls, young_women, contemporary, kids)
    - sort_by: Sort by trend_score/score (default), velocity_score, or submitted_at
    """
    query = db.query(TrendItem).filter(TrendItem.status == "active")

    # Apply filters (accept both field names)
    plat = source_platform or platform
    if category:
        query = query.filter(TrendItem.category == category)
    if plat:
        query = query.filter(TrendItem.source_platform == plat)
    if demographic:
        query = query.filter(TrendItem.demographic == demographic)

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


def _run_seed_in_background(brands: list):
    """Background worker: generates seed trends and saves to DB.
    Runs in a separate thread — fully synchronous, no asyncio."""
    import json
    import re
    import time
    import traceback
    from app.config import settings

    global _seed_status
    _seed_status["running"] = True
    _seed_status["done"] = False
    _seed_status["created"] = 0
    _seed_status["skipped"] = 0
    _seed_status["errors"] = 0
    _seed_status["total_brands"] = len(brands)
    _seed_status["brands_processed"] = 0
    _seed_status["progress"] = "Starting AI generation..."

    def _clean(text):
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
        text = text.strip()
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        return text

    all_results = []
    batch_size = 5
    trends_per_brand = 5

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=settings.CLAUDE_API_KEY)

        for i in range(0, len(brands), batch_size):
            batch = brands[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(brands) + batch_size - 1) // batch_size
            _seed_status["progress"] = f"Processing batch {batch_num}/{total_batches} ({', '.join(b.get('name','') for b in batch)})..."

            brand_list = "\n".join(
                f"- {b.get('name', 'Unknown')} ({b.get('url', '')})"
                for b in batch
            )

            prompt = f"""You are helping a women's fast fashion apparel company (Mark Edwards Apparel) populate their trend intelligence dashboard with realistic trending products from competitor brands.

For each brand below, generate {trends_per_brand} REALISTIC trending products that this brand would currently stock in early 2026. Use your knowledge of each brand's actual product range, price point, and target demographic.

Brands:
{brand_list}

For EACH product, provide:
- brand: The brand name (must match exactly)
- product_name: A realistic product name as it would appear on their site
- product_url: A realistic URL for this product on their site (use real URL patterns like /products/, /p/, /dp/)
- category: Fashion category (e.g., "midi dress", "crop top", "cargo pants", "mini skirt", "oversized blazer", "platform sneakers", "slip dress", "wide leg jeans", "tank top", "maxi dress")
- colors: Array of 1-3 colors (e.g., ["black", "cream"], ["sage green"])
- patterns: Array of patterns (e.g., ["solid"], ["floral", "ditsy"], ["plaid"])
- style_tags: Array of 2-4 style tags (e.g., ["y2k", "streetwear"], ["clean girl", "minimal"], ["cottagecore", "romantic"])
- fabrications: Array of materials (e.g., ["cotton"], ["polyester", "spandex"], ["denim"])
- price_point: "budget" | "mid" | "luxury"
- demographic: "junior_girls" | "young_women" | "contemporary"
- narrative: 1-2 sentence explanation of why this product is trending
- estimated_likes: Realistic number between 500-50000
- estimated_comments: Realistic number between 50-5000
- estimated_shares: Realistic number between 20-2000
- estimated_views: Realistic number between 5000-500000

IMPORTANT: Make products realistic for each brand's actual style and price range. Use real fashion categories and current 2026 trend language.

Return ONLY valid JSON as a flat array of product objects. Do NOT nest by brand — return one flat array.
Return ONLY valid JSON, no additional text."""

            try:
                message = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=8192,
                    messages=[{"role": "user", "content": prompt}],
                )

                response_text = message.content[0].text
                cleaned = _clean(response_text)
                batch_results = json.loads(cleaned)

                # Attach source_id from our brand list
                brand_id_map = {b.get('name', ''): b.get('id') for b in batch}
                for item in batch_results:
                    brand_name = item.get('brand', '')
                    item['source_id'] = brand_id_map.get(brand_name)
                all_results.extend(batch_results)

                _seed_status["brands_processed"] = min(i + batch_size, len(brands))
                _seed_status["progress"] = f"Batch {batch_num}/{total_batches} done — {len(all_results)} products so far"

            except json.JSONDecodeError as je:
                print(f"JSON parse error on seed batch {batch_num}: {je}")
                _seed_status["progress"] = f"Batch {batch_num} had JSON error, continuing..."
            except Exception as e:
                print(f"Error on seed batch {batch_num}: {e}")
                traceback.print_exc()
                _seed_status["progress"] = f"Batch {batch_num} error: {str(e)[:100]}, continuing..."

            # Small delay between batches
            if i + batch_size < len(brands):
                time.sleep(1)

    except Exception as e:
        _seed_status["progress"] = f"AI generation failed: {str(e)}"
        _seed_status["running"] = False
        _seed_status["done"] = True
        traceback.print_exc()
        return

    _seed_status["progress"] = f"Saving {len(all_results)} trends to database..."

    # Use our own DB session (not request-scoped)
    db = SessionLocal()
    try:
        for item in all_results:
            try:
                product_url = item.get("product_url", "")
                if not product_url:
                    _seed_status["errors"] += 1
                    continue

                existing = db.query(TrendItem).filter(TrendItem.url == product_url).first()
                if existing:
                    _seed_status["skipped"] += 1
                    continue

                trend = TrendItem(
                    url=product_url,
                    source_platform="ecommerce",
                    submitted_by="AI Seed Generator",
                    image_url=None,
                    source_id=item.get("source_id"),
                    category=item.get("category"),
                    subcategory=None,
                    colors=item.get("colors", []),
                    patterns=item.get("patterns", []),
                    style_tags=item.get("style_tags", []),
                    fabrications=item.get("fabrications", []),
                    price_point=item.get("price_point", "mid"),
                    demographic=item.get("demographic", "junior_girls"),
                    ai_analysis_text=item.get("narrative", ""),
                    likes=item.get("estimated_likes", 1000),
                    comments=item.get("estimated_comments", 200),
                    shares=item.get("estimated_shares", 50),
                    views=item.get("estimated_views", 10000),
                    engagement_rate=0.0,
                    status="active",
                )

                trend = ScoringService.update_trend_scores(trend)

                db.add(trend)
                db.commit()
                db.refresh(trend)

                metrics = TrendMetricsHistory(
                    trend_item_id=trend.id,
                    likes=trend.likes,
                    comments=trend.comments,
                    shares=trend.shares,
                    views=trend.views,
                    trend_score=trend.trend_score,
                )
                db.add(metrics)
                db.commit()

                _seed_status["created"] += 1

            except Exception as e:
                db.rollback()
                print(f"Error creating seed trend: {e}")
                _seed_status["errors"] += 1
    finally:
        db.close()

    _seed_status["progress"] = "Complete!"
    _seed_status["running"] = False
    _seed_status["done"] = True


@router.post("/seed")
async def seed_trends_from_sources(
    db: Session = Depends(get_db),
):
    """
    Start AI seed trend generation in the background.
    Returns immediately — poll GET /api/trends/seed/status for progress.
    """
    global _seed_status

    if _seed_status["running"]:
        return {"message": "Seed generation already in progress", "status": _seed_status}

    # Get all active ecommerce sources
    ecommerce = db.query(MonitoringTarget).filter(
        MonitoringTarget.type == "source",
        MonitoringTarget.platform == "ecommerce",
        MonitoringTarget.active == True,
    ).all()

    if not ecommerce:
        raise HTTPException(status_code=400, detail="No ecommerce sources found.")

    brands = [
        {"name": s.source_name, "url": s.source_url, "id": s.id}
        for s in ecommerce
    ]

    # Launch background thread
    thread = threading.Thread(target=_run_seed_in_background, args=(brands,), daemon=True)
    thread.start()

    return {
        "message": f"Seed generation started for {len(brands)} brands. Poll /api/trends/seed/status for progress.",
        "total_brands": len(brands),
    }


@router.get("/seed/status")
async def seed_status():
    """Poll this endpoint to get the progress of seed trend generation."""
    return _seed_status


@router.get("/metrics/{trend_id}", response_model=List[TrendMetricsResponse])
async def get_trend_metrics(
    trend_id: int,
    hours: int = Query(24, ge=1, le=720),
    db: Session = Depends(get_db),
):
    """
    Get time-series metrics data for a trend.
    """
    trend = db.query(TrendItem).filter(TrendItem.id == trend_id).first()
    if not trend:
        raise HTTPException(status_code=404, detail="Trend not found")

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
