from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_current_admin
from app.models.user import AdminUser

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

_scheduler_ref = None


def set_scheduler(scheduler):
    global _scheduler_ref
    _scheduler_ref = scheduler


@router.get("/scheduler", response_class=HTMLResponse)
async def scheduler_page(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
):
    jobs = []
    if _scheduler_ref:
        for job in _scheduler_ref.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run": str(job.next_run_time) if job.next_run_time else "—",
                "trigger": str(job.trigger),
            })

    return templates.TemplateResponse("admin/scheduler.html", {
        "request": request,
        "admin": current_admin,
        "jobs": jobs,
        "active_page": "scheduler",
        "triggered": request.query_params.get("triggered"),
    })


@router.post("/scheduler/trigger/{job_name}")
async def trigger_job(
    job_name: str,
    current_admin: AdminUser = Depends(get_current_admin),
):
    from app.tasks.keyword_fetch import daily_keyword_fetch_job
    from app.tasks.trend_alert import trend_alert_job

    job_map = {
        "keyword_fetch": daily_keyword_fetch_job,
        "trend_alert": trend_alert_job,
    }
    fn = job_map.get(job_name)
    if fn:
        fn()
    return JSONResponse({"triggered": job_name, "status": "ok" if fn else "not_found"})
