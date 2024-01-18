import csv
from io import StringIO
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlmodel import Session, select
from app import oauth2, schema
from app.db.db import get_db
from app.db.models import Blogs, Event_Registeration, Events, Mailing_List, Users, Members

router = APIRouter(prefix="/export")

@router.get("/")
def get_export(
    table: schema.Tables,
    db: Session = Depends(get_db), 
    _: schema.MemberOut = Depends(oauth2.get_current_member)
):
    table_map = {
        "users": Users,
        "members": Members,
        "events": Events,
        "event_registeration": Event_Registeration,
        "blogs": Blogs,
        "mailing_list": Mailing_List
    }
    db_data = db.exec(select(table_map[table.value])).all()
    mem_data = StringIO()
    writer = csv.writer(mem_data)
    csv_title = list(table_map[table.value].__annotations__.keys())
    writer.writerow(csv_title)
    for data in db_data:
        data_dict = data.model_dump()
        ordered_data = []
        for title in csv_title:
            ordered_data.append(data_dict[title])
        writer.writerow(ordered_data)
    mem_data.seek(0)
    return StreamingResponse(mem_data, media_type="text/csv")

