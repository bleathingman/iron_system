import sys
import json
from pathlib import Path

from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout,
    QLabel, QPushButton, QProgressBar, QLineEdit
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap

from quests import get_daily_quests
from progression import (
    SAVE_PATH,
    load_save, save_progress,
    add_xp_and_level_up,
    log_daily_progress,
    update_streak,
    update_badges,
    midnight_check,
    create_default_save
)
from ui import apply_style, get_rank
from profile_window import ProfileWindow


BASE_DIR = Path("/home/divh/iron_system")


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
    return BASE_DIR / "assets" / "ranks" / mapping.get(rank_name, "initie.png")


# =====================
# MINI LOGIN
# =====================
class UserSetup(QWidget):
    def __init__(self, save, on_done):
        super().__init__()
        self.save = save
        self.on_done = on_done

        self.setWindowTitle("Création du profil")
        self.setFixedSize(320, 260)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignTop)

        layout.addWidget(QLabel("👤 Création du profil"))

        self.name = QLineEdit()
        self.weight = QLineEdit()
        self.goal = QLineEdit()

        self.name.setPlaceholderText("Pseudo")
        self.weight.setPlaceholderText("Poids actuel (kg)")
        self.goal.setPlaceholderText("Objectif de poids (kg)")

        btn = QPushButton("Valider")
        btn.clicked.connect(self.validate)

        layout.addWidget(self.name)
        layout.addWidget(self.weight)
        layout.addWidget(self.goal)
        layout.addWidget(btn)

        apply_style(self, 1)
        self.show()

    def validate(self):
        try:
            self.save["user"]["name"] = self.name.text()
            self.save["user"]["weight"] = int(self.weight.text())
            self.save["user"]["goal_weight"] = int(self.goal.text())
        except ValueError:
            return

        save_progress(self.save)
        self.close()
        self.on_done()


# =====================
# MAIN APP
# =====================
class IronSystem(QWidget):
    def __init__(self):
        super().__init__()
        self.save = load_save()

        user = self.save.get("user", {})
        if not user.get("name"):
            self.setup = UserSetup(self.save, self.start)
            return

        self.start()

    def start(self):
        midnight_check(self.save)

        self.quests = get_daily_quests(self.save)
        self.completed = set(self.save.get("completed_today", []))

        self.setWindowTitle("IRON SYSTEM")
        self.setFixedSize(520, 720)

        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # ===== RANK ICON =====
        rank_name, _ = get_rank(self.save["level"])
        self.rank_icon = QLabel(alignment=Qt.AlignCenter)
        pixmap = QPixmap(str(get_rank_icon_path(rank_name)))
        self.rank_icon.setPixmap(
            pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        )
        self.layout.addWidget(self.rank_icon)

        # ===== PROFILE BTN =====
        profile_btn = QPushButton(f"👤 {self.save['user']['name']}")
        profile_btn.clicked.connect(self.open_profile)
        self.layout.addWidget(profile_btn)

        # ===== QUESTS =====
        self.labels = {}
        self.buttons = {}

        for quest, data in self.quests.items():
            label = QLabel(f"{quest} : {data['value']} (+{data['xp']} XP)")
            btn = QPushButton("Valider")
            btn.clicked.connect(lambda _, q=quest: self.validate_quest(q))

            self.layout.addWidget(label)
            self.layout.addWidget(btn)

            self.labels[quest] = label
            self.buttons[quest] = btn

            if quest in self.completed:
                label.setText(f"✔ {quest}")
                btn.setEnabled(False)

        # ===== XP BAR =====
        self.progress = QProgressBar()
        self.progress.setMaximum(self.save["xp_required"])
        self.progress.setValue(self.save["xp"])
        self.layout.addWidget(self.progress)

        self.info = QLabel()
        self.layout.addWidget(self.info)

        apply_style(self, self.save["level"])
        self.update_ui()
        self.show()

    def open_profile(self):
        self.profile_window = ProfileWindow(self.save, self.on_reset)
        self.profile_window.show()

    def validate_quest(self, quest):
        if quest in self.completed:
            return

        xp = self.quests[quest]["xp"]
        self.completed.add(quest)
        self.save["completed_today"] = list(self.completed)

        add_xp_and_level_up(self.save, xp)
        log_daily_progress(self.save, quest, xp)
        update_streak(self.save)
        update_badges(self.save)
        save_progress(self.save)

        self.labels[quest].setText(f"✔ {quest}")
        self.buttons[quest].setEnabled(False)

        self.progress.setMaximum(self.save["xp_required"])
        self.progress.setValue(self.save["xp"])
        self.update_ui()

    def update_ui(self):
        self.info.setText(
            f"Level {self.save['level']} | "
            f"XP {self.save['xp']} / {self.save['xp_required']} | "
            f"🔥 {self.save['streak']}"
        )

    def on_reset(self):
        with open(SAVE_PATH, "w", encoding="utf-8") as f:
            json.dump(create_default_save(), f, indent=2)
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = IronSystem()
    sys.exit(app.exec())
