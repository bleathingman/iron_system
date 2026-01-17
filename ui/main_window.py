from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QProgressBar
)
from PySide6.QtCore import Qt

from core.user import User
from core.storage import Storage
from core.engine import Engine

DAILY_EXP_GOAL = 100


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IronSystem")
        self.setMinimumSize(460, 480)

        # CORE
        # =========================
        self.storage = Storage()
        self.storage.seed_level_1_objectives()

        self.user = User()
        self.user.stats = self.storage.load_stats()
        self.engine = Engine(self.user, self.storage)

        self.objectives = self.storage.load_objectives()

        self._setup_ui()
        self.refresh_dashboard()

    # -------------------------
    # UI SETUP
    # -------------------------
    def _setup_ui(self):
        central = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        self.level_label = QLabel()
        self.exp_label = QLabel()
        self.streak_label = QLabel()
        self.best_streak_label = QLabel()

        for lbl in (self.level_label, self.exp_label,
                    self.streak_label, self.best_streak_label):
            lbl.setAlignment(Qt.AlignCenter)

        self.level_label.setStyleSheet("font-size: 22px; font-weight: bold;")
        self.exp_label.setStyleSheet("font-size: 18px;")
        self.streak_label.setStyleSheet("font-size: 16px;")
        self.best_streak_label.setStyleSheet("font-size: 14px; color: gray;")

        self.exp_bar = QProgressBar()
        self.exp_bar.setMaximum(DAILY_EXP_GOAL)
        self.exp_bar.setAlignment(Qt.AlignCenter)
        self.exp_bar.setFormat("%v / %m EXP")

        self.layout.addWidget(self.level_label)
        self.layout.addWidget(self.exp_label)
        self.layout.addWidget(self.exp_bar)
        self.layout.addWidget(self.streak_label)
        self.layout.addWidget(self.best_streak_label)
        self.layout.addSpacing(25)

        # -------- OBJECTIFS --------
        self.objective_buttons = {}

        for obj in self.objectives:
            row = QHBoxLayout()
            label = QLabel(f"{obj.title} (+{obj.value} EXP)")
            button = QPushButton("Valider")
            button.clicked.connect(lambda _, o=obj: self.validate_objective(o))

            row.addWidget(label)
            row.addStretch()
            row.addWidget(button)

            self.layout.addLayout(row)
            self.objective_buttons[obj.id] = button

        central.setLayout(self.layout)
        self.setCentralWidget(central)

    # -------------------------
    # ACTION
    # -------------------------
    def validate_objective(self, objective):
        success = self.engine.validate_objective(objective)
        if success:
            self.storage.save_stats(self.user.stats)
        self.refresh_dashboard()

    # -------------------------
    # DISPLAY
    # -------------------------
    def refresh_dashboard(self):
        level = self.user.stats.get_level()
        self.level_label.setText(f"🆙 Niveau {level}")

        self.exp_label.setText(f"🧬 EXP totale : {self.user.stats.total_points}")

        today_exp = self.storage.get_today_exp()
        self.exp_bar.setValue(min(today_exp, DAILY_EXP_GOAL))

        self.streak_label.setText(f"🔥 Streak : {self.user.stats.current_streak}")
        self.best_streak_label.setText(
            f"🏆 Meilleur streak : {self.user.stats.best_streak}"
        )
