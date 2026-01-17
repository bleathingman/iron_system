from datetime import date


class Progression:
    def __init__(self, stats):
        self.stats = stats

    def calculate_level(self):
        # 100 points = 1 niveau
        self.stats.level = (self.stats.total_points // 100) + 1

    def daily_progress(self, points_today: int, daily_goal: int = 100) -> int:
        return min(100, int((points_today / daily_goal) * 100))
