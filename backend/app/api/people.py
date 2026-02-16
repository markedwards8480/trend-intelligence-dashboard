"""API routes for the People database — celebrities, influencers, brands, etc."""

import logging
from collections import Counter
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func
from typing import Optional, List

from app.models.database import get_db
from app.models.people import Person, PersonPlatform, ScrapedPost
from app.schemas.people import (
    PersonCreate,
    PersonBulkCreate,
    PersonResponse,
    PersonUpdate,
    PersonStats,
    PersonPlatformCreate,
    ScrapedPostResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/people", tags=["people"])


@router.get("/stats", response_model=PersonStats)
async def get_people_stats(db: Session = Depends(get_db)):
    """Get aggregate stats about the people database."""
    total = db.query(func.count(Person.id)).scalar() or 0
    active = db.query(func.count(Person.id)).filter(Person.active == True).scalar() or 0
    total_platforms = db.query(func.count(PersonPlatform.id)).scalar() or 0

    # By type
    type_rows = db.query(Person.type, func.count(Person.id)).group_by(Person.type).all()
    by_type = {t: c for t, c in type_rows}

    # By region
    region_rows = db.query(
        Person.primary_region, func.count(Person.id)
    ).filter(Person.primary_region.isnot(None)).group_by(Person.primary_region).all()
    by_region = {r: c for r, c in region_rows}

    # By tier
    tier_rows = db.query(
        Person.tier, func.count(Person.id)
    ).filter(Person.tier.isnot(None)).group_by(Person.tier).all()
    by_tier = {t: c for t, c in tier_rows}

    return PersonStats(
        total_people=total,
        by_type=by_type,
        by_region=by_region,
        by_tier=by_tier,
        total_platforms=total_platforms,
        active_count=active,
    )


@router.post("", response_model=PersonResponse)
async def add_person(data: PersonCreate, db: Session = Depends(get_db)):
    """Add a new person to track."""
    person = Person(
        name=data.name,
        type=data.type,
        tier=data.tier,
        bio=data.bio,
        primary_region=data.primary_region,
        secondary_regions=data.secondary_regions,
        demographics=data.demographics,
        style_tags=data.style_tags,
        categories=data.categories,
        scrape_frequency=data.scrape_frequency,
        priority=data.priority,
        notes=data.notes,
    )
    db.add(person)
    db.flush()

    # Add platforms
    total_followers = 0
    for p in data.platforms:
        pp = PersonPlatform(
            person_id=person.id,
            platform=p.platform,
            handle=p.handle,
            profile_url=p.profile_url or _build_profile_url(p.platform, p.handle),
            follower_count=p.follower_count,
            is_verified=p.is_verified,
        )
        db.add(pp)
        total_followers += p.follower_count

    person.follower_count_total = total_followers
    db.commit()
    db.refresh(person)
    return person


@router.post("/bulk", response_model=dict)
async def bulk_add_people(data: PersonBulkCreate, db: Session = Depends(get_db)):
    """Bulk import people. Skips duplicates by name."""
    created = 0
    skipped = 0
    errors = []

    for person_data in data.people:
        try:
            # Skip if person with same name already exists
            existing = db.query(Person).filter(
                func.lower(Person.name) == person_data.name.lower()
            ).first()
            if existing:
                skipped += 1
                continue

            person = Person(
                name=person_data.name,
                type=person_data.type,
                tier=person_data.tier,
                bio=person_data.bio,
                primary_region=person_data.primary_region,
                secondary_regions=person_data.secondary_regions,
                demographics=person_data.demographics,
                style_tags=person_data.style_tags,
                categories=person_data.categories,
                scrape_frequency=person_data.scrape_frequency,
                priority=person_data.priority,
                notes=person_data.notes,
            )
            db.add(person)
            db.flush()

            total_followers = 0
            for p in person_data.platforms:
                pp = PersonPlatform(
                    person_id=person.id,
                    platform=p.platform,
                    handle=p.handle,
                    profile_url=p.profile_url or _build_profile_url(p.platform, p.handle),
                    follower_count=p.follower_count,
                    is_verified=p.is_verified,
                )
                db.add(pp)
                total_followers += p.follower_count

            person.follower_count_total = total_followers
            created += 1

        except Exception as e:
            errors.append({"name": person_data.name, "error": str(e)[:200]})

    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors}


