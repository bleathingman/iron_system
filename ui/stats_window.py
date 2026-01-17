from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QScrollArea, QSizePolicy
)
from PySide6.QtCore import Qt

from core.storage import Storage
from core.user import User


class StatsWindow(QWidget):
    """
    Écran Statistiques
    Global + Journalier + Hebdomadaire
    Responsive (scroll si fenêtre réduite)
    """

    def __init__(self, user: User, storage: Storage):
        super().__init__()

        self.user = user
        self.storage = storage

        self.setWindowTitle("Statistiques")
        self.setMinimumSize(360, 420)

        self._setup_ui()
        self._load_stats()

    # -------------------------
    # UI SETUP
    # -------------------------
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)

        # ===== Scroll Area =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(14)
        self.content_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # ===== Title =====
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

        title.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

        self.content_layout.addWidget(title)

    # -------------------------
    # DATA
    # -------------------------
    def _load_stats(self):
        stats = self.user.stats
        daily = self.storage.get_daily_stats()
        weekly = self.storage.get_weekly_stats()

        achievements_unlocked = self._count_achievements()

        # ===== GLOBAL =====
        self._add_section("GLOBAL")
        self._add_stat_card("Niveau", f"LEVEL {stats.get_level()}")
        self._add_stat_card("EXP totale", f"{stats.total_exp} EXP")
        self._add_stat_card("Objectifs validés", f"{stats.total_validations}")
        self._add_stat_card("Achievements", f"{achievements_unlocked}")

        # ===== DAILY =====
        self._add_section("AUJOURD'HUI")
        self._add_stat_card("Validations du jour", f"{daily['validations']}")
        self._add_stat_card("Streak actuel", f"{daily['streak']} jours")

        # ===== WEEKLY =====
        self._add_section("SEMAINE")
        self._add_stat_card("Validations (estim.)", f"{weekly['validations']}")
        self._add_stat_card("Meilleur streak", f"{weekly['best_streak']} jours")

        self.content_layout.addStretch()

    def _count_achievements(self) -> int:
        cursor = self.storage.conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM achievements WHERE unlocked = 1"
        )
        return cursor.fetchone()[0]

    # -------------------------
    # UI HELPERS
    # -------------------------
    def _add_section(self, title: str):
        label = QLabel(title)
        label.setStyleSheet("""
        QLabel {
            margin-top: 16px;
            font-size: 15px;
            font-weight: bold;
            color: #b8b8d1;
        }
        """)
        self.content_layout.addWidget(label)

    def _add_stat_card(self, title: str, value: str):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)

        card.setSizePolicy(
            QSizePolicy.Expanding,
            QSizePolicy.Fixed
        )

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

        self.content_layout.addWidget(card)
