import json
import os
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
REDIRECT_URI = "http://localhost:8004/admin/upload/oauth/callback"


def get_oauth_flow(client_id: str, client_secret: str) -> Flow:
    client_config = {
        "web": {
            "client_id": client_id,
            "client_secret": client_secret,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [REDIRECT_URI],
        }
    }
    flow = Flow.from_client_config(client_config, scopes=SCOPES)
    flow.redirect_uri = REDIRECT_URI
    return flow


def exchange_code_for_token(code: str, client_id: str, client_secret: str) -> dict:
    flow = get_oauth_flow(client_id, client_secret)
    flow.fetch_token(code=code)
    creds = flow.credentials
    return {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else [],
    }


def get_credentials(token_json: str) -> Credentials:
    data = json.loads(token_json)
    creds = Credentials(
        token=data.get("token"),
        refresh_token=data.get("refresh_token"),
        token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=data.get("client_id"),
        client_secret=data.get("client_secret"),
        scopes=data.get("scopes"),
    )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds


def upload_video(
    video_path: str,
    title: str,
    description: str,
    tags: list[str],
    category_id: str,
    privacy_status: str,
    token_json: str,
) -> dict:
    creds = get_credentials(token_json)
    youtube = build("youtube", "v3", credentials=creds)

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": category_id,
        },
        "status": {"privacyStatus": privacy_status},
    }

    media = MediaFileUpload(video_path, chunksize=1024 * 1024, resumable=True)
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        _, response = request.next_chunk()

    video_id = response.get("id", "")
    return {"video_id": video_id, "url": f"https://www.youtube.com/watch?v={video_id}"}


def search_keywords(query: str, api_key: str, max_results: int = 25) -> list[dict]:
    if not api_key:
        return []
    youtube = build("youtube", "v3", developerKey=api_key)
    response = youtube.search().list(
        part="snippet",
        q=query,
        type="video",
        order="viewCount",
        maxResults=max_results,
    ).execute()

    results = []
    for item in response.get("items", []):
        snippet = item.get("snippet", {})
        results.append({
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "video_id": item.get("id", {}).get("videoId", ""),
            "description": snippet.get("description", "")[:200],
        })
    return results


def get_trending_videos(region_code: str = "IN", category_id: str = "0", api_key: str = "") -> list[dict]:
    if not api_key:
        return []
    youtube = build("youtube", "v3", developerKey=api_key)
    response = youtube.videos().list(
        part="snippet,statistics",
        chart="mostPopular",
        regionCode=region_code,
        videoCategoryId=category_id,
        maxResults=25,
    ).execute()

    results = []
    for item in response.get("items", []):
        snippet = item.get("snippet", {})
        stats = item.get("statistics", {})
        results.append({
            "title": snippet.get("title", ""),
            "channel": snippet.get("channelTitle", ""),
            "video_id": item.get("id", ""),
            "view_count": stats.get("viewCount", "0"),
            "like_count": stats.get("likeCount", "0"),
            "published_at": snippet.get("publishedAt", ""),
        })
    return results
