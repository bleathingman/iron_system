import sys

# =========================
# CLI MODE (DEV / TEST)
# =========================
def run_cli():
    from core.objective import Objective, Frequency
    from core.user import User
    from core.storage import Storage
    from core.engine import Engine

    storage = Storage()
    user = User()
    user.stats = storage.load_stats()

    engine = Engine(user, storage)

    obj = Objective(
        id=1,
        title="Workout",
        frequency=Frequency.DAILY,
        value=20
    )

    success = engine.validate_objective(obj)
    storage.save_stats(user.stats)

    print("VALIDATED:", success)
    print("POINTS:", user.stats.total_points)
    print("STREAK:", user.stats.current_streak)
    print("BEST STREAK:", user.stats.best_streak)


# =========================
# UI MODE (PRODUCTION)
# =========================
def run_ui():
    from PySide6.QtWidgets import QApplication
    from PySide6.QtGui import QPalette, QColor
    from PySide6.QtCore import Qt

    from ui.main_window import MainWindow

    app = QApplication(sys.argv)

    # =========================
    # FORCE DARK PALETTE (ANTI THEME LINUX)
    # =========================
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#0b0f1a"))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor("#0b0f1a"))
    palette.setColor(QPalette.AlternateBase, QColor("#1a1f36"))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor("#1a1f36"))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.Highlight, QColor("#7f5af0"))
    palette.setColor(QPalette.HighlightedText, Qt.white)

    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


# =========================
# ENTRY POINT
# =========================
if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        run_ui()
