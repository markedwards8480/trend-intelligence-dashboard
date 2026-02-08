import random
import asyncio
import re
from typing import Dict, List, Optional
from app.config import settings


def _clean_json_response(text: str) -> str:
    """Strip markdown code fences, fix common JSON issues from Claude responses."""
    text = text.strip()
    # Remove ```json ... ``` or ``` ... ``` wrappers
    text = re.sub(r'^```(?:json)?\s*\n?', '', text)
    text = re.sub(r'\n?```\s*$', '', text)
    text = text.strip()
    # Fix trailing commas before } or ] (common LLM JSON error)
    text = re.sub(r',\s*}', '}', text)
    text = re.sub(r',\s*]', ']', text)
    # Fix single quotes used instead of double quotes (less common but possible)
    # Only do this if json.loads would fail — we'll try strict first
    return text

# Fashion-relevant mock data for realistic development
MOCK_CATEGORIES = [
    "midi dress",
    "crop top",
    "cargo pants",
    "mini skirt",
    "blazer",
    "oversized shirt",
    "slip dress",
    "bucket hat",
    "cargo jacket",
    "vintage jeans",
    "ballet flats",
    "platform sneakers",
    "tube top",
    "trench coat",
    "wrap dress",
    "bodysuit",
    "maxi skirt",
    "tank top",
    "leather jacket",
    "tote bag",
]

MOCK_COLORS = [
    "navy blue",
    "cream",
    "chocolate brown",
    "olive green",
    "mauve",
    "burnt orange",
    "sage green",
    "butter yellow",
    "blush pink",
    "charcoal grey",
    "white",
    "black",
    "camel",
    "rust",
    "burgundy",
    "forest green",
    "ivory",
    "taupe",
    "dusty rose",
    "powder blue",
]

MOCK_PATTERNS = [
    "solid",
    "plaid",
    "striped",
    "floral",
    "checkered",
    "polka dot",
    "paisley",
    "animal print",
    "houndstooth",
    "gingham",
    "abstract",
    "damask",
    "geometric",
]

MOCK_STYLE_TAGS = [
    "cottagecore",
    "y2k",
    "clean girl",
    "mob wife",
    "quiet luxury",
    "coquette",
    "dark academia",
    "soft girl",
    "indie sleaze",
    "gorpcore",
    "barbiecore",
    "maximalist",
    "minimalist",
    "grunge",
    "preppy",
    "romantic",
    "avant-garde",
    "vintage",
    "sustainable",
    "streetwear",
]

MOCK_PRICE_POINTS = [
    "budget",
    "mid",
    "luxury",
    "designer",
]

MOCK_DEMOGRAPHICS = [
    "junior_girls",
    "junior_girls",
    "junior_girls",  # Weighted toward primary demo
    "young_women",
    "young_women",
    "contemporary",
    "kids",
]

MOCK_FABRICATIONS = [
    "cotton",
    "polyester",
    "cotton blend",
    "rayon",
    "linen",
    "denim",
    "silk",
    "nylon",
    "spandex blend",
    "jersey knit",
    "chiffon",
    "satin",
    "velvet",
    "mesh",
    "ribbed knit",
    "fleece",
    "twill",
    "modal",
]


