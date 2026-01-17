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

    last_completed: date | None = None

    def can_be_completed_today(self) -> bool:
        return True
