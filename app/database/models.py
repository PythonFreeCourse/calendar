from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from sqlalchemy import (DDL, Boolean, Column, DateTime, ForeignKey, Index,
                        Integer, String, event, UniqueConstraint)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import relationship, Session

from app.config import PSQL_ENVIRONMENT
from app.database.database import Base
from app.dependencies import logger


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
    language = Column(String)
    description = Column(String, default="Happy new user!")
    avatar = Column(String, default="profile.png")
    telegram_id = Column(String, unique=True)
    is_active = Column(Boolean, default=False)

    events = relationship("UserEvent", back_populates="participants")
    comments = relationship("Comment", back_populates="user")

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
    color = Column(String, nullable=True)

    owner_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    owner = relationship("User")
    participants = relationship("UserEvent", back_populates="events")
    comments = relationship("Comment", back_populates="event")

    # PostgreSQL
    if PSQL_ENVIRONMENT:
        events_tsv = Column(TSVECTOR)
        __table_args__ = (Index(
            'events_tsv_idx',
            'events_tsv',
            postgresql_using='gin'),
        )

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
    def create(db_session: Session, name: str, color: str,
               user_id: int) -> Category:
        try:
            category = Category(name=name, color=color, user_id=user_id)
            db_session.add(category)
            db_session.flush()
            db_session.commit()
            db_session.refresh(category)
        except (SQLAlchemyError, IntegrityError) as e:
            logger.error(f"Failed to create category: {e}")
            raise e
        else:
            return category

    def to_dict(self) -> Dict[str, Any]:
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def __repr__(self) -> str:
        return f'<Category {self.id} {self.name} {self.color}>'


class PSQLEnvironmentError(Exception):
    pass


# PostgreSQL
if PSQL_ENVIRONMENT:
    trigger_snippet = DDL("""
    CREATE TRIGGER ix_events_tsv_update BEFORE INSERT OR UPDATE
    ON events
    FOR EACH ROW EXECUTE PROCEDURE
    tsvector_update_trigger(events_tsv,'pg_catalog.english','title','content')
    """)

    event.listen(
        Event.__table__,
        'after_create',
        trigger_snippet.execute_if(dialect='postgresql')
    )


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


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    author = Column(String)


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False)
    content = Column(String, nullable=False)
    time = Column(DateTime, nullable=False)

    user = relationship("User", back_populates="comments")
    event = relationship("Event", back_populates="comments")

    def __repr__(self):
        return f'<Comment {self.id}>'


class Zodiac(Base):
    __tablename__ = "zodiac-signs"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_month = Column(Integer, nullable=False)
    start_day_in_month = Column(Integer, nullable=False)
    end_month = Column(Integer, nullable=False)
    end_day_in_month = Column(Integer, nullable=False)

    def __repr__(self):
        return (
            f'<Zodiac '
            f'{self.name} '
            f'{self.start_day_in_month}/{self.start_month}-'
            f'{self.end_day_in_month}/{self.end_month}>'
        )
