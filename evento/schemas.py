from datetime import datetime
from pydantic import BaseModel, EmailStr, constr, conint
from .enums import EventCategory
from .constraints import PhoneNumber


class UserBaseSchema(BaseModel):
    name: str
    email: EmailStr
    photo: str

    class Config:
        orm_mode = True


class RegisterUserSchema(BaseModel):
    phone_number: PhoneNumber  # +77477542002
    password: constr(min_length=8)
    role: str = "USER"


class RegisterUserResponseSchema(BaseModel):
    phone_number: str
    id: int
    created_at: datetime


class SendOTPSchema(BaseModel):
    phone_number: constr(regex="\+\d{11}")


class VerifyOTPSchema(BaseModel):
    phone_number: PhoneNumber
    otp: str


class LoginUserSchema(BaseModel):
    phone_number: str
    password: constr(min_length=8)


class UserResponse(UserBaseSchema):
    id: int
    created_at: datetime
    updated_at: datetime


class ScheduleSchema(BaseModel):
    start_date: conint(ge=0)
    end_date: conint(ge=0)
    description: constr(min_length=1)


class CreateEventSchema(BaseModel):
    categories: list[EventCategory]
    schedules: list[ScheduleSchema]
    start_date: conint(ge=0)
    end_date: conint(ge=0)
    address: constr(min_length=1)
    description: constr(min_length=1)
    link_to_registration: str | None = None
    link_to_buy_ticket: str | None = None
