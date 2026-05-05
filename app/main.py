from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.background import BackgroundScheduler
from app.config import get_settings
from app.dependencies import RedirectException
from app.routers import auth
from app.routers.admin import (
    dashboard, day_tasks, niche_research, scripts,
    voiceover, assets, video_queue, youtube_uploader, scheduler, settings, api_guide,
)

settings_obj = get_settings()

app = FastAPI(title=settings_obj.APP_NAME, debug=settings_obj.DEBUG)
templates = Jinja2Templates(directory="app/templates")


@app.exception_handler(RedirectException)
async def redirect_exception_handler(request: Request, exc: RedirectException):
    return RedirectResponse(url=exc.url, status_code=exc.status_code)


app.mount("/static", StaticFiles(directory="app/static"), name="static")
app.mount("/uploads", StaticFiles(directory="app/uploads"), name="uploads")

app.include_router(auth.router)

for mod in [dashboard, day_tasks, niche_research, scripts, voiceover, assets, video_queue, youtube_uploader, scheduler, settings, api_guide]:
    app.include_router(mod.router, prefix="/admin")

# Also mount the API-level routes (queue stats, cached keywords)
app.include_router(niche_research.router)
app.include_router(video_queue.router)


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@app.get("/login")
async def login_redirect():
    return RedirectResponse(url="/auth/login", status_code=302)


bg_scheduler = BackgroundScheduler()


@app.on_event("startup")
def start_scheduler():
    from app.tasks.keyword_fetch import daily_keyword_fetch_job
    from app.tasks.trend_alert import trend_alert_job
    from app.routers.admin.scheduler import set_scheduler

    bg_scheduler.add_job(daily_keyword_fetch_job, "cron", hour=8, minute=0, id="keyword_fetch", name="Daily Keyword Fetch")
    bg_scheduler.add_job(trend_alert_job, "cron", hour=10, minute=0, id="trend_alert", name="Daily Trend Alert")
    bg_scheduler.start()
    set_scheduler(bg_scheduler)


@app.on_event("shutdown")
def stop_scheduler():
    bg_scheduler.shutdown(wait=False)
