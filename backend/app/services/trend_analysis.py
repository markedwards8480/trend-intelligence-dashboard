"""
Trend Analysis Engine — processes scraped posts to detect emerging fashion trends.

Analyzes hashtags, captions, and cross-person patterns to surface
trends relevant to the junior girls (15-28) market.
"""

import logging
import re
from collections import Counter, defaultdict
from datetime import datetime, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from app.models.people import Person, ScrapedPost

logger = logging.getLogger(__name__)

# Fashion-relevant hashtag categories for the junior market
FASHION_KEYWORDS = {
    "categories": [
        "dress", "dresses", "midi", "maxi", "mini", "skirt", "top", "crop",
        "jeans", "denim", "pants", "trousers", "blazer", "jacket", "coat",
        "sweater", "hoodie", "cardigan", "bodysuit", "romper", "jumpsuit",
        "bikini", "swimwear", "lingerie", "activewear", "athleisure",
        "sneakers", "heels", "boots", "sandals", "shoes", "bag", "handbag",
        "jewelry", "earrings", "necklace", "bracelet", "sunglasses",
        "hat", "scarf", "belt",
    ],
    "styles": [
        "streetwear", "y2k", "cottagecore", "coquette", "balletcore",
        "quietluxury", "oldmoney", "coastal", "coastalgranddaughter",
        "mobwife", "cleangirlera", "cleangirl", "thatgirl",
        "darkfeminine", "lightacademia", "darkacademia", "grunge",
        "boho", "bohemian", "minimalist", "maximalist", "preppy",
        "fairycore", "goblincore", "gorpcore", "normcore",
        "blokette", "tenniscore", "officecore", "corporate",
        "downtown", "uptown", "tomato", "tomatogirl",
        "vanilla", "vanillagirl", "strawberry", "strawberrygirl",
        "cherryred", "burgandyfall", "butter", "lavenderhaze",
        "dopamine", "dopaminedressing", "barbiecore", "mermaidcore",
        "retrofuturism", "cybercore", "westernchic",
        "quiet", "luxury", "effortless", "aesthetic",
    ],
    "colors": [
        "red", "blue", "green", "pink", "black", "white", "beige",
        "navy", "burgundy", "lavender", "sage", "olive", "coral",
        "pastel", "neon", "neutral", "earth", "jeweltone",
        "chocolate", "camel", "cream", "ivory", "blush",
        "terracotta", "rust", "mustard", "forest",
    ],
    "patterns": [
        "plaid", "stripe", "striped", "floral", "leopard", "animal",
        "polkadot", "checkered", "gingham", "houndstooth",
        "tie-dye", "tiedye", "camo", "abstract", "geometric",
        "paisley", "colorblock", "ombre",
    ],
    "fabrics": [
        "silk", "satin", "velvet", "leather", "denim", "linen",
        "cotton", "cashmere", "wool", "mesh", "lace", "tulle",
        "sequin", "crochet", "knit", "sheer",
    ],
}

# Flatten all fashion keywords for quick lookup
ALL_FASHION_TERMS = set()
for terms in FASHION_KEYWORDS.values():
    ALL_FASHION_TERMS.update(t.lower() for t in terms)

# Non-fashion hashtags to filter out
NOISE_HASHTAGS = {
    "love", "instagood", "photooftheday", "beautiful", "happy",
    "cute", "selfie", "me", "follow", "like", "followme",
    "picoftheday", "instadaily", "amazing", "fun", "summer",
    "winter", "spring", "fall", "life", "smile", "music",
    "food", "fitness", "workout", "travel", "photography",
    "nature", "art", "friends", "family", "dog", "cat",
    "reels", "reel", "viral", "trending", "fyp", "foryou",
    "foryoupage", "explore", "explorepage", "ad", "sponsored",
    "gifted", "collab", "collaboration",
}


