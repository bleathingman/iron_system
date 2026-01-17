import json
from pathlib import Path
from datetime import date

PROJECT_ROOT = Path("/home/divh/iron_system")
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(parents=True, exist_ok=True)

SAVE_PATH = DATA_DIR / "save.json"

DAILY_XP_CAP = 120


def create_default_save():
    return {
        "user": {"name": "", "weight": 0, "goal_weight": 0},
        "level": 1,
        "xp": 0,
        "xp_required": 100,
        "streak": 0,
        "week": 1,
        "completed_today": [],
        "last_completed_date": None,
        "last_xp_date": None,
        "profile": {
            "total_days": 0,
            "total_xp_earned": 0,
            "longest_streak": 0
        },
        "history": {},
        "badges": {},
        "daily_xp": 0
    }


def load_save():
    if not SAVE_PATH.exists():
        return create_default_save()

    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            save = json.load(f)
    except Exception:
        return create_default_save()

    return validate_save(save)


def validate_save(save):
    default = create_default_save()
    for k, v in default.items():
        if k not in save:
            save[k] = v
    return save


def save_progress(save):
    with open(SAVE_PATH, "w", encoding="utf-8") as f:
        json.dump(save, f, indent=2, ensure_ascii=False)
        f.flush()


# =====================
# XP & LEVEL
# =====================
def add_xp_and_level_up(save, xp):
    today = str(date.today())

    if save.get("last_xp_date") != today:
        save["daily_xp"] = 0
        save["last_xp_date"] = today

    xp_allowed = max(0, DAILY_XP_CAP - save["daily_xp"])
    xp = min(xp, xp_allowed)

    if xp <= 0:
        return

    save["daily_xp"] += xp
    save["xp"] += xp
    save["profile"]["total_xp_earned"] += xp

    while save["xp"] >= save["xp_required"]:
        save["xp"] -= save["xp_required"]
        save["level"] += 1
        save["xp_required"] = int(save["xp_required"] * 1.65)


# =====================
# DAILY LOGIC
# =====================
def log_daily_progress(save, quest, xp):
    today = str(date.today())
    save.setdefault("history", {})
    save["history"].setdefault(today, {"quests": [], "xp": 0})

    save["history"][today]["quests"].append(quest)
    save["history"][today]["xp"] += xp
    save["profile"]["total_days"] += 1


def update_streak(save):
    today = str(date.today())
    if save["last_completed_date"] == today:
        return

    save["streak"] += 1
    save["last_completed_date"] = today
    save["profile"]["longest_streak"] = max(
        save["profile"]["longest_streak"],
        save["streak"]
    )


def update_badges(save):
    if save["streak"] >= 7:
        save["badges"]["week_1"] = True
    if save["streak"] >= 14:
        save["badges"]["week_2"] = True
    if save["streak"] >= 21:
        save["badges"]["perfect_week"] = True


def midnight_check(save):
    today = str(date.today())
    if save["last_completed_date"] != today:
        save["completed_today"] = []
        save["daily_xp"] = 0
