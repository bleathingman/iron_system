from dataclasses import dataclass


@dataclass
class Stats:
    current_streak: int = 0
    best_streak: int = 0
    total_validations: int = 0
    total_points: int = 0
    level: int = 1
