from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QLabel,
    QSlider, QPushButton, QHBoxLayout
)
from PySide6.QtCore import Qt


class SettingsDialog(QDialog):
    """
    Fenêtre Paramètres
    Gère le volume et le mute des sons SYSTEM
    """

    def __init__(self, get_volume, set_volume, get_mute, set_mute, parent=None):
        super().__init__(parent)

        self.get_volume = get_volume
        self.set_volume = set_volume
        self.get_mute = get_mute
        self.set_mute = set_mute

        self.setWindowTitle("Paramètres")
        self.setFixedSize(300, 200)

        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout()

        # ===== VOLUME =====
        self.volume_label = QLabel("Volume SYSTEM")
        self.volume_label.setAlignment(Qt.AlignCenter)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(int(self.get_volume() * 100))
        self.volume_slider.valueChanged.connect(
            lambda v: self.set_volume(v / 100)
        )

        # ===== MUTE =====
        self.mute_button = QPushButton()
        self._update_mute_text()
        self.mute_button.clicked.connect(self._toggle_mute)

        layout.addWidget(self.volume_label)
        layout.addWidget(self.volume_slider)
        layout.addSpacing(15)
        layout.addWidget(self.mute_button)

        self.setLayout(layout)

    def _toggle_mute(self):
        self.set_mute(not self.get_mute())
        self._update_mute_text()

    def _update_mute_text(self):
        self.mute_button.setText(
            "🔇 Son coupé" if self.get_mute() else "🔊 Son actif"
        )
