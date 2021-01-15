from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)

    events = relationship(
        "Event", cascade="all, delete", back_populates="owner")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    VC_link = Column(String)
    content = Column(String)
    location = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    repeated_event_id = Column(Integer, ForeignKey("repeated_events.id"))

    owner = relationship("User", back_populates="events")
    repeated_id = relationship("Repeated_event", back_populates="repeated_event")


class Repeated_event(Base):
    """have an ID to every sequence of repeated events so you can select all the sequence in one"""
    __tablename__ = "repeated_events"

    id = Column(Integer, primary_key=True, index=True)
    
    repeated_event = relationship(
        "Event", cascade="all, delete", back_populates="repeated_id")