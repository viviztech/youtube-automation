import os
import uuid
from datetime import datetime
from fastapi import UploadFile
from app.config import get_settings

settings = get_settings()


def save_upload(file: UploadFile, subfolder: str) -> str:
    ext = os.path.splitext(file.filename)[1] if file.filename else ""
    filename = f"{uuid.uuid4()}{ext}"
    dirpath = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(dirpath, exist_ok=True)
    filepath = os.path.join(dirpath, filename)
    with open(filepath, "wb") as f:
        f.write(file.file.read())
    return filepath


def list_assets(subfolder: str) -> list[dict]:
    dirpath = os.path.join(settings.UPLOAD_DIR, subfolder)
    os.makedirs(dirpath, exist_ok=True)
    assets = []
    for fname in os.listdir(dirpath):
        fpath = os.path.join(dirpath, fname)
        if os.path.isfile(fpath):
            stat = os.stat(fpath)
            assets.append({
                "name": fname,
                "path": fpath,
                "url": f"/uploads/{subfolder}/{fname}",
                "size": stat.st_size,
                "ext": os.path.splitext(fname)[1].lower(),
                "created_at": datetime.fromtimestamp(stat.st_ctime),
            })
    return sorted(assets, key=lambda x: x["created_at"], reverse=True)


def delete_asset(subfolder: str, filename: str) -> bool:
    fpath = os.path.join(settings.UPLOAD_DIR, subfolder, filename)
    if os.path.isfile(fpath):
        os.remove(fpath)
        return True
    return False
