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

    # Platform group → actual platform values mapping
    PLATFORM_GROUPS = {
        "social": ["instagram", "tiktok", "pinterest", "facebook", "twitter", "snapchat", "youtube", "threads"],
        "ecommerce": ["ecommerce"],
        "media": ["fashion_media", "blog", "magazine", "editorial"],
        "search": ["google_trends", "search"],
    }

    # Apply filters (accept both field names)
    plat = source_platform or platform
    if category:
        query = query.filter(TrendItem.category == category)
    if plat:
        # Check if it's a group name or a specific platform
        if plat in PLATFORM_GROUPS:
            query = query.filter(TrendItem.source_platform.in_(PLATFORM_GROUPS[plat]))
        else:
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


# ============ Social Media Seed Generation ============

_social_seed_status = {
    "running": False,
    "done": False,
    "created": 0,
    "skipped": 0,
    "errors": 0,
    "progress": "",
}


def _run_social_seed_in_background(accounts: list):
    """Background worker: generates social media trend posts and saves to DB."""
    import json
    import re
    import time
    import traceback
    from app.config import settings

    global _social_seed_status
    _social_seed_status["running"] = True
    _social_seed_status["done"] = False
    _social_seed_status["created"] = 0
    _social_seed_status["skipped"] = 0
    _social_seed_status["errors"] = 0
    _social_seed_status["progress"] = "Starting social media AI generation..."

    def _clean(text):
        text = text.strip()
        text = re.sub(r'^```(?:json)?\s*\n?', '', text)
        text = re.sub(r'\n?```\s*$', '', text)
        text = text.strip()
        text = re.sub(r',\s*}', '}', text)
        text = re.sub(r',\s*]', ']', text)
        return text

    all_results = []
    batch_size = 8
    posts_per_account = 3

    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=settings.CLAUDE_API_KEY)

        for i in range(0, len(accounts), batch_size):
            batch = accounts[i:i + batch_size]
            batch_num = i // batch_size + 1
            total_batches = (len(accounts) + batch_size - 1) // batch_size
            _social_seed_status["progress"] = f"Processing batch {batch_num}/{total_batches}..."

            account_list = "\n".join(
                f"- {a.get('name', 'Unknown')} (@{a.get('handle', '')}) on {a.get('platform', 'instagram')} — {a.get('url', '')}"
                for a in batch
            )

            prompt = f"""You are helping a women's fast fashion apparel company (Mark Edwards Apparel) populate their trend intelligence dashboard with realistic SOCIAL MEDIA trending posts from brand and influencer accounts in early 2026.

For each social media account below, generate {posts_per_account} REALISTIC trending posts that this account would publish. These should be the kind of viral, high-engagement fashion content that drives trends.

Accounts:
{account_list}

For EACH post, provide:
- account_name: The account name (must match exactly)
- platform: The social media platform (instagram, tiktok, pinterest — must match the account's platform)
- post_url: A realistic post URL (use real URL patterns like instagram.com/p/xxx, tiktok.com/@user/video/xxx, pinterest.com/pin/xxx)
- post_type: "reel" | "carousel" | "story" | "video" | "pin" | "outfit_post" | "haul" | "styling_tip" | "trend_alert"
- category: Fashion category (e.g., "midi dress", "crop top", "cargo pants", "mini skirt", "oversized blazer", "platform sneakers", "slip dress", "wide leg jeans", "tank top", "maxi dress", "leggings", "puffer jacket", "blazer", "boots")
- colors: Array of 1-3 colors
- patterns: Array of patterns
- style_tags: Array of 2-4 trending style tags (e.g., ["quiet luxury", "clean girl"], ["mob wife", "coastal cowgirl"], ["coquette", "balletcore"], ["dark academia", "preppy"])
- fabrications: Array of materials
- price_point: "budget" | "mid" | "luxury"
- demographic: "junior_girls" | "young_women" | "contemporary"
- caption: A realistic social media caption (1-2 sentences with hashtags)
- estimated_likes: Realistic social media scale — 1000-500000
- estimated_comments: 100-50000
- estimated_shares: 50-100000
- estimated_views: 10000-5000000

IMPORTANT: Make posts realistic for each account's actual content style. TikTok posts should feel like TikTok (viral outfit checks, hauls). Instagram should feel like Instagram (curated aesthetics, reels). Pinterest should feel like Pinterest (mood boards, outfit inspo).

Return ONLY valid JSON as a flat array of post objects. No additional text."""

            try:
                message = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=8192,
                    messages=[{"role": "user", "content": prompt}],
                )

                response_text = message.content[0].text
                cleaned = _clean(response_text)
                batch_results = json.loads(cleaned)

                # Attach source_id from our account list
                account_id_map = {a.get('name', ''): a.get('id') for a in batch}
                for item in batch_results:
                    acct_name = item.get('account_name', '')
                    item['source_id'] = account_id_map.get(acct_name)
                all_results.extend(batch_results)

                _social_seed_status["progress"] = f"Batch {batch_num}/{total_batches} done — {len(all_results)} posts so far"

            except json.JSONDecodeError as je:
                print(f"JSON parse error on social seed batch {batch_num}: {je}")
                _social_seed_status["progress"] = f"Batch {batch_num} had JSON error, continuing..."
            except Exception as e:
                print(f"Error on social seed batch {batch_num}: {e}")
                traceback.print_exc()
                _social_seed_status["progress"] = f"Batch {batch_num} error: {str(e)[:100]}, continuing..."

            if i + batch_size < len(accounts):
                time.sleep(1)

    except Exception as e:
        _social_seed_status["progress"] = f"AI generation failed: {str(e)}"
        _social_seed_status["running"] = False
        _social_seed_status["done"] = True
        traceback.print_exc()
        return

    _social_seed_status["progress"] = f"Saving {len(all_results)} social media trends to database..."

    db = SessionLocal()
    try:
        for item in all_results:
            try:
                post_url = item.get("post_url", "")
                if not post_url:
                    _social_seed_status["errors"] += 1
                    continue

                existing = db.query(TrendItem).filter(TrendItem.url == post_url).first()
                if existing:
                    _social_seed_status["skipped"] += 1
                    continue

                plat = item.get("platform", "instagram").lower().strip()

                trend = TrendItem(
                    url=post_url,
                    source_platform=plat,
                    submitted_by="AI Social Media Seed",
                    image_url=None,
                    source_id=item.get("source_id"),
                    category=item.get("category"),
                    subcategory=item.get("post_type"),
                    colors=item.get("colors", []),
                    patterns=item.get("patterns", []),
                    style_tags=item.get("style_tags", []),
                    fabrications=item.get("fabrications", []),
                    price_point=item.get("price_point", "mid"),
                    demographic=item.get("demographic", "junior_girls"),
                    ai_analysis_text=item.get("caption", ""),
                    likes=item.get("estimated_likes", 5000),
                    comments=item.get("estimated_comments", 500),
                    shares=item.get("estimated_shares", 200),
                    views=item.get("estimated_views", 50000),
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

                _social_seed_status["created"] += 1

            except Exception as e:
                db.rollback()
                print(f"Error creating social seed trend: {e}")
                _social_seed_status["errors"] += 1
    finally:
        db.close()

    _social_seed_status["progress"] = "Complete!"
    _social_seed_status["running"] = False
    _social_seed_status["done"] = True


@router.post("/seed/social")
async def seed_social_media_trends(
    db: Session = Depends(get_db),
):
    """
    Start AI social media seed generation in the background.
    Generates trending posts from social media sources (Instagram, TikTok, Pinterest).
    Poll GET /api/trends/seed/social/status for progress.
    """
    global _social_seed_status

    if _social_seed_status["running"]:
        return {"message": "Social seed generation already in progress", "status": _social_seed_status}

    # Get all active social media sources
    social_platforms = ["instagram", "tiktok", "pinterest", "facebook", "twitter", "youtube"]
    social_sources = db.query(MonitoringTarget).filter(
        MonitoringTarget.type == "source",
        MonitoringTarget.platform.in_(social_platforms),
        MonitoringTarget.active == True,
    ).all()

    if not social_sources:
        raise HTTPException(status_code=400, detail="No social media sources found.")

    accounts = [
        {
            "name": s.source_name,
            "handle": s.source_name.replace(" ", "").lower(),
            "url": s.source_url,
            "platform": s.platform,
            "id": s.id,
        }
        for s in social_sources
    ]

    thread = threading.Thread(target=_run_social_seed_in_background, args=(accounts,), daemon=True)
    thread.start()

    return {
        "message": f"Social media seed generation started for {len(accounts)} accounts. Poll /api/trends/seed/social/status for progress.",
        "total_accounts": len(accounts),
    }


@router.get("/seed/social/status")
async def social_seed_status():
    """Poll this endpoint to get the progress of social media seed generation."""
    return _social_seed_status


@router.post("/backfill-images")
async def backfill_images(
    force: bool = Query(False, description="Re-assign images even if one exists"),
    db: Session = Depends(get_db),
):
    """
    Assign category-accurate fashion images to trends.
    All photo IDs sourced directly from Unsplash search results.
    Pass ?force=true to re-assign ALL trends (not just empty ones).
    """
    P = "https://images.unsplash.com/photo-"
    S = "?w=400&h=500&fit=crop"

    # Verified Unsplash photo IDs scraped from category-specific search pages
    FASHION_IMAGES = {
        "dress": [
            f"{P}1752797203245-3b9e233b2ac8{S}",
            f"{P}1753589435506-cfd036fba85e{S}",
            f"{P}1667890786022-98704b9b8fcb{S}",
            f"{P}1663044023283-9ea59358b6c0{S}",
            f"{P}1663044022894-68a5e6bccd64{S}",
            f"{P}1667890786333-ddb32e7e0d6e{S}",
            f"{P}1663044022903-caa195cb5b2e{S}",
            f"{P}1752797161382-3d0a4edc51dc{S}",
            f"{P}1730141100734-90e06e5966dd{S}",
            f"{P}1730140762303-8bc833a0c0bb{S}",
        ],
        "top": [
            f"{P}1724490056260-44bf1de2617e{S}",
            f"{P}1651507178496-7a42c1e19442{S}",
            f"{P}1618371360326-3583fcdb0b10{S}",
            f"{P}1760551600855-cbd4fd31d278{S}",
            f"{P}1574847872646-abff244bbd87{S}",
            f"{P}1763935723482-14ac7f49a3ae{S}",
            f"{P}1689700672469-0017bfeec930{S}",
            f"{P}1663044022913-8913ff9ff2bc{S}",
            f"{P}1766465525646-f4b47c41f061{S}",
            f"{P}1673999707565-8bb553c9765b{S}",
        ],
        "pants": [
            f"{P}1695231081377-2765f838043d{S}",
            f"{P}1770364018048-45c991a6c4d2{S}",
            f"{P}1770364018544-7ac645977a79{S}",
            f"{P}1758543144593-95061a3f418a{S}",
            f"{P}1762343290221-d2374e1e2e2c{S}",
            f"{P}1770294760762-1cd821ecc567{S}",
            f"{P}1770364020139-8feb0e4d41cf{S}",
            f"{P}1765828594000-1605dd96033e{S}",
            f"{P}1759851235367-2eb2282414fa{S}",
            f"{P}1762327162259-60c4e56b8523{S}",
        ],
        "skirt": [
            f"{P}1608033247410-817c68700611{S}",
            f"{P}1582142306909-195724d33ffc{S}",
            f"{P}1570700006701-4bdeaf669738{S}",
            f"{P}1741943716275-2eaf11f4e918{S}",
            f"{P}1739945533087-1f80850e7d86{S}",
            f"{P}1739945472394-3284ac02996b{S}",
            f"{P}1555180739-0cb3b1d85138{S}",
            f"{P}1633452696817-bae37e248741{S}",
            f"{P}1691315926449-53b463adc4ac{S}",
            f"{P}1544596758-7339ae9a0432{S}",
        ],
        "leggings": [
            f"{P}1603920346280-75b4832fb6a7{S}",
            f"{P}1597299001669-6454fec8ac25{S}",
            f"{P}1762331652034-2db35c56350e{S}",
            f"{P}1762331648554-94fdae0956da{S}",
            f"{P}1763771522867-c26bf75f12bc{S}",
            f"{P}1762331654306-49a7e79763c5{S}",
            f"{P}1762331660576-cbf66a7db84d{S}",
            f"{P}1762337380547-efe2df510d98{S}",
            f"{P}1611078844630-85c0a9a34623{S}",
            f"{P}1762337383598-96edda3d55f7{S}",
        ],
        "outerwear": [
            f"{P}1706765779494-2705542ebe74{S}",
            f"{P}1608113562252-b320e7628e17{S}",
            f"{P}1548624313-0396c75e4b1a{S}",
            f"{P}1614079290101-0c2181ac8ea3{S}",
            f"{P}1614031679232-0dae776a72ee{S}",
            f"{P}1711527088900-f7ebabda4e3f{S}",
            f"{P}1611025504703-8c143abe6996{S}",
            f"{P}1552327359-d86398116072{S}",
            f"{P}1677123718817-5a203404d638{S}",
            f"{P}1668934804959-2cc138045bfb{S}",
        ],
        "footwear": [
            f"{P}1760302318631-a8d342cd4951{S}",
            f"{P}1695459468644-717c8ae17eed{S}",
            f"{P}1768225286074-9039931bb9d3{S}",
            f"{P}1618153478389-b2ed8de18ed3{S}",
            f"{P}1636705941762-ae56d531a7d7{S}",
            f"{P}1597081206405-5a13f38c5f71{S}",
            f"{P}1759542890353-35f5568c1c90{S}",
            f"{P}1650320079970-b4ee8f0dae33{S}",
            f"{P}1560857792-215f9e3534ed{S}",
            f"{P}1598808696311-66be744a23c4{S}",
        ],
        "general": [
            f"{P}1739773375456-79be292cedb1{S}",
            f"{P}1739773375426-880a10bea9a9{S}",
            f"{P}1731577506253-0fd9cd00ab7f{S}",
            f"{P}1735553816867-88cd8496df58{S}",
            f"{P}1735553816725-76d4fa5a374e{S}",
            f"{P}1735553816746-229df9b3bd37{S}",
            f"{P}1735553816769-7d30e5b1a19a{S}",
            f"{P}1735553816645-8441289f6db7{S}",
            f"{P}1735553816887-95a2657d5fd8{S}",
            f"{P}1735553816655-1d4cab9fb64c{S}",
        ],
    }

    # Map specific product categories to image groups
    CATEGORY_MAP = {
        "midi dress": "dress", "mini dress": "dress", "slip dress": "dress",
        "maxi dress": "dress", "shirt dress": "dress", "wrap dress": "dress",
        "bodycon dress": "dress", "dress": "dress",
        "crop top": "top", "tank top": "top", "blouse": "top",
        "t-shirt": "top", "cami top": "top", "corset top": "top",
        "hoodie": "top", "sweater": "top", "cardigan": "top", "top": "top",
        "cargo pants": "pants", "wide leg jeans": "pants",
        "wide leg pants": "pants", "jeans": "pants", "trousers": "pants",
        "joggers": "pants", "shorts": "pants", "pants": "pants",
        "leggings": "leggings",
        "mini skirt": "skirt", "skirt": "skirt", "midi skirt": "skirt",
        "pleated skirt": "skirt",
        "platform sneakers": "footwear", "platform boots": "footwear",
        "boots": "footwear", "heels": "footwear",
        "sandals": "footwear", "sneakers": "footwear", "mules": "footwear",
        "loafers": "footwear", "footwear": "footwear",
        "oversized blazer": "outerwear", "puffer jacket": "outerwear",
        "trench coat": "outerwear", "denim jacket": "outerwear",
        "leather jacket": "outerwear", "coat": "outerwear", "jacket": "outerwear",
        "blazer": "outerwear",
        "bag": "general", "sunglasses": "general", "jewelry": "general",
        "hat": "general", "belt": "general", "scarf": "general",
        "hair accessories": "general", "accessories": "general",
        "matching set": "general", "co-ord set": "general", "romper": "dress",
        "jumpsuit": "dress", "bodysuit": "top",
    }

    if force:
        trends = db.query(TrendItem).filter(TrendItem.status == "active").all()
    else:
        trends = db.query(TrendItem).filter(
            (TrendItem.image_url == None) | (TrendItem.image_url == ""),
            TrendItem.status == "active",
        ).all()

    if not trends:
        return {"updated": 0, "message": "All trends already have images"}

    updated = 0
    for trend in trends:
        cat = (trend.category or "").lower().strip()
        img_group = CATEGORY_MAP.get(cat, "general")
        images = FASHION_IMAGES.get(img_group, FASHION_IMAGES["general"])
        idx = trend.id % len(images)
        trend.image_url = images[idx]
        updated += 1

    db.commit()
    return {"updated": updated, "total_trends": len(trends), "message": f"Assigned images to {updated} trends"}


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
