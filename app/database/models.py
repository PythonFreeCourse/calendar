from sqlalchemy import (Boolean, Column, DateTime, Float,
                        ForeignKey, Integer, String)
from sqlalchemy.ext.declarative.api import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import CheckConstraint

import app.routers.salary.config as SalaryConfig


Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    events = relationship(
        "Event", cascade="all, delete", back_populates="owner")
    salary_settings = relationship(
        "SalarySettings", cascade="all, delete", back_populates="user")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    date = Column(DateTime)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="events")


class SalarySettings(Base):
    # Code revision required after categories feature is added
    # Code revision required after holiday times feature is added
    # Code revision required after Shabbat times feature is added
    __tablename__ = "salary_settings"

    user_id = Column(
        Integer, ForeignKey("users.id"), primary_key=True,
    )
    category_id = Column(
        Integer, ForeignKey("categories.id"), primary_key=True,
    )
    wage = Column(
        Float, CheckConstraint(f"wage>{SalaryConfig.MINIMUM_WAGE}"),
        nullable=False, default=SalaryConfig.MINIMUM_WAGE,
    )
    off_day = Column(
        Integer, nullable=False, default=SalaryConfig.SATURDAY,
        CheckConstraint="0<=off_day<=6",
    )
    holiday_category_id = Column(
        Integer, ForeignKey("holidays.id"), nullable=False,
        default=SalaryConfig.ISRAELI_JEWISH,
    )
    regular_hour_basis = Column(
        Float, nullable=False, default=SalaryConfig.REGULAR_HOUR_BASIS,
    )
    night_hour_basis = Column(
        Float, nullable=False, default=SalaryConfig.NIGHT_HOUR_BASIS,
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
            f"daily_transport<={SalaryConfig.MAXIMUM_TRANSPORT}",
            ),
         nullable=False, default=SalaryConfig.STANDARD_TRANSPORT,
    )
    pension = Column(
        Float, nullable=False, default=SalaryConfig.PENSION,
    )
    tax_points = Column(
        Float, nullable=False, default=SalaryConfig.TAX_POINTS,
    )

    user = relationship("User", back_populates="salary_settings")
    category = relationship("Category", back_populates="salary_settings")
    holiday_category =relationship("HolidayCategory",
                                   back_populates="salary_settings")