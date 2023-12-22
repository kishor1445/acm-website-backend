import sqlite3
import pytz
from typing import List
from datetime import datetime
from fastapi import APIRouter, status, HTTPException, Path, Depends
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from .. import schema, oauth2
from utils.mail import normalize
from utils.others import get_dict, get_dict_one
from utils.security import verify, hash_, check_pass

router = APIRouter(prefix="/members", tags=["Members"])
IST = pytz.timezone("Asia/Kolkata")


@router.post("/", response_model=schema.MemberOut)
def create_member(
    data: schema.MemberCreate,
):
    """
    Adds a members
    """
    data.email_id = normalize(data.email_id)
    check_pass(data.password)
    data.password = hash_(data.password)
    _data = data.model_dump()
    _data["position"] = data.position.value
    _data["department"] = data.department.value
    _data["chapter"] = data.chapter.value
    _data["joined_at"] = datetime.now(IST)
    try:
        with sqlite3.connect("acm.db") as db:
            cur = db.cursor()
            cur.execute(
                """
                    INSERT INTO members 
                        VALUES (:reg_no,:name,:email_id,:password,:position,:department,:season,:chapter,:pic_url, 
                        :linkedin_tag,:twitter_tag,:instagram_tag,:facebook_tag,:joined_at)
                    """,
                _data,
            )
            db.commit()
            cur.execute("SELECT * FROM members WHERE reg_no = ?", (data.reg_no,))
    except sqlite3.IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Member already exists."
        )
    return get_dict_one(cur.fetchone(), cur.description)
    # raise HTTPException(
    #     status_code=status.HTTP_403_FORBIDDEN,
    #     detail="You don't have permission to perform this action.",
    # )


@router.post("/login", response_model=schema.TokenData)
def login_member(data: OAuth2PasswordRequestForm = Depends()):
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            "SELECT reg_no, password FROM members WHERE email_id = ?", (data.username,)
        )
        res = cur.fetchone()
        if not res or not verify(data.password, res[1]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Credentials"
            )
        access_token = oauth2.create_access_token({"reg_no": res[0], "type": "member"})
        return {"access_token": access_token, "token_type": "bearer"}


@router.patch("/", response_model=schema.MemberOut)
def update_member(
    data: schema.MemberUpdate,
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
    if current_member.reg_no == data.reg_no:
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
        _data["new_department"] = data.new_department.value if data.new_department else None
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
            cur.execute("SELECT * FROM members WHERE reg_no = ?", (reg_no,))
        return get_dict_one(cur.fetchone(), cur.description)
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to perform this action.",
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_member(
    data: schema.MemberDelete,
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
    if current_member.reg_no == data.reg_no:
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


@router.get("/department/{department}", response_model=List[schema.MemberOut])
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
    return get_dict(res, cur.description)


@router.get("/department/{department}/{season}", response_model=List[schema.MemberOut])
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
    return get_dict(res, cur.description)


@router.get("/position/{position}", response_model=List[schema.MemberOut])
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
    return get_dict(res, cur.description)


@router.get("/position/{position}/{season}", response_model=List[schema.MemberOut])
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
    return get_dict(res, cur.description)


@router.get("/chapter/{chapter}", response_model=List[schema.MemberOut])
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
    return get_dict(res, cur.description)


@router.get("/chapter/{chapter}/{season}", response_model=List[schema.MemberOut])
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
    return get_dict(res, cur.description)
