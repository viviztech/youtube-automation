# API Keys Setup Guide

This guide walks you through creating API keys for all 4 platforms used by the YT Automation app.

---

## Table of Contents

1. [Claude API Key (Anthropic)](#1-claude-api-key-anthropic)
2. [ElevenLabs API Key](#2-elevenlabs-api-key)
3. [YouTube Data API Key (Google)](#3-youtube-data-api-key-google)
4. [YouTube OAuth2 Credentials (Google)](#4-youtube-oauth2-credentials-google)

---

## 1. Claude API Key (Anthropic)

Used for: **AI script generation**

### Steps

1. Go to [console.anthropic.com](https://console.anthropic.com)
2. Sign up or log in to your Anthropic account
3. In the left sidebar, click **API Keys**
4. Click **Create Key**
5. Give it a name (e.g. `yt-automation`)
6. Copy the key — it starts with `sk-ant-...`

> **Important:** The key is shown only once. Copy it immediately.

### Add to App

Go to **Settings → Claude AI** in the app and paste the key into **Claude API Key**.

### Pricing Notes

- New accounts get free credits to start
- Script generation uses `claude-sonnet-4-6` — roughly **$0.003 per 1K input tokens** and **$0.015 per 1K output tokens**
- A typical 10-minute script uses ~2,000–4,000 tokens total (~$0.05–0.10 per script)

---

## 2. ElevenLabs API Key

Used for: **AI voiceover generation (text-to-speech)**

### Steps

1. Go to [elevenlabs.io](https://elevenlabs.io)
2. Click **Sign Up** and create an account
3. After logging in, click your **profile icon** (top right)
4. Select **Profile + API Key**
5. Under **API Key**, click the copy icon

### Get Your Voice ID

1. In the left sidebar, click **Voices**
2. Browse the Voice Library or use your own cloned voice
3. Click a voice to open it
4. Copy the **Voice ID** shown below the voice name (e.g. `21m00Tcm4TlvDq8ikWAM`)

### Add to App

Go to **Settings → ElevenLabs** in the app:
- **ElevenLabs API Key** → paste your API key
- **ElevenLabs Voice ID** → paste the voice ID (default: Rachel)

### Free Plan Limits

| Plan | Characters/month |
|------|-----------------|
| Free | 10,000 |
| Starter ($5/mo) | 30,000 |
| Creator ($22/mo) | 100,000 |

A typical 10-minute script ≈ 1,500 words ≈ 8,000 characters.

---

## 3. YouTube Data API Key (Google)

Used for: **Keyword research & trending video fetch** (read-only, no login required)

### Steps

**Step 1 — Create a Google Cloud Project**

1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Click the project dropdown at the top → **New Project**
3. Name it `yt-automation` → click **Create**
4. Wait for the project to be created, then select it

**Step 2 — Enable YouTube Data API v3**

1. In the left sidebar go to **APIs & Services → Library**
2. Search for `YouTube Data API v3`
3. Click on it → click **Enable**

**Step 3 — Create an API Key**

1. Go to **APIs & Services → Credentials**
2. Click **+ Create Credentials → API Key**
3. Your API key is created and shown (starts with `AIza...`)
4. Click **Edit API Key** to restrict it:
   - Under **API restrictions**, select **Restrict key**
   - Choose **YouTube Data API v3**
   - Click **Save**

### Add to App

Go to **Settings → YouTube** in the app and paste into **YouTube Data API Key**.

### Quota

- Free quota: **10,000 units/day**
- A keyword search costs 100 units
- Trending video fetch costs 1 unit
- You get ~100 keyword searches/day for free

---

## 4. YouTube OAuth2 Credentials (Google)

Used for: **Uploading videos to YouTube** (requires user authorization)

> This uses the same Google Cloud project from Step 3 above.

### Steps

**Step 1 — Configure OAuth Consent Screen**

1. Go to [console.cloud.google.com](https://console.cloud.google.com) → select your project
2. Go to **APIs & Services → OAuth consent screen**
3. Select **External** → click **Create**
4. Fill in:
   - **App name**: `YT Automation`
   - **User support email**: your Gmail address
   - **Developer contact email**: your Gmail address
5. Click **Save and Continue**
6. On **Scopes** page, click **Add or Remove Scopes**
7. Search and add:
   - `https://www.googleapis.com/auth/youtube.upload`
   - `https://www.googleapis.com/auth/youtube.readonly`
8. Click **Save and Continue**
9. On **Test Users**, click **+ Add Users** → add your Gmail address
10. Click **Save and Continue** → **Back to Dashboard**

**Step 2 — Create OAuth2 Client ID**

1. Go to **APIs & Services → Credentials**
2. Click **+ Create Credentials → OAuth client ID**
3. Application type: select **Web application**
4. Name: `YT Automation Local`
5. Under **Authorized redirect URIs**, click **+ Add URI**
6. Enter exactly: `http://localhost:8004/admin/upload/oauth/callback`
7. Click **Create**
8. A dialog shows your **Client ID** and **Client Secret** — copy both

> **Client ID** looks like: `123456789-abc...apps.googleusercontent.com`
> **Client Secret** looks like: `GOCSPX-...`

**Step 3 — Add to App**

Go to **Settings → YouTube** in the app:
- **YouTube OAuth Client ID** → paste Client ID
- **YouTube OAuth Client Secret** → paste Client Secret

**Step 4 — Connect Your YouTube Account**

1. Go to **YouTube Upload** page in the app
2. Click **Connect Account**
3. You are redirected to Google's consent screen
4. Log in with the Gmail account that owns your YouTube channel
5. Click **Allow**
6. You are redirected back — the app stores the token automatically
7. Status shows **Connected — ready to upload**

> You only need to do this once. The token is stored in the local database and auto-refreshed.

---

## Quick Reference

| Setting Key | Where to Find It | Used For |
|-------------|-----------------|----------|
| `claude_api_key` | console.anthropic.com → API Keys | Script generation |
| `elevenlabs_api_key` | elevenlabs.io → Profile → API Key | Voiceover generation |
| `elevenlabs_voice_id` | elevenlabs.io → Voices → Voice ID | Select voice |
| `youtube_data_api_key` | Google Cloud → Credentials → API Key | Keyword research |
| `youtube_client_id` | Google Cloud → Credentials → OAuth Client | Video upload auth |
| `youtube_client_secret` | Google Cloud → Credentials → OAuth Client | Video upload auth |

---

## Where to Enter Keys in the App

1. Start the app: `python run.py`
2. Open [http://localhost:8004](http://localhost:8004)
3. Log in: `admin@youtubetool.com` / `Admin@1234`
4. Go to **Settings** (bottom of left sidebar)
5. Fill in each section and click **Save All Settings**

---

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Claude API key not set` | Add key in Settings → Claude AI |
| `ElevenLabs error 401` | API key is invalid or expired — regenerate it |
| `YouTube API quota exceeded` | Wait 24 hours or request a quota increase in Google Cloud |
| `OAuth cancelled` | Make sure `http://localhost:8004/admin/upload/oauth/callback` is added as authorized redirect URI |
| `Token expired` | Go to YouTube Upload → click Connect Account again |
| `Access blocked` | Your Google app is in testing mode — add your email as a Test User in OAuth consent screen |
