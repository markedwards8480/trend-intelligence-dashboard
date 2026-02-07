import random
import asyncio
from typing import Dict, List, Optional
from app.config import settings

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

            client = Anthropic()

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
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            # Parse the response
            response_text = message.content[0].text
            import json

            analysis = json.loads(response_text)
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
                    "url": "https://www.prettylittlething.com",
                    "platform": "PrettyLittleThing",
                    "name": "PrettyLittleThing",
                    "reasoning": "Fast fashion brand popular with junior girls (15-25), similar price point and aesthetic to SHEIN and Fashion Nova.",
                    "demographics": ["junior_girls", "young_women"],
                },
                {
                    "url": "https://www.boohoo.com",
                    "platform": "Boohoo",
                    "name": "Boohoo",
                    "reasoning": "Budget-friendly fast fashion with strong social media presence, targets similar demographic as your current sources.",
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

            client = Anthropic()

            source_list = "\n".join(
                f"- {s.get('name', 'Unknown')} ({s.get('url', '')})" for s in existing_sources
            ) or "No sources added yet."

            prompt = f"""You are helping a women's fast fashion apparel company (Mark Edwards Apparel) find new sources to monitor for trending fashion.

Their primary market is junior girls (15-25) but they also track young women (25-35), contemporary (35+), and kids (6-14).

Currently monitored sources:
{source_list}

Suggest 3-5 NEW fashion sources (ecommerce sites, social media accounts, or fashion platforms) that would be valuable for tracking trends. Focus on:
- Budget to mid-range price points (not luxury)
- Sources popular with the target demographics
- Platforms with strong trend signals
- Sources not already in their list

Return ONLY valid JSON as an array of objects, each with:
- url: The website URL
- platform: Platform name
- name: Display name
- reasoning: Why this source is valuable (1-2 sentences)
- demographics: Array of applicable demographics from ["junior_girls", "young_women", "contemporary", "kids"]

Return ONLY valid JSON, no additional text."""

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}],
            )

            import json
            response_text = message.content[0].text
            suggestions = json.loads(response_text)
            return suggestions

        except Exception as e:
            print(f"Warning: Source suggestion failed: {e}")
            # Return empty list on failure
            return []
