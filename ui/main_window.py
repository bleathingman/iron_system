from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QProgressBar,
    QGraphicsDropShadowEffect, QMenuBar,
    QWidgetAction, QSlider
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    QUrl, QSettings
)
from PySide6.QtGui import QColor
from PySide6.QtMultimedia import QSoundEffect

from core.user import User
from core.storage import Storage
from core.engine import Engine


class MainWindow(QMainWindow):
    """
    Fenêtre principale d'IronSystem
    Dark Solo Leveling theme
    + animations
    + sons SYSTEM
    + paramètres audio persistants
    + achievements
    """

    def __init__(self):
        super().__init__()

        self.setWindowTitle("IronSystem")
        self.setMinimumSize(500, 560)

        # =========================
        # SETTINGS (persistants)
        # =========================
        self.settings = QSettings("IronSystem", "IronSystemApp")

        self._volume = self.settings.value("audio/volume", 0.4, float)
        self._muted = self.settings.value("audio/muted", False, bool)

        # =========================
        # CORE
        # =========================
        self.storage = Storage()
        self.storage.seed_objectives()

        self.user = User()
        self.user.stats = self.storage.load_stats()
        self.engine = Engine(self.user, self.storage)

        # =========================
        # AUDIO SYSTEM
        # =========================
        self._init_sounds()

        # =========================
        # UI
        # =========================
        self._setup_menu()
        self._setup_ui()
        self._apply_dark_theme()
        self.refresh_dashboard()

    # -------------------------
    # MENU PARAMÈTRES
    # -------------------------
    def _setup_menu(self):
        menu_bar = QMenuBar(self)
        settings_menu = menu_bar.addMenu("⚙ Paramètres")

        # Toggle audio ON/OFF
        self.audio_action = settings_menu.addAction("")
        self.audio_action.triggered.connect(self._toggle_mute)
        self._update_audio_action_text()

        # Slider volume (inline)
        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(self._volume * 100))
        slider.valueChanged.connect(self._on_volume_changed)

        slider_widget = QWidget()
        slider_layout = QHBoxLayout(slider_widget)
        slider_layout.setContentsMargins(8, 4, 8, 4)
        slider_layout.addWidget(QLabel("Volume"))
        slider_layout.addWidget(slider)

        slider_action = QWidgetAction(self)
        slider_action.setDefaultWidget(slider_widget)
        settings_menu.addAction(slider_action)

        self.setMenuBar(menu_bar)

    def _toggle_mute(self):
        self._muted = not self._muted
        self.settings.setValue("audio/muted", self._muted)
        self._apply_audio_settings()
        self._update_audio_action_text()

    def _update_audio_action_text(self):
        self.audio_action.setText(
            "Audio : OFF" if self._muted else "Audio : ON"
        )

    def _on_volume_changed(self, value: int):
        self._volume = value / 100
        self.settings.setValue("audio/volume", self._volume)
        self._apply_audio_settings()

    # -------------------------
    # AUDIO
    # -------------------------
    def _init_sounds(self):
        """
        Initialise les sons SYSTEM
        """
        self.sound_exp = QSoundEffect()
        self.sound_exp.setSource(QUrl.fromLocalFile("assets/sounds/exp.wav"))

        self.sound_level_up = QSoundEffect()
        self.sound_level_up.setSource(QUrl.fromLocalFile("assets/sounds/level_up.wav"))

        self._apply_audio_settings()

    def _apply_audio_settings(self):
        volume = 0 if self._muted else self._volume
        self.sound_exp.setVolume(volume)
        self.sound_level_up.setVolume(volume)

    # -------------------------
    # UI SETUP
    # -------------------------
    def _setup_ui(self):
        central = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(18)

        self.system_label = QLabel("SYSTEM")
        self.system_label.setAlignment(Qt.AlignCenter)
        self.system_label.setObjectName("systemLabel")

        self.level_label = QLabel()
        self.level_label.setAlignment(Qt.AlignCenter)
        self.level_label.setObjectName("levelLabel")

        self.level_glow = QGraphicsDropShadowEffect(self)
        self.level_glow.setBlurRadius(0)
        self.level_glow.setColor(QColor("#7f5af0"))
        self.level_glow.setOffset(0)
        self.level_label.setGraphicsEffect(self.level_glow)

        self.exp_label = QLabel()
        self.exp_label.setAlignment(Qt.AlignCenter)
        self.exp_label.setObjectName("expLabel")

        self.exp_bar = QProgressBar()
        self.exp_bar.setMaximum(100)
        self.exp_bar.setFormat("%v / %m EXP")
        self.exp_bar.setObjectName("expBar")

        self.exp_glow = QGraphicsDropShadowEffect(self)
        self.exp_glow.setBlurRadius(0)
        self.exp_glow.setColor(QColor("#7f5af0"))
        self.exp_glow.setOffset(0)
        self.exp_bar.setGraphicsEffect(self.exp_glow)

        self.layout.addWidget(self.system_label)
        self.layout.addWidget(self.level_label)
        self.layout.addWidget(self.exp_label)
        self.layout.addWidget(self.exp_bar)
        self.layout.addSpacing(25)

        self.objectives_container = QVBoxLayout()
        self.layout.addLayout(self.objectives_container)

        central.setLayout(self.layout)
        self.setCentralWidget(central)

    # -------------------------
    # THEME
    # -------------------------
    def _apply_dark_theme(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #0b0f1a;
            color: #e6e6f0;
            font-family: Segoe UI;
            font-size: 14px;
        }
        QLabel#systemLabel {
            color: #7f5af0;
            font-size: 26px;
            font-weight: bold;
            letter-spacing: 4px;
        }
        QLabel#levelLabel {
            font-size: 22px;
            font-weight: bold;
            color: #ffffff;
        }
        QLabel#expLabel {
            font-size: 14px;
            color: #b8b8d1;
        }
        QProgressBar#expBar {
            background-color: #14182b;
            border: 1px solid #2d325a;
            border-radius: 6px;
            height: 18px;
            text-align: center;
            color: #ffffff;
        }
        QProgressBar#expBar::chunk {
            background-color: #7f5af0;
            border-radius: 6px;
        }
        QPushButton {
            background-color: #1a1f36;
            border: 1px solid #2d325a;
            border-radius: 6px;
            padding: 6px 14px;
            color: #ffffff;
        }
        QPushButton:hover {
            background-color: #232863;
            border-color: #7f5af0;
        }
        QPushButton:pressed {
            background-color: #7f5af0;
        }
        """)

    # -------------------------
    # DASHBOARD
    # -------------------------
    def refresh_dashboard(self):
        prev_level = getattr(self, "_last_level", None)
        level = self.user.stats.get_level()

        self.level_label.setText(f"LEVEL {level}")
        self.exp_label.setText(
            f"EXP {self.user.stats.get_exp_in_level()} / 100 → Level {level + 1}"
        )
        self.exp_bar.setValue(self.user.stats.get_exp_in_level())

        if prev_level is not None and level > prev_level:
            self._animate_level_up()
            self.sound_level_up.play()

        self._last_level = level

        while self.objectives_container.count():
            item = self.objectives_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for obj in self.storage.load_objectives_for_level(level):
            row = QWidget()
            row_layout = QHBoxLayout(row)
            label = QLabel(f"{obj.title}  +{obj.value} EXP")
            button = QPushButton("VALIDER")
            button.clicked.connect(lambda _, o=obj: self.validate_objective(o))
            row_layout.addWidget(label)
            row_layout.addStretch()
            row_layout.addWidget(button)
            self.objectives_container.addWidget(row)

    # -------------------------
    # ACTION
    # -------------------------
    def validate_objective(self, objective):
        if self.engine.validate_objective(objective):
            self.storage.save_stats(self.user.stats)
            self.sound_exp.play()
            self._animate_exp_gain()
            self._check_achievements()

        self.refresh_dashboard()

    # -------------------------
    # ACHIEVEMENTS
    # -------------------------
    def _check_achievements(self):
        stats = self.user.stats
        level = stats.get_level()

        achievements = [
            (1, "First Blood", "Premier objectif validé", stats.total_validations >= 1),
            (2, "Getting Started", "5 objectifs validés", stats.total_validations >= 5),
            (3, "Consistent", "Streak de 3 jours", stats.current_streak >= 3),
            (4, "Grinder", "25 objectifs validés", stats.total_validations >= 25),
            (5, "Level 5", "Atteindre le niveau 5", level >= 5),
            (6, "Level 10", "Atteindre le niveau 10", level >= 10),
        ]

        for ach_id, title, desc, condition in achievements:
            if condition and not self.storage.is_achievement_unlocked(ach_id):
                self.storage.unlock_achievement(ach_id)
                self._show_achievement_popup(title, desc)

    def _show_achievement_popup(self, title: str, description: str):
        popup = QLabel(f"🏆 {title}\n{description}", self)
        popup.setAlignment(Qt.AlignCenter)
        popup.setStyleSheet("""
        QLabel {
            background-color: #1a1f36;
            border: 2px solid #7f5af0;
            border-radius: 8px;
            padding: 12px;
            color: white;
            font-size: 14px;
        }
        """)
        popup.setFixedSize(280, 80)
        popup.move((self.width() - popup.width()) // 2, 40)
        popup.show()

        anim = QPropertyAnimation(popup, b"windowOpacity")
        anim.setDuration(2000)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(popup.deleteLater)
        anim.start()

        self._achievement_anim = anim

    # -------------------------
    # ANIMATIONS
    # -------------------------
    def _animate_exp_gain(self):
        anim = QPropertyAnimation(self.exp_glow, b"blurRadius")
        anim.setDuration(400)
        anim.setStartValue(0)
        anim.setEndValue(28)
        anim.setEasingCurve(QEasingCurve.OutCubic)

        anim_back = QPropertyAnimation(self.exp_glow, b"blurRadius")
        anim_back.setDuration(600)
        anim_back.setStartValue(28)
        anim_back.setEndValue(0)
        anim_back.setEasingCurve(QEasingCurve.InCubic)

        anim.start()
        anim_back.start()

        self._exp_anim = anim
        self._exp_anim_back = anim_back

    def _animate_level_up(self):
        anim = QPropertyAnimation(self.level_glow, b"blurRadius")
        anim.setDuration(600)
        anim.setStartValue(0)
        anim.setEndValue(35)
        anim.setEasingCurve(QEasingCurve.OutBack)

        anim_back = QPropertyAnimation(self.level_glow, b"blurRadius")
        anim_back.setDuration(800)
        anim_back.setStartValue(35)
        anim_back.setEndValue(0)
        anim_back.setEasingCurve(QEasingCurve.InOutCubic)

        anim.start()
        anim_back.start()

        self._lvl_anim = anim
        self._lvl_anim_back = anim_back
