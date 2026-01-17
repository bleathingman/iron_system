import sqlite3
from datetime import datetime
from core.stats import Stats


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
            value INTEGER,
            completed INTEGER,
            last_completed TEXT
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

        # ligne unique stats
        cursor.execute("""
        INSERT OR IGNORE INTO stats
        (id, current_streak, best_streak, total_validations, total_points)
        VALUES (1, 0, 0, 0, 0)
        """)

        self.conn.commit()

    def save_history(self, entry):
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO history (timestamp, action, impact) VALUES (?, ?, ?)",
            (entry.timestamp.isoformat(), entry.action, entry.impact)
        )
        self.conn.commit()

    def get_last_validation_date(self):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT timestamp FROM history ORDER BY timestamp DESC LIMIT 1"
        )
        row = cursor.fetchone()

        if not row:
            return None

        return datetime.fromisoformat(row[0]).date()

    def load_stats(self) -> Stats:
        cursor = self.conn.cursor()
        cursor.execute("SELECT current_streak, best_streak, total_validations, total_points FROM stats WHERE id = 1")
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
