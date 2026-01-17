from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QLabel,
    QPushButton,
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
        self.setMinimumSize(400, 300)

        # =========================
        # CORE INITIALISATION
        # =========================
        self.storage = Storage()
        self.user = User()
        self.user.stats = self.storage.load_stats()
        self.engine = Engine(self.user, self.storage)

        # Objectif temporaire (test)
        self.objective = Objective(
            id=1,
            title="Workout",
            frequency=Frequency.DAILY,
            value=20,
        )

        # =========================
        # UI SETUP
        # =========================
        self._setup_ui()
        self.refresh_dashboard()

    # -------------------------
    # UI
    # -------------------------
    def _setup_ui(self):
        central_widget = QWidget()
        layout = QVBoxLayout()

        layout.setAlignment(Qt.AlignCenter)

        # Labels
        self.points_label = QLabel()
        self.streak_label = QLabel()
        self.best_streak_label = QLabel()

        self.points_label.setAlignment(Qt.AlignCenter)
        self.streak_label.setAlignment(Qt.AlignCenter)
        self.best_streak_label.setAlignment(Qt.AlignCenter)

        self.points_label.setStyleSheet("font-size: 18px;")
        self.streak_label.setStyleSheet("font-size: 16px;")
        self.best_streak_label.setStyleSheet("font-size: 14px; color: gray;")

        # Bouton validation
        self.validate_button = QPushButton("Valider l’objectif")
        self.validate_button.setFixedHeight(40)
        self.validate_button.clicked.connect(self.validate_objective)

        # Layout
        layout.addWidget(self.points_label)
        layout.addWidget(self.streak_label)
        layout.addWidget(self.best_streak_label)
        layout.addSpacing(20)
        layout.addWidget(self.validate_button)

        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    # -------------------------
    # ACTIONS
    # -------------------------
    def validate_objective(self):
        success = self.engine.validate_objective(self.objective)

        if success:
            self.storage.save_stats(self.user.stats)

        self.refresh_dashboard()

    # -------------------------
    # DISPLAY
    # -------------------------
    def refresh_dashboard(self):
        self.points_label.setText(f"Points : {self.user.stats.total_points}")
        self.streak_label.setText(f"🔥 Streak : {self.user.stats.current_streak}")
        self.best_streak_label.setText(
            f"🏆 Meilleur streak : {self.user.stats.best_streak}"
        )
