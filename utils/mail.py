import smtplib
import os
import time
from fastapi import HTTPException, status
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError, EmailUndeliverableError


TRUSTED_DOMAIN = (
    "gmail.com",
    "outlook.com",
    "yahoo.in",
    "icloud.com",
    "proton.me",
    "protonmail.com",
)


def send(email_ids: [str], subject: str, body: str) -> None:
    """
    sends mail to those email_ids
    """
    for email_id in email_ids:
        is_trusted_domain(email_id)
        if email_id.startswith("acm-test-"):
            continue
        message = MIMEMultipart()
        message["From"] = os.getenv("MAIL_USER")
        message["To"] = email_id
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.getenv("MAIL_USER"), os.getenv("MAIL_PASS"))

            server.sendmail(os.getenv("MAIL_USER"), email_id, message.as_string())
        time.sleep(2)


def is_trusted_domain(email: str) -> str:
    """
    Checks whether the email id is valid or not and the domain is in trusted domain
    """
    try:
        email = validate_email(email, check_deliverability=False)
    except (EmailUndeliverableError, EmailNotValidError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email ID"
        )
    domain = email.domain
    if domain not in TRUSTED_DOMAIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {', '.join(TRUSTED_DOMAIN)} are accepted.",
        )
    return email.normalized


def normalize(email: str) -> str:
    """
    Removes unwanted characters
    """
    try:
        email = validate_email(email, check_deliverability=False)
    except EmailNotValidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email ID"
        )
    return email.normalized
