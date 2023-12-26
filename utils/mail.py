import smtplib
import os
import time
from typing import List
from fastapi import HTTPException, status
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import (
    validate_email,
    EmailNotValidError,
    EmailUndeliverableError,
    ValidatedEmail,
)


TRUSTED_DOMAIN = (
    "gmail.com",
    "outlook.com",
    "yahoo.in",
    "icloud.com",
    "proton.me",
    "protonmail.com",
)


def send(email_ids: List[str], subject: str, html_body: str) -> None:
    """
    sends mail to those email_ids
    """
    with smtplib.SMTP(
        os.getenv("MAIL_SERVER", ""), int(os.getenv("MAIL_PORT", 0))
    ) as mail_server:
        mail_server.starttls()
        mail_server.login(os.getenv("MAIL_USER", ""), os.getenv("MAIL_PASS", ""))
        for email_id in email_ids:
            is_trusted_domain(email_id)
            if email_id.startswith("acm-test-"):
                continue
            msg = MIMEMultipart()
            msg["From"] = os.getenv("MAIL_USER", "")
            msg["To"] = email_id
            msg["Subject"] = subject
            msg.attach(MIMEText(html_body, "html"))
            mail_server.sendmail(os.getenv("MAIL_USER", ""), email_id, msg.as_string())
            time.sleep(2)


def is_trusted_domain(email_id: str) -> str:
    """
    Checks whether the email id is valid or not and the domain is in trusted domain
    """
    try:
        email: ValidatedEmail = validate_email(email_id, check_deliverability=False)
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


def normalize(email_id: str) -> str:
    """
    Removes unwanted characters
    """
    try:
        email: ValidatedEmail = validate_email(email_id, check_deliverability=False)
    except EmailNotValidError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email ID"
        )
    return email.normalized
