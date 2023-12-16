import sqlite3
from datetime import datetime
from fastapi import APIRouter, status, HTTPException, Depends
from .. import schema, oauth2
from utils.others import get_dict

router = APIRouter(
    prefix="/events",
    tags=["Events"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_event(data: schema.EventCreate, current_user: schema.TokenData = Depends(oauth2.get_current_user)):
    """
    Make an event
    """
    print(current_user)
    _id = data.name.replace(" ", "_").lower() + f"_{data.start.date()}"
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        try:
            cur.execute(
                """
                        INSERT INTO events (id, name, description, venue, start, end, link)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                (
                    _id,
                    data.name,
                    data.description,
                    data.venue,
                    data.start,
                    data.end,
                    data.link,
                ),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Event Already Exists."
            )
        db.commit()
    return {"message": "Event Created Successfully."}


@router.get("/")
def events():
    """
    Retrieves all the events
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM events ORDER BY start;")
        res = cur.fetchall()
    return {"events": get_dict(res, cur.description)}


@router.get("/upcoming")
def upcoming_events():
    """
    Retrieves all the upcoming events
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM events WHERE start > CURRENT_TIMESTAMP ORDER BY start;"
        )
        res = cur.fetchall()
    return {"events": get_dict(res, cur.description)}


@router.get("/past")
def past_events():
    """
    Retrieves all the past events
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM events WHERE start < CURRENT_TIMESTAMP ORDER BY start;"
        )
        res = cur.fetchall()
    return {"events": get_dict(res, cur.description)}


@router.patch("/")
def update_event(data: schema.EventUpdate):
    """
    Updates an event
    """
    _id = data.name.replace(" ", "_").lower() + f"_{data.date}"
    data = dict(filter(lambda x: x[1] is not None, data.model_dump().items()))
    data.pop("name")
    data.pop("date")
    data = dict(map(lambda x: (x[0].replace("new_", ""), x[1]), data.items()))
    k = data.keys()
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        old_data = cur.execute("SELECT name, start FROM events WHERE id = ?", (_id,))
        old_data = old_data.fetchone()
    if not old_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Event Not Found"
        )
    if "name" in k and "start" in k:
        data["id"] = data["name"].replace(" ", "_").lower() + f"_{data['start'].date()}"
    elif "name" in k:
        data["id"] = (
            data["name"].replace(" ", "_").lower()
            + f"_{datetime.strptime(old_data[1], '%Y-%m-%d %H:%M:%S').date()}"
        )
    elif "start" in k:
        data["id"] = old_data[0].replace(" ", "_").lower() + f"_{data['start'].date()}"
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        for k, v in data.items():
            cur.execute(f"UPDATE events SET {k} = ? WHERE id = ?", (v, _id))
            if k == "id":
                _id = v
        db.commit()
    return {"message": "Updated Successfully."}


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(data: schema.EventDelete):
    """
    Deletes an event
    """
    _id = data.name.replace(" ", "_").lower() + f"_{data.date}"
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM events WHERE id = ?", (_id,))
        if not cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Event Not Found."
            )
        cur.execute("DELETE FROM events WHERE id = ?", (_id,))
        db.commit()
