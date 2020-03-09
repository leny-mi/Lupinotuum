from datetime import timedelta, datetime
from pytz import timezone
import pytz

#https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

class Time:
    def __init__(self, zone):
        self.tz = pytz.timezone(zone)

    def get_time(self, time):
        return self.tz.localize(time).astimezone(timezone("UTC"))

    def get_reverse_time(self, time):
        return timezone("UTC").localize(time).astimezone(self.tz)

    def seconds_until(self, hour, minute):
        now = timezone("UTC").localize(datetime.utcnow())
        return (self.get_time(datetime(year = now.year, month = now.month, day = now.day, hour = hour, minute = minute)) - now).seconds
