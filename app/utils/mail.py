import smtplib
import os
import time
from typing import List
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send(
    email_ids: List[str],
    subject: str,
    html_body: str,
    mailing_list: bool = False,
    unsubscribe_url: str = "",
) -> None:
    """
    sends mail to those email_ids
    """
    with smtplib.SMTP(
        os.getenv("MAIL_SERVER", "smtp.gmail.com"), int(os.getenv("MAIL_PORT", 587))
    ) as mail_server:
        mail_server.starttls()
        mail_server.login(os.getenv("MAIL_USER", ""), os.getenv("MAIL_PASS", ""))
        for email_id in email_ids:
            # Don't send email if it is a test mail
            if email_id.startswith("test-acm-sist"):
                continue
            msg = MIMEMultipart()
            msg["From"] = os.getenv("MAIL_USER", "")
            msg["To"] = email_id
            msg["Subject"] = subject
            if mailing_list:
                msg.add_header("List-Unsubscribe", unsubscribe_url)
            msg.attach(MIMEText(html_body, "html"))
            mail_server.sendmail(os.getenv("MAIL_USER", ""), email_id, msg.as_string())
            time.sleep(2)


def verification_mail(request, verify_link) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ACM-SIST | Verify</title>
    </head>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px; background-color: #f8f8f8;">
            <div style="text-align: center;"><img src="{request.url.scheme}://{request.url.hostname}/static/logo.png" alt="ACM Logo" style="max-width: 100%; height: auto; margin-bottom: 20px;" /></div>
            <h2 style="color: #333;">Account Verification</h2>
            <p>Welcome to the ACM-SIST | Sathyabama Institute of Science and Technology</h2>
            <p>We're excited to have you on board. To complete your registration and start enjoying the benefits of our ACM-SIST community, please click the button below to verify your account:</p>
            <div style="text-align: center;"><a href="{verify_link}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 5px; margin-top: 15px;">Verify My Account</a></div>
            <p>If the button above doesn't work, you can also copy and past the following link into your browser:</p>
            <p>{verify_link}</p>
            <p>This verification only valid for 10 minutes</p>
            <p>Thank you for joining us!</p>

            <p>Best regards,<br />
            {os.getenv("ACM_SIST_CHAIR", "")}, Chair - ACM SIST<br>
            {os.getenv("ACM_W_SIST_CHAIR", "")}, Chair - ACM-W SIST</p>
        </div>
    </body>
    </html>
    """


def reset_password_mail(request, reset_password_link) -> str:
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>ACM-SIST | Reset Password</title>
    </head>
    <body style="font-family: Arial, sans-serif;">
        <div style="max-width: 600px; margin: 20px auto; padding: 20px; border: 1px solid #ccc; border-radius: 10px; background-color: #f8f8f8;">
            <div style="text-align: center;"><img src="{request.url.scheme}://{request.url.hostname}/static/logo.png" alt="ACM Logo" style="max-width: 100%; height: auto; margin-bottom: 20px;" /></div>
            <h2 style="color: #333;">Reset Password</h2>
            <p>Please click the below button to reset your password.</p>
            <p>If you didn't reuqest to reset your password please ignore this email.</p>
            <div style="text-align: center;"><a href="{reset_password_link}" style="display: inline-block; padding: 10px 20px; background-color: #007bff; color: #fff; text-decoration: none; border-radius: 5px; margin-top: 15px;">Reset Password</a></div>
            <p>If the button above doesn't work, you can also copy and past the following link into your browser:</p>
            <p>{reset_password_link}</p>
            <p>valid for only 10 minutes</p>

            <p>Best regards,<br />
            {os.getenv("ACM_SIST_CHAIR", "")}, Chair - ACM SIST<br>
            {os.getenv("ACM_W_SIST_CHAIR", "")}, Chair - ACM-W SIST</p>
        </div>
    </body>
    </html>
    """
