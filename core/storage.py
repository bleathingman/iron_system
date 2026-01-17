import sqlite3


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
