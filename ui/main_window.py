from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QProgressBar
)
from PySide6.QtCore import Qt

from core.user import User
from core.storage import Storage
from core.engine import Engine


class MainWindow(QMainWindow):
    """
    Fenêtre principale d'IronSystem.
    L'UI n'a AUCUNE logique métier.
    Elle affiche l'état du core et déclenche des actions.
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("IronSystem")
        self.setMinimumSize(480, 520)

        # =========================
        # CORE
        # =========================
        self.storage = Storage()
        self.storage.seed_objectives()

        self.user = User()
        self.user.stats = self.storage.load_stats()

        self.engine = Engine(self.user, self.storage)

        # =========================
        # UI
        # =========================
        self._setup_ui()
        self.refresh_dashboard()

    def _setup_ui(self):
        """
        Construit toute l'interface graphique.
        """
        central = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)

        # ---- Infos principales ----
        self.level_label = QLabel()
        self.exp_label = QLabel()

        self.level_label.setAlignment(Qt.AlignCenter)
        self.exp_label.setAlignment(Qt.AlignCenter)

        self.level_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        self.exp_label.setStyleSheet("font-size: 16px;")

        # Barre EXP vers niveau suivant
        self.exp_bar = QProgressBar()
        self.exp_bar.setMaximum(100)
        self.exp_bar.setFormat("%v / %m EXP")

        self.layout.addWidget(self.level_label)
        self.layout.addWidget(self.exp_label)
        self.layout.addWidget(self.exp_bar)
        self.layout.addSpacing(25)

        # Conteneur des objectifs (reconstruit dynamiquement)
        self.objectives_container = QVBoxLayout()
        self.layout.addLayout(self.objectives_container)

        central.setLayout(self.layout)
        self.setCentralWidget(central)

    def refresh_dashboard(self):
        """
        Met à jour tout l'affichage :
        - niveau
        - EXP
        - objectifs débloqués
        """
        level = self.user.stats.get_level()

        self.level_label.setText(f"🆙 Niveau {level}")
        self.exp_label.setText(
            f"EXP : {self.user.stats.get_exp_in_level()} / 100 "
            f"(Niveau {level} → {level + 1})"
        )


        # Barre de progression vers le prochain niveau
        self.exp_bar.setValue(self.user.stats.get_exp_in_level())

        # Nettoyage des anciens objectifs affichés
        while self.objectives_container.count():
            self.objectives_container.takeAt(0)

        # Chargement des objectifs accessibles
        objectives = self.storage.load_objectives_for_level(level)

        for obj in objectives:
            row = QHBoxLayout()
            label = QLabel(f"{obj.title} (+{obj.value} EXP)")
            button = QPushButton("Valider")

            # Chaque bouton déclenche une validation propre
            button.clicked.connect(lambda _, o=obj: self.validate_objective(o))

            row.addWidget(label)
            row.addStretch()
            row.addWidget(button)

            self.objectives_container.addLayout(row)

    def validate_objective(self, objective):
        """
        Appelé quand l'utilisateur valide un objectif.
        """
        if self.engine.validate_objective(objective):
            self.storage.save_stats(self.user.stats)

        self.refresh_dashboard()
