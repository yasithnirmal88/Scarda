from sqlalchemy.orm import Session

from app.models.string import String
from app.repositories.base import BaseRepository


class StringRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all(self) -> list[String]:
        return self.db.query(String).all()

    def get_by_id(self, string_id: int) -> String | None:
        return self.db.query(String).filter(String.id == string_id).first()

    def get_by_inverter(self, inverter_id: int) -> list[String]:
        return self.db.query(String).filter(String.inverter_id == inverter_id).all()
