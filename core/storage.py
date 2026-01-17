import sqlite3
from datetime import datetime


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
