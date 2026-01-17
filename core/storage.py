import sqlite3
from pathlib import Path


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

        # Initialisation stats (1 utilisateur)
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            frequency TEXT NOT NULL,
            value INTEGER NOT NULL,
            min_level INTEGER DEFAULT 1
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
    # STATS JOUR / SEMAINE
    # =========================
    def get_daily_stats(self):
        """
        Retourne les stats du jour
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            validations_today,
            current_streak
        FROM stats
        WHERE id = 1
        """)
        row = cursor.fetchone()

        return {
            "validations": row["validations_today"],
            "streak": row["current_streak"],
        }

    def get_weekly_stats(self):
        """
        Retourne les stats hebdomadaires (approximation v1)
        Basé sur total_validations et streak
        """
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT
            total_validations,
            best_streak
        FROM stats
        WHERE id = 1
        """)
        row = cursor.fetchone()

        # Heuristique simple v1 (sera raffinée plus tard)
        weekly_validations = min(row["total_validations"], 7 * 3)

        return {
            "validations": weekly_validations,
            "best_streak": row["best_streak"],
        }

    # =========================
    # OBJECTIVES
    # =========================
    def seed_objectives(self):
        """
        Injecte des objectifs de base (si DB vide)
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM objectives")
        count = cursor.fetchone()[0]

        if count > 0:
            return

        objectives = [
            # Niveau 1–3 (débutants)
            ("5 pompes", "daily", 10, 1),
            ("10 squats", "daily", 10, 1),
            ("5 min de marche", "daily", 10, 1),

            # Niveau 4–6
            ("10 pompes", "daily", 15, 4),
            ("20 squats", "daily", 15, 4),
            ("5 min gainage", "daily", 15, 4),

            # Niveau 7–10
            ("20 pompes", "daily", 20, 7),
            ("30 squats", "daily", 20, 7),
            ("10 min course", "daily", 20, 7),
        ]

        cursor.executemany("""
        INSERT INTO objectives (title, frequency, value, min_level)
        VALUES (?, ?, ?, ?)
        """, objectives)

        self.conn.commit()

    def load_objectives_for_level(self, level: int):
        """
        Charge les objectifs disponibles pour un niveau donné
        """
        from core.objective import Objective, Frequency

        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, title, frequency, value
        FROM objectives
        WHERE min_level <= ?
        """, (level,))

        rows = cursor.fetchall()
        objectives = []

        for row in rows:
            objectives.append(
                Objective(
                    id=row["id"],
                    title=row["title"],
                    frequency=Frequency(row["frequency"]),
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
