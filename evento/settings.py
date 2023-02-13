import logging
import sys
from typing import Any, Dict, List, Tuple
from loguru import logger
from pydantic import BaseSettings, EmailStr, PostgresDsn
from .logging import InterceptHandler


class Settings(BaseSettings):
    debug = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "Evento"
    version: str = "0.1.0"

    email: EmailStr = "example@gmail.com"
    postgres_password: str
    postgres_user: str
    postgres_db: str
    database_url: PostgresDsn

    blockchain_url: str
    lottery_contract_address: str
    betting_contract_address: str
    lottery_creation_block: int

    aws_access_key_id: str
    aws_secret_access_key: str
    aws_bucket_name: str

    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    betting_pg_ip: str
    betting_pg_password: str
    betting_pg_user: str
    betting_pg_db: str
    betting_database_url: PostgresDsn

    crypto_hunt_pg_ip: str
    crypto_hunt_database_url: str

    cors_origins: List[str]

    class Config:
        env_file = ".env"

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    def configure_logging(self) -> None:
        if len(logging.getLogger("uvicorn").handlers) > 0:
            logging.getLogger("uvicorn").removeHandler(
                logging.getLogger("uvicorn").handlers[0]
            )
        logging.getLogger().handlers = [InterceptHandler()]
        for logger_name in self.loggers:
            logging_logger = logging.getLogger(logger_name)
            logging_logger.handlers = [InterceptHandler(level=self.logging_level)]

        logger.configure(handlers=[{"sink": sys.stderr, "level": self.logging_level}])


settings = Settings()
settings.configure_logging()
