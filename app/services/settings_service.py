from datetime import datetime
from sqlalchemy.orm import Session
from app.models.api_settings import APISettings

DEFAULT_SETTINGS = [
    {"key": "claude_api_key", "label": "Claude API Key", "description": "Anthropic Claude API key (sk-ant-...)", "group": "claude", "is_secret": True},
    {"key": "claude_model", "label": "Claude Model", "description": "Model ID to use for script generation", "group": "claude", "is_secret": False, "default": "claude-sonnet-4-6"},
    {"key": "elevenlabs_api_key", "label": "ElevenLabs API Key", "description": "ElevenLabs API key for voiceover generation", "group": "elevenlabs", "is_secret": True},
    {"key": "elevenlabs_voice_id", "label": "ElevenLabs Voice ID", "description": "Voice ID from ElevenLabs (default: Rachel)", "group": "elevenlabs", "is_secret": False, "default": "21m00Tcm4TlvDq8ikWAM"},
    {"key": "youtube_data_api_key", "label": "YouTube Data API Key", "description": "YouTube Data API v3 server key for keyword research", "group": "youtube", "is_secret": True},
    {"key": "youtube_client_id", "label": "YouTube OAuth Client ID", "description": "Google OAuth2 client ID for video uploads", "group": "youtube", "is_secret": False},
    {"key": "youtube_client_secret", "label": "YouTube OAuth Client Secret", "description": "Google OAuth2 client secret", "group": "youtube", "is_secret": True},
    {"key": "youtube_oauth_token_json", "label": "YouTube OAuth Token (JSON)", "description": "Stored OAuth2 token after completing the consent flow", "group": "youtube", "is_secret": True},
    {"key": "youtube_channel_id", "label": "YouTube Channel ID", "description": "Your YouTube channel ID (UC...)", "group": "youtube", "is_secret": False},
    {"key": "channel_niche", "label": "Channel Niche", "description": "Your channel's niche (used for automated keyword research)", "group": "general", "is_secret": False, "default": ""},
]


def seed_default_settings(db: Session):
    for item in DEFAULT_SETTINGS:
        existing = db.query(APISettings).filter(APISettings.key == item["key"]).first()
        if not existing:
            db.add(APISettings(
                key=item["key"],
                value=item.get("default", ""),
                label=item["label"],
                description=item.get("description", ""),
                is_secret=item.get("is_secret", True),
                group=item.get("group", "general"),
            ))
    db.commit()


def get_setting(key: str, db: Session) -> str:
    row = db.query(APISettings).filter(APISettings.key == key).first()
    return row.value if row else ""


def set_setting(key: str, value: str, db: Session):
    row = db.query(APISettings).filter(APISettings.key == key).first()
    if row:
        row.value = value
        row.updated_at = datetime.utcnow()
    else:
        db.add(APISettings(key=key, value=value, label=key))
    db.commit()


def get_all_settings(db: Session) -> dict:
    rows = db.query(APISettings).all()
    return {r.key: r for r in rows}
