# coding: utf-8
import sqlite3 as sql
from extension import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_security import UserMixin, RoleMixin


from sqlalchemy import create_engine
from sqlalchemy.ext.automap import automap_base
def db_create():

    conn = sql.connect("Ddrung.db")
    with conn:
        cur = conn.cursor()
        cur.executescript("""
            DROP TABLE IF EXISTS User;
            CREATE TABLE User(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                email TEXT NOT NULL,
                name TEXT NOT NULL,
                password TEXT NOT NULL,
                age INTEGER,
                active  BOOLEAN,
                role REFERENCES Role(id)
            );
            
            DROP TABLE IF EXISTS Role;
            CREATE TABLE Role(
                id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                name TEXT,
                description TEXT
            ); 
            
            DROP TABLE IF EXISTS Nonmember;
            CREATE TABLE Nonmember (
                nonmember_num INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE ,
                time TEXT
            );
            
            DROP TABLE IF EXISTS Bookmark;
            CREATE TABLE Bookmark (
                bookmark_num INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE ,
                user_id REFERENCES User(id),
                bookmark_name CHAR(50),
                longitude DOUBLE NOT NULL, 
                latitude DOUBLE NOT NULL
            );
          
            DROP TABLE IF EXISTS Rent;
            CREATE TABLE Rent (
                gubun CHAR(50) ,
                rent_num INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
                rent_name CHAR(50),
                address TEXT,
                count INTEGER,
                latitude DOUBLE NOT NULL, 
                longitude DOUBLE NOT NULL
            );
            
            INSERT INTO Role VALUES (0, "Admin", "Who can manage this web");
            INSERT INTO Role VALUES (1, "User", "Who can use this web");
        """)
        conn.commit()



class Role(db.Model, RoleMixin):
    __tablename__ = 'Role'
    __table_args__ = {'extend_existing': True}
    id = db.Column(db.Integer, primary_key=True, unique=True)
    name = db.Column(db.Text)
    description = db.Column(db.Text)


class User(db.Model, UserMixin):
    __tablename__ = 'User'
    __table_args__ = {'extend_existing': True}

    id = db.Column(db.Integer, primary_key=True, unique=True)
    email = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    password = db.Column(db.Text, nullable=False)
    age = db.Column(db.Integer)
    active = db.Column(db.Boolean)
    role = db.Column(db.ForeignKey('Role.id'))

    Role = db.relationship('Role')

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class Bookmark(db.Model):
    __tablename__ = 'Bookmark'

    bookmark_num = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('User.id'))
    bookmark_name = db.Column(db.CHAR(50))
    longitude = db.Column(db.Float, nullable=False)
    latitude = db.Column(db.Float, nullable=False)

    user = db.relationship('User')

class Nonmember(db.Model):
    __tablename__ = 'Nonmember'

    nonmember_num = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.Text)


class Rent(db.Model):
    __tablename__ = 'Rent'

    gubun = db.Column(db.CHAR(50))
    rent_num = db.Column(db.Integer, primary_key=True)
    rent_name = db.Column(db.CHAR(50))
    address = db.Column(db.Text)
    count = db.Column(db.Integer)
    latitude = db.Column(db.Float, nullable=False)
    longitude = db.Column(db.Float, nullable=False)







if __name__ == '__main__':
    print(sql.version)