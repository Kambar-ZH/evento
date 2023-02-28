import uuid
from .database import Base
from sqlalchemy import (
    TIMESTAMP,
    Column,
    String,
    Boolean,
    text,
    Integer,
    Table,
    ForeignKey,
    Enum,
)
from sqlalchemy.orm import relationship
from sqlalchemy.types import ARRAY
from sqlalchemy.dialects.postgresql import UUID
from .enums import UserRole, EventCategory


def random_username() -> str:
    return f"User-{uuid.uuid4()}"


users_to_events_table = Table(
    "users_to_events",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("event_id", Integer, ForeignKey("events.id")),
)

users_to_friends_table = Table(
    "users_to_friends",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("friend_id", Integer, ForeignKey("users.id")),
)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    login = Column(String, nullable=False, unique=True, default=random_username)
    firstname = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    phone_number = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    otp = Column(String, nullable=True)
    verified = Column(Boolean, nullable=False, server_default="False")
    role = Column(Enum(UserRole), server_default=UserRole.USER.value, nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )

    participant_events = relationship(
        "Event",
        secondary=users_to_events_table,
        back_populates="participants",
    )
    friends = relationship(
        "User",
        secondary=users_to_friends_table,
        primaryjoin=id == users_to_friends_table.c.user_id,
        secondaryjoin=id == users_to_friends_table.c.friend_id,
        backref="friends_backref",
    )
    created_events = relationship("Event", back_populates="creator")
    comments = relationship("EventComment", back_populates="from_user")


# upload_image -> backend -> id; id_image ->
# TODO: AWS S3
class EventImage(Base):
    __tablename__ = "event_images"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    url = Column(String, nullable=False)


class EventSchedule(Base):
    __tablename__ = "event_schedules"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)  #
    end_date = Column(TIMESTAMP(timezone=True), nullable=False)
    description = Column(String, nullable=False)
    event_id = Column(Integer, ForeignKey("events.id"))


class EventComment(Base):
    __tablename__ = "event_comments"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    from_user_id = Column(Integer, ForeignKey("users.id"))
    from_user = relationship("User", back_populates="comments")
    event_id = Column(Integer, ForeignKey("events.id"))


class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    categories = Column(ARRAY(Enum(EventCategory)), nullable=False, default=[])
    creator_id = Column(Integer, ForeignKey("users.id"))
    creator = relationship("User", back_populates="created_events")
    participants = relationship(
        "User", secondary=users_to_events_table, back_populates="participant_events"
    )
    schedules = relationship("EventSchedule")
    comments = relationship("EventComment")
    start_date = Column(TIMESTAMP(timezone=True), nullable=False)
    end_date = Column(TIMESTAMP(timezone=True), nullable=False)
    address = Column(String, nullable=False)
    description = Column(String, nullable=False)
    link_to_registration = Column(String, nullable=True)
    link_to_buy_ticket = Column(String, nullable=True)
