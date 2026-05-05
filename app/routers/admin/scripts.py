from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.models.video_project import VideoProject
from app.models.script import Script
from app.services.claude_service import generate_script
from app.services.settings_service import get_setting

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/scripts", response_class=HTMLResponse)
async def scripts_page(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    projects = db.query(VideoProject).order_by(VideoProject.created_at.desc()).all()
    return templates.TemplateResponse("admin/scripts.html", {
        "request": request,
        "admin": current_admin,
        "projects": projects,
        "active_page": "scripts",
        "error": request.query_params.get("error"),
    })


@router.post("/scripts/generate")
async def generate(
    request: Request,
    topic: str = Form(...),
    niche: str = Form(...),
    style: str = Form("educational"),
    duration_minutes: int = Form(10),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    api_key = get_setting("claude_api_key", db)
    if not api_key:
        return RedirectResponse(url="/admin/scripts?error=Claude+API+key+not+set.+Go+to+Settings.", status_code=302)

    try:
        result = await generate_script(topic, niche, style, duration_minutes, api_key)

        project = VideoProject(title=topic, niche=niche, topic=topic, style=style, status="scripted")
        db.add(project)
        db.flush()

        script = Script(
            project_id=project.id,
            content=result["content"],
            word_count=result["word_count"],
            tokens_used=result["tokens_used"],
            prompt_used=result["prompt_used"],
        )
        db.add(script)
        db.commit()
        return RedirectResponse(url=f"/admin/scripts/{project.id}", status_code=302)

    except Exception as e:
        return RedirectResponse(url=f"/admin/scripts?error={str(e)[:100]}", status_code=302)


@router.get("/scripts/{project_id}", response_class=HTMLResponse)
async def script_detail(
    project_id: str,
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
    if not project:
        return RedirectResponse(url="/admin/scripts", status_code=302)
    return templates.TemplateResponse("admin/script_detail.html", {
        "request": request,
        "admin": current_admin,
        "project": project,
        "script": project.script,
        "active_page": "scripts",
    })


@router.post("/scripts/{project_id}/edit")
async def edit_script(
    project_id: str,
    content: str = Form(...),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
    if project and project.script:
        project.script.content = content
        project.script.word_count = len(content.split())
        db.commit()
    return RedirectResponse(url=f"/admin/scripts/{project_id}", status_code=302)