class AIService:
    """Service for AI analysis of trends using Claude or mock data."""

    @staticmethod
    def _generate_mock_analysis() -> Dict:
        """Generate realistic mock trend analysis for development."""
        return {
            "category": random.choice(MOCK_CATEGORIES),
            "subcategory": None,
            "colors": random.sample(MOCK_COLORS, random.randint(1, 3)),
            "patterns": random.sample(MOCK_PATTERNS, random.randint(1, 2)),
            "style_tags": random.sample(MOCK_STYLE_TAGS, random.randint(2, 4)),
            "fabrications": random.sample(MOCK_FABRICATIONS, random.randint(1, 3)),
            "price_point": random.choice(MOCK_PRICE_POINTS),
            "demographic": random.choice(MOCK_DEMOGRAPHICS),
            "engagement_estimate": random.randint(100, 50000),
            "narrative": f"This item exemplifies current trending aesthetics. The styling combines elements of popular substyles while maintaining contemporary appeal to junior fashion consumers. The color palette and silhouette align with emerging seasonal preferences.",
        }

    @staticmethod
    async def analyze_trend(url: str, source_platform: str) -> Dict:
        """
        Analyze a trend URL using Claude API or mock data.

        Args:
            url: The URL of the trend item
            source_platform: Platform where the item was found (instagram, tiktok, etc.)

        Returns:
            Dictionary with analysis results including category, colors, patterns,
            style_tags, price_point, and narrative analysis text.
        """
        if settings.USE_MOCK_AI:
            # Simulate async processing with a small delay
            await asyncio.sleep(0.1)
            return AIService._generate_mock_analysis()

        # Real Claude API analysis
        if not settings.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY not configured for real AI analysis")

        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=settings.CLAUDE_API_KEY)

            prompt = f"""Analyze this fashion trend item from {source_platform}.

URL: {url}

You are analyzing trends for a women's fast fashion apparel company (Mark Edwards Apparel) that primarily targets junior girls (15-25) but also tracks trends across other demographics.

Please provide a detailed analysis in JSON format with the following fields:
- category: The main fashion item category (e.g., "midi dress", "crop top", "cargo pants", "blazer")
- subcategory: Optional subcategory for more specificity
- colors: List of primary colors in the item
- patterns: List of patterns (solid, plaid, striped, floral, etc.)
- style_tags: List of relevant style tags (e.g., "cottagecore", "y2k", "quiet luxury", "coquette", "mob wife", "gorpcore")
- fabrications: List of materials/fabrics (e.g., "cotton", "polyester", "denim", "silk", "linen", "jersey knit", "chiffon")
- price_point: Estimated price tier (budget, mid, luxury, designer)
- demographic: Primary target demographic. Must be one of: "junior_girls" (ages 15-25), "young_women" (ages 25-35), "contemporary" (ages 35+), or "kids" (ages 6-14)
- narrative: A brief narrative analysis of why this is trending, its relevance to the target demographic, and how it fits current fashion movements

Return ONLY valid JSON, no additional text."""

            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse the response
            response_text = message.content[0].text
            import json

            analysis = json.loads(_clean_json_response(response_text))
            return analysis

        except Exception as e:
            # Fallback to mock if Claude API fails
            print(f"Warning: Claude API analysis failed: {e}")
            return AIService._generate_mock_analysis()

    @staticmethod
    async def batch_analyze_trends(
        trends: List[tuple]
    ) -> List[Dict]:
        """
        Analyze multiple trends concurrently.

        Args:
            trends: List of (url, source_platform) tuples

        Returns:
            List of analysis results
        """
        tasks = [
            AIService.analyze_trend(url, platform)
            for url, platform in trends
        ]
        return await asyncio.gather(*tasks)

    @staticmethod
    async def suggest_sources(existing_sources: List[Dict]) -> List[Dict]:
        """
        Use AI to suggest new sources based on existing watched sources.

        Args:
            existing_sources: List of dicts with name, url, platform

        Returns:
            List of suggested sources with reasoning
        """
        if settings.USE_MOCK_AI:
            await asyncio.sleep(0.1)
            return [
                {
                    "url": "https://www.whowhatwear.com",
                    "platform": "Who What Wear",
                    "name": "Who What Wear",
                    "reasoning": "Top fashion editorial site that surfaces emerging trends early, popular with young women and covers affordable to mid-range fashion.",
                    "demographics": ["junior_girls", "young_women", "contemporary"],
                },
                {
                    "url": "https://trends.google.com/trends/explore?cat=185",
                    "platform": "Google Trends",
                    "name": "Google Trends - Fashion",
                    "reasoning": "Search trend data reveals what consumers are actively looking for, provides quantitative signal on rising categories, colors, and styles.",
                    "demographics": ["junior_girls", "young_women", "contemporary", "kids"],
                },
                {
                    "url": "https://www.vogue.com/fashion/trends",
                    "platform": "Vogue",
                    "name": "Vogue Trends",
                    "reasoning": "Leading fashion authority for runway-to-retail trend forecasting, helps identify what's trickling down from designer collections.",
                    "demographics": ["young_women", "contemporary"],
                },
                {
                    "url": "https://www.refinery29.com/en-us/fashion",
                    "platform": "Refinery29",
                    "name": "Refinery29 Fashion",
                    "reasoning": "Editorial coverage focused on affordable fashion trends, strong alignment with junior and young women demographics.",
                    "demographics": ["junior_girls", "young_women"],
                },
                {
                    "url": "https://www.asos.com",
                    "platform": "ASOS",
                    "name": "ASOS",
                    "reasoning": "Wide range of brands and styles, strong trend-forward selection for young women, good for spotting cross-brand trends.",
                    "demographics": ["junior_girls", "young_women", "contemporary"],
                },
            ]

        if not settings.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY not configured")

        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=settings.CLAUDE_API_KEY)

            source_list = "\n".join(
                f"- {s.get('name', 'Unknown')} ({s.get('url', '')})" for s in existing_sources
            ) or "No sources added yet."

            prompt = f"""You are helping a women's fast fashion apparel company (Mark Edwards Apparel) find new sources to monitor for trending fashion.

Their primary market is junior girls (15-25) but they also track young women (25-35), contemporary (35+), and kids (6-14).

Currently monitored sources:
{source_list}

Suggest 3-5 NEW fashion sources that would be valuable for tracking trends. Include a MIX of:
- Ecommerce sites (budget to mid-range, not luxury)
- Fashion magazines and editorial sites (Vogue, Elle, WWD, Who What Wear, Refinery29, etc.)
- Google Trends or Google Shopping for search data
- Social media accounts (Instagram, TikTok, Pinterest)

Focus on:
- Sources popular with the target demographics
- Platforms with strong trend signals (especially early indicators)
- Sources not already in their list
- Fashion media that helps predict what's coming next season

Return ONLY valid JSON as an array of objects, each with:
- url: The website URL
- platform: Platform name
- name: Display name
- reasoning: Why this source is valuable (1-2 sentences)
- demographics: Array of applicable demographics from ["junior_girls", "young_women", "contemporary", "kids"]

Return ONLY valid JSON, no additional text."""

            message = client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            import json
            response_text = message.content[0].text
            suggestions = json.loads(_clean_json_response(response_text))
            return suggestions

        except Exception as e:
            print(f"Warning: Source suggestion failed: {e}")
            # Return empty list on failure
            return []

    @staticmethod
    async def discover_social_accounts(
        ecommerce_brands: List[Dict],
        batch_size: int = 5,
    ) -> List[Dict]:
        """
        Use AI to discover social media accounts (TikTok, Instagram) for ecommerce brands,
        plus related influencer accounts and hashtags.

        Args:
            ecommerce_brands: List of dicts with name, url
            batch_size: How many brands to process per AI call

        Returns:
            List of discovered social accounts with brand associations
        """
        if settings.USE_MOCK_AI:
            await asyncio.sleep(0.1)
            results = []
            for brand in ecommerce_brands[:5]:
                name = brand.get("name", "Unknown")
                handle = name.lower().replace(" ", "").replace("'", "").replace("&", "and")
                results.append({
                    "brand": name,
                    "accounts": [
                        {
                            "platform": "tiktok",
                            "handle": f"@{handle}",
                            "url": f"https://www.tiktok.com/@{handle}",
                            "name": f"{name} TikTok",
                            "type": "official",
                            "description": f"Official TikTok account for {name}",
                            "estimated_followers": "500K+",
                        },
                        {
                            "platform": "instagram",
                            "handle": f"@{handle}",
                            "url": f"https://www.instagram.com/{handle}/",
                            "name": f"{name} Instagram",
                            "type": "official",
                            "description": f"Official Instagram account for {name}",
                            "estimated_followers": "1M+",
                        },
                    ],
                    "related_influencers": [
                        {
                            "platform": "tiktok",
                            "handle": "@fashiontrendsetterxo",
                            "url": "https://www.tiktok.com/@fashiontrendsetterxo",
                            "name": "Fashion Trendsetter",
                            "description": f"Frequently features {name} hauls and try-ons",
                            "estimated_followers": "200K",
                        },
                    ],
                    "hashtags": [f"#{handle}", f"#{handle}haul", f"#{handle}finds"],
                })
            return results

        if not settings.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY not configured")

        try:
            from anthropic import Anthropic
            import json

            client = Anthropic(api_key=settings.CLAUDE_API_KEY)
            all_results = []

            # Process in batches to avoid token limits
            for i in range(0, len(ecommerce_brands), batch_size):
                batch = ecommerce_brands[i:i + batch_size]
                brand_list = "\n".join(
                    f"- {b.get('name', 'Unknown')} ({b.get('url', '')})"
                    for b in batch
                )

                prompt = f"""You are helping a women's fast fashion apparel company (Mark Edwards Apparel) build a social media intelligence database. Their primary market is junior girls (15-25) and young women (25-35).

For each of the following ecommerce fashion brands, provide their social media accounts and related influencer accounts.

Brands:
{brand_list}

For EACH brand, provide:
1. Their official TikTok account (handle and URL) — use real, known handles
2. Their official Instagram account (handle and URL) — use real, known handles
3. 1-2 related influencer/creator accounts on TikTok or Instagram who frequently feature that brand (hauls, try-ons, styling videos)
4. 2-3 relevant hashtags used for that brand on social media

IMPORTANT RULES:
- Use REAL social media handles that actually exist. If you're not sure about a handle, use the most common/likely format.
- For official accounts, the handle is usually the brand name (e.g., @zara, @shein, @prettylittlething)
- For influencers, suggest real popular fashion creators who are known to feature these brands
- Focus on accounts popular with junior girls (15-25) — Gen Z fashion content
- Include estimated follower counts where known

Return ONLY valid JSON as an array of objects with this structure:
[
  {{
    "brand": "Brand Name",
    "accounts": [
      {{
        "platform": "tiktok" or "instagram",
        "handle": "@handle",
        "url": "https://www.tiktok.com/@handle" or "https://www.instagram.com/handle/",
        "name": "Display Name",
        "type": "official",
        "description": "Brief description",
        "estimated_followers": "1M+" or "500K" etc
      }}
    ],
    "related_influencers": [
      {{
        "platform": "tiktok" or "instagram",
        "handle": "@handle",
        "url": "full URL",
        "name": "Creator Name",
        "description": "Why they're relevant to this brand",
        "estimated_followers": "200K" etc
      }}
    ],
    "hashtags": ["#brandname", "#brandhaul", "#brandfinds"]
  }}
]

Return ONLY valid JSON, no additional text."""

                message = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=4096,
                    messages=[{"role": "user", "content": prompt}],
                )

                response_text = message.content[0].text
                cleaned = _clean_json_response(response_text)
                try:
                    batch_results = json.loads(cleaned)
                except json.JSONDecodeError as je:
                    # Log the error with context for debugging
                    print(f"JSON parse error on batch {i//batch_size + 1}: {je}")
                    print(f"Response preview (first 500 chars): {cleaned[:500]}")
                    print(f"Response preview (last 500 chars): {cleaned[-500:]}")
                    # Try to salvage — skip this batch but continue
                    batch_results = []
                all_results.extend(batch_results)

                # Small delay between batches to avoid rate limiting
                if i + batch_size < len(ecommerce_brands):
                    await asyncio.sleep(1)

            return all_results

        except Exception as e:
            import traceback
            print(f"Warning: Social account discovery failed: {e}")
            traceback.print_exc()
            raise  # Re-raise so endpoint can return error details

    @staticmethod
    async def generate_seed_trends(
        brands: List[Dict],
        trends_per_brand: int = 5,
        batch_size: int = 5,
    ) -> List[Dict]:
        """
        Use AI to generate realistic trending product data for ecommerce brands.
        This populates the dashboard with trend items based on what each brand would stock.

        Args:
            brands: List of dicts with name, url, id (source_id)
            trends_per_brand: How many products per brand
            batch_size: How many brands per AI call

        Returns:
            List of trend dicts ready to insert as TrendItems
        """
        if not settings.CLAUDE_API_KEY:
            raise ValueError("CLAUDE_API_KEY not configured")

        try:
            from anthropic import Anthropic
            import json

            client = Anthropic(api_key=settings.CLAUDE_API_KEY)
            all_results = []

            for i in range(0, len(brands), batch_size):
                batch = brands[i:i + batch_size]
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

                message = client.messages.create(
                    model="claude-sonnet-4-5-20250929",
                    max_tokens=8192,
                    messages=[{"role": "user", "content": prompt}],
                )

                response_text = message.content[0].text
                cleaned = _clean_json_response(response_text)
                try:
                    batch_results = json.loads(cleaned)
                    # Attach source_id from our brand list
                    brand_id_map = {b.get('name', ''): b.get('id') for b in batch}
                    for item in batch_results:
                        brand_name = item.get('brand', '')
                        item['source_id'] = brand_id_map.get(brand_name)
                    all_results.extend(batch_results)
                except json.JSONDecodeError as je:
                    print(f"JSON parse error on seed batch {i//batch_size + 1}: {je}")
                    print(f"Response preview (first 500 chars): {cleaned[:500]}")

                # Small delay between batches to avoid rate limiting
                if i + batch_size < len(brands):
                    await asyncio.sleep(1)

            return all_results

        except Exception as e:
            import traceback
            print(f"Warning: Seed trend generation failed: {e}")
            traceback.print_exc()
            raise
