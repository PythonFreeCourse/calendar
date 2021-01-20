from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, \
    String, UniqueConstraint
from sqlalchemy.orm import relationship, Session

from app.database.database import Base
from app.database.database import Base
from sqlalchemy.orm import Session


class UserEvent(Base):
    __tablename__ = "user_event"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    event_id = Column('event_id', Integer, ForeignKey('events.id'))

    events = relationship("Event", back_populates="participants")
    participants = relationship("User", back_populates="events")

    def __repr__(self):
        return f'<UserEvent ({self.participants}, {self.events})>'


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String)
    description = Column(String, default="Happy new user!")
    avatar = Column(String, default="profile.png")
    is_active = Column(Boolean, default=False)

    events = relationship("UserEvent", back_populates="participants")

    def __repr__(self):
        return f'<User {self.id}>'


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    content = Column(String)
    location = Column(String)

    owner = relationship("User")
    owner_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    color = Column(String, nullable=True)

    participants = relationship("UserEvent", back_populates="events")

    def __repr__(self):
        return f'<Event {self.id}>'


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


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False, default="unread")
    recipient_id = Column(Integer, ForeignKey("users.id"))
    event_id = Column(Integer, ForeignKey("events.id"))
    creation = Column(DateTime, default=datetime.now)

    recipient = relationship("User")
    event = relationship("Event")

    def __repr__(self):
        return (
            f'<Invitation '
            f'({self.event.owner}'
            f'to {self.recipient})>'
        )


class Category(Base):
    __tablename__ = "categories"

    __table_args__ = (
        UniqueConstraint('user_id', 'name', 'color'),
    )
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    @classmethod
    def create(cls, db_session: Session, name: str, color: str, user_id: int):
        try:
            category = cls(name=name, color=color, user_id=user_id)
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
