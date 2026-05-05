from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.services.settings_service import get_all_settings, set_setting

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    all_settings = get_all_settings(db)
    groups = {}
    for key, row in all_settings.items():
        groups.setdefault(row.group, []).append(row)

    return templates.TemplateResponse("admin/settings.html", {
        "request": request,
        "admin": current_admin,
        "groups": groups,
        "saved": request.query_params.get("saved"),
        "active_page": "settings",
    })


@router.post("/settings")
async def save_settings(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    form = await request.form()
    for key, value in form.items():
        set_setting(key, str(value), db)
    return RedirectResponse(url="/admin/settings?saved=1", status_code=302)
