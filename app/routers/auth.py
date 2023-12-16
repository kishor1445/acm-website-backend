import sqlite3
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schema, oauth2
from utils.security import verify

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/login", response_model=schema.Token)
def login(data: OAuth2PasswordRequestForm = Depends()):
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT password, admin FROM users WHERE email_id = ?", (data.username,)
        )
        res = cur.fetchone()
        if not res or not verify(data.password, res[0]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
            )
        access_token = oauth2.create_access_token(
            {"email_id": data.username, "admin": res[1]}
        )

        return {"access_token": access_token, "token_type": "bearer"}
