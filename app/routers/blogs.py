from datetime import date
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status 
from sqlmodel import Session, select
from app import oauth2, schema
from app.db.db import get_db
from app.db.models import Blogs

router = APIRouter(prefix="/blogs")

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_blog(data: schema.BlogCreate, db: Session = Depends(get_db), _: schema.MemberOut = Depends(oauth2.get_current_member)):
    blog = Blogs(**data.model_dump())
    db.add(blog)
    db.commit()
    db.refresh(blog)
    return blog

@router.get("/search", response_model=list[schema.BlogOut])
def get_blogs(_id: UUID | None = Query(None, alias="id"), title: str | None = None, author: str | None = None, _date: date | None = Query(None, alias="date"), db: Session = Depends(get_db)):
    query = select(Blogs)
    filters = {}
    if _id:
        filters["id"] = _id
    if author:
        filters["author"] = author
    if title:
        filters["title"] = title
    if _date:
        filters["date"] = _date
    if filters:
        query = query.filter_by(**filters)
    blogs = db.exec(query).all()
    return blogs

@router.patch("/", response_model=schema.BlogOut)
def update_blog(data: schema.BlogUpdate, db: Session = Depends(get_db), _: schema.MemberOut = Depends(oauth2.get_current_member)):
    blog = db.exec(select(Blogs).where(Blogs.id == data.id)).first()
    if blog:
        for k, v in data.model_dump().items():
            if k.startswith("new_") and v is not None:
                setattr(blog, k.replace("new_", ""), v)
        db.commit()
        db.refresh(blog)
    return blog

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
def delete_blog(data: schema.BlogDelete, db: Session = Depends(get_db), _: schema.MemberOut = Depends(oauth2.get_current_member)):
    blog = db.exec(select(Blogs).where(Blogs.id == data.id)).first()
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog doesn't exist"
        )
    db.delete(blog)
    db.commit()

