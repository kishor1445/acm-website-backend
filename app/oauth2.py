import os
from datetime import datetime, timedelta
from fastapi import Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from . import schema

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def create_access_token(data: dict):
    _data = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")))
    _data.update({"exp": expire})
    return jwt.encode(_data, os.getenv("SECRET_KEY"), os.getenv("JWT_ALGORITHM"))


def verify_access_token(token: str, credentials_exceptions):
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("JWT_ALGORITHM")])
        email_id: str = payload.get("email_id")
        admin: bool = payload.get("admin")

        if email_id is None or admin is None:
            raise credentials_exceptions
        _data = schema.TokenData(email_id=email_id, admin=admin)
    except JWTError:
        raise credentials_exceptions
    return _data


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials", headers={
        "WWW-Authenticate": "Bearer"
    })
    return verify_access_token(token, credentials_exception)
