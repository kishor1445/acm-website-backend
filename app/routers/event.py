import sqlite3
from datetime import datetime
from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from .. import schema, oauth2
from utils.others import get_dict, event_responses_200

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    responses={
        201: {
            "description": "Successful Response",
            "content": {
                "application/json": {
                    "example": {"message": "Event Created Successfully."}
                }
            },
        },
        400: {
            "description": "Already Exists",
            "content": {
                "application/json": {"example": {"detail": "Event Already Exists."}}
            },
        },
        401: {
            "description": "Unauthorized Error",
            "content": {
                "application/json": {
                    "examples": {
                        "authorization_required": {
                            "value": {"detail": "Not authenticated"}
                        },
                        "invalid_token": {
                            "value": {"detail": "Could not validate credentials"}
                        },
                    }
                }
            },
        },
        403: {
            "description": "Forbidden Error",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "You don't have permission to perform this action."
                    }
                }
            },
        },
    },
)
def create_event(
    data: schema.EventCreate,
    current_user: schema.TokenData = Depends(oauth2.get_current_user),
):
    """
    Makes an event
    """
    if current_user.admin:
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
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Event Already Exists.",
                )
            db.commit()
        return {"message": "Event Created Successfully."}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )


@router.get(
    "/",
    response_model=List[schema.EventOut],
    responses=event_responses_200()
)
def events():
    """
    Retrieves all the events
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM events ORDER BY start;")
        res = cur.fetchall()
    return {"events": get_dict(res, cur.description)}


@router.get(
    "/upcoming",
    response_model=List[schema.EventOut],
    responses=event_responses_200()
)
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


@router.get(
    "/past",
    response_model=List[schema.EventOut],
    responses=event_responses_200()
)
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
def update_event(
    data: schema.EventUpdate,
    current_user: schema.TokenData = Depends(oauth2.get_current_user),
):
    """
    Updates an event
    """
    if current_user.admin:
        _id = data.name.replace(" ", "_").lower() + f"_{data.date}"
        data = dict(filter(lambda x: x[1] is not None, data.model_dump().items()))
        data.pop("name")
        data.pop("date")
        data = dict(map(lambda x: (x[0].replace("new_", ""), x[1]), data.items()))
        k = data.keys()
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            old_data = cur.execute(
                "SELECT name, start FROM events WHERE id = ?", (_id,)
            )
            old_data = old_data.fetchone()
        if not old_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Event Not Found"
            )
        if "name" in k and "start" in k:
            data["id"] = (
                data["name"].replace(" ", "_").lower() + f"_{data['start'].date()}"
            )
        elif "name" in k:
            data["id"] = (
                data["name"].replace(" ", "_").lower()
                + f"_{datetime.strptime(old_data[1], '%Y-%m-%d %H:%M:%S').date()}"
            )
        elif "start" in k:
            data["id"] = (
                old_data[0].replace(" ", "_").lower() + f"_{data['start'].date()}"
            )
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            for k, v in data.items():
                cur.execute(f"UPDATE events SET {k} = ? WHERE id = ?", (v, _id))
                if k == "id":
                    _id = v
            db.commit()
        return {"message": "Updated Successfully."}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    data: schema.EventDelete,
    current_user: schema.TokenData = Depends(oauth2.get_current_user),
):
    """
    Deletes an event
    """
    if current_user.admin:
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
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )
