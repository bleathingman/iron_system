import sqlite3
import random
from pathlib import Path
from datetime import date

from core.objective import Objective, Frequency, Category
from core.stats import Stats


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
        # STATS
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
        INSERT OR IGNORE INTO stats (id) VALUES (1)
        """)

        # -------------------------
        # ACHIEVEMENTS
        # -------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id INTEGER PRIMARY KEY,
            unlocked INTEGER DEFAULT 0
        )
        """)

        # -------------------------
        # OBJECTIVES (BASE)
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

        # -------------------------
        # OBJECTIVE PROGRESS
        # -------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS objective_progress (
            objective_id TEXT PRIMARY KEY,
            last_completed TEXT
        )
        """)

        # -------------------------
        # DAILY POOL
        # -------------------------
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_objectives (
            objective_id TEXT PRIMARY KEY
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS daily_meta (
            key TEXT PRIMARY KEY,
            value TEXT
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS elite_daily (
            objective_id TEXT PRIMARY KEY,
            date TEXT NOT NULL
        )
        """)

        self.conn.commit()

    # =========================
    # STATS
    # =========================
    def load_stats(self) -> Stats:
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

        if not row:
            return Stats()

        return Stats(
            total_exp=row["total_exp"],
            total_validations=row["total_validations"],
            current_streak=row["current_streak"],
            best_streak=row["best_streak"],
            last_validation_date=row["last_validation_date"],
            validations_today=row["validations_today"],
            combo_validations=row["combo_validations"],
        )

    def save_stats(self, stats: Stats):
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
            stats.combo_validations
        ))
        self.conn.commit()

    # =========================
    # OBJECTIVES BASE
    # =========================
    def save_objective(self, objective: Objective):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT OR IGNORE INTO objectives (
            id, title, category, frequency, min_level, value
        ) VALUES (?, ?, ?, ?, ?, ?)
        """, (
            objective.id,
            objective.title,
            objective.category.value,
            objective.frequency.value,
            objective.min_level,
            objective.value
        ))
        self.conn.commit()

    def seed_objectives(self):
        """
        Initialise la liste complète des objectifs
        - Scaling par niveau
        - Exercices Elite (weekly)
        - Recovery intelligent (OFF days inclus)
        - Anti-doublons par ID
        """

        objectives = [

            # ==================================================
            # 🥋 DISCIPLINE — FORCE / CONTRÔLE (MUSCU)
            # ==================================================

            # Niveau 1–4
            Objective("pushups_5", "5 pompes", Category.DISCIPLINE, Frequency.DAILY, 1, 10),
            Objective("squats_10", "10 squats", Category.DISCIPLINE, Frequency.DAILY, 1, 10),
            Objective("plank_20", "Gainage 20 secondes", Category.DISCIPLINE, Frequency.DAILY, 1, 10),

            # Niveau 5–9
            Objective("pushups_10", "10 pompes", Category.DISCIPLINE, Frequency.DAILY, 5, 15),
            Objective("squats_20", "20 squats", Category.DISCIPLINE, Frequency.DAILY, 5, 15),
            Objective("plank_40", "Gainage 40 secondes", Category.DISCIPLINE, Frequency.DAILY, 5, 15),

            # Niveau 10–19
            Objective("pushups_20", "20 pompes", Category.DISCIPLINE, Frequency.DAILY, 10, 25),
            Objective("lunges_20", "20 fentes", Category.DISCIPLINE, Frequency.DAILY, 10, 25),
            Objective("plank_60", "Gainage 1 minute", Category.DISCIPLINE, Frequency.DAILY, 10, 25),

            # Niveau 20+
            Objective("pushups_slow_20", "20 pompes lentes", Category.DISCIPLINE, Frequency.DAILY, 20, 40),
            Objective("squats_50", "50 squats", Category.DISCIPLINE, Frequency.DAILY, 20, 40),
            Objective("plank_120", "Gainage 2 minutes", Category.DISCIPLINE, Frequency.DAILY, 25, 45),

            # ==================================================
            # 🫀 ENDURANCE — CARDIO
            # ==================================================

            Objective("walk_10", "Marche 10 minutes", Category.ENDURANCE, Frequency.DAILY, 1, 10),
            Objective("walk_20", "Marche 20 minutes", Category.ENDURANCE, Frequency.DAILY, 5, 15),

            Objective("jog_5", "Jogging 5 minutes", Category.ENDURANCE, Frequency.DAILY, 5, 15),
            Objective("jog_10", "Jogging 10 minutes", Category.ENDURANCE, Frequency.DAILY, 10, 25),

            Objective("bike_20", "Vélo 20 minutes", Category.ENDURANCE, Frequency.DAILY, 15, 30),
            Objective("run_20", "Course 20 minutes", Category.ENDURANCE, Frequency.DAILY, 20, 40),

            # ==================================================
            # 🧠 RECOVERY — (MENTAL)
            # ==================================================

            Objective("stretch_5", "Étirements légers 5 minutes", Category.MENTAL, Frequency.DAILY, 1, 10),
            Objective("breathing_3", "Respiration post-effort 3 minutes", Category.MENTAL, Frequency.DAILY, 1, 10),

            Objective("mobility_shoulders", "Mobilité épaules 5 minutes", Category.MENTAL, Frequency.DAILY, 5, 15),
            Objective("stretch_10", "Étirements complets 10 minutes", Category.MENTAL, Frequency.DAILY, 10, 20),

            Objective("foam_5", "Auto-massage 5 minutes", Category.MENTAL, Frequency.DAILY, 15, 30),
            Objective("mobility_full", "Mobilité complète 15 minutes", Category.MENTAL, Frequency.DAILY, 20, 40),

            # ==================================================
            # 🏆 ELITE — WEEKLY
            # ==================================================

            Objective(
                "elite_pushups_100",
                "100 pompes (session unique)",
                Category.DISCIPLINE,
                Frequency.WEEKLY,
                10,
                120
            ),

            Objective(
                "elite_run_5k",
                "Course 5 km",
                Category.ENDURANCE,
                Frequency.WEEKLY,
                15,
                150
            ),

            Objective(
                "elite_full_body",
                "Séance full-body complète",
                Category.DISCIPLINE,
                Frequency.WEEKLY,
                20,
                180
            ),

            Objective(
                "elite_recovery",
                "Recovery complète (stretch + mobilité + respiration)",
                Category.MENTAL,
                Frequency.WEEKLY,
                10,
                100
            ),
        ]

        # 🔒 Anti-doublons + sauvegarde
        seen_ids = set()
        for obj in objectives:
            if obj.id in seen_ids:
                continue
            seen_ids.add(obj.id)
            self.save_objective(obj)


    def load_objectives_for_level(self, level: int):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT o.*, p.last_completed
        FROM objectives o
        LEFT JOIN objective_progress p
        ON o.id = p.objective_id
        WHERE o.min_level <= ?
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
                    value=row["value"],
                    last_completed=(
                        date.fromisoformat(row["last_completed"])
                        if row["last_completed"] else None
                    )
                )
            )
        return objectives

    # =========================
    # OBJECTIVE PROGRESS
    # =========================
    def save_objective_completion(self, objective):
        if objective.last_completed is None:
            return  # sécurité

        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO objective_progress (objective_id, last_completed)
        VALUES (?, ?)
        ON CONFLICT(objective_id)
        DO UPDATE SET last_completed = excluded.last_completed
        """, (
            objective.id,
            objective.last_completed.isoformat()
        ))
        self.conn.commit()


    # =========================
    # DAILY QUESTS
    # =========================
    def _get_daily_date(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT value FROM daily_meta WHERE key = 'date'"
        )
        row = cursor.fetchone()
        return row["value"] if row else None

    def _set_daily_date(self, today):
        cursor = self.conn.cursor()
        cursor.execute("""
        INSERT INTO daily_meta (key, value)
        VALUES ('date', ?)
        ON CONFLICT(key) DO UPDATE SET value = excluded.value
        """, (today,))
        self.conn.commit()

    def generate_daily_pool(self, level: int, count: int = 3):
        today = date.today().isoformat()
        if self._get_daily_date() == today:
            return

        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM daily_objectives")

        cursor.execute("""
        SELECT id FROM objectives
        WHERE min_level <= ?
        """, (level,))
        ids = [r["id"] for r in cursor.fetchall()]

        if not ids:
            return

        selected = random.sample(ids, min(count, len(ids)))

        for oid in selected:
            cursor.execute(
                "INSERT INTO daily_objectives (objective_id) VALUES (?)",
                (oid,)
            )

        self._set_daily_date(today)
        self.conn.commit()

    def load_daily_objectives(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT o.*
        FROM objectives o
        JOIN daily_objectives d
        ON o.id = d.objective_id
        """)
        return cursor.fetchall()

    def complete_daily_objective(self, objective_id: str):
        cursor = self.conn.cursor()
        cursor.execute(
            "DELETE FROM daily_objectives WHERE objective_id = ?",
            (objective_id,)
        )
        self.conn.commit()

    # =========================
    # ELITE DAILY
    # =========================

    def load_elite_daily(self):
        """
        Retourne l'Elite Daily du jour (ou None)
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT o.*
        FROM elite_daily e
        JOIN objectives o ON o.id = e.objective_id
        WHERE e.date = ?
        """, (date.today().isoformat(),))
        return cursor.fetchone()

    def generate_elite_daily(self, level: int):
        """
        Génère UNE elite daily par jour (si absente)
        """
        today = date.today().isoformat()
        cursor = self.conn.cursor()

        # Déjà générée aujourd'hui ?
        cursor.execute(
            "SELECT 1 FROM elite_daily WHERE date = ?",
            (today,)
        )
        if cursor.fetchone():
            return

        # Nettoyage ancien (sécurité)
        cursor.execute("DELETE FROM elite_daily")

        # Pool ELITE = objectifs WEEKLY accessibles
        cursor.execute("""
        SELECT id FROM objectives
        WHERE frequency = 'weekly'
        AND min_level <= ?
        """, (level,))
        rows = cursor.fetchall()

        if not rows:
            return

        selected_id = random.choice(rows)["id"]

        cursor.execute("""
        INSERT INTO elite_daily (objective_id, date)
        VALUES (?, ?)
        """, (selected_id, today))

        self.conn.commit()

    def complete_elite_daily(self):
        """
        Supprime l'elite daily après validation
        """
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM elite_daily")
        self.conn.commit()
    
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
        ON CONFLICT(id)
        DO UPDATE SET unlocked = 1
        """, (achievement_id,))
        self.conn.commit()
