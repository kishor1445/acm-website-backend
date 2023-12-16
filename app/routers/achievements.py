import sqlite3
from fastapi import APIRouter

router = APIRouter(
    prefix="/achievements",
    tags=["Achievements"]
)


@router.get("/")
def achievements():
    """
    Shows how many events have happened and how many members are/were in ACM and ACM-W SIST
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT COUNT(*) FROM events;")
        event_res = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM members;")
        member_res = cur.fetchone()
        cur.execute("SELECT COUNT(*) FROM users;")
        participants_res = cur.fetchone()
    _data = {"events": event_res[0], "members": member_res[0], "participants": participants_res[0]}
    return {"data": _data}
