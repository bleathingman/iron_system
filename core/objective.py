from enum import Enum
from dataclasses import dataclass
from datetime import date


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class Category(Enum):
    DISCIPLINE = "discipline"
    ENDURANCE = "endurance"
    MENTAL = "mental"   # affiché comme RECOVERY côté UI


@dataclass
class Objective:
    id: str
    title: str
    category: Category
    frequency: Frequency
    min_level: int
    value: int  # EXP

    # 🔥 NOUVEAU : exercice & répétitions
    exercise: str | None = None   # "pushups", "squats", "abs"
    reps: int = 0                 # nombre de répétitions

    last_completed: date | None = None

    def can_be_completed_today(self) -> bool:
        # FREE MODE pour l’instant
        return True
