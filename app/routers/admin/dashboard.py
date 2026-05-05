from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.models.day_task import DayTask
from app.models.video_project import VideoProject
from app.models.script import Script
from app.models.voiceover_job import VoiceoverJob
from app.models.youtube_upload import YouTubeUpload

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    total_tasks = db.query(DayTask).count()
    completed_tasks = db.query(DayTask).filter(DayTask.is_completed == True).count()
    progress_pct = round((completed_tasks / total_tasks * 100) if total_tasks else 0)

    stats = {
        "total_videos": db.query(VideoProject).count(),
        "scripted": db.query(VideoProject).filter(VideoProject.status == "scripted").count(),
        "voiced": db.query(VideoProject).filter(VideoProject.status == "voiced").count(),
        "ready": db.query(VideoProject).filter(VideoProject.status == "ready").count(),
        "uploaded": db.query(VideoProject).filter(VideoProject.status == "uploaded").count(),
        "tasks_done": completed_tasks,
        "tasks_total": total_tasks,
        "progress_pct": progress_pct,
    }

    recent_projects = (
        db.query(VideoProject)
        .order_by(VideoProject.created_at.desc())
        .limit(5)
        .all()
    )

    return templates.TemplateResponse("admin/dashboard.html", {
        "request": request,
        "admin": current_admin,
        "stats": stats,
        "recent_projects": recent_projects,
        "active_page": "dashboard",
    })
