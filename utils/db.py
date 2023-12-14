import sqlite3


def create_tables():
    with sqlite3.connect('acm.db') as db:
        cur = db.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS mailing_list(
            email_id TEXT PRIMARY KEY
        )
        """)
        db.commit()

