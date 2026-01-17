from PySide6.QtWidgets import (
<<<<<<< HEAD
    QWidget, QVBoxLayout, QLabel, QFrame,
    QScrollArea, QPushButton, QSizePolicy
=======
    QWidget, QVBoxLayout, QLabel, QFrame
>>>>>>> parent of 7a9c80e (feat: add daily and weekly statistics overview)
)
from PySide6.QtCore import Qt

from core.storage import Storage
from core.user import User


class StatsWindow(QWidget):
    """
    Écran Statistiques
<<<<<<< HEAD
    Global + Journalier + Hebdomadaire
    Responsive + scroll + fermeture explicite
=======
    Affiche la progression globale de l'utilisateur
>>>>>>> parent of 7a9c80e (feat: add daily and weekly statistics overview)
    """

    def __init__(self, user: User, storage: Storage, parent=None):
        super().__init__(parent)

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
<<<<<<< HEAD
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(10)

        # ===== TITLE =====
=======
        layout = QVBoxLayout()
        layout.setSpacing(14)
        layout.setAlignment(Qt.AlignTop)

>>>>>>> parent of 7a9c80e (feat: add daily and weekly statistics overview)
        title = QLabel("STATISTIQUES")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("""
        QLabel {
            font-size: 22px;
<<<<<<< HEAD
            font-weight: bold;
            color: #7f5af0;
            letter-spacing: 3px;
        }
        """)
        main_layout.addWidget(title)

        # ===== SCROLL AREA =====
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setSpacing(14)
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
=======
>>>>>>> parent of 7a9c80e (feat: add daily and weekly statistics overview)
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #232863;
            border-color: #7f5af0;
        }
        """)
<<<<<<< HEAD
        main_layout.addWidget(close_btn)
=======

        layout.addWidget(title)

        self.cards_container = QVBoxLayout()
        self.cards_container.setSpacing(10)

        layout.addLayout(self.cards_container)
        self.setLayout(layout)
>>>>>>> parent of 7a9c80e (feat: add daily and weekly statistics overview)

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

<<<<<<< HEAD
        # ===== TODAY =====
        self._add_section("AUJOURD'HUI")
        self._add_stat_card("Validations du jour", f"{daily['validations']}")
        self._add_stat_card("Streak actuel", f"{daily['streak']} jours")

        # ===== WEEK =====
        self._add_section("SEMAINE")
        self._add_stat_card("Validations (estim.)", f"{weekly['validations']}")
        self._add_stat_card("Meilleur streak", f"{weekly['best_streak']} jours")

        self.content_layout.addStretch()
=======
        for title, value in data:
            self._add_stat_card(title, value)
>>>>>>> parent of 7a9c80e (feat: add daily and weekly statistics overview)

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

<<<<<<< HEAD
        self.content_layout.addWidget(card)

    # -------------------------
    # UX
    # -------------------------
    def keyPressEvent(self, event):
        """
        Permet de fermer la fenêtre avec ESC
        """
        if event.key() == Qt.Key_Escape:
            self.close()
        else:
            super().keyPressEvent(event)
=======
        self.cards_container.addWidget(card)
>>>>>>> parent of 7a9c80e (feat: add daily and weekly statistics overview)
