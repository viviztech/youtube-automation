from datetime import datetime
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.models.day_task import DayTask

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/days", response_class=HTMLResponse)
async def day_tasks(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    tasks = db.query(DayTask).order_by(DayTask.day_number).all()
    weeks = {}
    for task in tasks:
        weeks.setdefault(task.week_number, []).append(task)

    week_names = {1: "Plan & Setup", 2: "Create & Produce", 3: "Optimize & Grow", 4: "Scale & Go Viral"}
    completed = sum(1 for t in tasks if t.is_completed)

    return templates.TemplateResponse("admin/day_tasks.html", {
        "request": request,
        "admin": current_admin,
        "weeks": weeks,
        "week_names": week_names,
        "total": len(tasks),
        "completed": completed,
        "active_page": "days",
    })


@router.post("/days/{day_number}/complete")
async def toggle_complete(
    day_number: int,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    task = db.query(DayTask).filter(DayTask.day_number == day_number).first()
    if task:
        task.is_completed = not task.is_completed
        task.completed_at = datetime.utcnow() if task.is_completed else None
        db.commit()
    return RedirectResponse(url="/admin/days", status_code=302)


@router.post("/days/{day_number}/notes")
async def save_notes(
    day_number: int,
    notes: str = Form(""),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    task = db.query(DayTask).filter(DayTask.day_number == day_number).first()
    if task:
        task.notes = notes
        db.commit()
    return RedirectResponse(url="/admin/days", status_code=302)
