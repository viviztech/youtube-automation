from fastapi import APIRouter, Request, UploadFile, File, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from app.dependencies import get_current_admin
from app.models.user import AdminUser
from app.services.file_service import save_upload, list_assets, delete_asset

router = APIRouter(tags=["admin"])
templates = Jinja2Templates(directory="app/templates")


@router.get("/assets", response_class=HTMLResponse)
async def assets_page(
    request: Request,
    current_admin: AdminUser = Depends(get_current_admin),
):
    videos = list_assets("videos")
    audio = list_assets("audio")
    misc = list_assets("assets")
    return templates.TemplateResponse("admin/assets.html", {
        "request": request,
        "admin": current_admin,
        "videos": videos,
        "audio": audio,
        "misc": misc,
        "active_page": "assets",
    })


@router.post("/assets/upload")
async def upload_asset(
    file: UploadFile = File(...),
    subfolder: str = "assets",
    current_admin: AdminUser = Depends(get_current_admin),
):
    ext = (file.filename or "").rsplit(".", 1)[-1].lower()
    if ext in ("mp4", "mov", "avi", "mkv"):
        subfolder = "videos"
    elif ext in ("mp3", "wav", "m4a"):
        subfolder = "audio"
    path = save_upload(file, subfolder)
    return RedirectResponse(url="/admin/assets", status_code=302)


@router.delete("/assets/{subfolder}/{filename}")
async def delete_asset_file(
    subfolder: str,
    filename: str,
    current_admin: AdminUser = Depends(get_current_admin),
):
    deleted = delete_asset(subfolder, filename)
    return JSONResponse({"deleted": deleted})
