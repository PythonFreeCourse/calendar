from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.database.database import Base
from sqlalchemy.orm import Session


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    full_name = Column(String)
    description = Column(String, default="Happy new user!")
    avatar = Column(String, default="profile.png")

    is_active = Column(Boolean, default=True)

    events = relationship(
        "Event", cascade="all, delete", back_populates="owner")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    owner = relationship("User", back_populates="events")


class Category(Base):
    __tablename__ = "categories"

    __table_args__ = (
        UniqueConstraint('user_id', 'name', 'color'),
    )
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    @staticmethod
    def create(db_session: Session, name: str, color: str, user_id: int):
        print(Base.metadata.tables.keys())
        try:
            category = Category(name=name, color=color, user_id=user_id)
            db_session.add(category)
            db_session.flush()
            db_session.commit()
            db_session.refresh(category)
            return category
        except Exception as e:
            raise e

    def to_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self):
        return f'<Category {self.id} {self.name} {self.color}>'
