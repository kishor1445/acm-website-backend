import sqlite3
import pytz
from datetime import datetime
from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schema, oauth2
from utils.security import hash_, check_pass, verify
from utils.mail import is_trusted_domain, TRUSTED_DOMAIN
from utils.others import get_dict_one

router = APIRouter(prefix="/users", tags=["Users"])
IST = pytz.timezone("Asia/Kolkata")


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.UserOut,
    responses={
        400: {
            "description": "Bad Request",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_email": {"value": {"detail": "Invalid Email ID"}},
                        "untrusted_domain": {
                            "value": {
                                "detail": f"Only {', '.join(TRUSTED_DOMAIN)} are accepted"
                            }
                        },
                        "already_exists": {"value": {"detail": "User Already Exists."}},
                    }
                }
            },
        },
    },
)
def create_user(data: schema.UserCreate):
    data.email_id = is_trusted_domain(data.email_id)
    check_pass(data.password)
    data.password = hash_(data.password)
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        _data = data.model_dump()
        _data["joined_at"] = datetime.now(IST)
        try:
            cur.execute(
                """INSERT INTO users VALUES(
                            :reg_no,:name,:email_id,:password,:department,:university,:year,:joined_at
                         )""",
                _data,
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="User Already Exists."
            )
        db.commit()
        cur.execute("SELECT * FROM users WHERE reg_no = ?", (data.reg_no,))
    return get_dict_one(cur.fetchone(), cur.description)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    data: schema.UserDelete,
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
    if current_member.reg_no == data.reg_no:
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM users WHERE reg_no = ?", (data.reg_no,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="User Not Found"
                )
            cur.execute("DELETE FROM users WHERE reg_no = ?", (data.reg_no,))
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )


@router.post("/login", response_model=schema.TokenData)
def login(data: OAuth2PasswordRequestForm = Depends()):
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT reg_no, password FROM users WHERE email_id = ?", (data.username,)
        )
        res = cur.fetchone()
        if not res or not verify(data.password, res[1]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
            )
        access_token = oauth2.create_access_token({"reg_no": res[0], "type": "user"})

        return {"access_token": access_token, "token_type": "bearer"}
