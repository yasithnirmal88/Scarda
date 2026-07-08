from sqlalchemy.orm import Session

from app.models.alert import Alert
from app.repositories.base import BaseRepository


class AlertRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all(self) -> list[Alert]:
        return self.db.query(Alert).all()

    def get_by_id(self, alert_id: int) -> Alert | None:
        return self.db.query(Alert).filter(Alert.id == alert_id).first()
