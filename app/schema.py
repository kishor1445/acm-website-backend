from enum import Enum
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date


class PaymentStatus(Enum):
    PENDING = "pending"
    VERIFY = "verified"


class ChapterType(Enum):
    ACM = "acm"
    ACM_W = "acm-w"


class TeamType(Enum):
    CORE = "core"
    MANAGEMENT = "management"
    CONTENT = "content"
    DESIGN = "design"
    TECHNICAL = "technical"


class PositionType(Enum):
    CHAIR = "chair"
    VICE_CHAIR = "vicr-chair"
    FACULTY = "faculty"
    MEMBER = "member"


class Tables(Enum):
    USERS = "users"
    MEMBERS = "members"
    EVENTS = "events"
    EVENT_REGISTERATION = "event_registeration"
    BLOGS = "blogs"
    MAILING_LIST = "mailing_list"


class Mail(BaseModel):
    email: list[str]
    subject: str
    body: str


class UserBase(BaseModel):
    reg_no: int
    name: str = Field(..., min_length=2)
    email: EmailStr
    department: str = Field(..., min_length=3)
    university: str = Field(..., min_length=3)
    year: int = Field(..., ge=1, le=4)


class UserOut(UserBase):
    joined_at: datetime
    verified: bool


class CreateUser(UserBase):
    password: str


class MemberBase(BaseModel):
    reg_no: int
    name: str = Field(..., min_length=2)
    email: EmailStr
    avatar_url: str | None = None
    position: PositionType = PositionType.MEMBER
    team: TeamType
    season: int = Field(..., ge=1)
    chapter: ChapterType = ChapterType.ACM
    department: str = Field(..., min_length=2)
    year: int = Field(..., ge=1, le=4)
    linkedin_tag: str = Field(..., min_length=2)
    instagram_tag: str = Field(..., min_length=2)


class MemberCreate(MemberBase):
    password: str


class MemberUpdate(BaseModel):
    new_reg_no: int | None = None
    new_name: str | None = None
    new_email: EmailStr | None = None
    new_avatar_url: str | None = None
    new_position: PositionType | None = None
    new_team: TeamType | None = None
    new_season: int | None = None
    new_chapter: ChapterType | None = None
    new_department: str | None = None
    new_year: int | None = None
    new_linkedin_tag: str | None = None
    new_instagram_tag: str | None = None


class MemberOut(MemberBase):
    joined_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str


class Verify(BaseModel):
    email: EmailStr


class ForgotPassword(BaseModel):
    email: EmailStr


class SetResetPassword(BaseModel):
    reset_token: str | None = None
    email: EmailStr | None = None
    new_password: str
    confirm_password: str


class EventBase(BaseModel):
    name: str
    description: str
    start: datetime
    end: datetime
    rules: str
    venue: str
    fee: float
    image_url: str


class CreateEvent(EventBase):
    ...


class EventUpdate(BaseModel):
    id: UUID
    new_name: str | None = None
    new_description: str | None = None
    new_start: datetime | None = None
    new_end: datetime | None = None
    new_rules: str | None = None
    new_venue: str | None = None
    new_fee: float | None = None
    new_image_url: str | None = None


class EventDelete(BaseModel):
    id: UUID


class EventOut(EventBase):
    id: UUID


class RegisterEventBase(BaseModel):
    event_id: UUID 
    transaction_id: str | None = None
    screenshot_id: str | None = None


class RegisterEventCreate(RegisterEventBase):
    ...


class RegisterEventOut(RegisterEventBase):
    user_reg_no: int
    status: PaymentStatus


class BlogBase(BaseModel):
    title: str
    description: str
    date: date
    author: str
    image_url: str

class BlogCreate(BlogBase):
    ...

class BlogUpdate(BaseModel):
    id: UUID
    new_title: str | None = None
    new_description: str | None = None
    new_date: date | None = None
    new_author: str | None = None
    new_image_url: str | None = None

class BlogDelete(BaseModel):
    id: UUID

class BlogOut(BlogBase):
    id: UUID

