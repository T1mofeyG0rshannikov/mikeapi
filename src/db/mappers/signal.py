from src.db.models.models import DealOrm


def from_orm_to_signal(signal: DealOrm) -> str:
    return f'''{signal.id}, {signal.user.code}, {signal.ticker}, {signal.operation}, {signal.time.date().strftime("%d.%m.%Y")}, {signal.time.time().strftime("%H:%M:%S")}, {signal.price}, {signal.currency}'''