import sqlite3
from typing import List
from fastapi import APIRouter, status, HTTPException, Depends
from utils.others import get_dict, get_dict_one
from .. import schema, oauth2

router = APIRouter(prefix="/blogs", tags=["Blogs"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schema.BlogCreate)
def create_blog(
    data: schema.BlogCreate,
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
    """
    Creates a blog
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        try:
            cur.execute(
                "INSERT INTO blogs VALUES(:title, :description, :date, :author, :image_url, :link)",
                data.model_dump(),
            )
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Title Already Exists",
            )
        db.commit()
        cur.execute("SELECT * FROM blogs WHERE title = ?", (data.title,))
    return get_dict_one(cur.fetchone(), cur.description)
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to perform this action.",
    #     )


@router.get("/", response_model=List[schema.BlogOut])
def blogs():
    """
    Retrieves all the blogs from the database in oldest to newest blog order
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM blogs ORDER BY date;")
    return get_dict(cur.fetchall(), cur.description)


@router.patch("/", response_model=schema.BlogOut)
def update_blog(
    data: schema.BlogUpdate,
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
    title = data.title
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM blogs WHERE title = ?", (title,))
        if not cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Blog Not Found"
            )
    _data = data.model_dump()
    _data = dict(filter(lambda x: x[1] is not None, _data.items()))
    _data.pop("title")
    _data = dict(map(lambda x: (x[0].replace("new_", ""), x[1]), _data.items()))
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        for k, v in _data.items():
            cur.execute(f"UPDATE blogs SET {k} = ? WHERE title = ?", (v, title))
            if k == "title":
                title = v
        db.commit()
        cur.execute("SELECT * FROM blogs WHERE title = ?", (title,))
    return get_dict_one(cur.fetchone(), cur.description)
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to perform this action.",
    #     )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(
    data: schema.BlogDelete,
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
    """
    Deletes the blog
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM blogs WHERE title = ?", (data.title,))
        if not cur.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Blog Not Found"
            )
        cur.execute("DELETE FROM blogs WHERE title = ?", (data.title,))
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="You don't have permission to perform this action.",
    #     )
