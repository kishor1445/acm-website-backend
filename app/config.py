import os
import pytz
from sqlmodel import create_engine
from fastapi.templating import Jinja2Templates
from dotenv import load_dotenv

load_dotenv()

IST = pytz.timezone("Asia/Kolkata")

HTML_TEMPLATES = Jinja2Templates(directory="./static/HTML")

db_engine = create_engine(os.getenv("SQL_DB_URL", "sqlite:///acm.db"))
