from enum import StrEnum


class ContactChannel(StrEnum):
    tg = "Телеграм"
    phone = "Мобильный"
    
    @classmethod
    @property
    def values_list(cls):
        return [
            (channel.value, channel.value) for channel in cls
        ]