import logging
from app.database import SessionLocal
from app.services.settings_service import get_setting
from app.services.youtube_service import get_trending_videos
from app.services.trends_service import fetch_google_trends
from app.models.keyword_result import KeywordResult

logger = logging.getLogger(__name__)


def daily_keyword_fetch_job():
    logger.info("Running daily keyword fetch job...")
    db = SessionLocal()
    try:
        niche = get_setting("channel_niche", db) or "technology"
        api_key = get_setting("youtube_data_api_key", db)

        # Fetch YouTube trending
        if api_key:
            trending = get_trending_videos(api_key=api_key)
            for item in trending:
                db.add(KeywordResult(
                    keyword=item["title"],
                    source="youtube",
                    search_volume=item.get("view_count", ""),
                    niche=niche,
                    is_trending=True,
                ))
            db.commit()
            logger.info(f"Saved {len(trending)} YouTube trending results.")

        # Fetch Google Trends
        trends = fetch_google_trends(keywords=[niche, f"{niche} tips", f"{niche} tutorial"])
        for kw, scores in trends.get("interest_over_time", {}).items():
            avg_score = sum(scores) / len(scores) if scores else 0
            db.add(KeywordResult(
                keyword=kw,
                source="google_trends",
                trend_score=avg_score,
                niche=niche,
                is_trending=avg_score > 50,
            ))
        db.commit()
        logger.info("Google Trends data saved.")

    except Exception as e:
        logger.error(f"Keyword fetch job failed: {e}")
    finally:
        db.close()
