import sqlite3
import hashlib
from datetime import datetime
from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from .. import schema, oauth2
from utils.others import get_dict, event_responses_200, get_dict_one
from utils.mail import send

router = APIRouter(prefix="/events", tags=["Events"])


@router.post(
    "/",
    status_code=status.HTTP_201_CREATED,
    response_model=schema.EventOut,
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
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
    """
    Makes an event
    """
    data = data.model_dump()
    data["_id"] = data["name"].replace(" ", "_").lower() + f"_{data['start'].date()}"
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        try:
            cur.execute(
                """
                        INSERT INTO events (id, name, description, venue, start, end, fee, link)
                        VALUES (:_id, :name, :description, :venue, :start, :end, :fee, :link)
                    """,
                data,
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Event Already Exists.",
            )
        cur.execute("SELECT * FROM events WHERE id = ?", (data["_id"],))
        db.commit()
    return get_dict_one(cur.fetchone(), cur.description)
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to perform this action.",
    #     )


@router.get("/", response_model=List[schema.EventOut], responses=event_responses_200())
def events():
    """
    Retrieves all the events
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM events ORDER BY start;")
        res = cur.fetchall()
    return get_dict(res, cur.description)


@router.get(
    "/upcoming", response_model=List[schema.EventOut], responses=event_responses_200()
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
    return get_dict(res, cur.description)


@router.get(
    "/past", response_model=List[schema.EventOut], responses=event_responses_200()
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
    return get_dict(res, cur.description)


@router.patch("/", response_model=schema.EventOut)
def update_event(
    data: schema.EventUpdate,
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
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
        cur.execute("SELECT * FROM events WHERE id = ?", (_id,))
    return get_dict_one(cur.fetchone(), cur.description)
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to perform this action.",
    #     )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    data: schema.EventDelete,
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
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
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to perform this action.",
    #     )


@router.post("/register", response_model=schema.EventRegisterOut)
def register_event(
    data: schema.EventRegister,
    current_user: schema.UserOut = Depends(oauth2.get_current_user),
):
    free = False
    _data = data.model_dump()
    _data["user_id"] = current_user.reg_no
    _data[
        "event_reg_id"
    ] = f"{current_user.reg_no}#{hashlib.sha256(data.event_id.encode()).hexdigest()[:8]}{data.event_id.split('_')[-1].replace('-', '')}"
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT fee FROM events WHERE id = ?", (data.event_id,))
        res = cur.fetchone()
        if not res:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Event Not Found"
            )
        free = False if res[0] > 0.0 else True
        if not data.transaction_id and not free:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"required": "transaction_id", "payment": res[0]},
            )
        cur.execute(
            "SELECT * FROM event_registrations WHERE event_reg_id = ?",
            (_data["event_reg_id"],),
        )
        if cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Already Registered"
            )
        if data.transaction_id:
            cur.execute(
                """
                SELECT * FROM event_registrations WHERE transaction_id = ?
            """,
                (data.transaction_id,),
            )
            if cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Repeated transaction_id",
                )
        _data["status"] = "pending" if not free else "verified"
        cur.execute(
            """
            INSERT INTO event_registrations VALUES (
                :event_reg_id, :user_id, :event_id, :transaction_id, :status
            )""",
            _data,
        )
        db.commit()
        cur.execute(
            "SELECT * FROM event_registrations WHERE event_reg_id = ?",
            (_data["event_reg_id"],),
        )
        _data = get_dict_one(cur.fetchone(), cur.description)
        cur.execute("SELECT * FROM events WHERE id = ?", (_data["event_id"],))
        res = cur.fetchone()
        email_body = f"""
        {current_user.name},
            You have registered for {res[1]}
            
            Event Details:
                Name: {res[1]}
                {f'Description: {res[2]}' if res[2] is not None else ''}
                Venue: {res[3]}
                Event Starts at {res[4]}
                Event Ends at {res[5]}
                Registration Fee: {res[6] if not free else 'Free'}
                Link to the event: {res[7]}
        """
        send(
            [current_user.email_id],
            f"ACM: Event Registration {'Verification Under Progress' if not free else 'Successful'}",
            email_body,
        )
    return _data


@router.get("/my_events", response_model=schema.MyEventOut)
def my_events(current_user: schema.UserOut = Depends(oauth2.get_current_user)):
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM event_registrations WHERE user_id = ?",
            (current_user.reg_no,),
        )
        reg_event = get_dict(cur.fetchall(), cur.description)
        print(reg_event)
        event = []
        for x in reg_event:
            cur.execute("SELECT * FROM events WHERE id = ?", (x["event_id"],))
            event.append(get_dict_one(cur.fetchone(), cur.description))
    return {"event": event, "reg_event": reg_event}
