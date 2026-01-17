from dataclasses import dataclass
from datetime import date


@dataclass
class Stats:
    """
    Statistiques globales de l'utilisateur
    Gère :
    - EXP totale
    - niveaux (1 → 100)
    - streaks
    - validations
    """

    EXP_PER_LEVEL = 100

    def __init__(
        self,
        total_exp: int = 0,
        total_validations: int = 0,
        current_streak: int = 0,
        best_streak: int = 0,
        last_validation_date: str | None = None,
        validations_today: int = 0,
        combo_validations: int = 0,
    ):
        self.total_exp = total_exp
        self.total_validations = total_validations

        self.current_streak = current_streak
        self.best_streak = best_streak

        self.last_validation_date = (
            date.fromisoformat(last_validation_date)
            if last_validation_date else None
        )

        self.validations_today = validations_today
        self.combo_validations = combo_validations

    # -------------------------
    # EXP / LEVEL
    # -------------------------
    def add_exp(self, amount: int):
        """
        Ajoute de l'EXP et gère la montée de niveau
        """
        self.total_exp += amount

    def get_level(self) -> int:
        """
        Niveau actuel (1 → 100)
        """
        return max(1, self.total_exp // self.EXP_PER_LEVEL + 1)

    def get_exp_in_level(self) -> int:
        """
        EXP actuelle dans le niveau en cours
        """
        return self.total_exp % self.EXP_PER_LEVEL

    # -------------------------
    # VALIDATIONS / STREAK
    # -------------------------
    def register_validation(self):
        """
        Met à jour streaks et validations
        """
        today = date.today()

        if self.last_validation_date == today:
            self.validations_today += 1
            self.combo_validations += 1
        else:
            # nouveau jour
            if self.last_validation_date == today.replace(day=today.day - 1):
                self.current_streak += 1
            else:
                self.current_streak = 1

            self.validations_today = 1
            self.combo_validations = 1

        self.best_streak = max(self.best_streak, self.current_streak)
        self.total_validations += 1
        self.last_validation_date = today
