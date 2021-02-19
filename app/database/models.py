from __future__ import annotations

from datetime import datetime
from typing import Any, Dict

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    DDL,
    event,
    Float,
    ForeignKey,
    Index,
    Integer,
    JSON,
    String,
    Time,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.declarative.api import declarative_base, DeclarativeMeta
from sqlalchemy.orm import relationship, Session
from sqlalchemy.sql.schema import CheckConstraint

from app.config import PSQL_ENVIRONMENT
from app.dependencies import logger
import app.routers.salary.config as SalaryConfig

Base: DeclarativeMeta = declarative_base()


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
    disabled = Column(Boolean, default=False, nullable=False)
    privacy = Column(String, default="Private", nullable=False)
    is_manager = Column(Boolean, default=False)
    language_id = Column(Integer, ForeignKey("languages.id"))

    owned_events = relationship(
        "Event",
        cascade="all, delete",
        back_populates="owner",
    )
    events = relationship(
        "UserEvent",
        cascade="all, delete",
        back_populates="participants",
    )
    salary_settings = relationship(
        "SalarySettings",
        cascade="all, delete",
        back_populates="user",
    )
    comments = relationship("Comment", back_populates="user")

    oauth_credentials = relationship(
        "OAuthCredentials",
        cascade="all, delete",
        back_populates="owner",
        uselist=False,
    )

    def __repr__(self):
        return f"<User {self.id}>"

    @staticmethod
    async def get_by_username(db: Session, username: str) -> User:
        """query database for a user by unique username"""
        return db.query(User).filter(User.username == username).first()


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    content = Column(String)
    location = Column(String, nullable=True)
    is_google_event = Column(Boolean, default=False)
    vc_link = Column(String)
    color = Column(String, nullable=True)
    all_day = Column(Boolean, default=False)
    invitees = Column(String)
    emotion = Column(String, nullable=True)
    availability = Column(Boolean, default=True, nullable=False)

    owner_id = Column(Integer, ForeignKey("users.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))

    owner = relationship("User", back_populates="owned_events")
    participants = relationship(
        "UserEvent",
        cascade="all, delete",
        back_populates="events",
    )
    comments = relationship("Comment", back_populates="event")

    # PostgreSQL
    if PSQL_ENVIRONMENT:
        events_tsv = Column(TSVECTOR)
        __table_args__ = (
            Index("events_tsv_idx", "events_tsv", postgresql_using="gin"),
        )

    def __repr__(self):
        return f"<Event {self.id}>"


class UserEvent(Base):
    __tablename__ = "user_event"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column("user_id", Integer, ForeignKey("users.id"))
    event_id = Column("event_id", Integer, ForeignKey("events.id"))

    events = relationship("Event", back_populates="participants")
    participants = relationship("User", back_populates="events")

    def __repr__(self):
        return f"<UserEvent ({self.participants}, {self.events})>"


class Language(Base):
    __tablename__ = "languages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)


class Category(Base):
    __tablename__ = "categories"

    __table_args__ = (UniqueConstraint("user_id", "name", "color"),)
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    color = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    @staticmethod
    def create(
        db_session: Session,
        name: str,
        color: str,
        user_id: int,
    ) -> Category:
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
        return f"<Category {self.id} {self.name} {self.color}>"


class PSQLEnvironmentError(Exception):
    pass


# PostgreSQL
if PSQL_ENVIRONMENT:
    trigger_snippet = DDL(
        """
    CREATE TRIGGER ix_events_tsv_update BEFORE INSERT OR UPDATE
    ON events
    FOR EACH ROW EXECUTE PROCEDURE
    tsvector_update_trigger(events_tsv,'pg_catalog.english','title','content')
    """,
    )

    event.listen(
        Event.__table__,
        "after_create",
        trigger_snippet.execute_if(dialect="postgresql"),
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
        return f"<Invitation " f"({self.event.owner}" f"to {self.recipient})>"


class OAuthCredentials(Base):
    __tablename__ = "oauth_credentials"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String)
    refresh_token = Column(String)
    token_uri = Column(String)
    client_id = Column(String)
    client_secret = Column(String)
    expiry = Column(DateTime)

    user_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates=__tablename__, uselist=False)


class SalarySettings(Base):
    # Code revision required after categories feature is added
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    __tablename__ = "salary_settings"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        primary_key=True,
    )
    # category_id = Column(
    #     Integer, ForeignKey("categories.id"), primary_key=True,
    # )
    category_id = Column(
        Integer,
        primary_key=True,
    )
    wage = Column(
        Float,
        nullable=False,
        default=SalaryConfig.MINIMUM_WAGE,
    )
    off_day = Column(
        Integer,
        CheckConstraint("0<=off_day<=6"),
        nullable=False,
        default=SalaryConfig.SATURDAY,
    )
    # holiday_category_id = Column(
    #     Integer, ForeignKey("holiday_categories.id"), nullable=False,
    #     default=SalaryConfig.ISRAELI_JEWISH,
    # )
    holiday_category_id = Column(
        Integer,
        nullable=False,
        default=SalaryConfig.ISRAELI_JEWISH,
    )
    regular_hour_basis = Column(
        Float,
        nullable=False,
        default=SalaryConfig.REGULAR_HOUR_BASIS,
    )
    night_hour_basis = Column(
        Float,
        nullable=False,
        default=SalaryConfig.NIGHT_HOUR_BASIS,
    )
    night_start = Column(
        Time,
        nullable=False,
        default=SalaryConfig.NIGHT_START,
    )
    night_end = Column(
        Time,
        nullable=False,
        default=SalaryConfig.NIGHT_END,
    )
    night_min_len = Column(
        Time,
        nullable=False,
        default=SalaryConfig.NIGHT_MIN_LEN,
    )
    first_overtime_amount = Column(
        Float,
        nullable=False,
        default=SalaryConfig.FIRST_OVERTIME_AMOUNT,
    )
    first_overtime_pay = Column(
        Float,
        nullable=False,
        default=SalaryConfig.FIRST_OVERTIME_PAY,
    )
    second_overtime_pay = Column(
        Float,
        nullable=False,
        default=SalaryConfig.SECOND_OVERTIME_PAY,
    )
    week_working_hours = Column(
        Float,
        nullable=False,
        default=SalaryConfig.WEEK_WORKING_HOURS,
    )
    daily_transport = Column(
        Float,
        CheckConstraint(f"daily_transport<={SalaryConfig.MAXIMUM_TRANSPORT}"),
        nullable=False,
        default=SalaryConfig.STANDARD_TRANSPORT,
    )

    user = relationship("User", back_populates="salary_settings")

    # category = relationship("Category", back_populates="salary_settings")
    # holiday_category =relationship("HolidayCategory",
    #                                back_populates="salary_settings")

    def __repr__(self):
        return f"<SalarySettings ({self.user_id}, {self.category_id})>"


class WikipediaEvents(Base):
    __tablename__ = "wikipedia_events"

    id = Column(Integer, primary_key=True, index=True)
    date_ = Column(String, nullable=False)
    wikipedia = Column(String, nullable=False)
    events = Column(JSON, nullable=True)
    date_inserted = Column(DateTime, default=datetime.utcnow)


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
        return f"<Comment {self.id}>"


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
            f"<Zodiac "
            f"{self.name} "
            f"{self.start_day_in_month}/{self.start_month}-"
            f"{self.end_day_in_month}/{self.end_month}>"
        )


# insert language data

# Credit to adrihanu   https://stackoverflow.com/users/9127249/adrihanu
# https://stackoverflow.com/questions/17461251
def insert_data(target, session: Session, **kw):
    session.execute(
        target.insert(),
        {"id": 1, "name": "English"},
        {"id": 2, "name": "עברית"},
    )


event.listen(Language.__table__, "after_create", insert_data)
