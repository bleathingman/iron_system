from dataclasses import dataclass


@dataclass
class Achievement:
    """
    Représente un succès débloquable
    """
    id: int
    title: str
    description: str
