from datetime import timedelta
from datetime import datetime

class Time:
    def __init__(self, diff):
        self.delta = timedelta(hours=diff)

    def get_time(self):
        return datetime.today() + self.delta
