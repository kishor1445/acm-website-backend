from enum import Enum
from typing import List
from pydantic import BaseModel, Field
from datetime import datetime
from datetime import date as _date


class PaymentStatus(Enum):
    Pending = "pending"
    Verify = "verified"


class ChapterType(Enum):
    ACM = "ACM"
    ACM_W = "ACM-W"


class DepartmentType(Enum):
    Core = "core_team"
    Management = "management_team"
    Content = "content_team"
    Design = "design_team"
    Technical = "technical_team"


class PositionType(Enum):
    Chair = "chair"
    Vice_Chair = "vice-chair"
    Faculty = "faculty"
    Member = "member"


class MailP(BaseModel):
    email_id: str
    name: str
    reg_no: str
    dep: str


class EventCreate(BaseModel):
    name: str
    description: str
    venue: str
    start: datetime
    end: datetime
    link: str
    fee: float


class EventOut(EventCreate):
    id: str


class EventUpdate(BaseModel):
    name: str
    date: _date
    new_name: str | None = None
    new_description: str | None = None
    new_venue: str | None = None
    new_start: datetime | None = None
    new_end: datetime | None = None
    new_link: str | None = None
    new_fee: float | None = None


class EventDelete(BaseModel):
    name: str
    date: _date


class EventRegister(BaseModel):
    event_id: str
    transaction_id: str | None = None


class EventRegisterOut(EventRegister):
    event_reg_id: str
    user_id: int
    status: PaymentStatus


class MyEventOut(BaseModel):
    event: List[EventOut]
    reg_event: List[EventRegisterOut]


class Achievements(BaseModel):
    members: int
    participants: int
    events: int


class MemberBase(BaseModel):
    reg_no: int
    name: str
    email_id: str
    position: PositionType = PositionType.Member
    department: DepartmentType
    season: int
    chapter: ChapterType = ChapterType.ACM
    pic_url: str | None = None
    linkedin_tag: str | None = None
    twitter_tag: str | None = None
    instagram_tag: str | None = None
    facebook_tag: str | None = None


class MemberCreate(MemberBase):
    password: str


class MemberOut(MemberBase):
    joined_at: datetime


class MemberUpdate(BaseModel):
    reg_no: int
    new_reg_no: int | None = None
    new_name: str | None = None
    new_position: PositionType = None
    new_department: DepartmentType = None
    new_season: int | None = None
    new_chapter: ChapterType = None
    new_pic_url: str | None = None
    new_linkedin_tag: str | None = None
    new_twitter_tag: str | None = None
    new_instagram_tag: str | None = None
    new_facebook_tag: str | None = None


class MemberDelete(BaseModel):
    reg_no: int


class BlogCreate(BaseModel):
    title: str
    description: str | None = None
    date: _date
    author: str
    image_url: str | None = None
    link: str


class BlogOut(BlogCreate):
    ...


class BlogUpdate(BaseModel):
    title: str
    new_title: str | None = None
    new_description: str | None = None
    new_date: _date | None = None
    new_author: str | None = None
    new_image_url: str | None = None
    new_link: str | None = None


class BlogDelete(BaseModel):
    title: str


class UserBase(BaseModel):
    reg_no: int
    name: str
    email_id: str
    department: str
    university: str
    year: int = Field(..., ge=1, le=4)


class UserCreate(UserBase):
    password: str


class UserDelete(BaseModel):
    reg_no: int


class UserOut(UserBase):
    joined_at: datetime


class UserLogin(BaseModel):
    email_id: str
    password: str


class TokenData(BaseModel):
    access_token: str
    token_type: str
