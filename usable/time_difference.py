from datetime import timedelta, datetime
from pytz import timezone
import pytz

#https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

class Time:
    def __init__(self, zone):
        self.tz = pytz.timezone(zone)

    def get_time(self, time):
        return self.tz.localize(time).astimezone(pytz.utc)
