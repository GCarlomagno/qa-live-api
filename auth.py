import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash
from pydantic import BaseModel


router = APIRouter(prefix="/auth", tags=["Authentication"])

SECRET_KEY = os.environ["JWT_SECRET_KEY"]
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


class CurrentUser(BaseModel):
    username: str
    full_name: str
    role: str


TEST_USER = {
    "username": "qauser",
    "full_name": "QA Test User",
    "role": "tester",
    "hashed_password": password_hash.hash("Test123!"),
}


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


def authenticate_user(username: str, password: str):
    if username != TEST_USER["username"]:
        return None

    if not verify_password(password, TEST_USER["hashed_password"]):
        return None

    return TEST_USER


def create_access_token(username: str) -> str:
    expires = datetime.now(timezone.utc) + timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": username,
        "exp": expires,
    }

    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(token: str = Depends(oauth2_scheme)) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired authentication token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")

        if username != TEST_USER["username"]:
            raise credentials_exception

    except InvalidTokenError:
        raise credentials_exception

    return CurrentUser(
        username=TEST_USER["username"],
        full_name=TEST_USER["full_name"],
        role=TEST_USER["role"],
    )


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(user["username"])

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me", response_model=CurrentUser)
def read_current_user(
    current_user: CurrentUser = Depends(get_current_user),
):
    return current_user
