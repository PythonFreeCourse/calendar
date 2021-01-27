from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.database.database import Base


############### fast-api Users
import databases
from fastapi_users.db import SQLAlchemyBaseUserTable, SQLAlchemyUserDatabase
from app.internal.security.security_schemas import UserDB
from app.database.database import SQLALCHEMY_DATABASE_URL

database = databases.Database(SQLALCHEMY_DATABASE_URL)
class UserTable(Base, SQLAlchemyBaseUserTable):
    pass
users = UserTable.__table__
user_db = SQLAlchemyUserDatabase(UserDB, database, users)

#############

class User(UserTable):
    # __tablename__ = "users"
    __table_args__ = {'extend_existing': True}
    # id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False)
    # email = Column(String, unique=True, nullable=False)
    # password = Column(String, nullable=True)
    full_name = Column(String)
    description = Column(String, default="Happy new user!")
    avatar = Column(String, default="Happy new user!")
    # is_active = Column(Boolean, default=False)

    events = relationship("UserEvent", back_populates="participants")
    
    def __repr__(self):
        return f'<User {self.id}>'


class UserEvent(Base):
    __tablename__ = "user_event"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column('user_id', Integer, ForeignKey('user.id'))
    event_id = Column('event_id', Integer, ForeignKey('events.id'))

    events = relationship("Event", back_populates="participants")
    participants = relationship("User", back_populates="events")

    def __repr__(self):
        return f'<UserEvent ({self.participants}, {self.events})>'

class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    content = Column(String)
    location = Column(String)

    owner = relationship("User")
    owner_id = Column(Integer, ForeignKey("user.id"))
    participants = relationship("UserEvent", back_populates="events")

    def __repr__(self):
        return f'<Event {self.id}>'


class Invitation(Base):
    __tablename__ = "invitations"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, nullable=False, default="unread")
    recipient_id = Column(Integer, ForeignKey("user.id"))
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


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     username = Column(String, unique=True, nullable=False)
#     email = Column(String, unique=True, nullable=False)
#     password = Column(String, nullable=False)
#     full_name = Column(String)
#     description = Column(String, default="Happy new user!")
#     avatar = Column(String, default="profile.png")
#     is_active = Column(Boolean, default=False)

#     events = relationship("UserEvent", back_populates="participants")

#     def __repr__(self):
#         return f'<User {self.id}>'


# class Event(Base):
#     __tablename__ = "events"

#     id = Column(Integer, primary_key=True, index=True)
#     title = Column(String, nullable=False)
#     start = Column(DateTime, nullable=False)
#     end = Column(DateTime, nullable=False)
#     content = Column(String)
#     location = Column(String)

#     owner = relationship("User")
#     owner_id = Column(Integer, ForeignKey("users.id"))
#     participants = relationship("UserEvent", back_populates="events")

#     def __repr__(self):
#         return f'<Event {self.id}>'

# class Invitation(Base):
#     __tablename__ = "invitations"

#     id = Column(Integer, primary_key=True, index=True)
#     status = Column(String, nullable=False, default="unread")
#     recipient_id = Column(Integer, ForeignKey("user.id"))
#     event_id = Column(Integer, ForeignKey("events.id"))
#     creation = Column(DateTime, default=datetime.now)

#     recipient = relationship("User")
#     event = relationship("Event")

#     def __repr__(self):
#         return (
#             f'<Invitation '
#             f'({self.event.owner}'
#             f'to {self.recipient})>'
#         )
