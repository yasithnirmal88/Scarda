from sqlalchemy.orm import Session

from app.models.inverter import Inverter
from app.repositories.base import BaseRepository


class InverterRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all(self) -> list[Inverter]:
        return self.db.query(Inverter).all()

    def get_by_id(self, inverter_id: int) -> Inverter | None:
        return self.db.query(Inverter).filter(Inverter.id == inverter_id).first()

    def get_by_section(self, section_id: int) -> list[Inverter]:
        return self.db.query(Inverter).filter(Inverter.section_id == section_id).all()
