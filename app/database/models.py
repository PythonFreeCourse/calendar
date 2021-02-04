from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from app.config import PSQL_ENVIRONMENT, DEVELOPMENT_DATABASE_STRING
from app.database.database import Base, SQLALCHEMY_DATABASE_URL
from app.dependencies import logger
from app.internal.security.security_schemas import UserDB
import databases
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from sqlalchemy import (DDL, Boolean, Column, DateTime, ForeignKey, Index, 
                        Integer, String, event, UniqueConstraint)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import relationship, Session

#config.DEVELOPMENT_DATABASE_STRING
database = databases.Database(DEVELOPMENT_DATABASE_STRING)


class UserTable(Base, SQLAlchemyBaseUserTable):
    pass


users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users)


class User(UserTable):
    __table_args__ = {'extend_existing': True}
    username = Column(String, unique=True, nullable=False)
    full_name = Column(String)
    language = Column(String)
    description = Column(String, default="Happy new user!")
    avatar = Column(String, default="profile.png")
    telegram_id = Column(String, unique=True)

    events = relationship("UserEvent", back_populates="participants")

    def __repr__(self):
        return f'<User {self.id}>'


class UserEvent(Base):
    __tablename__ = "user_event"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column('user_id', Integer, ForeignKey('user.id'))
    event_id = Column('event_id', Integer, ForeignKey('events.id'))
    events = relationship("Event", back_populates="participants")
    participants = relationship("User", back_populates="events")

    def __repr__(self):
        return f'<UserEvent ({self.participants}, {self.events})>'


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    content = Column(String)
    location = Column(String)
    owner = relationship("User")
    owner_id = Column(Integer, ForeignKey("user.id"))
    color = Column(String, nullable=True)
    category_id = Column(Integer, ForeignKey("categories.id"))
    owner = relationship("User")
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


class Category(Base):
    __tablename__ = "categories"

    __table_args__ = (
        UniqueConstraint('user_id', 'name', 'color'),
    )
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)

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
    recipient_id = Column(Integer, ForeignKey("user.id"))
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
