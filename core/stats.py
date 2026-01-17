from dataclasses import dataclass


@dataclass
class Stats:
    current_streak: int = 0
    best_streak: int = 0
    total_validations: int = 0
    total_points: int = 0  # EXP totale

    def get_level(self) -> int:
        # 100 EXP = 1 niveau
        return (self.total_points // 100) + 1
