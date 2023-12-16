from typing import Optional
from enum import Enum
from pydantic import BaseModel, EmailStr
from datetime import datetime
from datetime import date as _date


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


class EventUpdate(BaseModel):
    name: str
    date: _date
    new_name: Optional[str] = None
    new_description: Optional[str] = None
    new_venue: Optional[str] = None
    new_start: Optional[datetime] = None
    new_end: Optional[datetime] = None
    new_link: Optional[str] = None


class EventDelete(BaseModel):
    name: str
    date: _date


class MemberCreate(BaseModel):
    reg_no: int
    name: str
    position: PositionType = "Member"
    department: DepartmentType
    season: int
    chapter: ChapterType = "ACM"
    pic_url: str = None
    linkedin_tag: Optional[str] = None
    twitter_tag: Optional[str] = None
    instagram_tag: Optional[str] = None
    facebook_tag: Optional[str] = None


class MemberUpdate(BaseModel):
    reg_no: int
    new_reg_no: Optional[int] = None
    new_name: Optional[str] = None
    new_position: PositionType = None
    new_department: DepartmentType = None
    new_season: Optional[int] = None
    new_chapter: ChapterType = None
    new_pic_url: Optional[str] = None
    new_linkedin_tag: Optional[str] = None
    new_twitter_tag: Optional[str] = None
    new_instagram_tag: Optional[str] = None
    new_facebook_tag: Optional[str] = None


class MemberDelete(BaseModel):
    reg_no: int


class BlogCreate(BaseModel):
    title: str
    description: str = None
    date: _date
    author: str
    image_url: str = None
    link: str


class BlogUpdate(BaseModel):
    title: str
    new_title: Optional[str] = None
    new_description: Optional[str] = None
    new_date: Optional[_date] = None
    new_author: Optional[str] = None
    new_image_url: Optional[str] = None
    new_link: Optional[str] = None


class BlogDelete(BaseModel):
    title: str


class UserCreate(BaseModel):
    email_id: str
    password: str
    university: str
    department: str
    year: int


class UserLogin(BaseModel):
    email_id: str
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    email_id: str
    admin: bool
