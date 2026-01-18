from datetime import date


class Stats:
    """
    Statistiques globales de l'utilisateur

    Gère :
    - EXP totale
    - niveaux
    - streaks
    - validations
    - progression par exercice (achievements)
    """

    EXP_PER_LEVEL = 100

    def __init__(
        self,
        total_exp=0,
        total_validations=0,
        current_streak=0,
        best_streak=0,
        last_validation_date=None,
        validations_today=0,
        combo_validations=0,

        # 🔥 PROGRESSION EXERCICES
        total_pushups=0,
        total_squats=0,
        total_lunges=0,
        total_abs=0,
    ):
        # EXP / LEVEL
        self.total_exp = total_exp

        # VALIDATIONS / STREAK
        self.total_validations = total_validations
        self.current_streak = current_streak
        self.best_streak = best_streak
        self.last_validation_date = (
            date.fromisoformat(last_validation_date)
            if isinstance(last_validation_date, str)
            else last_validation_date
        )
        self.validations_today = validations_today
        self.combo_validations = combo_validations

        # 🔥 STATS D’EXERCICES (ACHIEVEMENTS)
        self.total_pushups = total_pushups
        self.total_squats = total_squats
        self.total_lunges = total_lunges
        self.total_abs = total_abs

    # -------------------------
    # EXP / LEVEL
    # -------------------------
    def add_exp(self, amount: int):
        """
        Ajoute de l'EXP (globale)
        """
        self.total_exp += amount

    def get_level(self) -> int:
        """
        Niveau actuel (1 → ∞)
        """
        return max(1, self.total_exp // self.EXP_PER_LEVEL + 1)

    def get_exp_in_level(self) -> int:
        """
        EXP dans le niveau en cours
        """
        return self.total_exp % self.EXP_PER_LEVEL

    # -------------------------
    # VALIDATIONS / STREAK
    # -------------------------
    def register_validation(self):
        """
        Met à jour streaks, combos et validations
        """
        today = date.today()

        if self.last_validation_date == today:
            self.validations_today += 1
            self.combo_validations += 1
        else:
            # Nouveau jour
            if self.last_validation_date and (today - self.last_validation_date).days == 1:
                self.current_streak += 1
            else:
                self.current_streak = 1

            self.validations_today = 1
            self.combo_validations = 1

        self.best_streak = max(self.best_streak, self.current_streak)
        self.last_validation_date = today

    # -------------------------
    # EXERCISES (ACHIEVEMENTS)
    # -------------------------
    def add_exercise_reps(self, exercise: str, reps: int):
        """
        Incrémente les compteurs d'exercices
        """
        if reps <= 0:
            return

        if exercise == "pushups":
            self.total_pushups += reps
        elif exercise == "squats":
            self.total_squats += reps
        elif exercise == "lunges":
            self.total_lunges += reps
        elif exercise == "abs":
            self.total_abs += reps
