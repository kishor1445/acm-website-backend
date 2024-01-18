import os
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import EmailStr
from sqlmodel import Session, select
from app.db.db import get_db
from app.db.models import Members, Users
from . import schema, config

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
oauth2_scheme_no_error = OAuth2PasswordBearer(tokenUrl="login", auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    _data = data.copy()
    expire = datetime.now(config.IST) + (
        expires_delta or timedelta(days=int(os.getenv("ACCESS_TOKEN_EXPIRE_DAYS", "1")))
    )
    _data.update({"exp": expire})
    return jwt.encode(
        _data, os.getenv("SECRET_KEY", ""), os.getenv("JWT_ALGORITHM", "")
    )


def get_payload(token, invalid_token_exception):
    try:
        return jwt.decode(
            token,
            os.getenv("SECRET_KEY", ""),
            algorithms=[os.getenv("JWT_ALGORITHM", "")],
        )
    except JWTError:
        raise invalid_token_exception


#
#
# def verify_access_token(token: str, credentials_exceptions):
#     payload = get_payload(token, credentials_exceptions)
#     reg_no: int | None = payload.get("reg_no")
#     type_: str | None = payload.get("type")
#     if reg_no is None or type_ is None:
#         raise credentials_exceptions
#     if type_ == "user":
#         with sqlite3.connect("acm.db") as db:
#             cur = db.cursor()
#             cur.execute("SELECT * FROM users WHERE reg_no = ?", (reg_no,))
#             res = cur.fetchone()
#             if not res:
#                 raise credentials_exceptions
#     else:
#         raise credentials_exceptions
#     return schema.UserOut(**get_dict_one(res, cur.description))
#
#
# def verify_member_access_token(token: str, credentials_exceptions):
#     payload = get_payload(token, credentials_exceptions)
#     reg_no: int | None = payload.get("reg_no")
#     type_: str | None = payload.get("type")
#     if reg_no is None or type_ is None:
#         raise credentials_exceptions
#     if type_ == "member":
#         with sqlite3.connect("acm.db") as db:
#             cur = db.cursor()
#             cur.execute("SELECT * FROM members WHERE reg_no = ?", (reg_no,))
#             res = cur.fetchone()
#             if not res:
#                 raise credentials_exceptions
#     else:
#         raise credentials_exceptions
#     return schema.MemberOut(**get_dict_one(res, cur.description))
#
#
# def get_current_user(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid Token",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     return verify_access_token(token, credentials_exception)
#
#
# def get_current_member(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Invalid Token",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     return verify_member_access_token(token, credentials_exception)
#


# def verify_member_access_token(token: str, credentials_exceptions):
#     payload = get_payload(token, credentials_exceptions)
#     reg_no: int | None = payload.get("reg_no")
#     type_: str | None = payload.get("type")
#     if reg_no is None or type_ is None:
#         raise credentials_exceptions
#     if type_ == "member":
#         with sqlite3.connect("acm.db") as db:
#             cur = db.cursor()
#             cur.execute("SELECT * FROM members WHERE reg_no = ?", (reg_no,))
#             res = cur.fetchone()
#             if not res:
#                 raise credentials_exceptions
#     else:
#         raise credentials_exceptions
#     return schema.MemberOut(**get_dict_one(res, cur.description))


def get_user_email(token: str, invalid_token_exception):
    payload = get_payload(token, invalid_token_exception)
    email: EmailStr | None = payload.get("email")
    acc_type = payload.get("account_type")
    if email and acc_type == "user":
        return email
    raise invalid_token_exception


def get_current_user_email_or_none(token: str | None = Depends(oauth2_scheme_no_error)):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token"
    )
    if token:
        return get_user_email(token, invalid_token_exception)
    return None


def get_member_email(token: str, invalid_token_exception):
    payload = get_payload(token, invalid_token_exception)
    email = payload.get("email")
    acc_type = payload.get("account_type")
    if email and acc_type == "member":
        return email
    raise invalid_token_exception


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token"
    )
    email = get_user_email(token, invalid_token_exception)
    user = db.exec(select(Users).where(Users.email == email)).first()
    if user:
        return user
    raise invalid_token_exception


def get_current_member(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    invalid_token_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Access Token"
    )

    email = get_member_email(token, invalid_token_exception)
    member = db.exec(select(Members).where(Members.email == email)).first()
    if member:
        return member
    raise invalid_token_exception
