import sqlite3


def create_tables():
    with sqlite3.connect("acm.db") as db:
        cur = db.cursor()
        cur.execute(
            """
        CREATE TABLE IF NOT EXISTS mailing_list(
            email_id TEXT PRIMARY KEY
        )
        """
        )
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS events(
                    id TEXT NOT NULL PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    venue TEXT NOT NULL,
                    start DATETIME NOT NULL,
                    end DATETIME NOT NULL,
                    fee REAL NOT NULL,
                    link TEXT
                )
            """
        )
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS members(
                    reg_no INT NOT NULL PRIMARY KEY,
                    name TEXT NOT NULL,
                    email_id TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    position TEXT NOT NULL,
                    department TEXT NOT NULL,
                    season INT,
                    chapter TEXT NOT NULL,
                    pic_url TEXT,
                    linkedin_tag TEXT,
                    twitter_tag TEXT,
                    instagram_tag TEXT,
                    facebook_tag TEXT,
                    joined_at DATETIME NOT NULL
                )
            """
        )
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS blogs(
                    title TEXT NOT NULL PRIMARY KEY,
                    description TEXT,
                    date DATE,
                    author TEXT NOT NULL,
                    image_url TEXT,
                    link TEXT NOT NULL
                )
            """
        )
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS users(
                    reg_no INT PRIMARY KEY,
                    name TEXT NOT NULL,
                    email_id TEXT NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    department TEXT NOT NULL,
                    university TEXT NOT NULL,
                    year INT NOT NULL,
                    joined_at DATETIME NOT NULL
                )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS event_registrations(
                event_reg_id TEXT PRIMARY KEY,
                user_id INT NOT NULL,
                event_id TEXT NOT NULL,
                transaction_id TEXT UNIQUE,
                status TEXT NOT NULL
            )
            """
        )
        db.commit()
