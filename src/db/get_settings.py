from sqlalchemy import select
from src.db.models.models import SettingsOrm
from src.db.database import Session


def get_settings():
    db = Session()
    return db.execute(select(SettingsOrm)).scalar()