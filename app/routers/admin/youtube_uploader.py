import json
import os
from datetime import datetime
from fastapi import APIRouter, Request, Form, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.models.video_project import VideoProject
from app.models.youtube_upload import YouTubeUpload
from app.services.youtube_service import get_oauth_flow, exchange_code_for_token, upload_video
from app.services.settings_service import get_setting, set_setting
from app.services.file_service import save_upload

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    ready_projects = db.query(VideoProject).filter(VideoProject.status == "ready").all()
    oauth_token = get_setting("youtube_oauth_token_json", db)
    client_id = get_setting("youtube_client_id", db)

    return templates.TemplateResponse("admin/youtube_upload.html", {
        "request": request,
        "admin": current_admin,
        "ready_projects": ready_projects,
        "oauth_connected": bool(oauth_token),
        "can_connect": bool(client_id),
        "active_page": "upload",
        "error": request.query_params.get("error"),
        "success": request.query_params.get("success"),
    })


@router.get("/upload/oauth/start")
async def oauth_start(
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    client_id = get_setting("youtube_client_id", db)
    client_secret = get_setting("youtube_client_secret", db)
    if not client_id or not client_secret:
        return RedirectResponse(url="/admin/upload?error=YouTube+OAuth+credentials+not+set+in+Settings.", status_code=302)

    flow = get_oauth_flow(client_id, client_secret)
    auth_url, _ = flow.authorization_url(prompt="consent", access_type="offline")
    return RedirectResponse(url=auth_url, status_code=302)


@router.get("/upload/oauth/callback")
async def oauth_callback(
    request: Request,
    code: str = None,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    if not code:
        return RedirectResponse(url="/admin/upload?error=OAuth+cancelled.", status_code=302)

    client_id = get_setting("youtube_client_id", db)
    client_secret = get_setting("youtube_client_secret", db)

    try:
        token_data = exchange_code_for_token(code, client_id, client_secret)
        set_setting("youtube_oauth_token_json", json.dumps(token_data), db)
        return RedirectResponse(url="/admin/upload?success=YouTube+account+connected+successfully!", status_code=302)
    except Exception as e:
        return RedirectResponse(url=f"/admin/upload?error={str(e)[:100]}", status_code=302)


@router.post("/upload/submit")
async def submit_upload(
    project_id: str = Form(...),
    yt_title: str = Form(...),
    yt_description: str = Form(""),
    yt_tags: str = Form(""),
    yt_category_id: str = Form("22"),
    privacy_status: str = Form("public"),
    video_file: UploadFile = File(...),
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    token_json = get_setting("youtube_oauth_token_json", db)
    if not token_json:
        return RedirectResponse(url="/admin/upload?error=Connect+YouTube+account+first.", status_code=302)

    project = db.query(VideoProject).filter(VideoProject.id == project_id).first()
    if not project:
        return RedirectResponse(url="/admin/upload?error=Project+not+found.", status_code=302)

    video_path = save_upload(video_file, "videos")
    upload = YouTubeUpload(
        project_id=project_id,
        yt_title=yt_title,
        yt_description=yt_description,
        yt_tags=yt_tags,
        yt_category_id=yt_category_id,
        privacy_status=privacy_status,
        video_file_path=video_path,
        status="uploading",
    )
    db.add(upload)
    db.flush()

    try:
        tags = [t.strip() for t in yt_tags.split(",") if t.strip()]
        result = upload_video(video_path, yt_title, yt_description, tags, yt_category_id, privacy_status, token_json)
        upload.youtube_video_id = result["video_id"]
        upload.youtube_url = result["url"]
        upload.status = "done"
        upload.uploaded_at = datetime.utcnow()
        project.status = "uploaded"
        db.commit()
        return RedirectResponse(url=f"/admin/upload?success=Video+uploaded!+ID:+{result['video_id']}", status_code=302)
    except Exception as e:
        upload.status = "failed"
        upload.error_msg = str(e)
        db.commit()
        return RedirectResponse(url=f"/admin/upload?error={str(e)[:150]}", status_code=302)
