import sqlite3
from fastapi import APIRouter, status, HTTPException, Path, Depends
from .. import schema, oauth2
from utils.others import get_dict

router = APIRouter(prefix="/members", tags=["Members"])


@router.post("/")
def create_member(
    data: schema.MemberCreate,
    current_user: schema.TokenData = Depends(oauth2.get_current_user),
):
    """
    Adds a members
    """
    if current_user.admin:
        _data = data.model_dump()
        _data["position"] = data.position.value
        _data["department"] = data.department.value
        _data["chapter"] = data.chapter.value
        try:
            with sqlite3.connect("acm.db") as db:
                cur = db.cursor()
                cur.execute(
                    """
                        INSERT INTO members 
                            VALUES (:reg_no, :name, :position, :department, :season, :chapter,:pic_url, 
                            :linkedin_tag, :twitter_tag, :instagram_tag, :facebook_tag)
                        """,
                    _data,
                )
                db.commit()
        except sqlite3.IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Member already exists."
            )
        return {"message": "Member Added."}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )


@router.patch("/")
def update_member(
    data: schema.MemberUpdate,
    current_user: schema.TokenData = Depends(oauth2.get_current_user),
):
    if current_user.admin:
        reg_no = data.reg_no
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM members WHERE reg_no = ?", (reg_no,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Member Not Found"
                )
        _data = data.model_dump()
        _data["new_position"] = data.new_position.value if data.new_position else None
        _data["new_department"] = (
            data.new_department.value if data.new_department else None
        )
        _data["new_chapter"] = data.new_chapter.value if data.new_chapter else None
        _data = dict(filter(lambda x: x[1] is not None, _data.items()))
        _data.pop("reg_no")
        _data = dict(map(lambda x: (x[0].replace("new_", ""), x[1]), _data.items()))
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            for k, v in _data.items():
                cur.execute(f"UPDATE members SET {k} = ? WHERE reg_no = ?", (v, reg_no))
                if k == "reg_no":
                    reg_no = v
            db.commit()
        return {"message": "Updated Successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )


@router.delete(
    "/",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_member(
    data: schema.MemberDelete,
    current_user: schema.TokenData = Depends(oauth2.get_current_user),
):
    if current_user.admin:
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            cur.execute("SELECT * FROM members WHERE reg_no = ?", (data.reg_no,))
            if not cur.fetchone():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Member Not Found"
                )
            cur.execute("DELETE FROM members WHERE reg_no = ?", (data.reg_no,))
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )


@router.get("/department/{department}")
def members_by_department(
    department: schema.DepartmentType = Path(
        ...,
        title="Department Name",
        description="Department members to get.",
    )
):
    """
    Retrieves the members by their department
    """
    department = department.value
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM members WHERE department = ?", (department,))
        res = cur.fetchall()
    return {"data": get_dict(res, cur.description)}


@router.get("/department/{department}/{season}")
def members_by_department_season(
    department: schema.DepartmentType = Path(
        ...,
        title="Department Name",
        description="Department Name to retrieve Members from that department",
    ),
    season: int = Path(
        ..., title="Season", description="Which season they belongs to."
    ),
):
    """
    Retrieves the members by their department with season number
    """
    department = department.value
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM members WHERE department = ? and season = ?",
            (department, season),
        )
        res = cur.fetchall()
    return {"data": get_dict(res, cur.description)}


@router.get("/position/{position}")
def members_by_position(
    position: schema.PositionType = Path(
        ...,
        title="Position",
        description="The position of the member like chair, vice-chair, faculty or member",
    )
):
    """
    Retrieves the members by their position (i.e. member, chair, vice-chair, faculty)
    """
    position = position.value
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM members WHERE position = ?", (position,))
        res = cur.fetchall()
    return {"data": get_dict(res, cur.description)}


@router.get("/position/{position}/{season}")
def members_by_position_season(
    position: schema.PositionType = Path(
        ...,
        title="Position",
        description="The position of the member like chair, vice-chair, faculty or member",
    ),
    season: int = Path(
        ..., title="Season", description="Which season they belongs to."
    ),
):
    """
    Retrieves the members by their position (i.e. member, chair, vice-chair, faculty) with season number
    """
    position = position.value
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM members WHERE position = ? and season = ?",
            (position, season),
        )
        res = cur.fetchall()
    return {"data": get_dict(res, cur.description)}


@router.get("/chapter/{chapter}")
def members_by_chapter(
    chapter: schema.ChapterType = Path(
        ..., title="Chapter", description="Which Chapter they belongs to."
    )
):
    """
    Retrieves the members of specific chapters (i.e. ACM, ACM-W)
    """
    chapter = chapter.value
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute("SELECT * FROM members WHERE chapter = ?", (chapter,))
        res = cur.fetchall()
    return {"data": get_dict(res, cur.description)}


@router.get("/chapter/{chapter}/{season}")
def members_by_chapter_season(
    chapter: schema.ChapterType = Path(
        ..., title="Chapter", description="Which Chapter they belongs to."
    ),
    season: int = Path(
        ..., title="Season", description="Which season they belongs to."
    ),
):
    """
    Retrieves the members of specific chapter (i.e. ACM, ACM-W) with season number
    """
    chapter = chapter.value
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT * FROM members WHERE chapter = ? and season = ?", (chapter, season)
        )
        res = cur.fetchall()
    return {"data": get_dict(res, cur.description)}
