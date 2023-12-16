import sqlite3
from fastapi import APIRouter, status, HTTPException, Depends
from utils.others import get_dict
from .. import schema, oauth2

router = APIRouter(
    prefix="/blogs",
    tags=["Blogs"]
)


@router.post("/", status_code=status.HTTP_201_CREATED)
def create_blog(data: schema.BlogCreate, current_user: schema.TokenData = Depends(oauth2.get_current_user)):
    """
    Creates a blog
    """
    if current_user.admin:
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            try:
                cur.execute(
                    "INSERT INTO blogs VALUES(:title, :description, :date, :author, :image_url, :link)",
                    data.model_dump(),
                )
            except sqlite3.IntegrityError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Title Already Exists"
                )
            db.commit()
        return {"message": "Blog Added."}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action."
        )


@router.get("/")
def blogs():
    """
    Retrieves all the blogs from the database in oldest to newest blog order
    """
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM blogs ORDER BY date;")
        res = cur.fetchall()
    return {"data": get_dict(res, cur.description)}


@router.patch("/")
def update_blog(data: schema.BlogUpdate, current_user: schema.TokenData = Depends(oauth2.get_current_user)):
    if current_user.admin:
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
        return {"message": "Updated Successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action."
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(data: schema.BlogDelete, current_user: schema.TokenData = Depends(oauth2.get_current_user)):
    """
    Deletes the blog
    """
    if current_user.admin:
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM blogs WHERE title = ?", (data.title,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Blog Not Found"
                )
            cur.execute("DELETE FROM blogs WHERE title = ?", (data.title,))
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action."
        )