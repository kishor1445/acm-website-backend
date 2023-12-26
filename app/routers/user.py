import sqlite3
import pytz
import os
import secrets
from datetime import datetime
from fastapi import APIRouter, Request, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schema, oauth2
from utils.security import hash_, check_pass, verify
from utils.mail import is_trusted_domain, TRUSTED_DOMAIN, send
from utils.others import get_dict_one, check_not_none

router = APIRouter(prefix="/users", tags=["Users"])
IST = pytz.timezone("Asia/Kolkata")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "message": "Verification mail has been sent to your email"
                    }
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {"value": {"detail": "Invalid Email ID"}},
                        "untrusted_domain": {
                            "value": {
                                "detail": f"Only {', '.join(TRUSTED_DOMAIN)} are accepted"
                            }
                        },
                        "already_exists": {"value": {"detail": "User Already Exists."}},
                        "empty data": {
                            "value": {"detail": "Required data cannot be empty"}
                        },
                        "invalid password format": {"value": {"detail": "message"}},
                    }
                }
            },
        },
    },
)
def create_user(data: schema.UserCreate, request: Request):
    """
    Creates a regular user who can register for events and all...
    """
    if not check_not_none(data.model_dump(), []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Required data cannot be empty",
        )
    data.email_id = is_trusted_domain(data.email_id)
    check_pass(data.password)
    data.password = hash_(data.password)
    v_token = secrets.token_urlsafe(32)
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        _data = data.model_dump()
        _data["joined_at"] = datetime.now(IST)
        _data["verified"] = False
        _data["v_token"] = v_token
        try:
            cur.execute(
                """INSERT INTO users VALUES(
                            :reg_no,:name,:email_id,:password,:department,:university,:year,:joined_at,:verified,:v_token
                         )""",
                _data,
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User Already Exists."
            )
        db.commit()
        verify_link = (
            f"{request.url.scheme}://{request.url.hostname}/users/verify/{v_token}"
        )
        html_body = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>ACM-SIST Registration Verification</title>
        </head>
        <body style="font-family: Arial, sans-serif;">
            <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px; background-color: #f8f8f8;">
                <div style="text-align: center;"><img src="{request.url.scheme}://{request.url.hostname}/static/logo.svg" alt="ACM Logo" style="max-width: 100%; height: auto; margin-bottom: 20px;" /></div>
                <h2 style="color: #333;">ACM-SIST Registration Verification</h2> 
                <p>Welcome to the ACM-SIST at Sathyabama University</p>
                <p>We're excited to have you on board. To complete your registration and start enjoying the benefits of our ACM-SIST community, please click the button below to verify your account:</p>
                <div style="text-align: center;"><a href="{verify_link}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 5px; margin-top: 15px;">Verify My Account</a></div>
                <p>If the button above doesn't work, you can also copy and past the following link into your browser:</p>
                <p>{verify_link}</p>
                <p>Thank you for joining us!</p>

                <p>Best regards,<br>
                {os.getenv("ACM_SIST_CHAIR", "")},<br>
                Chair - ACM SIST.</p>
            </div>
        </body>
        </html>
        """
        send([data.email_id], f"{data.name}, welcome to ACM-SIST!", html_body)
    return {"message": "Verification mail has been sent to your email"}


@router.get("/verify/{token}")
def verify_user(token: str):
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT reg_no FROM users WHERE v_token = ?", (token,))
        res = cur.fetchone()
        if res:
            cur.execute(
                "UPDATE users SET verified = 1, v_token = 'NaN' WHERE reg_no = ?",
                (res[0],),
            )
            return {"message": "Account verified successfully"}
        else:
            return {"detail": "Invalid verification token"}


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        403: {
            "description": "Forbidden Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "You don't have permission to perform this action."
                    }
                }
            },
        },
        401: {
            "description": "Unauthorized",
            "content": {"application/json": {"example": {"detail": "Invalid Token"}}},
        },
    },
)
def delete_user(
    data: schema.UserDelete,
    current_member: schema.MemberOut = Depends(oauth2.get_current_user),
):
    """
    Deletes a regular user. It should respond with 204 for successful deletion with no content
    """
    if current_member.reg_no == data.reg_no:
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM users WHERE reg_no = ?", (data.reg_no,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="User Not Found"
                )
            cur.execute("DELETE FROM users WHERE reg_no = ?", (data.reg_no,))
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )


@router.post(
    "/login",
    response_model=schema.TokenData,
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid login": {"value": {"detail": "Invalid Credentials"}},
                        "empty data": {
                            "value": {"detail": "Required data cannot be empty"}
                        },
                    }
                }
            },
        }
    },
)
def login(data: OAuth2PasswordRequestForm = Depends()):
    """
    Login for regular users
    """
    if not check_not_none({"username": data.username, "password": data.password}, []):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Required data cannot be empty",
        )
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT reg_no, password, verified FROM users WHERE email_id = ?",
            (data.username,),
        )
        res = cur.fetchone()
        if not res or not verify(data.password, res[1]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
            )
        if not res[2]:  # if not verified
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account not verified yet. Please check your email.",
            )
        access_token = oauth2.create_access_token({"reg_no": res[0], "type": "user"})

        return {"access_token": access_token, "token_type": "bearer"}
