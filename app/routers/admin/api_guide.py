from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.services.settings_service import get_setting

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/api-guide", response_class=HTMLResponse)
async def api_guide(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    api_status = {
        "claude_api_key": bool(get_setting("claude_api_key", db)),
        "elevenlabs_api_key": bool(get_setting("elevenlabs_api_key", db)),
        "youtube_data_api_key": bool(get_setting("youtube_data_api_key", db)),
        "youtube_client_id": bool(get_setting("youtube_client_id", db)),
    }
    return templates.TemplateResponse("admin/api_guide.html", {
        "request": request,
        "admin": current_admin,
        "api_status": api_status,
        "active_page": "api_guide",
    })
