import database as db
from datetime import datetime

class ChallengeManager:
    def __init__(self, start_date_str, duration=75):
        self.start_date_str = start_date_str
        self.start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        self.duration = duration

    def get_current_day_number(self):
        # 75 Hard Rule: Streak-based day numbering
        streak, streak_start, _ = db.get_streak_info(self.start_date_str)
        # The current day is the streak + 1 (unless it's over 75)
        day = streak + 1
        return day

    def is_challenge_active(self):
        day = self.get_current_day_number()
        return 1 <= day <= self.duration

    def get_progress_percentage(self):
        day = self.get_current_day_number()
        if day < 1: return 0
        if day > self.duration: return 100
        # Progress is (current day - 1) / duration for completed days
        # But usually challenge day 1 means 0% done until day 1 is finished.
        # We'll stick to (streak / duration) * 100
        streak, _, _ = db.get_streak_info(self.start_date_str)
        return (streak / self.duration) * 100

    @staticmethod
    def get_daily_tasks():
        return [
            {"id": "workout_1", "label": "Workout 1 (45 mins)"},
            {"id": "workout_2", "label": "Workout 2 (45 mins)"},
            {"id": "outdoor", "label": "Outdoor Workout"},
            {"id": "diet", "label": "Follow Diet / No Cheats"},
            {"id": "water", "label": "Drink 1 Gallon Water"},
            {"id": "reading", "label": "Read 10 Pages"},
            {"id": "photo", "label": "Progress Photo"},
        ]