class TrendAnalysisEngine:
    """Analyzes scraped posts to detect fashion trends."""

    def __init__(self, db: Session):
        self.db = db

    def analyze_recent_posts(
        self,
        days: int = 7,
        min_mentions: int = 2,
    ) -> dict:
        """
        Analyze all scraped posts from the last N days.
        Returns trend insights grouped by category.
        """
        cutoff = datetime.utcnow() - timedelta(days=days)

        posts = (
            self.db.query(ScrapedPost)
            .filter(ScrapedPost.scraped_at >= cutoff)
            .order_by(desc(ScrapedPost.scraped_at))
            .all()
        )

        if not posts:
            return {
                "period_days": days,
                "total_posts_analyzed": 0,
                "trending_hashtags": [],
                "trending_styles": [],
                "trending_categories": [],
                "trending_colors": [],
                "trending_patterns": [],
                "top_posts": [],
                "cross_person_trends": [],
                "insights": [],
            }

        # Collect all hashtags and caption keywords
        hashtag_counts = Counter()
        hashtag_engagement = defaultdict(lambda: {"likes": 0, "comments": 0, "posts": 0, "people": set()})
        style_mentions = Counter()
        category_mentions = Counter()
        color_mentions = Counter()
        pattern_mentions = Counter()
        fabric_mentions = Counter()
        person_trends = defaultdict(lambda: defaultdict(int))  # person_id -> {trend: count}

        for post in posts:
            # Process hashtags
            if post.hashtags:
                for tag in post.hashtags:
                    tag_lower = tag.lower().strip()
                    if tag_lower in NOISE_HASHTAGS or len(tag_lower) < 3:
                        continue
                    hashtag_counts[tag_lower] += 1
                    hashtag_engagement[tag_lower]["likes"] += (post.likes or 0)
                    hashtag_engagement[tag_lower]["comments"] += (post.comments or 0)
                    hashtag_engagement[tag_lower]["posts"] += 1
                    hashtag_engagement[tag_lower]["people"].add(post.person_id)

            # Process caption for fashion terms
            caption_text = (post.caption or "").lower()
            all_text = caption_text
            if post.hashtags:
                all_text += " " + " ".join(h.lower() for h in post.hashtags)

            for term in FASHION_KEYWORDS["styles"]:
                if term.lower() in all_text:
                    style_mentions[term] += 1
                    person_trends[post.person_id][f"style:{term}"] += 1

            for term in FASHION_KEYWORDS["categories"]:
                if re.search(rf'\b{re.escape(term.lower())}\b', all_text):
                    category_mentions[term] += 1
                    person_trends[post.person_id][f"cat:{term}"] += 1

            for term in FASHION_KEYWORDS["colors"]:
                if re.search(rf'\b{re.escape(term.lower())}\b', all_text):
                    color_mentions[term] += 1

            for term in FASHION_KEYWORDS["patterns"]:
                if re.search(rf'\b{re.escape(term.lower())}\b', all_text):
                    pattern_mentions[term] += 1

            for term in FASHION_KEYWORDS["fabrics"]:
                if re.search(rf'\b{re.escape(term.lower())}\b', all_text):
                    fabric_mentions[term] += 1

        # Build trending hashtags with engagement data
        trending_hashtags = []
        for tag, count in hashtag_counts.most_common(50):
            if count < min_mentions:
                continue
            eng = hashtag_engagement[tag]
            is_fashion = tag in ALL_FASHION_TERMS or any(
                kw in tag for kw in ["fashion", "style", "outfit", "ootd", "wear", "look"]
            )
            trending_hashtags.append({
                "hashtag": tag,
                "count": count,
                "total_likes": eng["likes"],
                "total_comments": eng["comments"],
                "unique_people": len(eng["people"]),
                "avg_engagement": round((eng["likes"] + eng["comments"]) / eng["posts"], 1) if eng["posts"] else 0,
                "is_fashion_related": is_fashion,
            })

        # Cross-person trend detection (trends appearing across multiple people)
        cross_person = []
        all_trend_keys = defaultdict(set)
        for person_id, trends in person_trends.items():
            for trend_key in trends:
                all_trend_keys[trend_key].add(person_id)

        for trend_key, people_set in all_trend_keys.items():
            if len(people_set) >= min_mentions:
                # Look up person names
                people_names = []
                people_objs = self.db.query(Person.name).filter(
                    Person.id.in_(list(people_set))
                ).all()
                people_names = [p.name for p in people_objs]

                kind, term = trend_key.split(":", 1)
                cross_person.append({
                    "trend": term,
                    "type": "style" if kind == "style" else "category",
                    "people_count": len(people_set),
                    "people": people_names[:10],
                })

        cross_person.sort(key=lambda x: x["people_count"], reverse=True)

        # Top posts by engagement
        top_posts = sorted(posts, key=lambda p: (p.likes or 0) + (p.comments or 0) * 3, reverse=True)[:20]
        top_post_data = []
        # Batch load person names
        person_ids = list(set(p.person_id for p in top_posts))
        person_map = {}
        if person_ids:
            people = self.db.query(Person).filter(Person.id.in_(person_ids)).all()
            person_map = {p.id: p for p in people}

        for post in top_posts:
            person = person_map.get(post.person_id)
            top_post_data.append({
                "id": post.id,
                "person_name": person.name if person else "Unknown",
                "person_type": person.type if person else "unknown",
                "platform": post.platform,
                "post_url": post.post_url,
                "image_urls": post.image_urls or [],
                "caption": (post.caption or "")[:300],
                "hashtags": post.hashtags or [],
                "likes": post.likes or 0,
                "comments": post.comments or 0,
                "shares": post.shares or 0,
                "views": post.views or 0,
                "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                "scraped_at": post.scraped_at.isoformat() if post.scraped_at else None,
            })

        # Generate insight summaries
        insights = self._generate_insights(
            style_mentions, category_mentions, color_mentions,
            cross_person, len(posts), days,
        )

        return {
            "period_days": days,
            "total_posts_analyzed": len(posts),
            "trending_hashtags": trending_hashtags[:30],
            "trending_styles": [
                {"term": t, "count": c} for t, c in style_mentions.most_common(20) if c >= min_mentions
            ],
            "trending_categories": [
                {"term": t, "count": c} for t, c in category_mentions.most_common(20) if c >= min_mentions
            ],
            "trending_colors": [
                {"term": t, "count": c} for t, c in color_mentions.most_common(15) if c >= min_mentions
            ],
            "trending_patterns": [
                {"term": t, "count": c} for t, c in pattern_mentions.most_common(10) if c >= min_mentions
            ],
            "trending_fabrics": [
                {"term": t, "count": c} for t, c in fabric_mentions.most_common(10) if c >= min_mentions
            ],
            "top_posts": top_post_data,
            "cross_person_trends": cross_person[:20],
            "insights": insights,
        }

    def get_posts_feed(
        self,
        platform: Optional[str] = None,
        person_id: Optional[int] = None,
        person_type: Optional[str] = None,
        days: int = 30,
        sort_by: str = "engagement",
        limit: int = 50,
        offset: int = 0,
    ) -> dict:
        """Get a feed of scraped posts with filtering."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        query = self.db.query(ScrapedPost).filter(
            ScrapedPost.scraped_at >= cutoff
        )

        if platform:
            query = query.filter(ScrapedPost.platform == platform)
        if person_id:
            query = query.filter(ScrapedPost.person_id == person_id)
        if person_type:
            query = query.join(Person).filter(Person.type == person_type)

        total = query.count()

        if sort_by == "engagement":
            query = query.order_by(desc(ScrapedPost.likes + ScrapedPost.comments * 3))
        elif sort_by == "recent":
            query = query.order_by(desc(ScrapedPost.scraped_at))
        elif sort_by == "views":
            query = query.order_by(desc(ScrapedPost.views))

        posts = query.offset(offset).limit(limit).all()

        # Load person names
        person_ids = list(set(p.person_id for p in posts))
        person_map = {}
        if person_ids:
            people = self.db.query(Person).filter(Person.id.in_(person_ids)).all()
            person_map = {p.id: p for p in people}

        feed = []
        for post in posts:
            person = person_map.get(post.person_id)
            feed.append({
                "id": post.id,
                "person_id": post.person_id,
                "person_name": person.name if person else "Unknown",
                "person_type": person.type if person else "unknown",
                "person_tier": person.tier if person else None,
                "platform": post.platform,
                "post_url": post.post_url,
                "image_urls": post.image_urls or [],
                "caption": post.caption or "",
                "hashtags": post.hashtags or [],
                "likes": post.likes or 0,
                "comments": post.comments or 0,
                "shares": post.shares or 0,
                "views": post.views or 0,
                "engagement_rate": post.engagement_rate or 0,
                "posted_at": post.posted_at.isoformat() if post.posted_at else None,
                "scraped_at": post.scraped_at.isoformat() if post.scraped_at else None,
                "analyzed": post.analyzed,
                "style_tags": post.style_tags or [],
                "category": post.category,
                "ai_narrative": post.ai_narrative,
            })

        return {
            "total": total,
            "limit": limit,
            "offset": offset,
            "posts": feed,
        }

    def get_feed_stats(self, days: int = 7) -> dict:
        """Get summary stats for the feed."""
        cutoff = datetime.utcnow() - timedelta(days=days)

        total = self.db.query(func.count(ScrapedPost.id)).filter(
            ScrapedPost.scraped_at >= cutoff
        ).scalar() or 0

        by_platform = dict(
            self.db.query(ScrapedPost.platform, func.count(ScrapedPost.id))
            .filter(ScrapedPost.scraped_at >= cutoff)
            .group_by(ScrapedPost.platform)
            .all()
        )

        total_engagement = self.db.query(
            func.sum(ScrapedPost.likes),
            func.sum(ScrapedPost.comments),
            func.sum(ScrapedPost.views),
        ).filter(ScrapedPost.scraped_at >= cutoff).first()

        unique_people = self.db.query(
            func.count(func.distinct(ScrapedPost.person_id))
        ).filter(ScrapedPost.scraped_at >= cutoff).scalar() or 0

        return {
            "period_days": days,
            "total_posts": total,
            "by_platform": by_platform,
            "total_likes": total_engagement[0] or 0,
            "total_comments": total_engagement[1] or 0,
            "total_views": total_engagement[2] or 0,
            "unique_people_scraped": unique_people,
        }

    def _generate_insights(
        self, styles, categories, colors,
        cross_person, total_posts, days,
    ) -> list[dict]:
        """Generate human-readable trend insights."""
        insights = []

        if total_posts == 0:
            return [{"type": "info", "title": "No Data Yet", "text": "Scrape some people to start seeing trend insights."}]

        # Top style insight
        top_styles = styles.most_common(3)
        if top_styles:
            style_list = ", ".join(f"{s} ({c} mentions)" for s, c in top_styles)
            insights.append({
                "type": "style",
                "title": "Trending Styles",
                "text": f"Top aesthetics in the last {days} days: {style_list}.",
            })

        # Top category insight
        top_cats = categories.most_common(3)
        if top_cats:
            cat_list = ", ".join(f"{c} ({n}x)" for c, n in top_cats)
            insights.append({
                "type": "category",
                "title": "Hot Categories",
                "text": f"Most-mentioned product categories: {cat_list}.",
            })

        # Color trend
        top_colors = colors.most_common(3)
        if top_colors:
            color_list = ", ".join(c for c, _ in top_colors)
            insights.append({
                "type": "color",
                "title": "Color Direction",
                "text": f"Colors trending across posts: {color_list}.",
            })

        # Cross-person convergence
        strong_cross = [t for t in cross_person if t["people_count"] >= 3]
        if strong_cross:
            top = strong_cross[0]
            insights.append({
                "type": "convergence",
                "title": "Cross-Person Convergence",
                "text": f'"{top["trend"]}" is appearing across {top["people_count"]} different people ({", ".join(top["people"][:4])}).',
            })

        # Volume insight
        insights.append({
            "type": "volume",
            "title": "Scrape Volume",
            "text": f"Analyzed {total_posts} posts over the last {days} days.",
        })

        return insights
