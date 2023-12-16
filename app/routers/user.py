import sqlite3
from fastapi import APIRouter, status, HTTPException
from .. import schema
from utils.security import hash_
from utils.mail import is_trusted_domain

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_user(data: schema.UserCreate):
    email_id = is_trusted_domain(data.email_id)
    data.email_id = email_id
    hashed_pass = hash_(data.password)
    data.password = hashed_pass
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        _data = data.model_dump()
        _data["admin"] = False
        try:
            cur.execute(
                "INSERT INTO users VALUES(:email_id, :password, :admin, CURRENT_TIMESTAMP,:university, :department, :year)",
                _data
            )
        except sqlite3.IntegrityError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User Already Exists.")
        db.commit()
    return {"message": "User Created."}
