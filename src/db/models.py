import enum
from datetime import datetime, timedelta

import pytz
from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
    select,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import relationship
from sqlalchemy.types import TIMESTAMP

from src.db.database import Model, Session, SessionLocal


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
    profit = Column(Float, default=0)
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

    ticker_id = Column(Integer, ForeignKey("tickers.id"))
    ticker = relationship("TickerOrm", back_populates="logs")


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


async def get_log_count(ticker_id: int, db=SessionLocal()):
    query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id)
    log_count = await db.execute(query)
    log_count = log_count.scalars().first()

    return log_count


class TickerOrm(Model):
    __tablename__ = "tickers"

    id = Column(Integer, index=True, primary_key=True)
    slug = Column(String, index=True)
    name = Column(String, nullable=True)
    lot = Column(Integer, default=0)
    type = Column(String, nullable=True)

    logs = relationship("LogOrm")

    def __str__(self) -> str:
        return self.slug

    @hybrid_property
    def last_trade_price(self, db=Session()) -> int:
        ticker_id = self.id
        query = select(LogOrm.price).where(LogOrm.ticker_id == ticker_id).order_by(LogOrm.id.desc())
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        return log_count

    @last_trade_price.expression
    def last_trade_price(self, db=Session()) -> int:
        ticker_id = self.id
        return select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id)

    @hybrid_property
    def last_hour(self, db=Session()) -> int:
        current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)
        last_our_time = current_time - timedelta(hours=1)
        ticker_id = self.id
        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time)
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        return log_count

    @last_hour.expression
    def last_hour(self, db=Session()) -> int:
        current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)
        last_our_time = current_time - timedelta(hours=1)
        ticker_id = self.id
        return select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time)

    @hybrid_property
    def last_day(self, db=Session()) -> int:
        current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)
        last_our_time = current_time - timedelta(hours=24)
        ticker_id = self.id
        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time)
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        return log_count

    @last_day.expression
    def last_day(self, db=Session()) -> int:
        current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)
        last_our_time = current_time - timedelta(hours=24)
        ticker_id = self.id
        return select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time)

    @hybrid_property
    def last_week(self, db=Session()) -> int:
        current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)
        last_our_time = current_time - timedelta(hours=24 * 7)
        ticker_id = self.id
        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time)
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        return log_count

    @last_week.expression
    def last_week(self, db=Session()) -> int:
        current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)
        last_our_time = current_time - timedelta(hours=24 * 7)
        ticker_id = self.id
        return select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time)

    @hybrid_property
    def last_month(self, db=Session()) -> int:
        current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)
        last_our_time = current_time - timedelta(days=30)
        ticker_id = self.id

        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time)
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        return log_count

    @last_month.expression
    def last_month(self, db=Session()) -> int:
        current_time = datetime.now(pytz.timezone("Europe/Moscow")).astimezone(pytz.utc)
        last_our_time = current_time - timedelta(days=30)
        ticker_id = self.id

        return select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id, LogOrm.time >= last_our_time)

    @hybrid_property
    def trades(self, db=Session()) -> int:
        ticker_id = self.id

        query = select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id)
        log_count = db.execute(query)
        log_count = log_count.scalars().first()

        return log_count

    @trades.expression
    def trades(self, db=Session()) -> int:
        ticker_id = self.id

        return select(func.count(LogOrm.id)).where(LogOrm.ticker_id == ticker_id)
