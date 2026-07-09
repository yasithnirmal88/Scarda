from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.telemetry.alert import Alert


class AlertRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, alert: Alert) -> Alert:
        self.db.add(alert)
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def update(self, alert: Alert) -> Alert:
        self.db.commit()
        self.db.refresh(alert)
        return alert

    def delete(self, alert: Alert) -> None:
        self.db.delete(alert)
        self.db.commit()

    def find_by_id(self, alert_id: int) -> Alert | None:
        return self.db.query(Alert).filter(Alert.id == alert_id).first()

    def find_all(self) -> Sequence[Alert]:
        return self.db.query(Alert).all()
