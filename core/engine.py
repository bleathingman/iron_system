from datetime import date, datetime
from core.history import HistoryEntry


class Engine:
    def __init__(self, user, storage):
        self.user = user
        self.storage = storage

    def validate_objective(self, objective):
        if not objective.can_be_completed_today():
            return False

        # ➕ EXP
        self.user.stats.add_exp(objective.value)

        # ➕ stats globales
        self.user.stats.total_validations += 1
        self.user.stats.register_validation()

        # 🏋️‍♂️ PROGRESSION EXERCICES
        if objective.exercise and objective.reps > 0:
            if objective.exercise == "pushups":
                self.user.stats.total_pushups += objective.reps
            elif objective.exercise == "squats":
                self.user.stats.total_squats += objective.reps
            elif objective.exercise == "lunges":
                self.user.stats.total_lunges += objective.reps
            elif objective.exercise == "abs":
                self.user.stats.total_abs += objective.reps

            print(
                "[ENGINE DEBUG]",
                objective.title,
                "exercise =", objective.exercise,
                "reps =", objective.reps
            )


        # 📅 date de validation
        objective.last_completed = date.today()
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

    def grant_daily_bonus_if_needed(self):
        BONUS_EXP = 50

        if not self.storage.all_daily_completed():
            return False

        if self.storage.daily_bonus_already_given():
            return False

        self.user.stats.add_exp(BONUS_EXP)
        self.storage.mark_daily_bonus_given()
        self.storage.save_stats(self.user.stats)

        return BONUS_EXP