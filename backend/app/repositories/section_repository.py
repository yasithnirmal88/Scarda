from collections.abc import Sequence

from sqlalchemy.orm import Session

from app.models.master.section import Section


class SectionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def create(self, section: Section) -> Section:
        self.db.add(section)
        self.db.commit()
        self.db.refresh(section)
        return section

    def update(self, section: Section) -> Section:
        self.db.commit()
        self.db.refresh(section)
        return section

    def delete(self, section: Section) -> None:
        self.db.delete(section)
        self.db.commit()

    def find_by_id(self, section_id: int) -> Section | None:
        return self.db.query(Section).filter(Section.id == section_id).first()

    def find_by_code(self, code: str) -> Section | None:
        return self.db.query(Section).filter(Section.code == code).first()

    def find_all(self) -> Sequence[Section]:
        return self.db.query(Section).all()
