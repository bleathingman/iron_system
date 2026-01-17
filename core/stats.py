from dataclasses import dataclass
from datetime import date


@dataclass
class Stats:
    """
    Statistiques de progression utilisateur
    """
    total_exp: int = 0
    total_validations: int = 0

    current_streak: int = 0
    best_streak: int = 0

    last_validation_date: str | None = None

    # =========================
    # ACHIEVEMENTS / SECRETS
    # =========================
    validations_today: int = 0
    combo_validations: int = 0

    # -------------------------
    # LEVEL SYSTEM
    # -------------------------
    def get_level(self) -> int:
        return self.total_exp // 100 + 1

    def get_exp_in_level(self) -> int:
        return self.total_exp % 100

    # -------------------------
    # VALIDATION UPDATE
    # -------------------------
    def register_validation(self):
        """
        Met à jour les stats lors d'une validation
        """
        today = date.today().isoformat()

        # Validation globale
        self.total_validations += 1
        self.total_exp += 20  # valeur par défaut (cohérente avec tes quests)

        # ---- Gestion streak ----
        if self.last_validation_date == today:
            pass
        else:
            if self.last_validation_date is not None:
                self.current_streak += 1
            else:
                self.current_streak = 1

        self.best_streak = max(self.best_streak, self.current_streak)

        # ---- Validations today ----
        if self.last_validation_date == today:
            self.validations_today += 1
            self.combo_validations += 1
        else:
            self.validations_today = 1
            self.combo_validations = 1

        self.last_validation_date = today
