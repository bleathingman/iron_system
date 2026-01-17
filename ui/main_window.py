from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
    QHBoxLayout,
)
from PySide6.QtCore import Qt

from core.user import User
from core.storage import Storage
from core.engine import Engine
from core.objective import Objective, Frequency


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("IronSystem")
        self.setMinimumSize(420, 380)

        # =========================
        # CORE
        # =========================
        self.storage = Storage()
        self.user = User()
        self.user.stats = self.storage.load_stats()
        self.engine = Engine(self.user, self.storage)

        # =========================
        # OBJECTIFS — NIVEAU 1 (SOLO LEVELING STYLE)
        # =========================
        self.objectives = [
            Objective(1, "20 Pompes", Frequency.DAILY, 20),
            Objective(2, "30 Abdos", Frequency.DAILY, 15),
            Objective(3, "30 Squats", Frequency.DAILY, 15),
            Objective(4, "Gainage 1 min", Frequency.DAILY, 10),
            Objective(5, "Marche rapide 20 min", Frequency.DAILY, 20),
        ]

        # =========================
        # UI
        # =========================
        self._setup_ui()
        self.refresh_dashboard()

    # -------------------------
    # UI SETUP
    # -------------------------
    def _setup_ui(self):
        central_widget = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # -------- DASHBOARD --------
        self.exp_label = QLabel()
        self.streak_label = QLabel()
        self.best_streak_label = QLabel()

        self.exp_label.setAlignment(Qt.AlignCenter)
        self.streak_label.setAlignment(Qt.AlignCenter)
        self.best_streak_label.setAlignment(Qt.AlignCenter)

        self.exp_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.streak_label.setStyleSheet("font-size: 16px;")
        self.best_streak_label.setStyleSheet("font-size: 14px; color: gray;")

        self.layout.addWidget(self.exp_label)
        self.layout.addWidget(self.streak_label)
        self.layout.addWidget(self.best_streak_label)
        self.layout.addSpacing(25)

        # -------- OBJECTIFS --------
        self.objective_buttons = {}

        for obj in self.objectives:
            row = QHBoxLayout()

            label = QLabel(f"{obj.title} (+{obj.value} EXP)")
            label.setStyleSheet("font-size: 14px;")

            button = QPushButton("Valider")
            button.setFixedHeight(32)
            button.clicked.connect(
                lambda checked, o=obj: self.validate_objective(o)
            )

            row.addWidget(label)
            row.addStretch()
            row.addWidget(button)

            self.layout.addLayout(row)
            self.objective_buttons[obj.id] = button

        central_widget.setLayout(self.layout)
        self.setCentralWidget(central_widget)

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
        self.exp_label.setText(f"🧬 EXP : {self.user.stats.total_points}")
        self.streak_label.setText(f"🔥 Streak : {self.user.stats.current_streak}")
        self.best_streak_label.setText(
            f"🏆 Meilleur streak : {self.user.stats.best_streak}"
        )
