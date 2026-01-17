from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QFrame, QScrollArea, QHBoxLayout,
    QPushButton, QProgressBar
)
from PySide6.QtCore import Qt

from core.storage import Storage


class AchievementsWindow(QWidget):
    """
    Fenêtre Achievements
    - compteur X / Y
    - barre de progression globale
    - filtres (Tous / Débloqués / Non débloqués / Secrets)
    - tri automatique
    - rareté (commun / rare / légendaire)
    - catégories (discipline / endurance / mental)
    - scroll
    """

    def __init__(self, storage: Storage):
        super().__init__()

        self.storage = storage
        self.current_filter = "all"

        self.setWindowTitle("Achievements")
        self.resize(460, 580)

        self._setup_ui()
        self._load_achievements()

    # -------------------------
    # UI
    # -------------------------
    def _setup_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setAlignment(Qt.AlignTop)
        main_layout.setSpacing(10)

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

        self.counter_label = QLabel("")
        self.counter_label.setAlignment(Qt.AlignCenter)
        self.counter_label.setStyleSheet("""
        QLabel {
            font-size: 13px;
            color: #b8b8d1;
        }
        """)
        main_layout.addWidget(self.counter_label)

        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(100)
        self.progress_bar.setFormat("%p% complété")
        self.progress_bar.setFixedHeight(16)
        self.progress_bar.setStyleSheet("""
        QProgressBar {
            background-color: #14182b;
            border: 1px solid #2d325a;
            border-radius: 6px;
            text-align: center;
            color: white;
        }
        QProgressBar::chunk {
            background-color: #7f5af0;
            border-radius: 6px;
        }
        """)
        main_layout.addWidget(self.progress_bar)

        # Filters
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        self.btn_all = QPushButton("Tous")
        self.btn_unlocked = QPushButton("Débloqués")
        self.btn_locked = QPushButton("Non débloqués")
        self.btn_secrets = QPushButton("Secrets")

        for btn in (
            self.btn_all,
            self.btn_unlocked,
            self.btn_locked,
            self.btn_secrets
        ):
            btn.setCheckable(True)
            btn.setStyleSheet("""
            QPushButton {
                background-color: #1a1f36;
                border: 1px solid #2d325a;
                border-radius: 6px;
                padding: 4px 10px;
            }
            QPushButton:checked {
                background-color: #7f5af0;
                border-color: #7f5af0;
            }
            """)

        self.btn_all.setChecked(True)

        self.btn_all.clicked.connect(lambda: self._set_filter("all"))
        self.btn_unlocked.clicked.connect(lambda: self._set_filter("unlocked"))
        self.btn_locked.clicked.connect(lambda: self._set_filter("locked"))
        self.btn_secrets.clicked.connect(lambda: self._set_filter("secrets"))

        filter_layout.addWidget(self.btn_all)
        filter_layout.addWidget(self.btn_unlocked)
        filter_layout.addWidget(self.btn_locked)
        filter_layout.addWidget(self.btn_secrets)

        main_layout.addLayout(filter_layout)

        # Scroll
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        self.content_layout.setAlignment(Qt.AlignTop)
        self.content_layout.setSpacing(12)

        scroll.setWidget(content)
        main_layout.addWidget(scroll)

    # -------------------------
    # DATA
    # -------------------------
    def _load_achievements(self):
        while self.content_layout.count():
            item = self.content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        achievements = [
            # id, title, desc, secret, rarity, category
            (1, "First Blood", "Premier objectif validé", False, "common", "discipline"),
            (2, "Getting Started", "5 objectifs validés", False, "common", "discipline"),
            (3, "Consistent", "Streak de 3 jours", False, "rare", "discipline"),
            (4, "Grinder", "25 objectifs validés", False, "rare", "endurance"),
            (5, "Level 5", "Atteindre le niveau 5", False, "rare", "mental"),
            (6, "Level 10", "Atteindre le niveau 10", False, "legendary", "mental"),

            # secrets
            (100, "Awakening", "Pouvoir caché éveillé", True, "legendary", "mental"),
            (101, "Lone Wolf", "Avancer seul", True, "legendary", "discipline"),
            (102, "Iron Mind", "Mental d'acier", True, "legendary", "mental"),
            (103, "No Mercy", "Aucune faiblesse", True, "legendary", "endurance"),
        ]

        unlocked_cards = []
        locked_cards = []

        unlocked_count = 0
        total = len(achievements)

        for ach_id, title, desc, secret, rarity, category in achievements:
            unlocked = self.storage.is_achievement_unlocked(ach_id)

            if unlocked:
                unlocked_count += 1

            if self.current_filter == "unlocked" and not unlocked:
                continue
            if self.current_filter == "locked" and unlocked:
                continue
            if self.current_filter == "secrets" and not secret:
                continue

            if secret and not unlocked:
                card = self._build_card("???", "Succès secret", False, rarity, category)
            else:
                card = self._build_card(title, desc, unlocked, rarity, category)

            (unlocked_cards if unlocked else locked_cards).append(card)

        self.counter_label.setText(f"{unlocked_count} / {total} débloqués")
        self.progress_bar.setValue(int((unlocked_count / total) * 100))

        for card in unlocked_cards:
            self.content_layout.addWidget(card)
        for card in locked_cards:
            self.content_layout.addWidget(card)

        self.content_layout.addStretch()

    # -------------------------
    # FILTER
    # -------------------------
    def _set_filter(self, value: str):
        self.current_filter = value

        self.btn_all.setChecked(value == "all")
        self.btn_unlocked.setChecked(value == "unlocked")
        self.btn_locked.setChecked(value == "locked")
        self.btn_secrets.setChecked(value == "secrets")

        self._load_achievements()

    # -------------------------
    # CARD
    # -------------------------
    def _build_card(self, title, description, unlocked, rarity, category) -> QFrame:
        rarity_styles = {
            "common": ("#9aa0b5", "🥉"),
            "rare": ("#7f5af0", "🥈"),
            "legendary": ("#f5c542", "🥇"),
        }

        category_styles = {
            "discipline": ("🥋", "#4ea8de"),
            "endurance": ("🫀", "#e63946"),
            "mental": ("🧠", "#9d4edd"),
        }

        r_color, r_icon = rarity_styles.get(rarity, ("#9aa0b5", "🥉"))
        c_icon, c_color = category_styles.get(category, ("❓", "#999"))

        card = QFrame()
        card.setStyleSheet(f"""
        QFrame {{
            background-color: {'#1a1f36' if unlocked else '#111426'};
            border: 2px solid {r_color};
            border-radius: 8px;
            padding: 12px;
        }}
        """)

        layout = QVBoxLayout(card)

        title_label = QLabel(
            f"{r_icon} {title}" if unlocked else f"🔒 {title}"
        )
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")

        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 13px; color: #b8b8d1;")

        category_label = QLabel(f"{c_icon} {category.upper()}")
        category_label.setStyleSheet(f"""
        QLabel {{
            font-size: 11px;
            font-weight: bold;
            color: {c_color};
        }}
        """)

        layout.addWidget(title_label)
        layout.addWidget(desc_label)
        layout.addWidget(category_label)

        return card
