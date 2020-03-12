from datetime import timedelta, datetime
import pytz


# https://en.wikipedia.org/wiki/List_of_tz_database_time_zones

class Time:
    def __init__(self, zone):
        self.tz = pytz.timezone(zone)

    def get_time(self, time):
        return self.tz.localize(time).astimezone(pytz.timezone("UTC"))

    def get_reverse_time(self, time):
        return pytz.timezone("UTC").localize(time).astimezone(self.tz)

    def seconds_until(self, hour, minute):
        now = pytz.timezone("UTC").localize(datetime.utcnow())
        return (self.get_time(
            datetime(year=now.year, month=now.month, day=now.day, hour=hour, minute=minute)) - now).seconds

    def get_next_time_string(self, hour, minute):
        current_time = pytz.timezone("UTC").localize(datetime.utcnow()).astimezone(self.tz)
        next_time = current_time.replace(hour=hour, minute=minute, second=0, microsecond=0)

        if next_time < current_time:
            next_time = next_time.replace(day=next_time.day + 1)

        return next_time.strftime("%b %d %Y %H:%M:%S %Z")

    def get_time_in_string(self, hour, minute):
        return self.get_reverse_time(datetime.utcnow() + timedelta(hours=hour, minutes=minute)).strftime(
            "%b %d %Y %H:%M:%S %Z")
