from fastapi import FastAPI
from .settings import settings
from loguru import logger
from .database import get_db

app = FastAPI()


@app.get("/")
def read_root():
    logger.info(settings.docs_url)
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str | None = None):
    return {"item_id": item_id, "q": q}
