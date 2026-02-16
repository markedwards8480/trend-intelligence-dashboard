"""
Celery application configuration for background and scheduled tasks.
"""

from celery import Celery
from celery.schedules import crontab
from app.config import settings

celery = Celery(
    "trend_intelligence",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["app.tasks.scraping_tasks"],
)

celery.conf.update(
    # Serialization
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="America/Los_Angeles",
    enable_utc=True,

    # Task behavior
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    task_soft_time_limit=300,   # 5 min soft limit
    task_time_limit=600,        # 10 min hard limit

    # Beat schedule — automated scraping jobs
    beat_schedule={
        # Nightly full scrape of high-priority people (priority 1-3)
        "nightly-scrape-priority": {
            "task": "app.tasks.scraping_tasks.scrape_priority_people",
            "schedule": crontab(hour=2, minute=0),  # 2 AM PT
            "kwargs": {"priority_max": 3, "limit": 50},
        },
        # Morning scrape of celebrities (most time-sensitive)
        "morning-scrape-celebrities": {
            "task": "app.tasks.scraping_tasks.scrape_by_type",
            "schedule": crontab(hour=7, minute=0),  # 7 AM PT
            "kwargs": {"person_type": "celebrity", "limit": 30},
        },
        # Midday scrape of influencers
        "midday-scrape-influencers": {
            "task": "app.tasks.scraping_tasks.scrape_by_type",
            "schedule": crontab(hour=12, minute=0),  # noon PT
            "kwargs": {"person_type": "influencer", "limit": 30},
        },
        # Weekly full database scrape (Sunday night)
        "weekly-full-scrape": {
            "task": "app.tasks.scraping_tasks.scrape_priority_people",
            "schedule": crontab(hour=1, minute=0, day_of_week=0),  # Sunday 1 AM
            "kwargs": {"priority_max": 10, "limit": 200},
        },
    },
)
