from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.master.string import String


class StringRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, string: String) -> String:
        self.db.add(string)
        self.db.commit()
        self.db.refresh(string)
        return string

    def update(self, string: String) -> String:
        self.db.commit()
        self.db.refresh(string)
        return string

    def delete(self, string: String) -> None:
        self.db.delete(string)
        self.db.commit()

    def find_by_id(self, string_id: int) -> String | None:
        return self.db.query(String).filter(String.id == string_id).first()

    def find_by_code(self, code: str) -> String | None:
        return self.db.query(String).filter(String.code == code).first()

    def find_all(self) -> Sequence[String]:
        return self.db.query(String).all()

    def find_by_inverter(self, inverter_id: int) -> Sequence[String]:
        return self.db.query(String).filter(String.inverter_id == inverter_id).all()
