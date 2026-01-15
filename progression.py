import json
import os
from datetime import date

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SAVE_PATH = os.path.join(BASE_DIR, "data", "save.json")

DAILY_XP_CAP = 120  # XP max gagnable par jour


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
    if not os.path.exists(SAVE_PATH):
        save = create_default_save()
        save_progress(save)
        return save

    try:
        with open(SAVE_PATH, "r") as f:
            save = json.load(f)
    except Exception:
        save = create_default_save()
        save_progress(save)
        return save

    return validate_save(save)


def validate_save(save):
    default = create_default_save()
    for k in default:
        if k not in save:
            save[k] = default[k]
    return save


def save_progress(save):
    os.makedirs(os.path.dirname(SAVE_PATH), exist_ok=True)
    with open(SAVE_PATH, "w") as f:
        json.dump(save, f, indent=2)


# =====================
# XP & LEVEL SYSTEM
# =====================
def add_xp_and_level_up(save, xp):
    today = str(date.today())

    # reset daily xp if new day
    if save.get("last_xp_date") != today:
        save["daily_xp"] = 0
        save["last_xp_date"] = today

    # cap XP
    xp_allowed = max(0, DAILY_XP_CAP - save["daily_xp"])
    xp = min(xp, xp_allowed)

    if xp <= 0:
        return

    save["daily_xp"] += xp
    save["xp"] += xp
    save["profile"]["total_xp_earned"] += xp

    # LEVEL UP
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
