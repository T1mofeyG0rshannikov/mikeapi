from enum import StrEnum


class AlertChannels(StrEnum):
    tg = "Телеграм"
    sms = "СМС"
    all = "Телеграм+СМС"
    
    @classmethod
    @property
    def values_list(cls):
        return [
            (channel.value, channel.value) for channel in cls
        ]