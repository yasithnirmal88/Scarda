from sqlalchemy.orm import Session

from app.models.string_reading import StringReading
from app.repositories.base import BaseRepository


class StringReadingRepository(BaseRepository):
    def __init__(self, db: Session):
        super().__init__(db)

    def get_all(self) -> list[StringReading]:
        return self.db.query(StringReading).all()

    def get_by_id(self, reading_id: int) -> StringReading | None:
        return self.db.query(StringReading).filter(StringReading.id == reading_id).first()

    def get_by_string(self, string_id: int) -> list[StringReading]:
        return self.db.query(StringReading).filter(StringReading.string_id == string_id).all()
