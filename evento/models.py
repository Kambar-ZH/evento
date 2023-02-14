import uuid
from .database import Base
from sqlalchemy import TIMESTAMP, Column, String, Boolean, text
from sqlalchemy.dialects.postgresql import UUID


def random_username() -> str:
    return f"User-{uuid.uuid4()}"


class User(Base):
    __tablename__ = "users"
    id = Column(
        UUID(as_uuid=True), primary_key=True, nullable=False, default=uuid.uuid4
    )
    login = Column(String, nullable=False, unique=True, default=random_username)
    firstname = Column(String, nullable=True)
    surname = Column(String, nullable=True)
    phone_number = Column(String, nullable=False, unique=True)
    password = Column(String, nullable=False)
    photo_url = Column(String, nullable=True)
    otp = Column(String, nullable=True)
    verified = Column(Boolean, nullable=False, server_default="False")
    role = Column(String, server_default="user", nullable=False)
    created_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
    updated_at = Column(
        TIMESTAMP(timezone=True), nullable=False, server_default=text("now()")
    )
