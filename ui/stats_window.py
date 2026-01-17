from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame
)
from PySide6.QtCore import Qt

from core.storage import Storage
from core.user import User


class StatsWindow(QWidget):
    """
    Écran Statistiques
    Affiche la progression globale de l'utilisateur
    """

    def __init__(self, user: User, storage: Storage):
        super().__init__()

        self.user = user
        self.storage = storage

        self.setWindowTitle("Statistiques")
        self.setMinimumSize(420, 520)

        self._setup_ui()
        self._load_stats()

    # -------------------------
    # UI SETUP
    # -------------------------
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignTop)

        title = QLabel("STATISTIQUES")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
        QLabel {
            font-size: 22px;
            font-weight: bold;
            color: #7f5af0;
            letter-spacing: 3px;
        }
        """)

        layout.addWidget(title)

        self.cards_container = QVBoxLayout()
        self.cards_container.setSpacing(10)

        layout.addLayout(self.cards_container)
        self.setLayout(layout)

    # -------------------------
    # DATA
    # -------------------------
    def _load_stats(self):
        """
        Charge les statistiques depuis le user
        """
        stats = self.user.stats

        achievements_unlocked = self._count_achievements()

        data = [
            ("Niveau actuel", f"LEVEL {stats.get_level()}"),
            ("EXP totale", f"{stats.total_exp} EXP"),
            ("Objectifs validés", f"{stats.total_validations}"),
            ("Streak actuel", f"{stats.current_streak} jours"),
            ("Meilleur streak", f"{stats.best_streak} jours"),
            ("Achievements", f"{achievements_unlocked} débloqués"),
        ]

        for title, value in data:
            self._add_stat_card(title, value)

    def _count_achievements(self) -> int:
        """
        Compte les achievements débloqués
        """
        cursor = self.storage.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM achievements WHERE unlocked = 1"
        )
        return cursor.fetchone()[0]

    # -------------------------
    # UI ELEMENT
    # -------------------------
    def _add_stat_card(self, title: str, value: str):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)

        card.setStyleSheet("""
        QFrame {
            background-color: #1a1f36;
            border: 1px solid #2d325a;
            border-radius: 8px;
            padding: 12px;
        }
        """)

        layout = QVBoxLayout(card)

        title_label = QLabel(title)
        title_label.setStyleSheet("""
        QLabel {
            font-size: 13px;
            color: #b8b8d1;
        }
        """)

        value_label = QLabel(value)
        value_label.setStyleSheet("""
        QLabel {
            font-size: 18px;
            font-weight: bold;
            color: #ffffff;
        }
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        self.cards_container.addWidget(card)
