import string
import time
import random
import bcrypt
import magic
from fastapi import HTTPException, status

ALLOWED_IMAGE_EXTENSIONS = (".jpg", ".png", ".jpeg")

def hash_(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def check_pass(password: str):
    error_ = None
    if len(password) < 8:
        error_ = "Password should be at least 8 characters"
    elif sum(1 for x in password if x in string.ascii_lowercase) < 1:
        error_ = "Password should contain at least 1 lowercase character"
    elif sum(1 for x in password if x in string.ascii_uppercase) < 1:
        error_ = "Password should contain at least 1 uppercase character"
    elif sum(1 for x in password if x in string.punctuation) < 1:
        error_ = "Password should contain at least 1 special character"
    elif sum(1 for x in password if x in string.digits) < 1:
        error_ = "Password should contain at least 1 digit"
    if error_:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=error_)


def pretend_like_sending_mail():
    """
    Pretend like sending an email to avoid user account enumeration attack
    """
    time.sleep(random.choice((6.63, 6.13, 5.32)))

def is_valid_image(file_name: str, file_content: bytes):
    file_mime = magic.from_buffer(file_content, True)
    return file_mime.startswith("image/") and any(file_name.lower().endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS)
    
