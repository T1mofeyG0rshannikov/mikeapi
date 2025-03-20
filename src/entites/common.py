from enum import StrEnum


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