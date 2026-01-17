from dataclasses import dataclass


@dataclass
class Stats:
    current_streak: int = 0
    best_streak: int = 0
    total_validations: int = 0
    total_points: int = 0  # EXP totale

    def get_level(self) -> int:
        return (self.total_points // 100) + 1

    def get_exp_in_level(self) -> int:
        return self.total_points % 100

    def get_exp_to_next_level(self) -> int:
        return 100 - self.get_exp_in_level()
