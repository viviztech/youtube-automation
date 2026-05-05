# YT Automation

An AI-powered faceless YouTube channel automation tool built with FastAPI. Automates the entire content pipeline — from niche research and script generation to voiceover, video upload, and performance tracking — following a structured 30-day growth framework.

---

## Screenshots

| Dashboard | 30-Day Plan | Script Generator |
|-----------|-------------|-----------------|
| Stats, progress bar, recent projects | Weekly accordion with task tracking | Claude AI script generation form |

| Video Queue | Keyword Research | API Keys Guide |
|-------------|-----------------|----------------|
| Kanban pipeline board | YouTube + Google Trends | Live connection status per platform |

---

## Features

- **AI Script Generation** — Claude `claude-sonnet-4-6` writes full video scripts with hook, segments, CTA, and B-roll suggestions
- **Voiceover Generation** — ElevenLabs text-to-speech converts scripts to MP3 with an inline audio player
- **Keyword Research** — YouTube Data API v3 search + Google Trends integration with trend spike detection
- **YouTube Upload** — OAuth2 video upload directly to your YouTube channel
- **30-Day Plan Tracker** — All 30 daily tasks across 4 weeks with checkboxes, notes, and progress bar
- **Video Pipeline (Kanban)** — Track projects through Scripted → Voiced → Edited → Ready → Uploaded
- **Asset Library** — Upload and manage B-roll clips, images, and audio files
- **Scheduled Jobs** — APScheduler runs daily keyword fetch (08:00) and trend alert (10:00) automatically
- **In-App API Guide** — Step-by-step setup instructions for all 4 platforms with live connection status

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Jinja2 |
| Frontend | TailwindCSS CDN (dark theme, YouTube red) |
| Database | SQLite via SQLAlchemy 2.0 |
| Auth | JWT cookies (python-jose + bcrypt) |
| AI Script | Anthropic Claude API (`claude-sonnet-4-6`) |
| Voiceover | ElevenLabs REST API |
| YouTube | Google API Python Client (OAuth2 + Data API v3) |
| Trends | pytrends (Google Trends) |
| Scheduler | APScheduler (background cron jobs) |

---

## Project Structure

```
youtube-automation/
├── app/
│   ├── main.py                  # FastAPI app factory + scheduler startup
│   ├── config.py                # Settings via pydantic-settings
│   ├── database.py              # SQLite engine + session
│   ├── dependencies.py          # Auth dependency + RedirectException
│   ├── models/                  # 8 SQLAlchemy models
│   ├── routers/
│   │   ├── auth.py              # Login / logout
│   │   └── admin/               # 11 admin page routers
│   ├── services/                # Claude, ElevenLabs, YouTube, Trends, Auth
│   ├── tasks/                   # APScheduler background jobs
│   ├── static/                  # CSS + JS
│   ├── templates/               # Jinja2 HTML templates
│   └── uploads/                 # videos / audio / assets
├── seed.py                      # DB init + admin user + 30 day tasks
├── run.py                       # uvicorn launcher
├── requirements.txt
└── .env.example
```

---

## Quick Start

### 1. Clone the repository

```bash
git clone https://github.com/viviztech/youtube-automation.git
cd youtube-automation
```

