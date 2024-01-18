from pydantic import EmailStr
from email_validator import validate_email
from fastapi import APIRouter, status, HTTPException, Depends
from sqlmodel import Session, select
from sqlalchemy.exc import IntegrityError
from app.db.db import get_db
from app.db.models import Mailing_List

router = APIRouter(prefix="/mail", tags=["Mail"])


@router.get(
    "/subscribe",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {
                        "msg": "You've successfully subscribed to our mailing list"
                    }
                }
            },
        },
        409: {
            "description": "Conflict Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Looks like you've already subscribed to our mailing list"
                    }
                }
            },
        },
    },
)
def subscribe(email: EmailStr, db: Session = Depends(get_db)):
    """
    Adds the email to mailing list
    """
    # Checks if the domain can get email
    email = validate_email(email, check_deliverability=True).normalized
    try:
        db.add(Mailing_List(email=email))
        db.commit()
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Looks like you've already subscribed to our mailing list",
        )
    return {"msg": "You've successfully subscribed to our mailing list"}


@router.get(
    "/unsubscribe",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        204: {
            "description": "Successful Response",
            "content": {"application/json": {"example": ""}},
        },
        404: {
            "description": "Not Found Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "Oops! Your email not found in our mailing list"
                    }
                }
            },
        },
    },
)
def unsubscribe(email: EmailStr, db: Session = Depends(get_db)):
    """
    Removes the email from mailing list
    """
    res = db.exec(select(Mailing_List).where(Mailing_List.email == email)).first()
    if not res:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Oops! Your email not found in our mailing list",
        )
    db.delete(res)
    db.commit()
    return {"msg": "You've successfully unsubscribed to our mailing list"}
