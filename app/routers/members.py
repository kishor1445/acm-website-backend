from datetime import datetime
from fastapi import APIRouter, Depends, Query, status, HTTPException
from fastapi.security.oauth2 import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select
from app.db.db import get_db
from app.config import IST
from app.utils.security import check_pass, hash_, verify
from email_validator import validate_email
from app.db.models import Members, Auth
from .. import config, schema, oauth2

router = APIRouter(prefix="/members", tags=["Members"])


@router.post("/", response_model=schema.MemberOut, status_code=status.HTTP_201_CREATED)
def create_member(data: schema.MemberCreate, db: Session = Depends(get_db)):
    data.email = validate_email(data.email, check_deliverability=True).normalized
    check_pass(data.password)
    data.password = hash_(data.password)
    _data = data.model_dump()
    _data["position"] = data.position.value
    _data["team"] = data.team.value
    _data["chapter"] = data.chapter.value
    _data["joined_at"] = datetime.now(config.IST)
    try:
        member = Members(**_data)
        db.add(member)
        auth = Auth(email=data.email, password=data.password, account_type="member")
        db.add(auth)
        db.commit()
        db.refresh(member)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Member already exist"
        )
    member.joined_at = member.joined_at.astimezone(config.IST)
    return member


@router.post("/login")
def login_member(
    data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)
):
    auth = db.exec(
        select(Auth)
        .where(Auth.email == data.username)
        .where(Auth.account_type == "member")
    ).first()
    if not auth or not verify(data.password, auth.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
        )
    access_token = oauth2.create_access_token(
        {"email": auth.email, "account_type": "member"}
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/search", response_model=list[schema.MemberOut])
def search_member(
    team: schema.TeamType | None = None,
    season: int | None = Query(None, ge=1),
    position: schema.PositionType | None = None,
    chapter: schema.ChapterType | None = None,
    db: Session = Depends(get_db),
):
    query = select(Members)
    filters = {}
    if team:
        filters["team"] = team.value
    if season:
        filters["season"] = season
    if position:
        filters["position"] = position.value
    if chapter:
        filters["chapter"] = chapter.value

    if filters:
        query = query.filter_by(**filters)

    members = db.exec(query).all()

    if members:
        for member in members:
            member.joined_at = member.joined_at.astimezone(IST)
    return members


@router.patch("/")
def update_member(
    data: schema.MemberUpdate,
    db: Session = Depends(get_db),
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
    email = current_member.email
    member = db.exec(select(Members).where(Members.email == email)).first()
    if member:
        for k, v in data.model_dump().items():
            if k.startswith("new_") and v is not None:
                setattr(member, k.replace("new_", ""), v)
        db.commit()
        db.refresh(member)
    return member


@router.post("/reset_password")
def reset_password_member(
    data: schema.SetResetPassword,
    db: Session = Depends(get_db),
    current_member: schema.MemberOut = Depends(oauth2.get_current_member),
):
    email = current_member.email
    auth = db.exec(
        select(Auth).where(Auth.email == email).where(Auth.account_type == "member")
    ).first()
    check_pass(data.new_password)
    if auth:
        auth.password = hash_(data.new_password)
        db.commit()
    return {"msg": "Successfully Updated your password"}


@router.get("/me", response_model=schema.MemberOut)
def get_member(current_member: schema.MemberOut = Depends(oauth2.get_current_member)):
    return current_member
