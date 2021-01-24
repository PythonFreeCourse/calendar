from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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
    description = Column(String, default="Happy new user!")
    avatar = Column(String, default="profile.png")
    is_active = Column(Boolean, default=False)

    events = relationship("UserEvent", back_populates="participants")
    
    oauth_credentials = relationship(
        "OAuthCredentials", cascade="all, delete", back_populates="owner", uselist=False)

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
    participants = relationship("UserEvent", back_populates="events")

    def __repr__(self):
        return f'<Event {self.id}>'


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
  