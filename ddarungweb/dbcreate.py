import sqlite3 as sql

from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
def db_create():


    conn = sql.connect("User.db")
    with conn:
        cur = conn.cursor()
        cur.executescript("""
            DROP TABLE IF EXISTS User;
            CREATE TABLE User(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                email TEXT,
                name TEXT,
                password TEXT,
                active  BOOLEAN,
                role REFERENCES Role(id)
            );
            
            DROP TABLE IF EXISTS Role;
            CREATE TABLE Role(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                name TEXT,
                description TEXT
            ); 
            
            INSERT INTO Role VALUES (0, "Admin", "Who can manage this web");
            INSERT INTO Role VALUES (1, "User", "Who can use this web");
        """)
        conn.commit()



def create_orm(engine):

    Base_auto = automap_base()
    Base_auto.prepare(engine)

    return Base_auto



if __name__ == '__main__':
    db_create()