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
                    link TEXT
                )
            """
        )
        cur.execute(
            """
                CREATE TABLE IF NOT EXISTS members(
                    reg_no INT NOT NULL PRIMARY KEY,
                    name TEXT NOT NULL,
                    position TEXT NOT NULL,
                    department TEXT NOT NULL,
                    season INT,
                    chapter TEXT NOT NULL,
                    pic_url TEXT,
                    linkedin_tag TEXT,
                    twitter_tag TEXT,
                    instagram_tag TEXT,
                    facebook_tag TEXT
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
                    email_id TEXT NOT NULL PRIMARY KEY,
                    password TEXT NOT NULL,
                    admin BOOLEAN NOT NULL,
                    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    university TEXT NOT NULL,
                    department TEXT NOT NULL,
                    year INT NOT NULL
                )
            """
        )
        db.commit()
