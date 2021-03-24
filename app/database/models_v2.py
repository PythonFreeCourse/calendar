"""SQLAlchemy database models."""
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    event,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative import DeclarativeMeta, declarative_base
from sqlalchemy.orm import Session, relationship

from app.config import PSQL_ENVIRONMENT
from app.internal.privacy import PrivacyKinds

Base: DeclarativeMeta = declarative_base()

PRIMARY_KEY_DOC = "An auto increment unique primary key."


class Event(Base):
    """A database model of an Event entity."""

    __tablename__ = "event"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        nullable=False,
        doc=PRIMARY_KEY_DOC,
    )
    color = Column(
        String,
        nullable=True,
        doc="",  # TODO: doc
    )
    content = Column(
        String,
        doc="",  # TODO: doc
    )
    datetime_end = Column(
        DateTime,
        nullable=False,
        doc="The event's end datetime.",
    )
    datetime_start = Column(
        DateTime,
        nullable=False,
        doc="The event's start datetime.",
    )
    emotion = Column(
        String,
        nullable=True,
        doc="",  # TODO: doc
    )
    image = Column(
        String,
        nullable=True,
        doc="The event's image file name.",
    )
    invited_emails = Column(
        String,
        doc="A list of emails separated by a comma.",  # TODO:  Refactor?
    )
    is_all_day = Column(
        Boolean,
        default=False,
        doc="Whether the event spans the whole day.",
    )
    # TODO: This is not an event data but a user data that shows on the event.
    is_available = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="",  # TODO: doc
    )
    is_google_event = Column(
        Boolean,
        default=False,
        doc="Whether the event was imported from a Google Calendar",
    )
    latitude = Column(
        Float,
        nullable=True,
        doc="The latitude of the event's location.",
    )
    location = Column(
        String,
        nullable=True,
        doc="The location of the event.",
    )
    longitude = Column(
        Float,
        nullable=True,
        doc="The longitude of the event's location.",
    )
    owner_id = Column(
        Integer,
        ForeignKey("user.id"),
        nullable=False,
        doc="The ID of the user who created the event.",
    )
    privacy = Column(
        Enum(PrivacyKinds),
        default=PrivacyKinds.Public,
        nullable=False,
        doc="The event's privacy setting. Defaults to PrivacyKinds.Public.",
    )
    title = Column(
        String,
        nullable=False,
        doc="The title of the event.",
    )
    video_chat_link = Column(
        String,
        nullable=True,
        doc="The event's video chat link.",
    )
    members = relationship(
        "User",
        secondary="user_event",
        back_populates="events",
        doc="A list of users who are attending the event.",
    )
    owner = relationship(
        "User",
        back_populates="owned_events",
        doc="The user who created the event.",
    )

    # PostgreSQL
    if PSQL_ENVIRONMENT:
        events_tsv = Column(TSVECTOR)
        __table_args__ = (
            Index("events_tsv_idx", "events_tsv", postgresql_using="gin"),
        )

    def __repr__(self):
        return f"<Event {self.id}>"


class Language(Base):
    """A database model of a Language entity.

    Languages in the database are the ones which are supported by the website.
    """

    __tablename__ = "language"

    id = Column(
        Integer,
        primary_key=True,
        index=True,
        nullable=False,
        doc=PRIMARY_KEY_DOC,
    )
    name = Column(
        String,
        unique=True,
        nullable=False,
        doc="The name of the language, in the language's script.",
    )
    code = Column(
        String,
        unique=True,
        nullable=False,
        doc="The ISO code of the language.",
    )


class User(Base):
    """A database model of a User entity."""

    __tablename__ = "user"

    id = Column(  # TODO: Should id be changed to a UUID?
        Integer,
        primary_key=True,
        index=True,
        nullable=False,
        doc=PRIMARY_KEY_DOC,
    )
    avatar = Column(
        String,
        default="profile.png",
        nullable=False,
        doc="The user's avatar image file name. Defaults to 'profile.png'.",
    )
    description = Column(
        String,
        nullable=True,
        doc="A freeform description field.",
    )
    email = Column(
        String,
        unique=True,
        nullable=False,
        doc="A unique email. Email must be valid.",
    )
    full_name = Column(
        String,
        nullable=False,
        doc="The user's full name. A full name must be at least 2 characters"
        " long.",
    )
    is_active = Column(
        Boolean,
        default=True,
        nullable=False,
        doc="Whether the user account is active or temporarily disabled."
        " Defaults to True.",
    )
    is_admin = Column(
        Boolean,
        default=False,
        nullable=False,
        doc="Whether the user is a site admin. Defaults to False.",
    )
    language_id = Column(
        Integer,
        ForeignKey("language.id"),
        default=1,
        nullable=False,
        doc="The user's UI language's ID. Defaults to 1.",
    )
    password = Column(
        String,
        nullable=False,
        doc="The user's password. A password must be a minimum length of 3"
        " characters and a maximum length of 20 characters.",
    )
    privacy = Column(
        Enum(PrivacyKinds),
        default=PrivacyKinds.Private,
        nullable=False,
        doc="The user's privacy setting. Defaults to PrivacyKinds.Private.",
    )
    target_weight = Column(
        Float,
        nullable=True,
        doc="The user's target weight goal.",
    )
    telegram_id = Column(
        String,
        unique=True,
        nullable=True,
        doc="A unique Telegram ID.",
    )
    username = Column(
        String,
        unique=True,
        nullable=False,
        doc="A unique username. A valid username must be a minimum length of 3"
        " characters, a maximum length of 20 characters, and use only the"
        " following characters: a-zA-Z0-9_.",
    )
    events = relationship(
        "Event",
        secondary="user_event",
        cascade="all, delete",
        back_populates="members",
        doc="A list of events the user is attending.",
    )
    language = relationship(
        "Language",
        doc="The user's UI language.",
    )
    owned_events = relationship(
        "Event",
        cascade="all, delete",
        back_populates="owner",
        doc="A list of events the user created.",
    )

    def __repr__(self):
        return f"<User {self.id}>"


user_event = Table(
    "user_event",
    Base.metadata,
    Column("user.id", Integer, ForeignKey("user.id"), primary_key=True),
    Column("event.id", Integer, ForeignKey("event.id"), primary_key=True),
)


# TODO: move this into a json file and load it from the json loader.
def insert_data(target, session: Session, **kw):
    """Inserts the supported languages into the Language table."""
    session.execute(
        target.insert(),
        {"id": 1, "name": "English", "code": "en"},
        {"id": 2, "name": "עברית", "code": "he"},
    )


event.listen(Language.__table__, "after_create", insert_data)
