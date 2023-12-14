import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv


def send(email_ids: [str], subject: str, body: str):
    for email_id in email_ids:
        message = MIMEMultipart()
        message["From"] = os.getenv("MAIL_USER")
        message["To"] = email_id
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(os.getenv("MAIL_USER"), os.getenv("MAIL_PASS"))

            server.sendmail(os.getenv("MAIL_USER"), email_id, message.as_string())


if __name__ == "__main__":
    load_dotenv()
    send(
        ["kishor1445t@gmail.com", "kishor1445@icloud.com", "kishorpriya2005@gmail.com"],
        "Testing",
        "just a testing email",
    )
