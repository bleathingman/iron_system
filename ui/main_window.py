from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QLabel,
    QPushButton, QHBoxLayout, QProgressBar,
    QGraphicsDropShadowEffect, QMenuBar,
    QWidgetAction, QSlider
)
from PySide6.QtCore import (
    Qt, QPropertyAnimation, QEasingCurve,
    QUrl, QSettings, QTimer
)
from PySide6.QtGui import QColor
from PySide6.QtMultimedia import QSoundEffect

from core.user import User
from core.storage import Storage
from core.objective import Objective, Frequency, Category
from core.engine import Engine
from ui.achievements_window import AchievementsWindow
from ui.stats_window import StatsWindow
from datetime import datetime, timedelta


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
        self.DEBUG = False

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

        # Popup achievement actif (anti-bug)
        self._achievement_popup = None

        # =========================
        # DAILY TIMER (AUTO UPDATE)
        # =========================
        self._last_daily_date = datetime.now().date()

        self.daily_timer = QTimer(self)
        self.daily_timer.timeout.connect(self._on_daily_timer_tick)
        self.daily_timer.start(60_000)  # toutes les 60 secondes


    # ------------------------------------------------------------------
    # MENU
    # ------------------------------------------------------------------
    def _setup_menu(self):
        menu_bar = QMenuBar(self)
        settings_menu = menu_bar.addMenu("⚙ Paramètres")

        achievements_action = settings_menu.addAction("🏆 Mes Achievements")
        achievements_action.triggered.connect(self.open_achievements)

        stats_action = settings_menu.addAction("📊 Statistiques")
        stats_action.triggered.connect(self.open_stats)

        settings_menu.addSeparator()

        self.audio_action = settings_menu.addAction("")
        self.audio_action.triggered.connect(self._toggle_mute)
        self._update_audio_action_text()

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

    def open_achievements(self):
        self.achievements_window = AchievementsWindow(self.storage)
        self.achievements_window.show()

    def open_stats(self):
        self.stats_window = StatsWindow(self.user, self.storage)
        self.stats_window.show()

    # ------------------------------------------------------------------
    # AUDIO
    # ------------------------------------------------------------------
    def _init_sounds(self):
        self.sound_exp = QSoundEffect()
        self.sound_exp.setSource(QUrl.fromLocalFile("assets/sounds/exp.wav"))

        self.sound_level_up = QSoundEffect()
        self.sound_level_up.setSource(QUrl.fromLocalFile("assets/sounds/level_up.wav"))

        self._apply_audio_settings()

    def _apply_audio_settings(self):
        volume = 0 if self._muted else self._volume
        self.sound_exp.setVolume(volume)
        self.sound_level_up.setVolume(volume)

    def _toggle_mute(self):
        self._muted = not self._muted
        self.settings.setValue("audio/muted", self._muted)
        self._apply_audio_settings()
        self._update_audio_action_text()

    def _update_audio_action_text(self):
        self.audio_action.setText("Audio : OFF" if self._muted else "Audio : ON")

    def _on_volume_changed(self, value: int):
        self._volume = value / 100
        self.settings.setValue("audio/volume", self._volume)
        self._apply_audio_settings()

    # ------------------------------------------------------------------
    # UI SETUP
    # ------------------------------------------------------------------
    def _setup_ui(self):
        central = QWidget()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignTop)
        self.layout.setSpacing(18)

        # ===== HEADER (JAMAIS NETTOYÉ) =====
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

        # ===== DAILY RESET TIMER =====
        self.daily_timer_label = QLabel()
        self.daily_timer_label.setAlignment(Qt.AlignCenter)
        self.daily_timer_label.setObjectName("expLabel")
        self.layout.addWidget(self.daily_timer_label)


        # ===== OBJECTIVES (SEUL LAYOUT NETTOYÉ) =====
        self.objectives_container = QVBoxLayout()
        self.layout.addLayout(self.objectives_container)

        central.setLayout(self.layout)
        self.setCentralWidget(central)

    # ------------------------------------------------------------------
    # THEME
    # ------------------------------------------------------------------
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

    # ------------------------------------------------------------------
    # DASHBOARD (FIX PRINCIPAL ICI)
    # ------------------------------------------------------------------
    def refresh_dashboard(self):
        stats = self.user.stats
        level = stats.get_level()
        exp = stats.get_exp_in_level()

        # 🔒 HEADER TOUJOURS MIS À JOUR
        self.level_label.setText(f"LEVEL {level}")
        self.exp_label.setText(f"EXP {exp} / 100 → Level {level + 1}")
        self.exp_bar.setValue(exp)

        # ⏱ DAILY TIMER
        self._update_daily_timer()


        # DAILY
        self.storage.generate_daily_pool(level, count=3)

        # NETTOYAGE UNIQUEMENT DES OBJECTIFS
        while self.objectives_container.count():
            item = self.objectives_container.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        daily_label = QLabel("DAILY QUESTS")
        daily_label.setAlignment(Qt.AlignCenter)
        daily_label.setObjectName("systemLabel")
        self.objectives_container.addWidget(daily_label)

        for row in self.storage.load_daily_objectives():
            obj = Objective(
                id=row["id"],
                title=row["title"],
                category=Category(row["category"]),
                frequency=Frequency.DAILY,
                min_level=row["min_level"],
                value=row["value"]
            )

            row_widget = QWidget()
            layout = QHBoxLayout(row_widget)

            label = QLabel(f"{obj.title}  +{obj.value} EXP")
            button = QPushButton("VALIDER")
            button.clicked.connect(lambda _, o=obj: self._validate_daily(o))

            layout.addWidget(label)
            layout.addStretch()
            layout.addWidget(button)

            self.objectives_container.addWidget(row_widget)

        # ===== ELITE DAILY =====
        self.storage.generate_elite_daily(level)
        elite = self.storage.load_elite_daily()

        if elite:
            elite_label = QLabel("🔥 ELITE DAILY")
            elite_label.setAlignment(Qt.AlignCenter)
            elite_label.setObjectName("systemLabel")
            self.objectives_container.addWidget(elite_label)

            obj = Objective(
                id=elite["id"],
                title=elite["title"],
                category=Category(elite["category"]),
                frequency=Frequency.WEEKLY,
                min_level=elite["min_level"],
                value=elite["value"]
            )

            row = QWidget()
            layout = QHBoxLayout(row)

            label = QLabel(f"{obj.title}  +{obj.value} EXP")
            button = QPushButton("VALIDER")

            button.clicked.connect(
                lambda _, o=obj: self._validate_elite_daily(o)
            )

            layout.addWidget(label)
            layout.addStretch()
            layout.addWidget(button)

            self.objectives_container.addWidget(row)


    # ------------------------------------------------------------------
    # ACTIONS
    # ------------------------------------------------------------------
    def _validate_daily(self, objective):
        if self.engine.validate_objective(objective):
            self.storage.save_stats(self.user.stats)
            self.storage.complete_daily_objective(objective.id)

            self.sound_exp.play()
            self._animate_exp_gain()

            # 🎁 BONUS D'ABORD
            bonus = self.engine.grant_daily_bonus_if_needed()
            if bonus:
                self._show_info_popup(
                    "🎉 Daily complétées",
                    f"Bonus +{bonus} EXP"
                )
                self.sound_level_up.play()

            # 🏆 ACHIEVEMENTS ENSUITE
            self._check_achievements()

            self.refresh_dashboard()


    def _validate_elite_daily(self, objective):
        if self.engine.validate_objective(objective):
            self.storage.save_stats(self.user.stats)
            self.storage.complete_elite_daily()

            self.sound_level_up.play()
            self._animate_level_up()
            self._check_achievements()

            self._show_info_popup(
                "🔥 Elite Daily complétée",
                f"+{objective.value} EXP"
            )

            self.refresh_dashboard()



    # -------------------------
    # ACHIEVEMENTS
    # -------------------------
    def _achievement_conditions(self):
        """
        Conditions de déblocage des achievements
        Doit matcher EXACTEMENT achievements_window.py
        """
        stats = self.user.stats
        level = stats.get_level()

        return {
            # publics
            1: stats.total_validations >= 1,
            2: stats.total_validations >= 5,
            3: stats.current_streak >= 3,
            4: stats.total_validations >= 25,
            5: level >= 5,
            6: level >= 10,

            # secrets
            100: level >= 7,
            101: stats.validations_today >= 3,
            102: stats.current_streak >= 7,
            103: stats.combo_validations >= 5,
        }
    
    def _achievement_rarity(self, ach_id: int) -> str:
        """
        Rareté d'un achievement
        Doit matcher achievements_window.py
        """
        if ach_id >= 100:
            return "legendary"
        if ach_id in (3, 4, 5):
            return "rare"
        return "common"

    def _check_achievements(self):
        """
        Vérifie et débloque les achievements
        Basé sur la liste officielle achievements_window.py
        """
        conditions = self._achievement_conditions()

        for ach_id, unlocked in conditions.items():
            if unlocked and not self.storage.is_achievement_unlocked(ach_id):
                self.storage.unlock_achievement(ach_id)

                rarity = self._achievement_rarity(ach_id)

                # 🔥 LÉGENDAIRE → écran spécial
                if rarity == "legendary":
                    self._show_legendary_screen("AWAKENING")
                else:
                    self._show_achievement_popup(
                        "Achievement débloqué",
                        "Consulte la liste des achievements",
                        rarity
                    )

    def _show_achievement_popup(self, title: str, description: str, rarity: str):
        """
        Popup d'achievement avec animation selon rareté
        """

        # Nettoyage ancien popup
        if self._achievement_popup is not None:
            self._achievement_popup.deleteLater()
            self._achievement_popup = None

        popup = QLabel(f"🏆 {title}\n{description}", self)
        popup.setAlignment(Qt.AlignCenter)

        border_color = {
            "common": "#9aa0b5",
            "rare": "#7f5af0",
            "legendary": "#f5c542"
        }.get(rarity, "#9aa0b5")

        popup.setStyleSheet(f"""
        QLabel {{
            background-color: #1a1f36;
            border: 2px solid {border_color};
            border-radius: 10px;
            padding: 14px;
            color: white;
            font-size: 14px;
        }}
        """)

        popup.setFixedSize(320, 90)
        popup.move(
            (self.width() - popup.width()) // 2,
            50
        )
        popup.show()

        self._achievement_popup = popup

        # Animation selon rareté
        if rarity == "common":
            self._animate_common_popup(popup)
        elif rarity == "rare":
            self._animate_rare_popup(popup)

    # -------------------------
    # INFO POPUP
    # -------------------------
    def _show_info_popup(self, title: str, message: str):
        """
        Popup simple d'information (cooldown, info système, etc.)
        """
        popup = QLabel(f"{title}\n{message}", self)
        popup.setAlignment(Qt.AlignCenter)

        popup.setStyleSheet("""
        QLabel {
            background-color: #1a1f36;
            border: 2px solid #7f5af0;
            border-radius: 10px;
            padding: 14px;
            color: white;
            font-size: 14px;
        }
        """)

        popup.setFixedSize(340, 90)
        popup.move(
            (self.width() - popup.width()) // 2,
            120
        )
        popup.show()

        # Fade out automatique
        fade = QPropertyAnimation(popup, b"windowOpacity", self)
        fade.setDuration(2200)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.finished.connect(popup.deleteLater)
        fade.start()

        self._info_popup_anim = fade


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

    # -------------------------
    # LEGENDARY ANIMATION
    # -------------------------
    def _show_legendary_screen(self, title: str):
        """
        Affiche une animation plein écran pour événements légendaires
        """
        overlay = QWidget(self)
        overlay.setAttribute(Qt.WA_DeleteOnClose)
        overlay.setGeometry(self.rect())
        overlay.setStyleSheet("""
        QWidget {
            background-color: rgba(11, 15, 26, 0.96);
        }
        """)

        layout = QVBoxLayout(overlay)
        layout.setAlignment(Qt.AlignCenter)

        label = QLabel(title)
        label.setAlignment(Qt.AlignCenter)
        label.setStyleSheet("""
        QLabel {
            color: #7f5af0;
            font-size: 42px;
            font-weight: bold;
            letter-spacing: 6px;
        }
        """)

        glow = QGraphicsDropShadowEffect(self)
        glow.setColor(QColor("#7f5af0"))
        glow.setBlurRadius(0)
        glow.setOffset(0)
        label.setGraphicsEffect(glow)

        layout.addWidget(label)
        overlay.show()

        # Glow animation
        anim = QPropertyAnimation(glow, b"blurRadius")
        anim.setDuration(900)
        anim.setStartValue(0)
        anim.setEndValue(60)
        anim.setEasingCurve(QEasingCurve.OutBack)

        anim_back = QPropertyAnimation(glow, b"blurRadius")
        anim_back.setDuration(1200)
        anim_back.setStartValue(60)
        anim_back.setEndValue(0)
        anim_back.setEasingCurve(QEasingCurve.InOutCubic)

        # Fade out
        fade = QPropertyAnimation(overlay, b"windowOpacity")
        fade.setDuration(1600)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.finished.connect(overlay.close)

        anim.start()
        anim_back.start()
        fade.start()

        self._legendary_anim = anim
        self._legendary_anim_back = anim_back
        self._legendary_fade = fade

        # Son légendaire (si présent)
        try:
            from PySide6.QtMultimedia import QSoundEffect
            sfx = QSoundEffect(self)
            sfx.setSource(QUrl.fromLocalFile("assets/sounds/legendary.wav"))
            sfx.setVolume(0 if self._muted else self._volume)
            sfx.play()
            self._legendary_sfx = sfx
        except Exception:
            pass

    def _animate_common_popup(self, popup: QLabel):
        anim = QPropertyAnimation(popup, b"windowOpacity", self)
        anim.setDuration(2200)
        anim.setStartValue(1.0)
        anim.setEndValue(0.0)
        anim.finished.connect(popup.deleteLater)
        anim.finished.connect(lambda: setattr(self, "_achievement_popup", None))
        anim.start()

        self._achievement_anim = anim
    
    def _animate_rare_popup(self, popup: QLabel):
        # Glow
        glow = QGraphicsDropShadowEffect(self)
        glow.setColor(QColor("#7f5af0"))
        glow.setBlurRadius(0)
        glow.setOffset(0)
        popup.setGraphicsEffect(glow)

        glow_anim = QPropertyAnimation(glow, b"blurRadius", self)
        glow_anim.setDuration(500)
        glow_anim.setStartValue(0)
        glow_anim.setEndValue(30)
        glow_anim.setEasingCurve(QEasingCurve.OutCubic)

        # Fade
        fade = QPropertyAnimation(popup, b"windowOpacity", self)
        fade.setDuration(2800)
        fade.setStartValue(1.0)
        fade.setEndValue(0.0)
        fade.finished.connect(popup.deleteLater)
        fade.finished.connect(lambda: setattr(self, "_achievement_popup", None))

        glow_anim.start()
        fade.start()

        self._achievement_anim = glow_anim
        self._achievement_fade = fade
    
    # -------------------------
    # TIMER
    # -------------------------
    def _on_daily_timer_tick(self):
        """
        Tick du timer daily (toutes les minutes)
        - met à jour le countdown
        - détecte le nouveau jour
        """
        self._update_daily_timer()

        today = datetime.now().date()
        if today != self._last_daily_date:
            self._last_daily_date = today
            self._on_new_day()

    def _update_daily_timer(self):
        now = datetime.now()
        tomorrow = (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        remaining = tomorrow - now
        seconds = int(remaining.total_seconds())
        hours, remainder = divmod(seconds, 3600)
        minutes = remainder // 60

        self.daily_timer_label.setText(
            f"⏳ Nouvelles Daily Quests dans {hours:02d}h {minutes:02d}m"
        )

        # 🔥 Glow si < 1h
        if hours < 1:
            self.daily_timer_label.setStyleSheet(
                "color: #f5c542; font-weight: bold;"
            )
        else:
            self.daily_timer_label.setStyleSheet(
                "color: #b8b8d1;"
            )

    def _on_new_day(self):
        """
        Appelé automatiquement à minuit
        """
        # Regénération des daily
        level = self.user.stats.get_level()
        self.storage.generate_daily_pool(level, count=3)

        # Feedback visuel
        self._show_info_popup(
            "🌅 Nouveau jour",
            "Nouvelles Daily Quests disponibles"
        )

        # Refresh UI
        self.refresh_dashboard()



