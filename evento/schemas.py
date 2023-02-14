from datetime import datetime
import uuid
from pydantic import BaseModel, EmailStr, constr


class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr
    photo: str

    class Config:
        orm_mode = True


class RegisterUserSchema(BaseModel):
    phone_number: str  # +77477542002
    password: constr(min_length=8)
    role: str = "user"


class RegisterUserResponseSchema(BaseModel):
    phone_number: str
    id: uuid.UUID
    created_at: datetime


class SendOTPSchema(BaseModel):
    phone_number: str


class VerifyOTPSchema(BaseModel):
    phone_number: str
    otp: str


class LoginUserSchema(BaseModel):
    phone_number: str
    password: constr(min_length=8)


class UserResponse(UserBaseSchema):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
