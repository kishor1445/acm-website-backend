from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from utils.db import create_tables
from dotenv import load_dotenv
from .routers import user, event, achievements, member, blog, mail, auth

load_dotenv()
create_tables()

app = FastAPI(
    title="ACM-SIST Backend API",
    contact={
        "name": "ACM-SIST",
        "url": "https://example.com",
        "email": "acm.sathyabama@gmail.com",
    },
)

for x in [user, event, achievements, member, blog, mail, auth]:
    app.include_router(x.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
