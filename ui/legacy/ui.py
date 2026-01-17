def get_rank(level: int):
    """
    Retourne le rank et la couleur associée
    Ranks tous les 10 niveaux
    Thème musculation / progression physique
    """

    if level >= 90:
        return "LÉGENDE", "#ff3b3b"
    elif level >= 80:
        return "HÉROS", "#ff6f3b"
    elif level >= 70:
        return "TITAN", "#c03bff"
    elif level >= 60:
        return "COLOSSUS", "#3b6cff"
    elif level >= 50:
        return "VÉTÉRAN", "#3bbfff"
    elif level >= 40:
        return "PUISSANCE", "#3bffb3"
    elif level >= 30:
        return "FORCE", "#6bff3b"
    elif level >= 20:
        return "ATHLÈTE", "#b3ff3b"
    elif level >= 10:
        return "APPRENTI", "#ffd93b"
    else:
        return "INITIÉ", "#cfcfcf"


def apply_style(widget, level=1):
    rank_name, xp_color = get_rank(level)

    widget.setStyleSheet(f"""
    /* =========================
       GLOBAL
       ========================= */
    QWidget {{
        background-color: #1e1e1e;
        color: #e6e6e6;
        font-size: 13px;
        font-family: Segoe UI, Arial, sans-serif;
    }}

    QLabel {{
        background: transparent;
    }}

    /* =========================
       BUTTONS
       ========================= */
    QPushButton {{
        background-color: #2f2f2f;
        border: 1px solid #444;
        border-radius: 8px;
        padding: 8px;
    }}

    QPushButton:hover {{
        background-color: #3a3a3a;
    }}

    QPushButton:disabled {{
        background-color: #1f1f1f;
        color: #777;
        border: 1px solid #333;
    }}

    /* =========================
       PROGRESS BAR (XP)
       ========================= */
    QProgressBar {{
        background-color: #1b1b1b;
        border: 1px solid #444;
        border-radius: 8px;
        height: 14px;
        text-align: center;
        color: #e6e6e6;
    }}

    QProgressBar::chunk {{
        background-color: {xp_color};
        border-radius: 6px;
    }}

    /* =========================
       XP TEXT
       ========================= */
    QLabel[xp="true"] {{
        color: {xp_color};
        font-weight: bold;
    }}

    /* =========================
       RANK TEXT
       ========================= */
    QLabel[rank="true"] {{
        color: {xp_color};
        font-weight: bold;
        letter-spacing: 1px;
    }}

    /* =========================
       SCROLLBAR
       ========================= */
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 4px 2px;
    }}

    QScrollBar::handle:vertical {{
        background: #555;
        border-radius: 4px;
        min-height: 30px;
    }}

    QScrollBar::handle:vertical:hover {{
        background: #777;
    }}

    QScrollBar::add-line:vertical,
    QScrollBar::sub-line:vertical {{
        height: 0px;
    }}

    QScrollBar::add-page:vertical,
    QScrollBar::sub-page:vertical {{
        background: none;
    }}
    """)