### 2. Create virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # Mac/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
```

Open `.env` and fill in your API keys (see [API Keys Setup](#api-keys-setup) below):

```ini
SECRET_KEY=your-random-secret-key-here
CLAUDE_API_KEY=sk-ant-...
ELEVENLABS_API_KEY=...
YOUTUBE_DATA_API_KEY=AIza...
YOUTUBE_CLIENT_ID=...apps.googleusercontent.com
YOUTUBE_CLIENT_SECRET=GOCSPX-...
```

### 5. Initialize the database

```bash
python seed.py
```

This creates all tables, the admin user, and seeds all 30 day tasks.

### 6. Start the app

```bash
python run.py
```

Open [http://localhost:8004](http://localhost:8004)

**Login:** `admin@youtubetool.com` / `Admin@1234`

---

## API Keys Setup

All API keys are entered inside the app at **Settings** → each section. An interactive setup guide with step-by-step instructions is available at `/admin/api-guide` after logging in.

| Key | Platform | Used For | Cost |
|-----|----------|----------|------|
| `CLAUDE_API_KEY` | [console.anthropic.com](https://console.anthropic.com) | Script generation | ~$0.05–0.10/script |
| `ELEVENLABS_API_KEY` | [elevenlabs.io](https://elevenlabs.io) | Voiceover (TTS) | Free: 10K chars/mo |
| `YOUTUBE_DATA_API_KEY` | [Google Cloud Console](https://console.cloud.google.com) | Keyword research | Free: 10K units/day |
| `YOUTUBE_CLIENT_ID` + `YOUTUBE_CLIENT_SECRET` | Google Cloud → OAuth2 | Video upload | Free |

### YouTube OAuth2 Redirect URI

When creating your OAuth2 credentials in Google Cloud Console, add this as an **Authorized Redirect URI**:

```
http://localhost:8004/admin/upload/oauth/callback
```

---

## Admin Pages

| Page | Route | Description |
|------|-------|-------------|
| Dashboard | `/admin/dashboard` | Stats cards, 30-day progress bar, recent projects |
| 30-Day Plan | `/admin/days` | All 30 tasks in 4 weekly accordions with notes |
| Script Generator | `/admin/scripts` | Generate scripts via Claude AI |
| Voiceover | `/admin/voiceover` | Generate MP3 voiceovers via ElevenLabs |
| Assets | `/admin/assets` | Upload and manage B-roll, images, audio |
| Video Queue | `/admin/queue` | Kanban pipeline board |
| YouTube Upload | `/admin/upload` | Upload videos via YouTube Data API |
| Keyword Research | `/admin/research` | YouTube search + Google Trends |
| Scheduler | `/admin/scheduler` | View and manually trigger cron jobs |
| Settings | `/admin/settings` | API keys configuration |
| API Keys Guide | `/admin/api-guide` | Step-by-step platform setup instructions |

---

## Database Models

| Model | Description |
|-------|-------------|
| `AdminUser` | Single admin account |
| `DayTask` | 30-day plan tasks (seeded from framework) |
| `VideoProject` | Central pipeline entity linking all content |
| `Script` | Claude-generated script content |
| `VoiceoverJob` | ElevenLabs job record + audio path |
| `YouTubeUpload` | Upload result + YouTube video ID |
| `APISettings` | Key-value store for all API credentials |
| `KeywordResult` | Cached keyword and trend research data |

---

## Background Jobs

| Job | Schedule | Description |
|-----|----------|-------------|
| `daily_keyword_fetch_job` | 08:00 daily | Fetches YouTube trending + Google Trends for your niche |
| `trend_alert_job` | 10:00 daily | Detects keywords with >50% score spike, marks as trending |

Both jobs can be triggered manually from the **Scheduler** page.

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `APP_NAME` | `YT Automation` | App display name |
| `SECRET_KEY` | — | JWT signing secret (change this!) |
| `DEBUG` | `True` | Enable hot reload |
| `PORT` | `8004` | Server port |
| `DATABASE_URL` | `sqlite:///./youtube_automation.db` | Database path |
| `CLAUDE_MODEL` | `claude-sonnet-4-6` | Claude model ID |
| `ELEVENLABS_VOICE_ID` | `21m00Tcm4TlvDq8ikWAM` | Default voice (Rachel) |
| `UPLOAD_DIR` | `app/uploads` | File upload directory |

---

## 30-Day Framework

The app is built around this growth roadmap:

| Week | Focus | Days |
|------|-------|------|
| Week 1 | Plan & Setup | Niche, research, branding, content strategy |
| Week 2 | Create & Produce | Scripts, voiceovers, editing, first 3 uploads |
| Week 3 | Optimize & Grow | SEO, thumbnails, promotion, analytics |
| Week 4 | Scale & Go Viral | Batch production, trends, playlists, collab |

> **Remember:** Niche + Value + Consistency = Viral Growth

---

## License

MIT
