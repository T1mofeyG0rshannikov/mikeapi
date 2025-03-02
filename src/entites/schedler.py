from enum import StrEnum
from dataclasses import dataclass
from time import time


class WeekDays(StrEnum):
    Monday="пн"
    Tuesday="вт"
    Wednesday="ср"
    Thursday="чт"
    Friday="пт"
    Saturday="сб"
    Sunday="вс"
    
    @classmethod
    @property
    def values_list(cls):
        return [
            (channel.value, channel.value) for channel in cls
        ]


WEEKDAYS_LIST = [
    day.value for day in WeekDays
]
from datetime import timedelta, datetime

@dataclass
class ScheduleRule:
    day_l: WeekDays
    day_r: WeekDays
    
    hour_l: int
    hour_r: int

    minute_l: int
    minute_r: int
    
    interval1: int
    interval2: int
    
    @property
    def weekrange(self) -> list[WeekDays]:
        today = datetime.now()
        
        WEEKDAYS_DICT = {
            "пн": today + timedelta(days=(0 - today.weekday()) % 7),  # Понедельник
            "вт": today + timedelta(days=(1 - today.weekday()) % 7),  # Вторник
            "ср": today + timedelta(days=(2 - today.weekday()) % 7),  # Среда
            "чт": today + timedelta(days=(3 - today.weekday()) % 7),  # Четверг
            "пт": today + timedelta(days=(4 - today.weekday()) % 7),  # Пятница
            "сб": today + timedelta(days=(5 - today.weekday()) % 7),  # Суббота
            "вс": today + timedelta(days=(6 - today.weekday()) % 7),  # Воскресенье
        }
        
        return list(range(WEEKDAYS_LIST.index(self.day_l), WEEKDAYS_LIST.index(self.day_r)+1))

        return [
            WEEKDAYS_DICT[day] for day in WEEKDAYS_LIST[WEEKDAYS_LIST.index(self.day_l):WEEKDAYS_LIST.index(self.day_r)+1]
        ]

    @property
    def time_l(self):
        return datetime.strptime(f"{self.hour_l}:{self.minute_l}", '%H:%M').time()
        return time(self.hour_l, self.minute_l)
          
    @property
    def time_r(self):
        return datetime.strptime(f"{self.hour_r}:{self.minute_r}", '%H:%M').time()
        return time(self.hour_r, self.minute_r) 