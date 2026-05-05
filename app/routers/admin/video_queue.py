from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.models.video_project import VideoProject

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")

STATUSES = ["scripted", "voiced", "edited", "ready", "uploaded"]


@router.get("/queue", response_class=HTMLResponse)
async def queue_page(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    projects = db.query(VideoProject).order_by(VideoProject.updated_at.desc()).all()
    columns = {s: [] for s in STATUSES}
    failed = []
    for p in projects:
        if p.status in columns:
            columns[p.status].append(p)
        elif p.status == "failed":
            failed.append(p)

    return templates.TemplateResponse("admin/video_queue.html", {
        "request": request,
        "admin": current_admin,
        "columns": columns,
        "failed": failed,
        "statuses": STATUSES,
        "active_page": "queue",
    })


@router.post("/queue/{project_id}/status")
async def update_status(
    project_id: str,
    status: str = Form(...),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
    if project and status in STATUSES + ["failed"]:
        project.status = status
        db.commit()
    return JSONResponse({"project_id": project_id, "status": status})


@router.get("/api/queue/stats")
async def queue_stats(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    stats = {s: db.query(VideoProject).filter(VideoProject.status == s).count() for s in STATUSES}
    return JSONResponse(stats)
