"""
Celery tasks for scheduled social media scraping.

These tasks run on a schedule (via celery beat) to keep the
scraped_posts table fresh with the latest content from tracked
celebrities, influencers, and brands.
"""

import logging
import asyncio
from typing import Optional

from app.celery_app import celery
from app.models.database import SessionLocal
from app.models.people import Person, PersonPlatform
from app.services.scraping_service import ScrapingService
from sqlalchemy.orm import joinedload
from sqlalchemy import func

logger = logging.getLogger(__name__)


def _run_async(coro):
    """Run an async function from a sync Celery task."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@celery.task(name="app.tasks.scraping_tasks.scrape_priority_people")
def scrape_priority_people(priority_max: int = 5, limit: int = 50):
    """
    Scrape active people with priority <= priority_max.
    Ordered by priority (most important first), then by least recently scraped.
    """
    db = SessionLocal()
    scraper = ScrapingService()
    results = {"scraped": 0, "new_posts": 0, "errors": []}

    try:
        people = (
            db.query(Person)
            .options(joinedload(Person.platforms))
            .filter(Person.active == True, Person.priority <= priority_max)
            .order_by(Person.priority, Person.last_scraped_at.asc().nullsfirst())
            .limit(limit)
            .all()
        )

        # Deduplicate from joinedload
        seen = set()
        unique = []
        for p in people:
            if p.id not in seen:
                seen.add(p.id)
                unique.append(p)

        logger.info(
            f"Starting priority scrape: {len(unique)} people "
            f"(priority <= {priority_max})"
        )

        for person in unique:
            try:
                new_posts = _run_async(scraper.scrape_person(person, db))
                results["new_posts"] += new_posts
                results["scraped"] += 1
                logger.info(f"  {person.name}: {new_posts} new posts")
            except Exception as e:
                error_msg = f"{person.name}: {str(e)[:200]}"
                results["errors"].append(error_msg)
                logger.error(f"  Error scraping {person.name}: {e}")

    except Exception as e:
        logger.error(f"scrape_priority_people failed: {e}")
        results["errors"].append(str(e)[:200])
    finally:
        db.close()

    logger.info(
        f"Priority scrape complete: {results['scraped']} people, "
        f"{results['new_posts']} new posts, {len(results['errors'])} errors"
    )
    return results


@celery.task(name="app.tasks.scraping_tasks.scrape_by_type")
def scrape_by_type(
    person_type: str,
    region: Optional[str] = None,
    limit: int = 30,
):
    """
    Scrape active people of a specific type (celebrity, influencer, brand, etc.).
    """
    db = SessionLocal()
    scraper = ScrapingService()
    results = {"type": person_type, "scraped": 0, "new_posts": 0, "errors": []}

    try:
        query = (
            db.query(Person)
            .options(joinedload(Person.platforms))
            .filter(Person.active == True, Person.type == person_type)
        )
        if region:
            query = query.filter(Person.primary_region == region)

        people = (
            query.order_by(Person.priority, Person.last_scraped_at.asc().nullsfirst())
            .limit(limit)
            .all()
        )

        seen = set()
        unique = []
        for p in people:
            if p.id not in seen:
                seen.add(p.id)
                unique.append(p)

        logger.info(f"Starting type scrape: {len(unique)} {person_type}s")

        for person in unique:
            try:
                new_posts = _run_async(scraper.scrape_person(person, db))
                results["new_posts"] += new_posts
                results["scraped"] += 1
            except Exception as e:
                results["errors"].append(f"{person.name}: {str(e)[:200]}")
                logger.error(f"  Error scraping {person.name}: {e}")

    except Exception as e:
        logger.error(f"scrape_by_type({person_type}) failed: {e}")
        results["errors"].append(str(e)[:200])
    finally:
        db.close()

    logger.info(
        f"Type scrape ({person_type}) complete: {results['scraped']} people, "
        f"{results['new_posts']} new posts"
    )
    return results


@celery.task(name="app.tasks.scraping_tasks.scrape_single_person")
def scrape_single_person(person_id: int):
    """Scrape a single person by ID. Used for on-demand scraping from the UI."""
    db = SessionLocal()
    scraper = ScrapingService()

    try:
        person = (
            db.query(Person)
            .options(joinedload(Person.platforms))
            .filter(Person.id == person_id)
            .first()
        )
        if not person:
            return {"error": f"Person {person_id} not found"}

        new_posts = _run_async(scraper.scrape_person(person, db))
        return {"person": person.name, "new_posts": new_posts}

    except Exception as e:
        logger.error(f"scrape_single_person({person_id}) failed: {e}")
        return {"error": str(e)[:200]}
    finally:
        db.close()
