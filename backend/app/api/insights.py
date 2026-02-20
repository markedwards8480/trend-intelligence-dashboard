import threading
from datetime import datetime, timezone
from typing import List, Optional
from collections import Counter

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.database import get_db, SessionLocal
from app.models.models import TrendItem, TrendInsight, ThemedLook
from app.schemas.schemas import (
    TrendInsightResponse,
    ThemedLookResponse,
    InsightsResponse,
    InsightsStatusResponse,
)
from app.services.ai_service import AIService

router = APIRouter(prefix="/api/insights", tags=["insights"])

# Background job state
_insights_status = {
    "status": "idle",
    "progress": None,
    "started_at": None,
    "completed_at": None,
    "error": None,
}


def _run_insights_generation():
    """Background thread: aggregate trend data and generate AI insights."""
    global _insights_status
    db = SessionLocal()

    try:
        _insights_status["progress"] = "Aggregating trend data by category..."

        # 1. Get all active trends
        trends = db.query(TrendItem).filter(TrendItem.status == "active").all()
        if not trends:
            _insights_status["status"] = "failed"
            _insights_status["error"] = "No active trends found"
            return

        # 2. Aggregate by category
        category_map = {}
        for t in trends:
            cat = t.category or "uncategorized"
            if cat not in category_map:
                category_map[cat] = {
                    "category": cat,
                    "items": [],
                    "colors": [],
                    "patterns": [],
                    "styles": [],
                    "fabrications": [],
                    "demographics": [],
                    "price_points": [],
                    "scores": [],
                }
            entry = category_map[cat]
            entry["items"].append(t)
            entry["scores"].append(t.trend_score or 0)
            entry["colors"].extend(t.colors or [])
            entry["patterns"].extend(t.patterns or [])
            entry["styles"].extend(t.style_tags or [])
            entry["fabrications"].extend(t.fabrications or [])
            if t.demographic:
                entry["demographics"].append(t.demographic)
            if t.price_point:
                entry["price_points"].append(t.price_point)

        # Build aggregated data for AI
        category_data = []
        for cat, data in sorted(category_map.items(), key=lambda x: len(x[1]["items"]), reverse=True):
            if len(data["items"]) < 2:
                continue  # Skip categories with very few items
            category_data.append({
                "category": cat,
                "count": len(data["items"]),
                "avg_score": sum(data["scores"]) / len(data["scores"]) if data["scores"] else 0,
                "top_colors": [c for c, _ in Counter(data["colors"]).most_common(5)],
                "top_patterns": [p for p, _ in Counter(data["patterns"]).most_common(4)],
                "top_styles": [s for s, _ in Counter(data["styles"]).most_common(5)],
                "top_fabrications": [f for f, _ in Counter(data["fabrications"]).most_common(4)],
                "demographics": [d for d, _ in Counter(data["demographics"]).most_common(3)],
                "price_points": [p for p, _ in Counter(data["price_points"]).most_common(3)],
            })

        _insights_status["progress"] = f"Generating AI insights for {len(category_data)} categories..."

        # 3. Call AI for category insights
        try:
            insights_results = AIService.generate_category_insights_sync(category_data)
        except Exception as e:
            print(f"Category insights generation failed: {e}")
            import traceback
            traceback.print_exc()
            _insights_status["status"] = "failed"
            _insights_status["error"] = f"Category insights failed: {str(e)}"
            return

        # 4. Persist category insights (upsert)
        _insights_status["progress"] = "Saving category insights..."
        for insight in insights_results:
            cat_name = insight.get("category", "")
            if not cat_name:
                continue

            existing = db.query(TrendInsight).filter(TrendInsight.category == cat_name).first()
            agg = next((c for c in category_data if c["category"] == cat_name), None)

            if existing:
                existing.summary = insight.get("summary", "")
                existing.key_characteristics = insight.get("key_characteristics", {})
                existing.trending_items_count = agg["count"] if agg else 0
                existing.avg_trend_score = agg["avg_score"] if agg else 0
                existing.style_tags_distribution = {
                    s: c for s, c in Counter(
                        category_map.get(cat_name, {}).get("styles", [])
                    ).most_common(10)
                } if cat_name in category_map else {}
                existing.generated_at = datetime.now(timezone.utc)
            else:
                new_insight = TrendInsight(
                    category=cat_name,
                    summary=insight.get("summary", ""),
                    key_characteristics=insight.get("key_characteristics", {}),
                    trending_items_count=agg["count"] if agg else 0,
                    avg_trend_score=agg["avg_score"] if agg else 0,
                    style_tags_distribution={
                        s: c for s, c in Counter(
                            category_map.get(cat_name, {}).get("styles", [])
                        ).most_common(10)
                    } if cat_name in category_map else {},
                )
                db.add(new_insight)

        db.commit()

        # 5. Generate themed looks
        _insights_status["progress"] = "Creating themed fashion looks..."

        # Build a summary of all trends for the theme generator
        all_colors = []
        all_styles = []
        all_categories = []
        all_fabrications = []
        for data in category_map.values():
            all_colors.extend(data["colors"])
            all_styles.extend(data["styles"])
            all_fabrications.extend(data["fabrications"])
            all_categories.append(data["category"])

        trend_summary = (
            f"Total trends: {len(trends)} across {len(category_map)} categories.\n"
            f"Top categories: {', '.join(c for c, _ in Counter(t.category or '' for t in trends).most_common(10))}\n"
            f"Top colors: {', '.join(c for c, _ in Counter(all_colors).most_common(10))}\n"
            f"Top style tags: {', '.join(s for s, _ in Counter(all_styles).most_common(10))}\n"
            f"Top fabrications: {', '.join(f for f, _ in Counter(all_fabrications).most_common(8))}\n"
            f"Demographics: mostly junior_girls and young_women\n"
        )

        try:
            themes_results = AIService.generate_themed_looks_sync(
                trend_summary, list(set(all_categories))
            )
        except Exception as e:
            print(f"Themed looks generation failed: {e}")
            import traceback
            traceback.print_exc()
            # Don't fail the whole job — category insights were saved
            _insights_status["progress"] = "Category insights saved. Themed looks generation failed."
            themes_results = []

        # 6. Persist themed looks (clear old, insert new)
        if themes_results:
            _insights_status["progress"] = "Saving themed looks..."
            db.query(ThemedLook).delete()

            for theme in themes_results:
                # Try to find matching trend IDs for this theme
                theme_styles = theme.get("style_tags", [])
                theme_colors = theme.get("color_palette", [])
                featured_ids = []

                # Match trends that share style tags or colors
                for t in trends:
                    t_styles = set(t.style_tags or [])
                    t_colors = set(c.lower() for c in (t.colors or []))
                    theme_style_set = set(s.lower() for s in theme_styles)
                    theme_color_set = set(c.lower() for c in theme_colors)

                    if (t_styles & theme_style_set) or (t_colors & theme_color_set):
                        featured_ids.append(t.id)
                        if len(featured_ids) >= 12:
                            break

                new_theme = ThemedLook(
                    theme_name=theme.get("theme_name", "Untitled"),
                    description=theme.get("description", ""),
                    color_palette=theme.get("color_palette", []),
                    key_items=theme.get("key_items", []),
                    style_tags=theme.get("style_tags", []),
                    mood_description=theme.get("mood_description"),
                    demographic_appeal=theme.get("demographic_appeal", []),
                    featured_trend_ids=featured_ids if featured_ids else None,
                )
                db.add(new_theme)

            db.commit()

        _insights_status["status"] = "completed"
        _insights_status["progress"] = f"Generated {len(insights_results)} category insights and {len(themes_results)} themed looks"
        _insights_status["completed_at"] = datetime.now(timezone.utc).isoformat()

    except Exception as e:
        import traceback
        traceback.print_exc()
        _insights_status["status"] = "failed"
        _insights_status["error"] = str(e)
    finally:
        db.close()


