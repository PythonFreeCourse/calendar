from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    full_name = Column(String)
    description = Column(String, default="Happy new user!")
    avatar = Column(String, default="profile.png")

    is_active = Column(Boolean, default=True)

    speedy_meetings_enabled = Column(Boolean, default=False)

    events = relationship(
        "Event", cascade="all, delete", back_populates="owner")
    
    def has_speedy_meetings_enabled(self) -> bool:
        return self.speedy_meetings_enabled


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    default_end = get_default_end_time()
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="events")

    user = get_user_by_id(owner_id)

    def get_user_by_id(self, owner_id):
        return owner

    def get_default_end_time(self):
        return start + get_event_duration()

    def get_event_duration(self):
        default_duration = get_default_duration()
        if user.has_speedy_meetings_enabled():
            return default_duration * .75
        return default_duration

    def get_default_duration(self):
        return 60
