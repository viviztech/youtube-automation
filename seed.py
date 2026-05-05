"""
Run once to initialize the database:
    python seed.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app.database import engine, SessionLocal, Base
from app.models import AdminUser, DayTask, APISettings
from app.services.auth_service import hash_password
from app.services.settings_service import seed_default_settings

# Import all models so SQLAlchemy registers them before create_all
import app.models  # noqa


def seed():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # Admin user
        existing = db.query(AdminUser).filter(AdminUser.email == "admin@youtubetool.com").first()
        if not existing:
            db.add(AdminUser(
                email="admin@youtubetool.com",
                password_hash=hash_password("Admin@1234"),
                full_name="Admin",
                is_active=True,
            ))
            db.commit()
            print("Admin user created: admin@youtubetool.com / Admin@1234")
        else:
            print("Admin user already exists.")

        # Default API settings
        seed_default_settings(db)
        print("Default API settings seeded.")

        # 30-day tasks
        if db.query(DayTask).count() == 0:
            tasks = [
                # Week 1 — Plan & Setup
                (1, 1, "Choose Your Niche", "Pick a profitable niche with high demand and low competition."),
                (2, 1, "Research & Validate", "Analyze trends, keywords, and competitors. Validate your content ideas."),
                (3, 1, "Create Your Channel", "Create your channel, write a keyword-rich title, description & upload avatar logo."),
                (4, 1, "Brand Your Channel", "Design banner, choose colors, fonts, and create a strong brand identity."),
                (5, 1, "Content Strategy", "Plan your content pillar, video formats, and posting schedule."),
                (6, 1, "Setup Systems", "Organize folders, scripts, tools & a workflow for consistency."),
                (7, 1, "Prepare Content", "Brainstorm 10–15 video ideas and pick your first 3 videos."),
                # Week 2 — Create & Produce
                (8, 2, "Script Your Videos", "Write engaging scripts that hook, deliver value & retain viewers."),
                (9, 2, "Record Voiceover", "Record high-quality voiceovers using a good mic or AI voice tools."),
                (10, 2, "Gather Assets", "Collect or create video clips, images, animations, B-roll & audio."),
                (11, 2, "Edit Video 1", "Edit your first video with cuts, captions, effects & engaging visuals."),
                (12, 2, "Edit Video 2", "Edit your second video. Focus on pacing, retention & storytelling."),
                (13, 2, "Edit Video 3", "Edit your third video and make it your best one yet!"),
                (14, 2, "Upload 3 Videos", "Optimize titles, thumbnails, descriptions & end screens."),
                # Week 3 — Optimize & Grow
                (15, 3, "Keyword Research", "Find high-ranking keywords for titles, tags & descriptions."),
                (16, 3, "Create Viral Thumbnails", "Design click-worthy thumbnails that stand out and create curiosity."),
                (17, 3, "Optimize Everything", "Optimize metadata, chapters, cards, tags & playlists for SEO."),
                (18, 3, "Promote Smartly", "Share on Reddit, Facebook groups, Twitter, Pinterest & niche forums."),
                (19, 3, "Engage & Reply", "Reply to comments, ask questions & build a community early."),
                (20, 3, "Analyze Performance", "Check CTR, retention, traffic sources & improve weak areas."),
                (21, 3, "Improve & Iterate", "Apply insights and plan your next 3 high-performing videos."),
                # Week 4 — Scale & Go Viral
                (22, 4, "Batch Script Your Next Videos", "Write 5–10 scripts to stay consistent."),
                (23, 4, "Batch Create Content", "Record voiceovers and collect assets in batches."),
                (24, 4, "Edit in Bulk", "Edit multiple videos to save time and stay ahead."),
                (25, 4, "Upload Consistently", "Upload on schedule. Consistency builds momentum."),
                (26, 4, "Leverage Trends", "Create trend-based videos in your niche to get more reach."),
                (27, 4, "Build Playlists", "Organize videos into playlists to increase watch time."),
                (28, 4, "Collab & Network", "Reach out to other creators, collab & expand your audience."),
                # Final Days
                (29, 4, "Double Down on What Works", "Analyze top performers and create more of what your audience loves."),
                (30, 4, "Launch Your Growth System", "You now have a content machine. Keep creating, optimizing & scaling!"),
            ]
            for day, week, title, desc in tasks:
                db.add(DayTask(day_number=day, week_number=week, title=title, description=desc))
            db.commit()
            print(f"30 day tasks seeded.")
        else:
            print("Day tasks already exist.")

        print("\nDatabase initialized successfully!")
        print("Login: admin@youtubetool.com / Admin@1234")
        print("Start: python run.py  →  http://localhost:8004")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
