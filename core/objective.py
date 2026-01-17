from enum import Enum
from dataclasses import dataclass
from datetime import date


class Frequency(Enum):
    DAILY = "daily"
    WEEKLY = "weekly"


class Category(Enum):
    DISCIPLINE = "discipline"
    ENDURANCE = "endurance"
    MENTAL = "mental"


@dataclass
class Objective:
    """
    Représente un objectif / exercice unique
    """

    id: str                    # ID UNIQUE (anti-doublon)
    title: str                 # Texte affiché
    category: Category         # Discipline / Endurance / Mental
    frequency: Frequency       # Daily / Weekly
    min_level: int             # Niveau minimum requis
    value: int                 # EXP gagnée

    completed: bool = False
    last_completed: date | None = None

    def can_be_completed_today(self) -> bool:
        """
        Empêche la validation multiple le même jour
        """
        return self.last_completed != date.today()
