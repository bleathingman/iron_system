import sqlite3
from datetime import datetime
from core.stats import Stats
from core.objective import Objective, Frequency


class Storage:
    def __init__(self, db_path="data/ironsystem.db"):
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS objectives (
            id INTEGER PRIMARY KEY,
            title TEXT,
            frequency TEXT,
            value INTEGER
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY,
            timestamp TEXT,
            action TEXT,
            impact INTEGER
        )
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS stats (
            id INTEGER PRIMARY KEY CHECK (id = 1),
            current_streak INTEGER,
            best_streak INTEGER,
            total_validations INTEGER,
            total_points INTEGER
        )
        """)

        cursor.execute("""
        INSERT OR IGNORE INTO stats
        (id, current_streak, best_streak, total_validations, total_points)
        VALUES (1, 0, 0, 0, 0)
        """)

        self.conn.commit()

    # -------------------------
    # STATS
    # -------------------------
    def load_stats(self) -> Stats:
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
        cursor = self.conn.cursor()
        cursor.execute("""
        UPDATE stats
        SET current_streak = ?, best_streak = ?, total_validations = ?, total_points = ?
        WHERE id = 1
        """, (
            stats.current_streak,
            stats.best_streak,
            stats.total_validations,
            stats.total_points,
        ))
        self.conn.commit()

    # -------------------------
    # HISTORY / EXP
    # -------------------------
    def save_history(self, entry):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO history (timestamp, action, impact) VALUES (?, ?, ?)",
            (entry.timestamp.isoformat(), entry.action, entry.impact)
        )
        self.conn.commit()

    def get_last_validation_date(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT timestamp FROM history
        ORDER BY timestamp DESC LIMIT 1
        """)
        row = cursor.fetchone()
        return datetime.fromisoformat(row[0]).date() if row else None

    def get_today_exp(self) -> int:
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT SUM(impact)
        FROM history
        WHERE DATE(timestamp) = DATE('now')
        """)
        row = cursor.fetchone()
        return row[0] if row and row[0] else 0

    # -------------------------
    # OBJECTIVES
    # -------------------------
    def load_objectives(self):
        cursor = self.conn.cursor()
        cursor.execute("""
        SELECT id, title, frequency, value
        FROM objectives
        """)
        rows = cursor.fetchall()

        return [
            Objective(
                id=row[0],
                title=row[1],
                frequency=Frequency(row[2]),
                value=row[3],
            )
            for row in rows
        ]

    def seed_level_1_objectives(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM objectives")
        if cursor.fetchone()[0] == 0:
            cursor.executemany("""
            INSERT INTO objectives (id, title, frequency, value)
            VALUES (?, ?, ?, ?)
            """, [
                (1, "5 Pompes (genoux ok)", "daily", 10),
                (2, "10 Abdos", "daily", 10),
                (3, "10 Squats lents", "daily", 10),
                (4, "Gainage 30 sec", "daily", 10),
                (5, "Marche 10 min", "daily", 10),
            ])
            self.conn.commit()