@router.post("/generate")
async def start_insights_generation():
    """Start background AI generation of category insights and themed looks."""
    global _insights_status

    if _insights_status["status"] == "running":
        return {"message": "Generation already in progress", "status": "running"}

    _insights_status = {
        "status": "running",
        "progress": "Starting...",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "completed_at": None,
        "error": None,
    }

    thread = threading.Thread(target=_run_insights_generation, daemon=True)
    thread.start()

    return {"message": "Insights generation started", "status": "running"}


@router.get("/status", response_model=InsightsStatusResponse)
async def get_insights_status():
    """Poll the status of insights generation."""
    return InsightsStatusResponse(**_insights_status)


@router.get("", response_model=InsightsResponse)
async def get_insights(
    demographic: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    """Get latest generated insights and themed looks."""
    insights_query = db.query(TrendInsight).order_by(desc(TrendInsight.trending_items_count))
    insights = insights_query.all()

    themes_query = db.query(ThemedLook).order_by(desc(ThemedLook.generated_at))
    if demographic:
        # Filter themes that appeal to this demographic
        themes = [
            t for t in themes_query.all()
            if demographic in (t.demographic_appeal or [])
        ]
    else:
        themes = themes_query.all()

    latest_date = None
    if insights:
        latest_date = max(i.generated_at for i in insights if i.generated_at)

    return InsightsResponse(
        category_insights=insights,
        themed_looks=themes,
        generated_at=latest_date,
    )
