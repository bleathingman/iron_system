import os
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QMessageBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from ui import apply_style, get_rank


BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def get_rank_icon_path(rank_name: str):
    mapping = {
        "INITIÉ": "initie.png",
        "APPRENTI": "apprenti.png",
        "ATHLÈTE": "athlete.png",
        "FORCE": "force.png",
        "PUISSANCE": "puissance.png",
        "VÉTÉRAN": "veteran.png",
        "COLOSSUS": "colossus.png",
        "TITAN": "titan.png",
        "HÉROS": "heros.png",
        "LÉGENDE": "legende.png",
    }
    filename = mapping.get(rank_name, "initie.png")
    return os.path.join(BASE_DIR, "assets", "ranks", filename)


class ProfileWindow(QWidget):
    def __init__(self, save, on_reset):
        super().__init__()
        self.save = save
        self.on_reset = on_reset

        self.setWindowTitle("Profil")
        self.setFixedSize(360, 520)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        # =====================
        # BADGE + RANK
        # =====================
        rank_name, _ = get_rank(self.save["level"])

        badge_layout = QHBoxLayout()
        badge_layout.setAlignment(Qt.AlignLeft)

        badge = QLabel()
        pixmap = QPixmap(get_rank_icon_path(rank_name))
        badge.setPixmap(
            pixmap.scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )

        rank_label = QLabel(rank_name)
        rank_label.setProperty("rank", True)

        badge_layout.addWidget(badge)
        badge_layout.addWidget(rank_label)

        layout.addLayout(badge_layout)

        # =====================
        # USER INFO
        # =====================
        layout.addSpacing(10)

        layout.addWidget(QLabel(f"👤 {self.save['user']['name']}"))
        layout.addWidget(QLabel(f"⚖️ Poids actuel : {self.save['user']['weight']} kg"))
        layout.addWidget(QLabel(f"🎯 Objectif : {self.save['user']['goal_weight']} kg"))

        layout.addSpacing(15)

        # =====================
        # STATS
        # =====================
        layout.addWidget(QLabel(f"📈 Niveau : {self.save['level']}"))
        layout.addWidget(QLabel(f"🔥 Streak : {self.save['streak']} jours"))
        layout.addWidget(QLabel(f"📅 Jours complétés : {self.save['profile']['total_days']}"))

        layout.addSpacing(25)

        # =====================
        # RESET BUTTON (WITH CONFIRM)
        # =====================
        reset_btn = QPushButton("🔁 Reset progression")
        reset_btn.clicked.connect(self.confirm_reset)
        layout.addWidget(reset_btn)

        apply_style(self, self.save["level"])
        self.show()

    # =====================
    # CONFIRM RESET
    # =====================
    def confirm_reset(self):
        msg = QMessageBox(self)
        msg.setWindowTitle("Confirmation")
        msg.setText("⚠️ Cette action réinitialisera toute votre progression.")
        msg.setInformativeText("Êtes-vous sûr de vouloir continuer ?")
        msg.setIcon(QMessageBox.Warning)

        confirm = msg.addButton("Oui, réinitialiser", QMessageBox.YesRole)
        cancel = msg.addButton("Annuler", QMessageBox.NoRole)

        msg.exec()

        if msg.clickedButton() == confirm:
            self.on_reset()
            self.close()
