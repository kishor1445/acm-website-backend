import csv
import io
import sqlite3
from fastapi import APIRouter, Depends, Path
from fastapi.responses import StreamingResponse
from .. import oauth2, schema


router = APIRouter(prefix="/export")


def get_csv_data(statement):
    with sqlite3.connect("acm.db") as db:
        cur = db.execute(statement)
        data = io.StringIO()
        writer = csv.writer(data)
        writer.writerow([x[0] for x in cur.description])
        writer.writerows(cur.fetchall())
        data.seek(0)
    return data


@router.get("/{table}")
def export(
    table: schema.Tables = Path(
        ...,
        title="Database table name",
        description="Converts the given database table into csv file",
    )
):
    if table == schema.Tables.members:
        statement = "SELECT reg_no, name, email_id, position, department, season, chapter, pic_url, linkedin_tag, twitter_tag, instagram_tag, facebook_tag, joined_at FROM members"
    else:
        statement = f"SELECT * FROM {table.value}"

    return StreamingResponse(
        get_csv_data(
            statement
        ),
        media_type="text/csv"
    )
