from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from evento.routers import user, auth
from .settings import settings
from loguru import logger
from .database import get_db

app = FastAPI()

origins = [
    settings.cors_origins,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, tags=["Auth"], prefix="/api/auth")
app.include_router(user.router, tags=["Users"], prefix="/api/users")


@app.get("/api/healthchecker")
def root():
    return {"message": "Hello World"}
