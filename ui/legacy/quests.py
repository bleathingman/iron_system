def get_daily_quests(save):
    """
    Génère les quêtes du jour.
    Le jour 1 permet de passer niveau 2.
    Ensuite, l'XP ne garantit plus un level up quotidien.
    """

    level = save.get("level", 1)

    # =====================
    # JOUR 1 (ONBOARDING)
    # =====================
    if level == 1:
        quests = [
            ("Pompes", 10, 30),
            ("Abdos", 10, 30),
            ("Gainage (sec)", 60, 20),
            ("Marche (min)", 10, 20),
        ]

        return {
            name: {"value": value, "xp": xp}
            for name, value, xp in quests
        }

    # =====================
    # JOURS SUIVANTS
    # =====================
    quests = [
        # exercices de base
        ("Pompes", min(10 + level * 2, 50), 25),
        ("Abdos", min(10 + level * 2, 50), 25),

        # gainage (temps)
        ("Gainage (sec)", min(60 + level * 5, 180), 25),

        # marche (cardio doux)
        ("Marche (min)", min(10 + level * 2, 60), 20),
    ]

    # =====================
    # QUÊTE BONUS (PAS TOUS LES JOURS)
    # =====================
    if level >= 3:
        quests.append(
            ("Burpees", min(5 + level, 30), 25)
        )

    return {
        name: {"value": value, "xp": xp}
        for name, value, xp in quests
    }
