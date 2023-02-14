from datetime import timedelta
from fastapi import APIRouter, Request, Response, status, Depends, HTTPException

from evento import oauth2
from .. import schemas, models, utils
from sqlalchemy.orm import Session
from evento.database import get_db
from evento.oauth2 import AuthJWT
from evento.settings import settings
from loguru import logger


router = APIRouter()
ACCESS_TOKEN_EXPIRES_IN = settings.ACCESS_TOKEN_EXPIRES_IN
REFRESH_TOKEN_EXPIRES_IN = settings.REFRESH_TOKEN_EXPIRES_IN


@router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=schemas.RegisterUserResponseSchema,
)
async def create_user(
    payload: schemas.RegisterUserSchema, db: Session = Depends(get_db)
):
    #  Hash the password
    payload.password = utils.hash_password(payload.password)
    new_user = models.User(**payload.dict())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return schemas.RegisterUserResponseSchema(
        created_at=new_user.created_at,
        phone_number=new_user.phone_number,
        id=new_user.id,
    )


@router.post(
    "/send-otp",
    status_code=status.HTTP_201_CREATED,
)
async def send_otp(payload: schemas.SendOTPSchema, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.phone_number == payload.phone_number)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Phone number or Password",
        )

    if user.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already verified",
        )

    from pyotp import random_base32

    otp = random_base32(length=32)[:6]

    db.query(models.User).filter(
        models.User.phone_number == payload.phone_number
    ).update({models.User.otp: otp})
    db.commit()

    logger.info(otp)

    from evento.services.otp import send_otp

    response_status_code = send_otp(otp, user.phone_number)
    if response_status_code != 0:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="OTP is DEAD",
        )

    return {"status": "sucess"}


@router.post(
    "/verify-otp",
    status_code=status.HTTP_201_CREATED,
)
async def verify_otp(payload: schemas.VerifyOTPSchema, db: Session = Depends(get_db)):
    user = (
        db.query(models.User)
        .filter(models.User.phone_number == payload.phone_number)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Phone number or Password",
        )

    if user.verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already verified",
        )

    if user.otp != payload.otp:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="OTP is incorrect",
        )

    db.query(models.User).filter(
        models.User.phone_number == payload.phone_number
    ).update({models.User.verified: True})
    db.commit()

    return {"status": "success"}


@router.post("/login")
def login(
    payload: schemas.LoginUserSchema,
    response: Response,
    db: Session = Depends(get_db),
    Authorize: AuthJWT = Depends(),
):
    # Check if the user exist
    user = (
        db.query(models.User)
        .filter(models.User.phone_number == payload.phone_number)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Phone number or Password",
        )

    # Check if user verified his email
    if not user.verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Please verify your phone number",
        )

    # Check if the password is valid
    if not utils.verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Incorrect Phone number or Password",
        )

    # Create access token
    access_token = Authorize.create_access_token(
        subject=str(user.id), expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN)
    )

    # Create refresh token
    refresh_token = Authorize.create_refresh_token(
        subject=str(user.id), expires_time=timedelta(minutes=REFRESH_TOKEN_EXPIRES_IN)
    )

    # Store refresh and access tokens in cookie
    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "refresh_token",
        refresh_token,
        REFRESH_TOKEN_EXPIRES_IN * 60,
        REFRESH_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )

    # Send both access
    return {"status": "success"}


@router.get("/refresh")
def refresh_token(
    response: Response,
    request: Request,
    Authorize: AuthJWT = Depends(),
    db: Session = Depends(get_db),
):
    try:
        print(Authorize._refresh_cookie_key)
        Authorize.jwt_refresh_token_required()

        user_id = Authorize.get_jwt_subject()
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not refresh access token",
            )
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The user belonging to this token no logger exist",
            )
        access_token = Authorize.create_access_token(
            subject=str(user.id),
            expires_time=timedelta(minutes=ACCESS_TOKEN_EXPIRES_IN),
        )
    except Exception as e:
        error = e.__class__.__name__
        if error == "MissingTokenError":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide refresh token",
            )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error)

    response.set_cookie(
        "access_token",
        access_token,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        True,
        "lax",
    )
    response.set_cookie(
        "logged_in",
        "True",
        ACCESS_TOKEN_EXPIRES_IN * 60,
        ACCESS_TOKEN_EXPIRES_IN * 60,
        "/",
        None,
        False,
        False,
        "lax",
    )
    return {"status": "success"}


@router.get("/logout", status_code=status.HTTP_200_OK)
def logout(
    response: Response,
    Authorize: AuthJWT = Depends(),
    user_id: str = Depends(oauth2.require_user),
):
    Authorize.unset_jwt_cookies()
    response.set_cookie("logged_in", "", -1)

    return {"status": "success"}
