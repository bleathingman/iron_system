import sqlite3
from datetime import datetime
from core.stats import Stats
from core.objective import Objective, Frequency


class Storage:
    """
    Gestionnaire de persistance SQLite.
    Toute interaction avec la base passe par cette classe.
    """

    def __init__(self, db_path="data/ironsystem.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        """
        Crée les tables nécessaires et gère les migrations simples
        (ex: ajout de colonnes manquantes).
        """
        cursor = self.conn.cursor()

        # =========================
        # TABLE OBJECTIVES
        # =========================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS objectives (
            id INTEGER PRIMARY KEY,
            title TEXT,
            frequency TEXT,
            value INTEGER
        )
        """)

        # Migration : ajout de la colonne min_level si absente
        cursor.execute("PRAGMA table_info(objectives)")
        columns = [row[1] for row in cursor.fetchall()]
        if "min_level" not in columns:
            cursor.execute(
                "ALTER TABLE objectives ADD COLUMN min_level INTEGER DEFAULT 1"
            )

        # =========================
        # TABLE HISTORY
        # =========================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            action TEXT,
            impact INTEGER
        )
        """)

        # =========================
        # TABLE STATS
        # =========================
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_streak INTEGER,
            best_streak INTEGER,
            total_validations INTEGER,
            total_points INTEGER
        )
        """)

        # Initialisation des stats si absentes
        cursor.execute("""
        INSERT OR IGNORE INTO stats
        VALUES (1, 0, 0, 0, 0)
        """)

        self.conn.commit()

    # =========================
    # STATS
    # =========================
    def load_stats(self) -> Stats:
        """
        Charge les statistiques globales depuis la base.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT current_streak, best_streak, total_validations, total_points
        FROM stats WHERE id = 1
        """)
        row = cursor.fetchone()

        return Stats(
            current_streak=row[0],
            best_streak=row[1],
            total_validations=row[2],
            total_points=row[3],
        )

    def save_stats(self, stats: Stats):
        """
        Sauvegarde les statistiques globales.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE stats
        SET current_streak = ?,
            best_streak = ?,
            total_validations = ?,
            total_points = ?
        WHERE id = 1
        """, (
            stats.current_streak,
            stats.best_streak,
            stats.total_validations,
            stats.total_points,
        ))
        self.conn.commit()

    # =========================
    # HISTORY / EXP
    # =========================
    def save_history(self, entry):
        """
        Enregistre une validation d'objectif dans l'historique.
        """
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO history (timestamp, action, impact) VALUES (?, ?, ?)",
            (entry.timestamp.isoformat(), entry.action, entry.impact)
        )
        self.conn.commit()

    def get_last_validation_date(self):
        """
        Retourne la date de la dernière validation (pour le streak).
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT timestamp
        FROM history
        ORDER BY timestamp DESC
        LIMIT 1
        """)
        row = cursor.fetchone()

        if not row:
            return None

        return datetime.fromisoformat(row[0]).date()

    def get_today_exp(self) -> int:
        """
        Calcule l'EXP gagnée aujourd'hui depuis l'historique.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT SUM(impact)
        FROM history
        WHERE DATE(timestamp) = DATE('now')
        """)
        row = cursor.fetchone()

        return row[0] if row and row[0] else 0

    # =========================
    # OBJECTIVES
    # =========================
    def load_objectives_for_level(self, level: int):
        """
        Charge les objectifs accessibles pour un niveau donné.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, title, frequency, value
        FROM objectives
        WHERE min_level <= ?
        """, (level,))
        rows = cursor.fetchall()

        return [
            Objective(
                id=r[0],
                title=r[1],
                frequency=Frequency(r[2]),
                value=r[3],
            )
            for r in rows
        ]

    def seed_objectives(self):
        """
        Injecte les objectifs de base (une seule fois).
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM objectives")
        if cursor.fetchone()[0] > 0:
            return

        cursor.executemany("""
        INSERT INTO objectives (id, title, frequency, value, min_level)
        VALUES (?, ?, ?, ?, ?)
        """, [
            # Niveau 1 – Awakening
            (1, "5 Pompes", "daily", 10, 1),
            (2, "10 Abdos", "daily", 10, 1),
            (3, "10 Squats", "daily", 10, 1),
            (4, "Gainage 30 sec", "daily", 10, 1),
            (5, "Marche 10 min", "daily", 10, 1),

            # Progression
            (6, "15 Pompes", "daily", 15, 5),
            (7, "20 Squats", "daily", 15, 5),
            (8, "30 Pompes", "daily", 20, 10),
            (9, "Course 2 km", "daily", 25, 10),
        ])

        self.conn.commit()
