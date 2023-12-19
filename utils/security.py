import string
from fastapi import HTTPException, status
from passlib.context import CryptContext

pass_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_(password: str):
    return pass_context.hash(password)


def verify(password: str, hashed_password: str):
    return pass_context.verify(password, hashed_password)


def check_pass(password: str):
    error_ = None
    if len(password) < 8:
        error_ = "Password should be at least 8 characters."
    elif sum(1 for x in password if x in string.ascii_lowercase) < 1:
        error_ = "Password should contain at least 1 lowercase character."
    elif sum(1 for x in password if x in string.ascii_uppercase) < 1:
        error_ = "Password should contain at least 1 uppercase character."
    elif sum(1 for x in password if x in string.punctuation) < 1:
        error_ = "Password should contain at least 1 special character."
    elif sum(1 for x in password if x in string.digits) < 1:
        error_ = "Password should contain at least 1 digit."
    if error_:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_)
