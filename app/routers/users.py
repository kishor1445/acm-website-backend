"""
NOTES:
    1) Since we are using SQLite, SQLite doesn't store timezone information in database so we have to specify the timezone explictly using .astimezone() in datetime object
    2) pretend_like_sending_mail() is used to prevent User Account Enumeration Attack. It will wait for few seconds which is almost the same seconds as the time it took to send the actual mail
    3) Mostly it will give the same error message if it's caused by the actual error or if the user account is not found.
        Example:
            Gives Invalid/Expired Verification Token even if the user account doesn't exist or the user already verified
"""

from datetime import datetime, timedelta
from secrets import token_urlsafe
from fastapi import APIRouter, HTTPException, Request, status, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from fastapi.responses import HTMLResponse
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from email_validator import validate_email
from app.config import IST
from app.db.db import get_db
from app.db.models import Auth, Users, Verify, ResetPassword
from app.utils.mail import send, verification_mail, reset_password_mail
from app.utils.security import check_pass, hash_, verify, pretend_like_sending_mail
from .. import schema, oauth2

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.UserOut)
def create_user(
    request: Request, data: schema.CreateUser, db: Session = Depends(get_db)
):
    check_pass(data.password)
    # Checks whether the email domain can get emails and normalize the email
    data.email = validate_email(data.email, check_deliverability=True).normalized
    # Adds login details to Auth table
    user_auth = Auth(
        email=data.email, password=hash_(data.password), account_type="user"
    )
    # Crafting required data to store in Users table
    user_data = data.model_dump()
    user_data["joined_at"] = datetime.now(IST)
    user_data["verified"] = False
    user = Users(**user_data)
    try:
        db.add(user)
        db.add(user_auth)
        db.commit()
        db.refresh(user)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="User already exist"
        )
    # Adds the verify token to Verify table for to use when the user clicks on the verify button in email
    verification_token = token_urlsafe(32)
    db.add(Verify(email=data.email, token=verification_token, time=datetime.now(IST)))
    db.commit()
    # Send verification email to the user
    verify_link = f"{request.url.scheme}://{request.url.hostname}/users/verify?token={verification_token}&email={data.email}"
    # Only send email if the email is not test mail
    if not data.email.startswith("test-acm-sist"):
        send(
            [data.email],
            "ACM-SIST Account Verification",
            verification_mail(request, verify_link),
        )
    else:
        # If it is a test mail then set the verify token
        from tests import test_users

        test_users.VERIFY_TOKEN = verification_token
    user.joined_at = user.joined_at.astimezone(IST)
    return user


@router.post("/login")
def login_user(
    data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    auth = db.exec(
        select(Auth)
        .where(Auth.email == data.username)
        .where(Auth.account_type == "user")
    ).first()
    if not auth or not verify(data.password, auth.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )
    # Checks whether the user verified their account or not
    user = db.exec(select(Users).where(Users.email == data.username)).first()
    if not user or not user.verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Account Not Verified Yet"
        )
    access_token = oauth2.create_access_token(
        {"email": user.email, "account_type": "user"}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/verify")
def verify_user(token: str, email: EmailStr, db: Session = Depends(get_db)):
    verify = db.exec(select(Verify).where(Verify.email == email)).first()
    # Checks whether the token is correct or not
    if verify and verify.token == token:
        verify.time = verify.time.astimezone(IST)
        # Only valid if verified within 10 minutes
        if datetime.now(IST) <= verify.time + timedelta(minutes=10):
            db.delete(verify)
            user_data = db.exec(select(Users).where(Users.email == email)).first()
            if user_data:
                user_data.verified = True
            db.commit()
            return {"msg": "Verified successfully"}
    # Sends the same message for both invalid/expire token and user not found
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid/Expired Verification Token",
    )


@router.post("/verify")
def send_verify_user_mail(
    request: Request, data: schema.Verify, db: Session = Depends(get_db)
):
    user = db.exec(select(Users).where(Users.email == data.email)).first()
    verification_token = token_urlsafe(32)

    if user and not user.verified:
        verify = db.exec(select(Verify).where(Verify.email == data.email)).first()
        if verify:
            # Since we are using SQLite
            # SQLite doesn't store timezone information so we have to specify the timezone explictly again
            verify.time = verify.time.astimezone(IST)
            resend_time = verify.time + timedelta(minutes=5)
            current_time = datetime.now(IST)
            if resend_time >= current_time:
                time_left = resend_time - current_time
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Please wait {(time_left.seconds / 60):.2f} minutes before requesting to send verification mail again",
                )
            verify.token = verification_token
            verify.time = datetime.now(IST)
            db.commit()

        verify_link = f"{request.url.scheme}://{request.url.hostname}/users/verify?token={verification_token}&email={data.email}"
        send(
            [data.email],
            "ACM-SIST Account Verification",
            verification_mail(request, verify_link),
        )
    else:
        pretend_like_sending_mail()
    return {
        "msg": "You will get an email to verify your account if we found your account in our database and your account is not already verified"
    }


