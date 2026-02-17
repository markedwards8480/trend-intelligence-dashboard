"""
Scraping Service — orchestrates data collection from social media
via Apify actors and official APIs.
"""

import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.models.people import Person, PersonPlatform, ScrapedPost

logger = logging.getLogger(__name__)

# Apify actor IDs for each platform
APIFY_ACTORS = {
    "instagram": "apify/instagram-post-scraper",
    "tiktok": "clockworks/tiktok-scraper",
    "twitter": "apify/twitter-scraper",
    "pinterest": "alexey/pinterest-crawler",
}


class ScrapingService:
    """Manages scraping jobs across platforms."""

    def __init__(self, apify_token: Optional[str] = None):
        self.apify_token = apify_token or settings.APIFY_TOKEN
        self._client = None

    @property
    def client(self):
        """Lazy-init Apify client."""
        if self._client is None:
            try:
                from apify_client import ApifyClient
                self._client = ApifyClient(self.apify_token)
            except ImportError:
                raise RuntimeError(
                    "apify-client not installed. Run: pip install apify-client"
                )
        return self._client

    async def scrape_instagram_profile(
        self, handle: str, max_posts: int = 10
    ) -> list[dict]:
        """
        Scrape recent posts from an Instagram profile via Apify.

        Returns list of dicts with: post_url, image_urls, caption,
        hashtags, likes, comments, posted_at, platform_post_id.
        """
        if not self.apify_token:
            logger.warning("No APIFY_TOKEN configured, returning empty results")
            return []

        actor = self.client.actor(APIFY_ACTORS["instagram"])
        run = actor.call(
            run_input={
                "username": [handle.lstrip("@")],
                "resultsLimit": max_posts,
                "resultsType": "posts",
            },
            timeout_secs=120,
        )

        results = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            hashtags = []
            caption = item.get("caption", "") or ""
            # Extract hashtags from caption
            import re
            hashtags = re.findall(r"#(\w+)", caption)

            results.append({
                "platform": "instagram",
                "platform_post_id": item.get("id") or item.get("shortCode"),
                "post_url": item.get("url") or f"https://www.instagram.com/p/{item.get('shortCode', '')}/",
                "image_urls": item.get("images") or ([item["displayUrl"]] if item.get("displayUrl") else []),
                "caption": caption,
                "hashtags": hashtags,
                "likes": item.get("likesCount", 0),
                "comments": item.get("commentsCount", 0),
                "shares": 0,  # Instagram doesn't expose shares
                "views": item.get("videoViewCount", 0),
                "posted_at": item.get("timestamp"),
            })

        logger.info(f"Scraped {len(results)} posts from Instagram @{handle}")
        return results

    async def scrape_tiktok_profile(
        self, handle: str, max_posts: int = 10
    ) -> list[dict]:
        """Scrape recent posts from a TikTok profile via Apify."""
        if not self.apify_token:
            return []

        actor = self.client.actor(APIFY_ACTORS["tiktok"])
        run = actor.call(
            run_input={
                "profiles": [handle.lstrip("@")],
                "resultsPerPage": max_posts,
                "shouldDownloadVideos": False,
            },
            timeout_secs=120,
        )

        results = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            caption = item.get("text", "") or ""
            import re
            hashtags = re.findall(r"#(\w+)", caption)

            results.append({
                "platform": "tiktok",
                "platform_post_id": str(item.get("id", "")),
                "post_url": item.get("webVideoUrl") or f"https://www.tiktok.com/@{handle}/video/{item.get('id', '')}",
                "image_urls": [item["videoMeta"]["coverUrl"]] if item.get("videoMeta", {}).get("coverUrl") else [],
                "caption": caption,
                "hashtags": hashtags,
                "likes": item.get("diggCount", 0),
                "comments": item.get("commentCount", 0),
                "shares": item.get("shareCount", 0),
                "views": item.get("playCount", 0),
                "posted_at": item.get("createTimeISO"),
            })

        logger.info(f"Scraped {len(results)} posts from TikTok @{handle}")
        return results

    async def scrape_person(
        self, person: Person, db: Session, max_posts_per_platform: int = 10
    ) -> dict:
        """
        Scrape all enabled platforms for a given person.
        Saves results to scraped_posts table.
        Returns dict with count and debug info.
        """
        new_count = 0
        debug_info = []

        if not self.apify_token:
            return {"new_posts": 0, "debug": ["NO APIFY_TOKEN configured — cannot scrape"]}

        for pp in person.platforms:
            if not pp.scrape_enabled:
                debug_info.append(f"{pp.platform}/@{pp.handle}: scrape_enabled=False, skipped")
                continue

            try:
                if pp.platform == "instagram":
                    posts = await self.scrape_instagram_profile(pp.handle, max_posts_per_platform)
                elif pp.platform == "tiktok":
                    posts = await self.scrape_tiktok_profile(pp.handle, max_posts_per_platform)
                else:
                    debug_info.append(f"{pp.platform}/@{pp.handle}: unsupported platform, skipped")
                    continue

                debug_info.append(f"{pp.platform}/@{pp.handle}: got {len(posts)} posts from Apify")

                for post_data in posts:
                    # Skip if we already have this post
                    existing = db.query(ScrapedPost).filter(
                        ScrapedPost.platform == post_data["platform"],
                        ScrapedPost.platform_post_id == post_data["platform_post_id"],
                    ).first()

                    if existing:
                        # Update engagement metrics
                        existing.likes = post_data["likes"]
                        existing.comments = post_data["comments"]
                        existing.shares = post_data["shares"]
                        existing.views = post_data["views"]
                        continue

                    # Create new scraped post
                    scraped = ScrapedPost(
                        person_id=person.id,
                        platform=post_data["platform"],
                        platform_post_id=post_data["platform_post_id"],
                        post_url=post_data["post_url"],
                        image_urls=post_data["image_urls"],
                        caption=post_data["caption"],
                        hashtags=post_data["hashtags"],
                        likes=post_data["likes"],
                        comments=post_data["comments"],
                        shares=post_data["shares"],
                        views=post_data["views"],
                        posted_at=post_data.get("posted_at"),
                    )
                    db.add(scraped)
                    new_count += 1

                # Update platform last_checked
                pp.last_checked = datetime.utcnow()

            except Exception as e:
                debug_info.append(f"{pp.platform}/@{pp.handle}: ERROR — {str(e)[:300]}")
                logger.error(f"Error scraping {pp.platform} for {person.name}: {e}")
                continue

        # Update person last_scraped
        person.last_scraped_at = datetime.utcnow()
        db.commit()

        logger.info(f"Scraped {person.name}: {new_count} new posts")
        return {"new_posts": new_count, "debug": debug_info}

    async def scrape_hashtag_instagram(
        self, hashtag: str, max_posts: int = 20
    ) -> list[dict]:
        """Scrape top posts for an Instagram hashtag."""
        if not self.apify_token:
            return []

        actor = self.client.actor("apify/instagram-hashtag-scraper")
        run = actor.call(
            run_input={
                "hashtags": [hashtag.lstrip("#")],
                "resultsLimit": max_posts,
                "resultsType": "posts",
            },
            timeout_secs=120,
        )

        results = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            caption = item.get("caption", "") or ""
            import re
            hashtags = re.findall(r"#(\w+)", caption)

            results.append({
                "platform": "instagram",
                "platform_post_id": item.get("id") or item.get("shortCode"),
                "post_url": item.get("url", ""),
                "image_urls": [item["displayUrl"]] if item.get("displayUrl") else [],
                "caption": caption,
                "hashtags": hashtags,
                "likes": item.get("likesCount", 0),
                "comments": item.get("commentsCount", 0),
                "owner_username": item.get("ownerUsername", ""),
            })

        return results
