from datetime import timedelta
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException

from sqlalchemy.orm import Session
from evento.database import get_db
from loguru import logger
from .. import schemas
from evento.oauth2 import AuthJWT

router = APIRouter()


@router.post(
    "/create",
    status_code=status.HTTP_201_CREATED,
    # response_model=schemas.RegisterUserResponseSchema,
)
async def create_user(
    # payload: schemas.CreateEventSchema,
    # db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    user_id = Authorize.get_jwt_subject()
    print(user_id)
    return {"durka": 0}
