import sqlite3
from fastapi import APIRouter, status, Path, HTTPException
from .. import schema
from utils.mail import send, TRUSTED_DOMAIN, is_trusted_domain, normalize

router = APIRouter(
    prefix="/mail",
    tags=["Mail"]
)


@router.post("/send_mail")
def send_mail(data: schema.MailP):
    """
    Sends a mail to the email id with subject and body
    """
    send(
        [data.email_id],
        "Demo Subject Text",
        f"Reg no.: {data.reg_no}\nName: {data.name}\nDepartment: {data.dep}",
    )
    return {"message": "Mail sent successfully"}


@router.get(
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
def subscribe(
    email_id: str = Path(
        ..., title="Email ID", description="Email ID to subscribe the mailing service"
    )
):
    """
    Adds the email to mailing service
    """
    email_id = is_trusted_domain(email_id)
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        try:
            cur.execute("INSERT INTO mailing_list(email_id) VALUES (?);", (email_id,))
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Oops! It seems like your email address is already subscribed to our mailing list.",
            )
        db.commit()
    return {"message": "You've successfully subscribed to our mailing list."}


@router.delete(
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
def unsubscribe(
    email_id: str = Path(
        ..., title="Email ID", description="Email ID to unsubscribe the mailing service"
    )
):
    """
    Removes the email from mailing service
    """
    email_id = normalize(email_id)
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT email_id FROM mailing_list WHERE email_id = ?;", (email_id,)
        )
        res = cur.fetchone()
        if not res:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Oops! Your email address is not in our mailing list.",
            )
        cur.execute("DELETE FROM mailing_list WHERE email_id = ?;", (email_id,))
