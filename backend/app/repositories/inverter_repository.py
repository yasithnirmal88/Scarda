from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.inverter import Inverter


class InverterRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, inverter: Inverter) -> Inverter:
        self.db.add(inverter)
        self.db.commit()
        self.db.refresh(inverter)
        return inverter

    def update(self, inverter: Inverter) -> Inverter:
        self.db.commit()
        self.db.refresh(inverter)
        return inverter

    def delete(self, inverter: Inverter) -> None:
        self.db.delete(inverter)
        self.db.commit()

    def find_by_id(self, inverter_id: int) -> Inverter | None:
        return self.db.query(Inverter).filter(Inverter.id == inverter_id).first()

    def find_all(self) -> Sequence[Inverter]:
        return self.db.query(Inverter).all()

    def find_by_section(self, section_id: int) -> Sequence[Inverter]:
        return self.db.query(Inverter).filter(Inverter.section_id == section_id).all()
