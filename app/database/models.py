from datetime import datetime

from app.config import PSQL_ENVIRONMENT
from app.database.database import Base
from sqlalchemy import (DDL, Boolean, Column, DateTime, ForeignKey, Index,
                        Integer, String, event)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship


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
    telegram_id = Column(String, unique=True)
    is_active = Column(Boolean, default=False)

    events = relationship("UserEvent", back_populates="participants")

    weekly_tasks = relationship(
        "WeeklyTask", cascade="all, delete", back_populates="owner")

    tasks = relationship(
        "Task", cascade="all, delete", back_populates="owner")

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
    color = Column(String, nullable=True)

    participants = relationship("UserEvent", back_populates="events")

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


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    is_done = Column(Boolean, nullable=False)
    is_important = Column(Boolean, nullable=False)
    date_time = Column(DateTime, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="tasks")


class WeeklyTask(Base):
    __tablename__ = "weekly_task"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    days = Column(String, nullable=False)
    content = Column(String)
    is_important = Column(Boolean, nullable=False)
    the_time = Column(String, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="weekly_tasks")


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    author = Column(String)
