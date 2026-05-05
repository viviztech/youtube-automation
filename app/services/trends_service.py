from pytrends.request import TrendReq


def fetch_google_trends(
    keywords: list[str],
    timeframe: str = "now 7-d",
    geo: str = "IN",
) -> dict:
    try:
        pytrends = TrendReq(hl="en-US", tz=330)
        pytrends.build_payload(keywords[:5], cat=0, timeframe=timeframe, geo=geo)

        interest_df = pytrends.interest_over_time()
        related = pytrends.related_queries()

        interest_data = {}
        if not interest_df.empty:
            for kw in keywords[:5]:
                if kw in interest_df.columns:
                    interest_data[kw] = interest_df[kw].tolist()

        rising_queries = {}
        for kw in keywords[:5]:
            if kw in related and related[kw].get("rising") is not None:
                rising_df = related[kw]["rising"]
                if not rising_df.empty:
                    rising_queries[kw] = rising_df.head(10).to_dict("records")

        return {
            "status": "ok",
            "interest_over_time": interest_data,
            "rising_queries": rising_queries,
        }
    except Exception as e:
        return {"status": "error", "error": str(e), "interest_over_time": {}, "rising_queries": {}}
