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
        """
        Vérifie si l'objectif peut être validé
        - DAILY  : une fois par jour
        - WEEKLY : une fois par semaine (Elite)
        """

        today = date.today()

        # Jamais complété → OK
        if self.last_completed is None:
            return True

        # Sécurité : forcer le type
        if not isinstance(self.last_completed, date):
            return True

        # DAILY → une fois par jour
        if self.frequency == Frequency.DAILY:
            return self.last_completed != today

        # WEEKLY → une fois par semaine (Elite)
        if self.frequency == Frequency.WEEKLY:
            last_year, last_week, _ = self.last_completed.isocalendar()
            curr_year, curr_week, _ = today.isocalendar()
            return (last_year, last_week) != (curr_year, curr_week)

        return True
