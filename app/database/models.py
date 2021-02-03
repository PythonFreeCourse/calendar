from datetime import datetime

from sqlalchemy import (DDL, Boolean, Column, DateTime, ForeignKey, Index,
                        Integer, String, event)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship

from app.config import PSQL_ENVIRONMENT
from app.database.database import Base


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


class AudioSettings(Base):
    __tablename__ = "audio_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    music_on = Column(Boolean, nullable=False)
    music_vol = Column(Integer)
    sfxs_on = Column(Boolean, nullable=False)
    sfxs_vol = Column(Integer)


class AudioTracks(Base):
    __tablename__ = "audio_tracks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, unique=True)
    is_music = Column(Boolean, nullable=False)


class UserAudioTracks(Base):
    __tablename__ = "user_audio_tracks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    track_id = Column(Integer, ForeignKey("audio_tracks.id"))


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    author = Column(String)
