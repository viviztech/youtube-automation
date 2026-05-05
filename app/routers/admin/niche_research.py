import json
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.models.keyword_result import KeywordResult
from app.services.youtube_service import search_keywords, get_trending_videos
from app.services.trends_service import fetch_google_trends
from app.services.settings_service import get_setting

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/research", response_class=HTMLResponse)
async def research_page(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    cached = db.query(KeywordResult).order_by(KeywordResult.fetched_at.desc()).limit(50).all()
    return templates.TemplateResponse("admin/niche_research.html", {
        "request": request,
        "admin": current_admin,
        "cached_keywords": cached,
        "search_results": [],
        "active_page": "research",
        "error": request.query_params.get("error"),
    })


@router.post("/research/search")
async def keyword_search(
    request: Request,
    query: str = Form(...),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    api_key = get_setting("youtube_data_api_key", db)
    results = []
    error = None

    if not api_key:
        error = "YouTube Data API key not set. Go to Settings."
    else:
        try:
            results = search_keywords(query, api_key)
            for item in results:
                db.add(KeywordResult(
                    keyword=item["title"],
                    source="youtube",
                    niche=query,
                ))
            db.commit()
        except Exception as e:
            error = str(e)[:200]

    cached = db.query(KeywordResult).order_by(KeywordResult.fetched_at.desc()).limit(50).all()
    return templates.TemplateResponse("admin/niche_research.html", {
        "request": request,
        "admin": current_admin,
        "cached_keywords": cached,
        "search_results": results,
        "query": query,
        "active_page": "research",
        "error": error,
    })


@router.post("/research/trends")
async def fetch_trends(
    request: Request,
    keywords: str = Form(...),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    kw_list = [k.strip() for k in keywords.split(",") if k.strip()][:5]
    result = fetch_google_trends(kw_list)

    for kw, scores in result.get("interest_over_time", {}).items():
        avg = sum(scores) / len(scores) if scores else 0
        db.add(KeywordResult(
            keyword=kw,
            source="google_trends",
            trend_score=avg,
            is_trending=avg > 50,
            related_terms=json.dumps(result.get("rising_queries", {}).get(kw, [])),
        ))
    db.commit()
    return RedirectResponse(url="/admin/research", status_code=302)


@router.get("/api/keywords/cached")
async def cached_keywords_api(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    rows = db.query(KeywordResult).order_by(KeywordResult.fetched_at.desc()).limit(50).all()
    return JSONResponse([{
        "keyword": r.keyword,
        "source": r.source,
        "trend_score": r.trend_score,
        "is_trending": r.is_trending,
    } for r in rows])
