import os
import sqlite3
import pytz
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from . import schema
from utils.others import get_dict_one

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
IST = pytz.timezone("Asia/Kolkata")


def create_access_token(data: dict):
    _data = data.copy()
    expire = datetime.now(IST) + timedelta(
        days=int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS"))
    )
    _data.update({"exp": expire})
    return jwt.encode(_data, os.getenv("SECRET_KEY"), os.getenv("JWT_ALGORITHM"))


def get_payload(token, credentials_exceptions):
    try:
        return jwt.decode(
            token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")]
        )
    except JWTError:
        raise credentials_exceptions


def verify_access_token(token: str, credentials_exceptions):
    payload = get_payload(token, credentials_exceptions)
    reg_no: int = payload.get("reg_no")
    if reg_no is None:
        raise credentials_exceptions
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM users WHERE reg_no = ?", (reg_no,))
        res = cur.fetchone()
        if not res:
            raise credentials_exceptions
    return schema.UserOut(**get_dict_one(res, cur.description))


def verify_member_access_token(token: str, credentials_exceptions):
    payload = get_payload(token, credentials_exceptions)
    reg_no: int | None = payload.get("reg_no")
    if reg_no is None:
        raise credentials_exceptions
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM members WHERE reg_no = ?", (reg_no,))
        res = cur.fetchone()
        if not res:
            raise credentials_exceptions
    return schema.MemberOut(**get_dict_one(res, cur.description))


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_access_token(token, credentials_exception)


def get_current_member(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_member_access_token(token, credentials_exception)
