from enum import Enum
from dataclasses import dataclass
from datetime import date


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Objective:
    id: int
    title: str
    frequency: Frequency
    value: int  # points
    completed: bool = False
    last_completed: date | None = None

    def can_be_completed_today(self) -> bool:
        return self.last_completed != date.today()
