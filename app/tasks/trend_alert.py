import logging
from datetime import datetime, timedelta
from sqlalchemy import func
from app.database import SessionLocal
from app.models.keyword_result import KeywordResult

logger = logging.getLogger(__name__)


def trend_alert_job():
    logger.info("Running trend alert job...")
    db = SessionLocal()
    try:
        cutoff = datetime.utcnow() - timedelta(days=2)
        recent = (
            db.query(KeywordResult)
            .filter(KeywordResult.fetched_at >= cutoff, KeywordResult.source == "google_trends")
            .all()
        )

        # Group by keyword and detect spikes (>50% score increase)
        scores_by_kw: dict[str, list[float]] = {}
        for row in recent:
            if row.trend_score is not None:
                scores_by_kw.setdefault(row.keyword, []).append(row.trend_score)

        spiked = []
        for kw, scores in scores_by_kw.items():
            if len(scores) >= 2:
                pct_change = ((scores[-1] - scores[0]) / max(scores[0], 1)) * 100
                if pct_change > 50:
                    spiked.append(kw)
                    db.query(KeywordResult).filter(
                        KeywordResult.keyword == kw
                    ).update({"is_trending": True})

        if spiked:
            db.commit()
            logger.info(f"Trend spikes detected for: {', '.join(spiked)}")
        else:
            logger.info("No significant trend spikes detected.")

    except Exception as e:
        logger.error(f"Trend alert job failed: {e}")
    finally:
        db.close()
