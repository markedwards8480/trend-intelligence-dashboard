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
            "price_point": random.choice(MOCK_PRICE_POINTS),
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

Please provide a detailed analysis in JSON format with the following fields:
- category: The main fashion item category (e.g., "midi dress", "crop top")
- subcategory: Optional subcategory for more specificity
- colors: List of primary colors in the item
- patterns: List of patterns (solid, plaid, striped, floral, etc.)
- style_tags: List of relevant style tags (e.g., "cottagecore", "y2k", "quiet luxury", "coquette")
- price_point: Estimated price tier (budget, mid, luxury, designer)
- narrative: A brief narrative analysis of why this is trending and its relevance

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
