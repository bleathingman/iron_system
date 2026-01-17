from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from core.user import User
from core.storage import Storage


class StatsWindow(QWidget):
    """
    Fenêtre Statistiques
    Version desktop simple mais lisible
    """

    def __init__(self, user: User, storage: Storage):
        super().__init__()

        self.user = user
        self.storage = storage

        self.setWindowTitle("Statistiques")
        self.resize(420, 520)

        self._setup_ui()
        self._load_stats()

    # -------------------------
    # UI
    # -------------------------
    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(14)

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
        self.layout.addWidget(title)

    # -------------------------
    # DATA
    # -------------------------
    def _load_stats(self):
        stats = self.user.stats

        self._add_card("🎯 Niveau", f"LEVEL {stats.get_level()}")
        self._add_card("⚡ EXP totale", f"{stats.total_exp} EXP")
        self._add_card("✅ Objectifs validés", stats.total_validations)
        self._add_card("🔥 Streak actuel", f"{stats.current_streak} jours")
        self._add_card("🏆 Meilleur streak", f"{stats.best_streak} jours")

    # -------------------------
    # CARD
    # -------------------------
    def _add_card(self, title: str, value):
        card = QFrame()
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
            font-size: 14px;
            color: #b8b8d1;
        }
        """)

        value_label = QLabel(str(value))
        value_label.setStyleSheet("""
        QLabel {
            font-size: 20px;
            font-weight: bold;
            color: #ffffff;
        }
        """)

        layout.addWidget(title_label)
        layout.addWidget(value_label)

        self.layout.addWidget(card)
