from datetime import datetime
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, or_, select
from app import oauth2, schema
from app.config import IST
from pathlib import Path
from app.db.db import get_db
from app.db.models import Events, Event_Registeration

router = APIRouter(prefix="/events")


@router.post("/", response_model=schema.EventOut)
def create_event(
    data: schema.CreateEvent,
    db: Session = Depends(get_db),
    _: schema.MemberOut = Depends(oauth2.get_current_member),
):
    event = Events(**data.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    event.start = event.start.astimezone(IST)
    event.end = event.end.astimezone(IST)
    return event


@router.get("/search", response_model=list[schema.EventOut])
def search_events(
    _id: UUID | None = Query(None, alias="id"),
    upcoming: bool = Query(False),
    past: bool = Query(False),
    db: Session = Depends(get_db),
):
    current_time = datetime.now(IST)
    if upcoming and past:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You can't use both past and upcoming at the same time. If you want to get all the events then send the same request with neither of past nor upcomming",
        )
    query = select(Events)
    if _id:
        query = query.where(Events.id == _id)
    elif upcoming:
        query = query.filter(or_(Events.start > current_time))
    elif past:
        query = query.filter(or_(Events.start <= current_time))
    events = db.exec(query).all()
    if events:
        for event in events:
            event.start = event.start.astimezone(IST)
            event.end = event.end.astimezone(IST)
    return events


@router.patch("/", response_model=schema.EventOut)
def update_event(
    data: schema.EventUpdate,
    db: Session = Depends(get_db),
    _: schema.MemberOut = Depends(oauth2.get_current_member),
):
    event = db.exec(select(Events).where(Events.id == data.id)).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event does not exist"
        )
    event_new_data = data.model_dump()
    for k, v in event_new_data.items():
        if k.startswith("new_") and v is not None:
            setattr(event, k.replace("new_", ""), v)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_event(
    data: schema.EventDelete,
    db: Session = Depends(get_db),
    _: schema.MemberOut = Depends(oauth2.get_current_member),
):
    event = db.exec(select(Events).where(Events.id == data.id)).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event does not exist"
        )
    db.delete(event)
    db.commit()


@router.post("/register")
def register_event(
    data: schema.RegisterEventCreate,
    db: Session = Depends(get_db),
    current_user: schema.UserOut = Depends(oauth2.get_current_user),
):
    event = db.exec(select(Events).where(Events.id == data.event_id)).first()
    if not event:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event does not exist"
        )
    if event.fee > 0:
        if not data.transaction_id:
            raise HTTPException(
                status_code=status.HTTP_402_PAYMENT_REQUIRED,
                detail=f"{event.name} registeration fee is ₹{event.fee}. Please provide transaction_id to verify",
            )
        if not data.screenshot_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Screenshot of the payment ₹{event.fee} is required for verification"
            )
        if not Path(f"payment_proof/{data.screenshot_id}").exists():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Did you upload the screenshot? We couldn't able to find that screenshot which belongs to that ID"
                    )
    if event.fee > 0:
        payment_status = "pending"
    else:
        payment_status = "verified"
    event_reg_data = data.model_dump()
    event_reg_data["user_reg_no"] = current_user.reg_no
    event_reg_data["status"] = payment_status
    event_reg = Event_Registeration(**event_reg_data)
    try:
        db.add(event_reg)
        db.commit()
        db.refresh(event_reg)
    except IntegrityError as e:
        if str(e.orig).endswith("transaction_id"):
            message = "Transaction ID already used"
        elif str(e.orig).endswith("screenshot_url"):
            message = "This screenshot url is already used"
        else:
            message = "You have already registed for this event"
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
    return event_reg

@router.get("/me")
def get_my_events(db: Session = Depends(get_db), current_user: schema.UserOut = Depends(oauth2.get_current_user)):
    my_events_reg = db.exec(select(Event_Registeration).where(Event_Registeration.user_reg_no == current_user.reg_no)).all()
    my_events = []
    for my_event_reg in my_events_reg:
        my_events.append(
            db.exec(select(Events).where(Events.id == my_event_reg.event_id)).first()
        )
    return {"events": my_events, "events_reg": my_events_reg}

@router.get("/verify", response_model=list[schema.RegisterEventOut])
def get_pending_verification(db: Session = Depends(get_db), _: schema.MemberOut = Depends(oauth2.get_current_member)):
    events_reg = db.exec(select(Event_Registeration).where(Event_Registeration.status == "pending")).all()
    return events_reg

