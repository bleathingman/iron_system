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
    value: int  # points gagnés
    completed: bool = False
    last_completed: date | None = None
