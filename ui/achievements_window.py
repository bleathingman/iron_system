from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFrame
from PySide6.QtCore import Qt

from core.storage import Storage


class AchievementsWindow(QWidget):
    """
    Fenêtre Achievements
    Version desktop simple avec différenciation visuelle
    """

    def __init__(self, storage: Storage):
        super().__init__()

        self.storage = storage

        self.setWindowTitle("Achievements")
        self.resize(420, 520)

        self._setup_ui()
        self._load_achievements()

    # -------------------------
    # UI
    # -------------------------
    def _setup_ui(self):
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(12)

        title = QLabel("ACHIEVEMENTS")
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
    def _load_achievements(self):
        achievements = [
            (1, "First Blood", "Premier objectif validé", False),
            (2, "Getting Started", "5 objectifs validés", False),
            (3, "Consistent", "Streak de 3 jours", False),
            (4, "Grinder", "25 objectifs validés", False),
            (5, "Level 5", "Atteindre le niveau 5", False),
            (6, "Level 10", "Atteindre le niveau 10", False),

            # Secrets
            (100, "???", "Succès secret", True),
            (101, "???", "Succès secret", True),
            (102, "???", "Succès secret", True),
            (103, "???", "Succès secret", True),
        ]

        for ach_id, title, desc, secret in achievements:
            unlocked = self.storage.is_achievement_unlocked(ach_id)

            if secret and not unlocked:
                self._add_card("🔒 ???", "Succès secret", False)
            else:
                self._add_card(title, desc, unlocked)

    # -------------------------
    # CARD
    # -------------------------
    def _add_card(self, title: str, description: str, unlocked: bool):
        card = QFrame()
        card.setStyleSheet(f"""
        QFrame {{
            background-color: {'#1a1f36' if unlocked else '#111426'};
            border: 1px solid {'#7f5af0' if unlocked else '#2d325a'};
            border-radius: 8px;
            padding: 12px;
        }}
        """)

        layout = QVBoxLayout(card)

        title_label = QLabel(
            f"🏆 {title}" if unlocked else f"🔒 {title}"
        )
        title_label.setStyleSheet("""
        QLabel {
            font-size: 15px;
            font-weight: bold;
            color: #ffffff;
        }
        """)

        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
        QLabel {
            font-size: 13px;
            color: #b8b8d1;
        }
        """)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)

        self.layout.addWidget(card)
