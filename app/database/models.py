import datetime

from app.database.database import Base
from sqlalchemy import (DDL, Boolean, Column, DateTime, ForeignKey, Index,
                        Integer, String, event)
from sqlalchemy.dialects import postgresql
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.orm import relationship


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

    events = relationship(
        "Event", cascade="all, delete", back_populates="owner")


class Event(Base):
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    start = Column(DateTime, nullable=False)
    end = Column(DateTime, nullable=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    # PostgreSQL
    events_tsv = Column(TSVECTOR)

    # PostgreSQL
    events_tsv = Column(TSVECTOR)

    owner = relationship("User", back_populates="events")

    # PostgreSQL
    __table_args__ = (Index('events_tsv_idx', 'events_tsv', postgresql_using='gin'),)


# PostgreSQL
trigger_snippet = DDL("""
CREATE TRIGGER ix_events_tsv_update BEFORE INSERT OR UPDATE
ON events
FOR EACH ROW EXECUTE PROCEDURE
tsvector_update_trigger(events_tsv,'pg_catalog.english', 'title', 'content')
""")

# PostgreSQL
event.listen(Event.__table__, 'after_create', trigger_snippet.execute_if(dialect='postgresql'))
