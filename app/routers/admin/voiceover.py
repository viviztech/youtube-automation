import os
from datetime import datetime
from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.models.video_project import VideoProject
from app.models.voiceover_job import VoiceoverJob
from app.services.elevenlabs_service import generate_voiceover, list_voices
from app.services.settings_service import get_setting
from app.config import get_settings

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")
settings = get_settings()


@router.get("/voiceover", response_class=HTMLResponse)
async def voiceover_page(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    api_key = get_setting("elevenlabs_api_key", db)
    voices = await list_voices(api_key) if api_key else []
    jobs = db.query(VoiceoverJob).order_by(VoiceoverJob.created_at.desc()).all()
    scripted_projects = db.query(VideoProject).filter(VideoProject.status == "scripted").all()

    return templates.TemplateResponse("admin/voiceover.html", {
        "request": request,
        "admin": current_admin,
        "jobs": jobs,
        "voices": voices,
        "scripted_projects": scripted_projects,
        "active_page": "voiceover",
        "error": request.query_params.get("error"),
    })


@router.post("/voiceover/generate")
async def generate(
    project_id: str = Form(...),
    voice_id: str = Form(...),
    voice_name: str = Form(""),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    api_key = get_setting("elevenlabs_api_key", db)
    if not api_key:
        return RedirectResponse(url="/admin/voiceover?error=ElevenLabs+API+key+not+set.", status_code=302)

    project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
    if not project or not project.script:
        return RedirectResponse(url="/admin/voiceover?error=Project+or+script+not+found.", status_code=302)

    job = VoiceoverJob(
        project_id=project_id,
        voice_id=voice_id,
        voice_name=voice_name,
        status="processing",
    )
    db.add(job)
    db.flush()

    output_path = os.path.join(settings.UPLOAD_DIR, "audio", f"{project_id}.mp3")
    result = await generate_voiceover(project.script.content, voice_id, api_key, output_path)

    job.status = result["status"]
    job.audio_path = result.get("path", "")
    job.duration_seconds = result.get("duration_seconds")
    job.error_msg = result.get("error")
    job.completed_at = datetime.utcnow()

    if result["status"] == "done":
        project.status = "voiced"

    db.commit()
    return RedirectResponse(url="/admin/voiceover", status_code=302)


@router.get("/voiceover/{job_id}/download")
async def download_audio(
    job_id: str,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    job = db.query(VoiceoverJob).filter(VoiceoverJob.id == job_id).first()
    if not job or not job.audio_path or not os.path.isfile(job.audio_path):
        return RedirectResponse(url="/admin/voiceover", status_code=302)
    return FileResponse(job.audio_path, media_type="audio/mpeg", filename=f"voiceover_{job_id}.mp3")
