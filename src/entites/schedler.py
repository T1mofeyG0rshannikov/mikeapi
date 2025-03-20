from dataclasses import dataclass
from datetime import datetime

from src.entites.common import WEEKDAYS_LIST, WeekDays


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
        return list(range(WEEKDAYS_LIST.index(self.day_l), WEEKDAYS_LIST.index(self.day_r)+1))

    @property
    def time_l(self):
        return datetime.strptime(f"{self.hour_l}:{self.minute_l}", '%H:%M').time()
          
    @property
    def time_r(self):
        return datetime.strptime(f"{self.hour_r}:{self.minute_r}", '%H:%M').time()
