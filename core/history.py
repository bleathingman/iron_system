from dataclasses import dataclass
from datetime import datetime


@dataclass
class HistoryEntry:
    timestamp: datetime
    action: str
    impact: int  # points / streak impact
