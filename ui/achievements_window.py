from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QScrollArea,
    QFrame
)
from PySide6.QtCore import Qt

from core.storage import Storage


class AchievementsWindow(QWidget):
    """
    Écran "Mes Achievements"
    Affiche tous les succès, débloqués ou non
    """

    def __init__(self, storage: Storage):
        super().__init__()

        self.storage = storage

        self.setWindowTitle("Achievements")
        self.setMinimumSize(420, 500)

        self._setup_ui()
        self._load_achievements()

    # -------------------------
    # UI SETUP
    # -------------------------
    def _setup_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(14)

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

        layout.addWidget(title)

        # Scroll container
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setSpacing(10)

        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.scroll_content)

        layout.addWidget(self.scroll)
        self.setLayout(layout)

    # -------------------------
    # DATA
    # -------------------------
    def _load_achievements(self):
        """
        Charge tous les achievements connus
        """
        achievements = [
            (1, "First Blood", "Premier objectif validé"),
            (2, "Getting Started", "5 objectifs validés"),
            (3, "Consistent", "Streak de 3 jours"),
            (4, "Grinder", "25 objectifs validés"),
            (5, "Level 5", "Atteindre le niveau 5"),
            (6, "Level 10", "Atteindre le niveau 10"),
        ]

        for ach_id, title, desc in achievements:
            unlocked = self.storage.is_achievement_unlocked(ach_id)
            self._add_achievement_card(title, desc, unlocked)

    # -------------------------
    # UI ELEMENT
    # -------------------------
    def _add_achievement_card(self, title, description, unlocked: bool):
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)

        card.setStyleSheet("""
        QFrame {
            background-color: %s;
            border: 1px solid %s;
            border-radius: 8px;
            padding: 10px;
        }
        """ % (
            "#1a1f36" if unlocked else "#111426",
            "#7f5af0" if unlocked else "#2d325a"
        ))

        layout = QVBoxLayout(card)

        title_label = QLabel(
            f"🏆 {title}" if unlocked else f"🔒 {title}"
        )
        title_label.setStyleSheet("""
        QLabel {
            font-size: 16px;
            font-weight: bold;
            color: %s;
        }
        """ % ("#ffffff" if unlocked else "#777777"))

        desc_label = QLabel(description)
        desc_label.setStyleSheet("""
        QLabel {
            font-size: 13px;
            color: %s;
        }
        """ % ("#b8b8d1" if unlocked else "#555555"))

        layout.addWidget(title_label)
        layout.addWidget(desc_label)

        self.scroll_layout.addWidget(card)
