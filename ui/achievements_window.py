from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QFrame, QScrollArea, QHBoxLayout,
    QPushButton, QProgressBar, QSizePolicy
)
from PySide6.QtCore import Qt

from core.storage import Storage


class AchievementsWindow(QWidget):
    """
    Fenêtre Achievements
    - compteur X / Y
    - barre de progression globale
    - filtres
    - succès secrets
    - rareté / catégories
    - achievements à progression (Steam-like)
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

            (1, "Premier Pas", "Valider ton premier objectif", False, "common", "discipline"),
            (2, "Routine", "Valider 5 objectifs", False, "common", "discipline"),
            (3, "Déterminé", "Valider 10 objectifs", False, "rare", "discipline"),
            (4, "Machine", "Valider 25 objectifs", False, "rare", "endurance"),

            (10, "Sur la lancée", "3 validations consécutives", False, "common", "discipline"),
            (11, "Focus", "5 validations consécutives", False, "rare", "mental"),
            (12, "Mental d’acier", "10 validations consécutives", False, "rare", "mental"),

            (20, "Ça pique", "50 validations", False, "rare", "endurance"),
            (21, "No Pain No Gain", "100 validations", False, "legendary", "endurance"),

            (100, "Awakening", "Atteindre le niveau 5", True, "legendary", "mental"),
            (101, "Overdrive", "3 validations dans la même journée", True, "rare", "discipline"),
            (102, "Berserk", "5 validations d’affilée", True, "legendary", "endurance"),
            (103, "Iron Will", "Atteindre le niveau 10", True, "legendary", "mental"),

            (200, "Pushups I", "Effectuer 100 pompes", False, "common", "endurance"),
            (201, "Pushups II", "Effectuer 500 pompes", False, "rare", "endurance"),
            (202, "Pushups III", "Effectuer 1000 pompes", False, "legendary", "endurance"),
            (203, "Pushups IV", "Effectuer 5000 pompes", False, "legendary", "endurance"),

            (210, "Squats I", "Effectuer 250 squats", False, "common", "endurance"),
            (211, "Squats II", "Effectuer 1000 squats", False, "rare", "endurance"),
            (212, "Squats III", "Effectuer 2500 squats", False, "legendary", "endurance"),

            (220, "Abdos I", "Effectuer 500 abdos", False, "common", "mental"),
            (221, "Abdos II", "Effectuer 1500 abdos", False, "rare", "mental"),
            (222, "Abdos III", "Effectuer 3000 abdos", False, "legendary", "mental"),
        ]

        stats = self.storage.load_stats()
        print(
            "[ACH DEBUG]",
            "pushups =", stats.total_pushups,
            "squats =", stats.total_squats
        )


        progress_targets = {
            200: (stats.total_pushups, 100),
            201: (stats.total_pushups, 500),
            202: (stats.total_pushups, 1000),
            203: (stats.total_pushups, 5000),

            210: (stats.total_squats, 250),
            211: (stats.total_squats, 1000),
            212: (stats.total_squats, 2500),

            220: (stats.total_abs, 500),
            221: (stats.total_abs, 1500),
            222: (stats.total_abs, 3000),
        }

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
                card = self._build_card(
                    ach_id, "???", "Succès secret", False, rarity, category, progress_targets
                )
            else:
                card = self._build_card(
                    ach_id, title, desc, unlocked, rarity, category, progress_targets
                )

            (unlocked_cards if unlocked else locked_cards).append(card)

        self.counter_label.setText(f"{unlocked_count} / {total} débloqués")
        self.progress_bar.setValue(int((unlocked_count / total) * 100))

        for card in unlocked_cards + locked_cards:
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
    def _build_card(
        self, ach_id, title, description, unlocked, rarity, category, progress_targets
    ) -> QFrame:

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
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        card.setStyleSheet(f"""
        QFrame {{
            background-color: {'#1a1f36' if unlocked else '#111426'};
            border: 2px solid {r_color};
            border-radius: 8px;
            padding: 12px;
        }}
        """)

        layout = QVBoxLayout(card)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        title_label = QLabel(f"{r_icon} {title}" if unlocked else f"🔒 {title}")
        title_label.setWordWrap(True)
        title_label.setStyleSheet("font-size: 15px; font-weight: bold; color: white;")
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("font-size: 13px; color: #b8b8d1;")
        desc_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)

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

        # -------------------------
        # MINI PROGRESSION BAR
        # -------------------------
        if ach_id in progress_targets and not unlocked:
            current, goal = progress_targets[ach_id]
            percent = int((current / goal) * 100) if goal > 0 else 0

            bar_container = QHBoxLayout()
            bar_container.setSpacing(8)

            bar = QProgressBar()
            bar.setMaximum(goal)
            bar.setValue(min(current, goal))
            bar.setTextVisible(False)   # ⛔ pas de texte dans la barre
            bar.setFixedHeight(20)

            bar.setStyleSheet("""
                QProgressBar {
                    background-color: #14182b;
                    border-radius: 6px;
                }
                QProgressBar::chunk {
                    background-color: #7f5af0;
                    border-radius: 6px;
                }
            """)

            percent_label = QLabel(f"{percent}%")
            percent_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
            percent_label.setStyleSheet("""
                QLabel {
                    border: 0px;
                    color: #b8b8d1;
                    font-size: 12px;
                    font-weight: bold;
                    min-width: 36px;
                }
            """)

            bar_container.addWidget(bar, 1)      # prend tout l'espace
            bar_container.addWidget(percent_label, 0)

            layout.addSpacing(6)
            layout.addLayout(bar_container)


        return card
