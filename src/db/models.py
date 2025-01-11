import enum

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    func,
)
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import relationship

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

    portfolio = Column(Integer, nullable=True)
    trades = Column(Integer, nullable=True)
    profit = Column(Float, nullable=True)
    badges = Column(ARRAY(String), nullable=True)

    watch = Column(String, server_default="new")

    logs = relationship("LogOrm", back_populates="user")

    def __str__(self) -> str:
        return self.username


class LogOrm(Model):
    __tablename__ = "log"

    id = Column(Integer, primary_key=True, index=True)
    app_id = Column(Integer, ForeignKey("vendors.id"))
    app = relationship(VendorOrm, back_populates="logs")
    text = Column(String)
    time = Column(DateTime)
    created_at = Column(DateTime, default=func.now())
    user_id = Column(Integer, ForeignKey("traders.id"))
    user = relationship(TraderOrm, back_populates="")
    main_server = Column(Boolean)
    price = Column(Float)
    currency = Column(String)
    operation = Column(String)
    ticker = Column(String)
