from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


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

    events = relationship("Event", cascade="all, delete", back_populates="owner")
    
    oauth_credentials = relationship("OAuthCredentials", cascade="all, delete", back_populates="owner", uselist=False)


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="events")


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
