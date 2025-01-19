import enum
from datetime import datetime

import pytz
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Time,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from src.db.database import Model


class UrlEnum(str, enum.Enum):
    in_work = "Включен"
    unavailable = "Недоступен"
    error = "Сбой"
    failure = "Ошибка"


class VendorOrm(Model):
    __tablename__ = "vendors"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(String)
    auth_token = Column(String)
    logs = relationship("LogOrm", back_populates="app")
    traders = relationship("TraderOrm", back_populates="app")

    def __str__(self) -> str:
        return f"vendor({self.app_id})"


class APIURLSOrm(Model):
    __tablename__ = "main_url"

    id = Column(Integer, primary_key=True, index=True)
    main_url = Column(String)
    main_url_status = Column(Enum(UrlEnum, native_enum=False))
    reverse_url = Column(String)
    reverse_url_status = Column(Enum(UrlEnum, native_enum=False))


class UserOrm(Model):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String)
    email = Column(String, unique=True)
    hash_password = Column(String)
    is_superuser = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)

    def __str__(self) -> str:
        return self.username


class TraderOrm(Model):
    __tablename__ = "traders"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    code = Column(String, unique=True)

    status = Column(String, nullable=True)
    subscribes = Column(Integer, nullable=True)
    subscribers = Column(Integer, nullable=True)

    portfolio = Column(String, nullable=True)
    trades = Column(Integer, nullable=True)
    profit = Column(Float, nullable=True)
    badges = Column(ARRAY(String), nullable=True)

    watch = Column(String, server_default="new")
    count = Column(Integer, default=0)
    logs = relationship("LogOrm", back_populates="user")
    app_id = Column(Integer, ForeignKey("vendors.id"), nullable=True)
    app = relationship(VendorOrm, back_populates="traders")

    def __str__(self) -> str:
        return self.username


class LogOrm(Model):
    __tablename__ = "log"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("vendors.id"))
    app = relationship(VendorOrm, back_populates="logs")
    time = Column(TIMESTAMP(timezone=True), index=True)
    created_at = Column(TIMESTAMP(timezone=True), default=lambda: datetime.now(pytz.timezone("Europe/Moscow")))
    user_id = Column(Integer, ForeignKey("traders.id", ondelete="CASCADE"))
    user = relationship(TraderOrm, back_populates="")
    main_server = Column(Boolean)
    price = Column(Float)
    currency = Column(String)
    operation = Column(String)
    ticker = Column(String)


class LogActivityOrm(Model):
    __tablename__ = "logsactivity"

    id = Column(Integer, index=True, primary_key=True)
    date = Column(Date)

    hour00 = Column(Integer, default=0)
    hour01 = Column(Integer, default=0)
    hour02 = Column(Integer, default=0)
    hour03 = Column(Integer, default=0)
    hour04 = Column(Integer, default=0)
    hour05 = Column(Integer, default=0)
    hour06 = Column(Integer, default=0)
    hour07 = Column(Integer, default=0)
    hour08 = Column(Integer, default=0)
    hour09 = Column(Integer, default=0)
    hour10 = Column(Integer, default=0)
    hour11 = Column(Integer, default=0)
    hour12 = Column(Integer, default=0)
    hour13 = Column(Integer, default=0)
    hour14 = Column(Integer, default=0)
    hour15 = Column(Integer, default=0)
    hour16 = Column(Integer, default=0)
    hour17 = Column(Integer, default=0)
    hour18 = Column(Integer, default=0)
    hour19 = Column(Integer, default=0)
    hour20 = Column(Integer, default=0)
    hour21 = Column(Integer, default=0)
    hour22 = Column(Integer, default=0)
    hour23 = Column(Integer, default=0)

    last_day = Column(Integer, default=0)


class TickerOrm(Model):
    __tablename__ = "tickers"

    id = Column(Integer, index=True, primary_key=True)

    name = Column(String)
