from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from utils.db import create_tables
from dotenv import load_dotenv
from .routers import user, event, achievements, member, blog, mail, export
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
create_tables()

app = FastAPI(
    title="ACM-SIST API",
    summary="Backend for the ACM-SIST club website",
    contact={
        "name": "ACM-SIST",
        "url": "https://example.com/contact",
        "email": "acm.sathyabama@gmail.com",
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for x in [user, event, achievements, member, blog, mail, export]:
    app.include_router(x.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