@router.get("", response_model=List[PersonResponse])
async def list_people(
    type: Optional[str] = None,
    tier: Optional[str] = None,
    region: Optional[str] = None,
    platform: Optional[str] = None,
    active: Optional[bool] = None,
    search: Optional[str] = None,
    sort_by: str = Query("relevance_score", regex="^(relevance_score|follower_count_total|name|added_at)$"),
    limit: int = Query(50, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """List people with filtering, search, and sorting."""
    query = db.query(Person).options(joinedload(Person.platforms))

    if type:
        query = query.filter(Person.type == type)
    if tier:
        query = query.filter(Person.tier == tier)
    if region:
        query = query.filter(Person.primary_region == region)
    if active is not None:
        query = query.filter(Person.active == active)
    if search:
        query = query.filter(Person.name.ilike(f"%{search}%"))
    if platform:
        query = query.join(PersonPlatform).filter(PersonPlatform.platform == platform)

    sort_col = getattr(Person, sort_by, Person.relevance_score)
    if sort_by == "name":
        query = query.order_by(sort_col)
    else:
        query = query.order_by(desc(sort_col))

    people = query.limit(limit).offset(offset).all()

    # Deduplicate from joinedload
    seen = set()
    unique = []
    for p in people:
        if p.id not in seen:
            seen.add(p.id)
            unique.append(p)

    return unique


@router.get("/{person_id}", response_model=PersonResponse)
async def get_person(person_id: int, db: Session = Depends(get_db)):
    """Get a specific person with their platforms."""
    person = db.query(Person).options(
        joinedload(Person.platforms)
    ).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    return person


@router.put("/{person_id}", response_model=PersonResponse)
async def update_person(
    person_id: int, update: PersonUpdate, db: Session = Depends(get_db)
):
    """Update a person's info."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    for field, value in update.model_dump(exclude_unset=True).items():
        setattr(person, field, value)

    db.commit()
    db.refresh(person)
    return person


@router.delete("/{person_id}")
async def delete_person(person_id: int, db: Session = Depends(get_db)):
    """Delete a person and all their platforms/scraped posts."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")
    db.delete(person)
    db.commit()
    return {"message": f"Deleted {person.name}"}


@router.post("/{person_id}/platforms", response_model=dict)
async def add_platform_to_person(
    person_id: int, platform: PersonPlatformCreate, db: Session = Depends(get_db)
):
    """Add a platform handle to an existing person."""
    person = db.query(Person).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    # Check duplicate
    existing = db.query(PersonPlatform).filter(
        PersonPlatform.person_id == person_id,
        PersonPlatform.platform == platform.platform,
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Already has {platform.platform} handle")

    pp = PersonPlatform(
        person_id=person_id,
        platform=platform.platform,
        handle=platform.handle,
        profile_url=platform.profile_url or _build_profile_url(platform.platform, platform.handle),
        follower_count=platform.follower_count,
        is_verified=platform.is_verified,
    )
    db.add(pp)

    # Update total follower count
    person.follower_count_total = (person.follower_count_total or 0) + platform.follower_count
    db.commit()
    return {"status": "added", "platform": platform.platform, "handle": platform.handle}


# --- Scraping endpoints ---

@router.post("/{person_id}/scrape")
async def scrape_person(person_id: int, db: Session = Depends(get_db)):
    """Trigger a scrape for a specific person."""
    person = db.query(Person).options(
        joinedload(Person.platforms)
    ).filter(Person.id == person_id).first()
    if not person:
        raise HTTPException(status_code=404, detail="Person not found")

    from app.services.scraping_service import ScrapingService
    scraper = ScrapingService()

    try:
        new_posts = await scraper.scrape_person(person, db)
        return {"status": "completed", "new_posts": new_posts, "person": person.name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scraping failed: {str(e)}")


@router.get("/{person_id}/posts", response_model=List[ScrapedPostResponse])
async def get_person_posts(
    person_id: int,
    limit: int = Query(20, ge=1, le=100),
    analyzed_only: bool = False,
    db: Session = Depends(get_db),
):
    """Get scraped posts for a person."""
    query = db.query(ScrapedPost).filter(ScrapedPost.person_id == person_id)
    if analyzed_only:
        query = query.filter(ScrapedPost.analyzed == True)
    posts = query.order_by(desc(ScrapedPost.scraped_at)).limit(limit).all()
    return posts


@router.post("/scrape-batch")
async def scrape_batch(
    type: Optional[str] = None,
    region: Optional[str] = None,
    priority_max: int = Query(5, ge=1, le=10),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    Trigger batch scraping for multiple people.
    Filters by type, region, and priority. Use for scheduled jobs.
    """
    query = db.query(Person).options(
        joinedload(Person.platforms)
    ).filter(
        Person.active == True,
        Person.priority <= priority_max,
    )
    if type:
        query = query.filter(Person.type == type)
    if region:
        query = query.filter(Person.primary_region == region)

    people = query.order_by(Person.priority, Person.last_scraped_at.asc().nullsfirst()).limit(limit).all()

    # Deduplicate
    seen = set()
    unique = []
    for p in people:
        if p.id not in seen:
            seen.add(p.id)
            unique.append(p)

    from app.services.scraping_service import ScrapingService
    scraper = ScrapingService()

    results = {"total_people": len(unique), "total_new_posts": 0, "errors": []}

    for person in unique:
        try:
            new_posts = await scraper.scrape_person(person, db)
            results["total_new_posts"] += new_posts
        except Exception as e:
            results["errors"].append({"name": person.name, "error": str(e)[:200]})

    return results


# --- Seed endpoint ---

@router.post("/seed")
async def seed_people_database(db: Session = Depends(get_db)):
    """
    Seed the people database with 60+ real celebrities, influencers,
    brands, editors, and stylists. Skips duplicates by name.
    """
    from app.data.seed_people import SEED_PEOPLE

    created = 0
    skipped = 0
    errors = []

    for person_data in SEED_PEOPLE:
        try:
            # Skip if already exists
            existing = db.query(Person).filter(
                func.lower(Person.name) == person_data["name"].lower()
            ).first()
            if existing:
                skipped += 1
                continue

            person = Person(
                name=person_data["name"],
                type=person_data["type"],
                tier=person_data.get("tier"),
                primary_region=person_data.get("primary_region"),
                secondary_regions=person_data.get("secondary_regions"),
                demographics=person_data.get("demographics"),
                style_tags=person_data.get("style_tags"),
                categories=person_data.get("categories"),
                scrape_frequency=person_data.get("scrape_frequency", "daily"),
                priority=person_data.get("priority", 5),
                notes=person_data.get("notes"),
            )
            db.add(person)
            db.flush()

            total_followers = 0
            for p in person_data.get("platforms", []):
                pp = PersonPlatform(
                    person_id=person.id,
                    platform=p["platform"],
                    handle=p["handle"],
                    profile_url=_build_profile_url(p["platform"], p["handle"]),
                    follower_count=p.get("follower_count", 0),
                    is_verified=p.get("is_verified", False),
                )
                db.add(pp)
                total_followers += p.get("follower_count", 0)

            person.follower_count_total = total_followers
            created += 1

        except Exception as e:
            errors.append({"name": person_data.get("name", "?"), "error": str(e)[:200]})

    db.commit()

    return {
        "message": f"Seeded {created} people ({skipped} already existed)",
        "created": created,
        "skipped": skipped,
        "errors": errors,
        "total_in_seed": len(SEED_PEOPLE),
    }


# --- Helpers ---

def _build_profile_url(platform: str, handle: str) -> str:
    """Build a profile URL from platform + handle."""
    handle = handle.lstrip("@")
    urls = {
        "instagram": f"https://www.instagram.com/{handle}/",
        "tiktok": f"https://www.tiktok.com/@{handle}",
        "twitter": f"https://x.com/{handle}",
        "pinterest": f"https://www.pinterest.com/{handle}/",
        "youtube": f"https://www.youtube.com/@{handle}",
    }
    return urls.get(platform, "")
