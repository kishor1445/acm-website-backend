from datetime import datetime, date
from uuid import UUID, uuid4
from sqlmodel import SQLModel, Field


class Mailing_List(SQLModel, table=True):
    email: str = Field(..., primary_key=True, index=True)


class Users(SQLModel, table=True):
    reg_no: int = Field(..., primary_key=True, index=True)
    name: str
    email: str = Field(..., unique=True, index=True)
    department: str
    university: str
    year: int
    joined_at: datetime
    verified: bool


class Members(SQLModel, table=True):
    reg_no: int = Field(..., primary_key=True, index=True)
    name: str
    email: str = Field(..., unique=True, index=True)
    avatar_url: str | None = Field(nullable=True)
    position: str
    team: str
    season: int
    chapter: str
    department: str
    year: int
    linkedin_tag: str
    instagram_tag: str
    joined_at: datetime


class Auth(SQLModel, table=True):
    email: str = Field(..., primary_key=True, index=True)
    password: str
    account_type: str = Field(..., primary_key=True, index=True)


class Verify(SQLModel, table=True):
    email: str = Field(..., primary_key=True, index=True)
    token: str
    time: datetime


class ResetPassword(SQLModel, table=True):
    email: str = Field(..., primary_key=True, index=True)
    token: str
    time: datetime


class Events(SQLModel, table=True):
    id: UUID = Field(..., default_factory=uuid4, primary_key=True, index=True)
    name: str
    description: str
    start: datetime
    end: datetime
    rules: str
    venue: str
    fee: float
    image_url: str


class Event_Registeration(SQLModel, table=True):
    user_reg_no: int = Field(..., primary_key=True, index=True)
    event_id: UUID = Field(..., primary_key=True, index=True)
    transaction_id: str | None = Field(..., unique=True)
    screenshot_id: str | None = Field(..., unique=True)
    status: str = Field(..., index=True)

class Blogs(SQLModel, table=True):
    id: UUID = Field(..., default_factory=uuid4, primary_key=True, index=True)
    title: str 
    description: str
    date: date
    author: str
    image_url: str | None

