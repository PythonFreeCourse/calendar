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
    is_active = Column(Boolean, default=False)

    events = relationship("UserEvent", back_populates="participants")

    def __repr__(self):
        return f'<User {self.id}>'


def create_events_tsv(psql_environment):
    if psql_environment:
        events_tsv = Column(TSVECTOR)
        __table_args__ = (Index(
            'events_tsv_idx',
            'events_tsv',
            postgresql_using='gin'),
            )
        return True
    return False


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


# PostgreSQL
def create_event_listen(psql_environment):
    trigger_snippet = DDL("""
    CREATE TRIGGER ix_events_tsv_update BEFORE INSERT OR UPDATE
    ON events
    FOR EACH ROW EXECUTE PROCEDURE
    tsvector_update_trigger(events_tsv,'pg_catalog.english','title','content')
    """)

    if psql_environment:
        event.listen(
            Event.__table__,
            'after_create',
            trigger_snippet.execute_if(dialect='postgresql')
            )
        return True
    return False


# PostgreSQL
create_event_listen(PSQL_ENVIRONMENT)


# PostgreSQL
class PSQLEnvironmentError(Exception):
    pass


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
