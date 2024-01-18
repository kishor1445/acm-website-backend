from fastapi import APIRouter, Depends
from sqlmodel import Session, func, select
from app.db.db import get_db
from app.db.models import Events, Members, Users

router = APIRouter(prefix="/achievements")

@router.get("/")
def get_achievements(db: Session = Depends(get_db)):
    """
    Shows the number of members, users and events
    """
    query = select(func.count())

    members_count = db.exec(query.select_from(Members)).one()
    users_count = db.exec(query.select_from(Users)).one()
    events_count = db.exec(query.select_from(Events)).one()
    
    return {"members_count": members_count, "users_count": users_count, "events_count": events_count}

