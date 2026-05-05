from fastapi import Request, Depends
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.auth_service import decode_token
from app.models.user import AdminUser


class RedirectException(Exception):
    def __init__(self, url: str, status_code: int = 302):
        self.url = url
        self.status_code = status_code


def get_current_admin(request: Request, db: Session = Depends(get_db)) -> AdminUser:
    token = request.cookies.get("access_token")
    if not token:
        raise RedirectException(url="/auth/login")
    payload = decode_token(token)
    if not payload:
        raise RedirectException(url="/auth/login")
    user = db.query(AdminUser).filter(AdminUser.email == payload.get("sub")).first()
    if not user or not user.is_active:
        raise RedirectException(url="/auth/login")
    return user
