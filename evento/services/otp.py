from requests import get
from evento.settings import settings
from loguru import logger


def send_otp(otp: str, phone_number: str) -> int:
    # remove plus symbol
    phone_number = phone_number.replace("+", "")

    response = get(
        "https://api.mobizon.kz/service/message/sendsmsmessage",
        params={
            "recipient": phone_number,
            "text": f"Код верификации: {otp} \nНИКОМУ НЕ ГОВОРИТЕ КОД!",
            "apiKey": settings.OTP_API_KEY,
        },
    )

    logger.info(response.json())

    return response.json()["code"]
