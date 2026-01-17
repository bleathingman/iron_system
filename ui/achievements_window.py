from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton
)
from PySide6.QtCore import Qt

from core.storage import Storage


class AchievementsWindow(QWidget):
    """
    Écran Achievements
    Responsive + scroll + fermeture explicite
    """

    def __init__(self, storage: Storage, parent=None):
        super().__init__(parent)

        self.storage = storage

        self.setWindowTitle("Achievements")
        self.setMinimumSize(380, 420)

        self._setup_ui()
        self._load_achievements()

    # -------------------------
    # UI SETUP
    # -------------------------
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ===== TITLE =====
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
        main_layout.addWidget(title)

        # ===== SCROLL =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(10)
        self.content_layout.setAlignment(Qt.AlignTop)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

        # ===== CLOSE BUTTON =====
        close_btn = QPushButton("FERMER")
        close_btn.setFixedHeight(34)
        close_btn.clicked.connect(self.close)
        close_btn.setStyleSheet("""
        QPushButton {
            background-color: #1a1f36;
            border: 1px solid #2d325a;
            border-radius: 6px;
            color: #ffffff;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #232863;
            border-color: #7f5af0;
        }
        """)
        main_layout.addWidget(close_btn)

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

            # --- SECRETS ---
            (100, "Lone Wolf", "3 objectifs validés le même jour", True),
            (101, "No Mercy", "5 validations d'affilée", True),
            (102, "Awakening", "Atteindre exactement le niveau 7", True),
            (103, "Iron Mind", "Streak de 7 jours", True),
        ]

        for ach_id, title, desc, secret in achievements:
            unlocked = self.storage.is_achievement_unlocked(ach_id)

            if secret and not unlocked:
                self._add_card("???", "Succès secret", False)
            else:
                self._add_card(title, desc, unlocked)

        self.content_layout.addStretch()

    # -------------------------
    # UI CARD
    # -------------------------
    def _add_card(self, title: str, description: str, unlocked: bool):
        card = QFrame()
        card.setStyleSheet(f"""
        QFrame {{
            background-color: {'#1a1f36' if unlocked else '#111426'};
            border: 1px solid {'#7f5af0' if unlocked else '#2d325a'};
            border-radius: 8px;
            padding: 10px;
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

        self.content_layout.addWidget(card)

    # -------------------------
    # UX
    # -------------------------
    def keyPressEvent(self, event):
        """
        Permet de fermer avec ESC
        """
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
