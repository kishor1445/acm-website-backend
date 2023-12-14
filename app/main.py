import uvicorn
import sqlite3
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from utils.mail import send
from utils.db import create_tables
from dotenv import load_dotenv

load_dotenv()
create_tables()

app = FastAPI(
    title="ACM-SIST Backend API",
    contact={
        "name": "ACM-SIST",
        "url": "https://example.com",
        "email": "acm.sathyabama@gmail.com",
    },
)

app.mount("/static", StaticFiles(directory="static"), name="static")


class MailP(BaseModel):
    email_id: str
    name: str
    reg_no: str
    dep: str


TRUSTED_DOMAIN = (
    "gmail.com",
    "outlook.com",
    "yahoo.in",
    "icloud.com",
    "proton.me",
    "protonmail.com",
)


def is_trusted_domain(email: str) -> None:
    try:
        domain = email.split("@")[1]
    except IndexError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Email ID."
        )
    if domain not in TRUSTED_DOMAIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Only {', '.join(TRUSTED_DOMAIN)} are accepted",
        )
    return None


@app.post("/send_mail")
def send_mail(data: MailP):
    send(
        [data.email_id],
        "Demo Subject Text",
        f"Reg no.: {data.reg_no}\nName: {data.name}\nDepartment: {data.dep}",
    )
    return {"message": "Mail sent successfully"}


@app.get(
    "/subscribe/{email_id}",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "message": "You've successfully subscribed to our mailing list."
                    }
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {"value": "Invalid Email ID."},
                        "untrusted_domain": {
                            "value": f"Only {', '.join(TRUSTED_DOMAIN)} are accepted"
                        },
                    }
                }
            },
        },
    },
)
def subscribe(email_id: str):
    """Adds the email to mailing list"""
    is_trusted_domain(email_id)
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        res = cur.execute(
            "SELECT email_id from mailing_list WHERE email_id = ?", (email_id,)
        )
        if res.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Oops! It seems like your email address is already subscribed to our mailing list.",
            )
        cur.execute("INSERT INTO mailing_list(email_id) VALUES (?)", (email_id,))
        db.commit()
    return {"message": "You've successfully subscribed to our mailing list."}


@app.delete(
    "/subscribe/{email_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ""}},
        },
        404: {
            "description": "Not Found",
            "content": {
                "application/json": {
                    "example": "Oops! Your email address is not in our mailing list."
                }
            },
        },
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {"value": "Invalid Email ID."},
                        "untrusted_domain": {
                            "value": f"Only {', '.join(TRUSTED_DOMAIN)} are accepted"
                        },
                    }
                }
            },
        },
    },
)
def unsubscribe(email_id: str):
    """
    Removes the email from mailing list
    """
    is_trusted_domain(email_id)
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT email_id FROM mailing_list WHERE email_id = ?", (email_id,))
        res = cur.fetchone()
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Oops! Your email address is not in our mailing list.",
            )
        cur.execute("DELETE FROM mailing_list WHERE email_id = ?", (email_id,))


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
