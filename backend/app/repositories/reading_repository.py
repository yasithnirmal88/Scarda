from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.string_reading import StringReading


class ReadingRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, reading: StringReading) -> StringReading:
        self.db.add(reading)
        self.db.commit()
        self.db.refresh(reading)
        return reading

    def find_by_id(self, reading_id: int) -> StringReading | None:
        return self.db.query(StringReading).filter(StringReading.id == reading_id).first()

    def find_all(self) -> Sequence[StringReading]:
        return self.db.query(StringReading).all()

    def find_by_string(self, string_id: int) -> Sequence[StringReading]:
        return self.db.query(StringReading).filter(StringReading.string_id == string_id).all()
