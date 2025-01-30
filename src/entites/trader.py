from enum import StrEnum


class TraderWatch(StrEnum):
    on = "on"
    new = "new"
    off = "off"
    raw = "raw"
    bad = "bad"


class TraderStatus(StrEnum):
    active = "Активный"
    unactive = "Не активен"
    hidden = "Скрытый"
    blocked = "Заблокированный"