@router.post("/forgot_password")
def forgot_password(
    request: Request, data: schema.ForgotPassword, db: Session = Depends(get_db)
):
    auth = db.exec(
        select(Auth).where(Auth.email == data.email).where(Auth.account_type == "user")
    ).first()
    if auth:
        reset_pass = db.exec(
            select(ResetPassword).where(ResetPassword.email == data.email)
        ).first()
        reset_token = token_urlsafe(32)
        if reset_pass:
            reset_pass.time = reset_pass.time.astimezone(IST)
            resend_time = reset_pass.time + timedelta(minutes=10)
            current_time = datetime.now(IST)
            if resend_time >= current_time:
                time_left = resend_time - current_time
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Please wait {(time_left.seconds / 60):.2f} minutes before sending request again",
                )
            reset_pass.time = datetime.now(IST)
            reset_pass.token = reset_token
            db.commit()
        else:
            db.add(
                ResetPassword(
                    email=data.email, token=reset_token, time=datetime.now(IST)
                )
            )
            db.commit()
        reset_url = f"{request.url.scheme}://{request.url.hostname}/users/reset_password?token={reset_token}&email={data.email}"
        if data.email.startswith("test-acm-sist"):
            from tests import test_users

            test_users.PASSWORD_RESET_TOKEN = reset_token
        else:
            send(
                [data.email], "Reset Password", reset_password_mail(request, reset_url)
            )
    else:
        # If the user account is not found
        pretend_like_sending_mail()
    return {
        "msg": "You will get an email to reset your password if we found your account in our database"
    }


@router.get("/reset_password")
def get_reset_password(request: Request, email: EmailStr, token: str):
    """
    This endpoint is used by the forgot_password which sends the link to this endpoint through email
    Shows Reset Password Webpage
    """
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ACM-SIST Password Reset</title>
        <script src="https://cdn.jsdelivr.net/npm/axios/dist/axios.min.js"></script>
    </head>
    <body style="font-family: Arial, sans-serif; background-color: #f4f4f4; margin: 0; padding: 0;">
        <div style="max-width: 400px; margin: 50px auto; background-color: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);">
            <div style="text-align: center;"><img src="{request.url.scheme}://{request.url.hostname}/static/logo.svg" alt="ACM Logo" style="max-width: 100%; height: auto; margin-bottom: 20px;" /></div>
            <h2 style="text-align: center; color: #333;">Password Reset</h2>
            <form id="resetForm" style="display: flex; flex-direction: column;">
                <input type="hidden" id="reset_token" name="reset_token" value="{token}">
                <input type="hidden" id="email" name="email" value="{email}"
                <label for="new_password" style="margin-bottom: 8px;">New Password:</label>
                <input style="padding: 8px; margin-bottom: 16px; border: 1px solid #ccc; border-radius: 4px;" type="password" id="new_password" name="new_password" required>
                
                <label for="confirm_password" style="margin-bottom: 8px;">Confirm Password:</label>
                <input style="padding: 8px; margin-bottom: 16px; border: 1px solid #ccc; border-radius: 4px;" type="password" id="confirm_password" name="confirm_password" required>

                <button type="button" onclick="resetPassword(event);" style="background-color: #4caf50; color: #fff; padding: 10px; border: none; border-radius: 4px; cursor: ponter; font-size: 16px;">Reset Password</button>
            </form>
        </div>
        <script src="{request.url.scheme}://{request.url.hostname}/static/js/reset_password.js"></script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


@router.post("/reset_password")
def reset_password(
    data: schema.SetResetPassword,
    db: Session = Depends(get_db),
    email: EmailStr | None = Depends(oauth2.get_current_user_email_or_none),
):
    # Runs this if block if the user gave all the required data to reset their password
    if data.reset_token and data.email:
        reset_pass = db.exec(
            select(ResetPassword).where(ResetPassword.email == data.email)
        ).first()
        if reset_pass and reset_pass.token == data.reset_token:
            if data.new_password == data.confirm_password:
                reset_pass.time = reset_pass.time.astimezone(IST)
                if reset_pass.time + timedelta(minutes=10) >= datetime.now(IST):
                    auth = db.exec(
                        select(Auth)
                        .where(Auth.email == data.email)
                        .where(Auth.account_type == "user")
                    ).first()
                    if auth:
                        check_pass(data.new_password)
                        auth.password = hash_(data.new_password)
                        db.delete(reset_pass)
                        db.commit()
                        return {"msg": "Password Updated Successfully"}
                    # If auth is None then it will raise Invalid/Expired Token
                    # It shouldn't show that the user is not found
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New Password and Confirm Password does not match",
                )
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid/Expired Token"
        )
    # Runs this if block if the user is logged in
    if email:
        auth = db.exec(select(Auth).where(Auth.email == email)).first()
        if auth:
            if data.new_password == data.confirm_password:
                check_pass(data.new_password)
                auth.password = hash_(data.new_password)
                db.commit()
                return {"msg": "Password Updated"}
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="New Password and Confirm Password does not match",
                )
    # Raise Exception if the user not logged-in and doesn't provide the data needed to reset their password
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="You must login to do this action",
    )


@router.get("/me", response_model=schema.UserOut)
def get_user(current_user: schema.UserOut = Depends(oauth2.get_current_user)):
    return current_user
