from datetime import datetime, timedelta
from enum import StrEnum

from src.entites.common import WEEKDAYS_LIST
from dataclasses import dataclass


class TraderWatch(StrEnum):
    on = "on"
    new = "new"
    off = "off"
    raw = "raw"
    bad = "bad"
    pre = "pre"


class TraderStatus(StrEnum):
    active = "Активный"
    unactive = "Не активен"
    hidden = "Скрытый"
    blocked = "Заблокирован"


class TradefBadge(StrEnum):
    verified = "Верифицирован"
    author = "Автор стратегии"
    Tchoice = "Выбор Т-Инвестиций"
    popular = "Популярный"
    helper = "Помощник пульса"


class LoadTraderAction(StrEnum):
    profiles = "profiles"
    subscribes = "subscribes"


class StatisticPeriodEnum(StrEnum):
    day = "День"
    week = "7 дней"
    month = "30 дней"
    three_months = "90 дней"
    
    @classmethod
    @property
    def list(cls) -> list[str]:
        return [
            channel for channel in cls
        ]


@dataclass
class StatisticPeriod:
    view: StatisticPeriodEnum
    
    @property
    def days(self) -> int:
        if self.view == StatisticPeriodEnum.day:
            return 1
        elif self.view == StatisticPeriodEnum.week:
            return 7
        elif self.view == StatisticPeriodEnum.month:
            return 30
        elif self.view == StatisticPeriodEnum.three_months:
            return 90
    
    def date_value(self, date: datetime) -> str:
        if self.view == StatisticPeriodEnum.day:
            return date.strftime("%d.%m.%Y")
        
        elif self.view == StatisticPeriodEnum.week:
            today_ind = date.weekday()
            last_day_ind = today_ind - 1
            if last_day_ind == -1:
                last_day_ind = 6
            
            return f'''{WEEKDAYS_LIST[today_ind]} {(date - timedelta(days=self.days)).strftime("%d.%m")} - {WEEKDAYS_LIST[last_day_ind]} {date.strftime("%d.%m")}'''
    
        return f'''{(date - timedelta(days=self.days)).strftime("%d.%m")} - {date.strftime("%d.%m")}'''
    
    def start_date(self, date: datetime = None) -> datetime:
        if date is None:
            date = datetime.today()
 
        return date - timedelta(days=self.days)