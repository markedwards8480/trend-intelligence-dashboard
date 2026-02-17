"""
Scraping Service — orchestrates data collection from social media
via Apify actors and official APIs.
"""

import re
import logging
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session

from app.config import settings
from app.models.people import Person, PersonPlatform, ScrapedPost

logger = logging.getLogger(__name__)

# Correct Apify actor IDs (verified Feb 2026)
APIFY_ACTORS = {
    "instagram": "apify/instagram-scraper",        # General IG scraper — profiles, posts, hashtags
    "tiktok": "clockworks/tiktok-scraper",          # TikTok profile/post scraper
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
        """Lazy-init Apify client, auto-installing if needed."""
        if self._client is None:
            try:
                from apify_client import ApifyClient
            except ImportError:
                logger.warning("apify-client not found, installing...")
                import subprocess
                subprocess.check_call(["pip", "install", "apify-client>=2.4.0"])
                from apify_client import ApifyClient
            self._client = ApifyClient(self.apify_token)
        return self._client

    async def scrape_instagram_profile(
        self, handle: str, max_posts: int = 10
    ) -> list[dict]:
        """
        Scrape recent posts from an Instagram profile via Apify.
        Uses apify/instagram-scraper with username input.
        """
        if not self.apify_token:
            logger.warning("No APIFY_TOKEN configured, returning empty results")
            return []

        clean_handle = handle.lstrip("@")
        logger.info(f"Starting IG scrape for @{clean_handle} (max {max_posts} posts)")

        actor = self.client.actor(APIFY_ACTORS["instagram"])
        run = actor.call(
            run_input={
                "username": [clean_handle],
                "resultsLimit": max_posts,
            },
            timeout_secs=180,
        )

        logger.info(f"IG Apify run completed, dataset: {run.get('defaultDatasetId')}")

        results = []
        item_count = 0
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            item_count += 1
            caption = item.get("caption", "") or ""
            hashtags = re.findall(r"#(\w+)", caption)

            # Build post URL from various possible fields
            post_url = (
                item.get("url")
                or item.get("postUrl")
                or item.get("displayUrl")
                or f"https://www.instagram.com/p/{item.get('shortCode', item.get('id', ''))}/",
            )
            if isinstance(post_url, tuple):
                post_url = post_url[0]

            # Gather image URLs from various possible fields
            image_urls = []
            if item.get("images"):
                image_urls = item["images"] if isinstance(item["images"], list) else [item["images"]]
            elif item.get("displayUrl"):
                image_urls = [item["displayUrl"]]
            elif item.get("imageUrl"):
                image_urls = [item["imageUrl"]]

            # Post ID from various possible fields
            post_id = str(item.get("id") or item.get("shortCode") or item.get("pk") or f"ig_{item_count}")

            results.append({
                "platform": "instagram",
                "platform_post_id": post_id,
                "post_url": post_url,
                "image_urls": image_urls,
                "caption": caption,
                "hashtags": hashtags,
                "likes": item.get("likesCount", 0) or item.get("likes", 0) or 0,
                "comments": item.get("commentsCount", 0) or item.get("comments", 0) or 0,
                "shares": 0,
                "views": item.get("videoViewCount", 0) or item.get("videoPlayCount", 0) or 0,
                "posted_at": item.get("timestamp") or item.get("takenAtTimestamp"),
            })

        logger.info(f"Scraped {len(results)} posts from Instagram @{clean_handle} ({item_count} items from Apify)")
        return results

    async def scrape_tiktok_profile(
        self, handle: str, max_posts: int = 10
    ) -> list[dict]:
        """Scrape recent posts from a TikTok profile via Apify."""
        if not self.apify_token:
            return []

        clean_handle = handle.lstrip("@")
        logger.info(f"Starting TikTok scrape for @{clean_handle}")

        actor = self.client.actor(APIFY_ACTORS["tiktok"])
        run = actor.call(
            run_input={
                "profiles": [clean_handle],
                "resultsPerPage": max_posts,
                "shouldDownloadVideos": False,
            },
            timeout_secs=180,
        )

        logger.info(f"TikTok Apify run completed, dataset: {run.get('defaultDatasetId')}")

        results = []
        item_count = 0
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            item_count += 1
            caption = item.get("text", "") or item.get("desc", "") or ""
            hashtags = re.findall(r"#(\w+)", caption)

            # Cover image from various possible fields
            cover_url = None
            if item.get("videoMeta", {}).get("coverUrl"):
                cover_url = item["videoMeta"]["coverUrl"]
            elif item.get("covers", {}).get("default"):
                cover_url = item["covers"]["default"]
            elif item.get("video", {}).get("cover"):
                cover_url = item["video"]["cover"]

            post_id = str(item.get("id", "") or f"tt_{item_count}")

            results.append({
                "platform": "tiktok",
                "platform_post_id": post_id,
                "post_url": item.get("webVideoUrl") or item.get("url") or f"https://www.tiktok.com/@{clean_handle}/video/{post_id}",
                "image_urls": [cover_url] if cover_url else [],
                "caption": caption,
                "hashtags": hashtags,
                "likes": item.get("diggCount", 0) or item.get("likes", 0) or 0,
                "comments": item.get("commentCount", 0) or item.get("comments", 0) or 0,
                "shares": item.get("shareCount", 0) or item.get("shares", 0) or 0,
                "views": item.get("playCount", 0) or item.get("views", 0) or 0,
                "posted_at": item.get("createTimeISO") or item.get("createTime"),
            })

        logger.info(f"Scraped {len(results)} posts from TikTok @{clean_handle} ({item_count} items from Apify)")
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
                logger.error(f"Error scraping {pp.platform} for {person.name}: {e}", exc_info=True)
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

        actor = self.client.actor("apify/instagram-scraper")
        run = actor.call(
            run_input={
                "hashtags": [hashtag.lstrip("#")],
                "resultsLimit": max_posts,
            },
            timeout_secs=120,
        )

        results = []
        for item in self.client.dataset(run["defaultDatasetId"]).iterate_items():
            caption = item.get("caption", "") or ""
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
