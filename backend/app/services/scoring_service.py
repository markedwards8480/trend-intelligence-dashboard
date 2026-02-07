import math
from datetime import datetime, timedelta
from typing import Dict
from app.models.models import TrendItem


class ScoringService:
    """Service for calculating trend scores based on engagement and velocity."""

    # Configuration for scoring algorithm
    BASE_ENGAGEMENT_WEIGHT = 0.3  # Weight for engagement score
    VELOCITY_WEIGHT = 0.4  # Weight for velocity score
    RECENCY_WEIGHT = 0.3  # Weight for recency factor
    CROSS_PLATFORM_BONUS = 10  # Points per additional platform
    MAX_TREND_SCORE = 100

    @staticmethod
    def calculate_engagement_score(item: TrendItem) -> float:
        """
        Calculate base engagement score from interaction metrics.

        Uses normalized weighted sum of likes, comments, shares, and views.
        """
        # Normalize each metric (log scale for stability)
        likes_normalized = math.log10(item.likes + 1) / 5  # max ~50k likes
        comments_normalized = math.log10(item.comments + 1) / 4  # max ~10k comments
        shares_normalized = math.log10(item.shares + 1) / 4  # max ~10k shares
        views_normalized = math.log10(item.views + 1) / 6  # max ~1M views

        # Weighted combination
        engagement_score = (
            likes_normalized * 0.3
            + comments_normalized * 0.3
            + shares_normalized * 0.25
            + views_normalized * 0.15
        ) * 100

        return min(engagement_score, 100)

    @staticmethod
    def calculate_velocity_score(item: TrendItem) -> float:
        """
        Calculate velocity score based on engagement growth rate.

        Faster-growing trends get higher velocity scores.
        Returns a multiplier (1.0-3.0) applied to engagement score.
        """
        if not item.metrics_history or len(item.metrics_history) < 2:
            # Not enough history, return base velocity
            return 1.0

        # Get metrics from 24 hours ago if available
        now = datetime.utcnow()
        day_ago = now - timedelta(hours=24)

        historical_metrics = [m for m in item.metrics_history if m.recorded_at >= day_ago]

        if len(historical_metrics) < 2:
            return 1.0

        # Compare first and last metric in the time window
        first_metric = historical_metrics[0]
        last_metric = historical_metrics[-1]

        # Calculate growth rate
        likes_growth = (last_metric.likes - first_metric.likes) / (
            first_metric.likes + 1
        )
        comments_growth = (last_metric.comments - first_metric.comments) / (
            first_metric.comments + 1
        )
        shares_growth = (last_metric.shares - first_metric.shares) / (
            first_metric.shares + 1
        )

        # Average growth
        avg_growth = (likes_growth + comments_growth + shares_growth) / 3

        # Convert growth rate to velocity multiplier (1.0 to 3.0)
        # Growth > 100% gets max multiplier, no growth gets 1.0
        velocity_multiplier = 1.0 + min(avg_growth / 2, 2.0)

        return max(1.0, min(velocity_multiplier, 3.0))

    @staticmethod
    def calculate_recency_factor(item: TrendItem) -> float:
        """
        Calculate recency factor to boost recently submitted trends.

        Trends submitted in the last 24 hours get a 1.5x boost,
        declining linearly to 1.0x after 7 days.
        """
        now = datetime.utcnow()

        # Handle None submitted_at
        if item.submitted_at is None:
            return 1.0

        age = now - (item.submitted_at.replace(tzinfo=None) if item.submitted_at.tzinfo else item.submitted_at)

        if age < timedelta(hours=24):
            return 1.5
        elif age < timedelta(days=7):
            # Linear decline from 1.5 to 1.0 over 6 days
            days_old = age.total_seconds() / 86400
            return 1.5 - (0.5 * (days_old - 1) / 6)
        else:
            return 1.0

    @staticmethod
    def calculate_cross_platform_score(item: TrendItem) -> float:
        """
        Calculate cross-platform bonus.

        Simulated based on whether the item appears on multiple platforms.
        In a real system, you'd check if the same trend exists on other platforms.
        """
        # Placeholder: could be expanded to check actual cross-platform presence
        base_bonus = 0
        # Award bonus if style/category has been seen on multiple platforms
        return base_bonus

    @staticmethod
    def calculate_trend_score(item: TrendItem) -> Dict[str, float]:
        """
        Calculate the complete trend score for an item.

        Returns:
            Dictionary with trend_score, velocity_score, and cross_platform_score
        """
        # Calculate individual components
        engagement_score = ScoringService.calculate_engagement_score(item)
        velocity_multiplier = ScoringService.calculate_velocity_score(item)
        recency_factor = ScoringService.calculate_recency_factor(item)
        cross_platform_bonus = ScoringService.calculate_cross_platform_score(item)

        # Combine scores
        # Base trend score from engagement
        base_trend = engagement_score * ScoringService.BASE_ENGAGEMENT_WEIGHT

        # Apply velocity multiplier
        velocity_adjusted = engagement_score * velocity_multiplier * ScoringService.VELOCITY_WEIGHT

        # Apply recency boost
        recency_adjusted = engagement_score * recency_factor * ScoringService.RECENCY_WEIGHT

        # Sum everything
        trend_score = base_trend + velocity_adjusted + recency_adjusted

        # Add cross-platform bonus
        trend_score += cross_platform_bonus

        # Cap at maximum
        trend_score = min(trend_score, ScoringService.MAX_TREND_SCORE)

        return {
            "trend_score": round(trend_score, 2),
            "velocity_score": round(velocity_multiplier * engagement_score, 2),
            "cross_platform_score": round(cross_platform_bonus, 2),
        }

    @staticmethod
    def update_trend_scores(item: TrendItem) -> TrendItem:
        """
        Update all score fields on a trend item.

        Args:
            item: The TrendItem to update

        Returns:
            Updated TrendItem with new scores
        """
        scores = ScoringService.calculate_trend_score(item)
        item.trend_score = scores["trend_score"]
        item.velocity_score = scores["velocity_score"]
        item.cross_platform_score = scores["cross_platform_score"]
        return item
