from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .db import db
from . import config
from .routers import users, members, events, payment_proof, blogs, achievements, mail, export

app = FastAPI(title="ACM-SIST APIs", version="2.0.0")


db.create_table(config.db_engine)

# Allows All Domain to access the API
app.add_middleware(CORSMiddleware, allow_origins=["*"])

for api in (users, members, events, payment_proof, blogs, achievements, mail, export):
    app.include_router(api.router)


# Show Favicon
@app.get("/favicon.ico")
def get_favicon():
    return FileResponse("static/favicon.ico", media_type="image/x-icon")


# Acts like a CDN
app.mount("/static", StaticFiles(directory="static"), name="static")
