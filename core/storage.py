import sqlite3
from pathlib import Path

from core.objective import Objective, Frequency, Category


class Storage:
    """
    Gestion du stockage local (SQLite)
    """

    def __init__(self, db_path: str = "data/ironsystem.db"):
        Path("data").mkdir(exist_ok=True)

        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        self._create_tables()

    # =========================
    # TABLE CREATION
    # =========================
    def _create_tables(self):
        cursor = self.conn.cursor()

        # -------------------------
        # STATS TABLE
        # -------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY,
            total_exp INTEGER DEFAULT 0,
            total_validations INTEGER DEFAULT 0,

            current_streak INTEGER DEFAULT 0,
            best_streak INTEGER DEFAULT 0,

            last_validation_date TEXT,

            validations_today INTEGER DEFAULT 0,
            combo_validations INTEGER DEFAULT 0
        )
        """)

        cursor.execute("""
        INSERT OR IGNORE INTO stats (
            id,
            total_exp,
            total_validations,
            current_streak,
            best_streak,
            last_validation_date,
            validations_today,
            combo_validations
        )
        VALUES (1, 0, 0, 0, 0, NULL, 0, 0)
        """)

        # -------------------------
        # ACHIEVEMENTS TABLE
        # -------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY,
            unlocked INTEGER DEFAULT 0
        )
        """)

        # -------------------------
        # OBJECTIVES TABLE
        # -------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS objectives (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL,
            frequency TEXT NOT NULL,
            min_level INTEGER NOT NULL,
            value INTEGER NOT NULL
        )
        """)

        self.conn.commit()

    # =========================
    # STATS
    # =========================
    def load_stats(self):
        """
        Charge les statistiques utilisateur
        """
        from core.stats import Stats

        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT
            total_exp,
            total_validations,
            current_streak,
            best_streak,
            last_validation_date,
            validations_today,
            combo_validations
        FROM stats
        WHERE id = 1
        """)
        row = cursor.fetchone()

        if row:
            return Stats(
                total_exp=row["total_exp"],
                total_validations=row["total_validations"],
                current_streak=row["current_streak"],
                best_streak=row["best_streak"],
                last_validation_date=row["last_validation_date"],
                validations_today=row["validations_today"],
                combo_validations=row["combo_validations"],
            )

        return Stats()

    def save_stats(self, stats):
        """
        Sauvegarde les statistiques utilisateur
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE stats SET
            total_exp = ?,
            total_validations = ?,
            current_streak = ?,
            best_streak = ?,
            last_validation_date = ?,
            validations_today = ?,
            combo_validations = ?
        WHERE id = 1
        """, (
            stats.total_exp,
            stats.total_validations,
            stats.current_streak,
            stats.best_streak,
            stats.last_validation_date,
            stats.validations_today,
            stats.combo_validations,
        ))
        self.conn.commit()

    # =========================
    # OBJECTIVES
    # =========================
    def seed_objectives(self):
        """
        Initialise la liste des objectifs (exercices)
        Aucune duplication possible grâce aux IDs uniques
        """

        objectives = [
            # ------------------
            # DISCIPLINE
            # ------------------
            Objective(
                id="pushups_5",
                title="5 pompes",
                category=Category.DISCIPLINE,
                frequency=Frequency.DAILY,
                min_level=1,
                value=10
            ),
            Objective(
                id="squats_10",
                title="10 squats",
                category=Category.DISCIPLINE,
                frequency=Frequency.DAILY,
                min_level=1,
                value=10
            ),
            Objective(
                id="plank_30s",
                title="Gainage 30 secondes",
                category=Category.DISCIPLINE,
                frequency=Frequency.DAILY,
                min_level=1,
                value=10
            ),

            # ------------------
            # ENDURANCE
            # ------------------
            Objective(
                id="walk_10min",
                title="Marche 10 minutes",
                category=Category.ENDURANCE,
                frequency=Frequency.DAILY,
                min_level=1,
                value=10
            ),
            Objective(
                id="jog_5min",
                title="Jogging 5 minutes",
                category=Category.ENDURANCE,
                frequency=Frequency.DAILY,
                min_level=5,
                value=15
            ),

            # ------------------
            # MENTAL
            # ------------------
            Objective(
                id="breathing_3min",
                title="Respiration contrôlée 3 minutes",
                category=Category.MENTAL,
                frequency=Frequency.DAILY,
                min_level=1,
                value=10
            ),
            Objective(
                id="stretching_5min",
                title="Étirements 5 minutes",
                category=Category.MENTAL,
                frequency=Frequency.DAILY,
                min_level=1,
                value=10
            ),
            Objective(
                id="meditation_5min",
                title="Méditation 5 minutes",
                category=Category.MENTAL,
                frequency=Frequency.DAILY,
                min_level=5,
                value=15
            ),
        ]

        for obj in objectives:
            self.save_objective(obj)

    def save_objective(self, objective: Objective):
        """
        Sauvegarde un objectif dans la DB
        Aucun doublon possible grâce à l'ID unique
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR IGNORE INTO objectives (
            id, title, category, frequency, min_level, value
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            objective.id,
            objective.title,
            objective.category.value,
            objective.frequency.value,
            objective.min_level,
            objective.value
        ))
        self.conn.commit()

    def load_objectives_for_level(self, level: int) -> list[Objective]:
        """
        Charge les objectifs disponibles pour un niveau donné
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT
            id,
            title,
            category,
            frequency,
            min_level,
            value
        FROM objectives
        WHERE min_level <= ?
        ORDER BY min_level ASC
        """, (level,))

        objectives = []

        for row in cursor.fetchall():
            objectives.append(
                Objective(
                    id=row["id"],
                    title=row["title"],
                    category=Category(row["category"]),
                    frequency=Frequency(row["frequency"]),
                    min_level=row["min_level"],
                    value=row["value"]
                )
            )

        return objectives

    # =========================
    # ACHIEVEMENTS
    # =========================
    def is_achievement_unlocked(self, achievement_id: int) -> bool:
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT unlocked FROM achievements WHERE id = ?",
            (achievement_id,)
        )
        row = cursor.fetchone()
        return bool(row and row["unlocked"])

    def unlock_achievement(self, achievement_id: int):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO achievements (id, unlocked)
        VALUES (?, 1)
        ON CONFLICT(id) DO UPDATE SET unlocked = 1
        """, (achievement_id,))
        self.conn.commit()
