from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, DDL, event, Float,
                        ForeignKey, Index, Integer, String, Time)
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint

from app.config import PSQL_ENVIRONMENT
import app.routers.salary.config as SalaryConfig


Base = declarative_base()


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

    owned_events = relationship(
        "Event", cascade="all, delete", back_populates="owner",
    )
    events = relationship(
        "UserEvent", cascade="all, delete", back_populates="participants",
    )
    salary_settings = relationship(
        "SalarySettings", cascade="all, delete", back_populates="user",
    )

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
    owner_id = Column(Integer, ForeignKey("users.id"))
    color = Column(String, nullable=True)

    owner = relationship("User", back_populates="owned_events")
    participants = relationship(
        "UserEvent", cascade="all, delete", back_populates="events",
    )

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


class UserEvent(Base):
    __tablename__ = "user_event"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column('user_id', Integer, ForeignKey('users.id'))
    event_id = Column('event_id', Integer, ForeignKey('events.id'))

    events = relationship("Event", back_populates="participants")
    participants = relationship("User", back_populates="events")

    def __repr__(self):
        return f'<UserEvent ({self.participants}, {self.events})>'


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


class SalarySettings(Base):
    # Code revision required after categories feature is added
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    __tablename__ = "salary_settings"

    user_id = Column(
        Integer, ForeignKey("users.id"), primary_key=True,
    )
    # category_id = Column(
    #     Integer, ForeignKey("categories.id"), primary_key=True,
    # )
    category_id = Column(
        Integer, primary_key=True,
    )
    wage = Column(
        Float, nullable=False, default=SalaryConfig.MINIMUM_WAGE,
    )
    off_day = Column(
        Integer, CheckConstraint("0<=off_day<=6"), nullable=False,
        default=SalaryConfig.SATURDAY,
    )
    # holiday_category_id = Column(
    #     Integer, ForeignKey("holiday_categories.id"), nullable=False,
    #     default=SalaryConfig.ISRAELI_JEWISH,
    # )
    holiday_category_id = Column(
        Integer, nullable=False,
        default=SalaryConfig.ISRAELI_JEWISH,
    )
    regular_hour_basis = Column(
        Float, nullable=False, default=SalaryConfig.REGULAR_HOUR_BASIS,
    )
    night_hour_basis = Column(
        Float, nullable=False, default=SalaryConfig.NIGHT_HOUR_BASIS,
    )
    night_start = Column(
        Time, nullable=False, default=SalaryConfig.NIGHT_START,
    )
    night_end = Column(
        Time, nullable=False, default=SalaryConfig.NIGHT_END,
    )
    night_min_len = Column(
        Time, nullable=False, default=SalaryConfig.NIGHT_MIN_LEN,
    )
    first_overtime_amount = Column(
        Float, nullable=False, default=SalaryConfig.FIRST_OVERTIME_AMOUNT,
    )
    first_overtime_pay = Column(
        Float, nullable=False, default=SalaryConfig.FIRST_OVERTIME_PAY,
    )
    second_overtime_pay = Column(
        Float, nullable=False, default=SalaryConfig.SECOND_OVERTIME_PAY,
    )
    week_working_hours = Column(
        Float, nullable=False, default=SalaryConfig.WEEK_WORKING_HOURS,
    )
    daily_transport = Column(
        Float, CheckConstraint(
            f"daily_transport<={SalaryConfig.MAXIMUM_TRANSPORT}"),
        nullable=False, default=SalaryConfig.STANDARD_TRANSPORT,
    )

    user = relationship("User", back_populates="salary_settings")
    # category = relationship("Category", back_populates="salary_settings")
    # holiday_category =relationship("HolidayCategory",
    #                                back_populates="salary_settings")

    def __repr__(self):
        return f'<SalarySettings ({self.user_id}, {self.category_id})>'


class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    author = Column(String)
