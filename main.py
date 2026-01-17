from core.objective import Objective, Frequency
from core.user import User
from core.storage import Storage
from core.engine import Engine

user = User()
storage = Storage()
engine = Engine(user, storage)

obj = Objective(
    id=1,
    title="Workout",
    frequency=Frequency.DAILY,
    value=20
)

success = engine.validate_objective(obj)

print("VALIDATED:", success)
print("POINTS:", user.stats.total_points)
print("STREAK:", user.stats.current_streak)
print("BEST STREAK:", user.stats.best_streak)
