from datetime import date, datetime
from core.history import HistoryEntry


class Engine:
    def __init__(self, user, storage):
        self.user = user
        self.storage = storage

    def validate_objective(self, objective):
        """
        Valide un objectif (mode entraînement libre)
        """
        # ➕ EXP
        self.user.stats.add_exp(objective.value)

        # ➕ stats
        self.user.stats.total_validations += 1
        self.user.stats.register_validation()

        # Objective
        self.storage.save_objective_completion(objective)

        return True


    def _update_streak(self):
        today = date.today()
        last_day = self.storage.get_last_validation_date()

        if last_day is None:
            self.user.stats.current_streak = 1

        elif (today - last_day).days == 1:
            self.user.stats.current_streak += 1

        elif (today - last_day).days == 0:
            if self.user.stats.current_streak == 0:
                self.user.stats.current_streak = 1

        else:
            self.user.stats.current_streak = 1

        self.user.stats.best_streak = max(
            self.user.stats.best_streak,
            self.user.stats.current_streak
        )
