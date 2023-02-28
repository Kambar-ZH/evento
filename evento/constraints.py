from pydantic import validator
import re


class PhoneNumber(str):
    regex = r"^\+\d{11}$"

    @validator("value")
    def validate_phone(cls, value):
        if not re.match(cls.regex, value):
            raise ValueError("Invalid phone number format")
        return value
