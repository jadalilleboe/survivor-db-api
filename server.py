from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify

# app
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///survivordb.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = 0

# configure sqlite3 to enforce foreign key constraints
@event.listens_for(Engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, SQLite3Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.close()

db = SQLAlchemy(app)

# models

# helper tables
season_castaway = db.Table('SeasonCastaway',
    db.Column('season_number', db.Integer, db.ForeignKey('Seasons.season_number')),
    db.Column('castaway_id', db.Integer, db.ForeignKey('Castaways.id')),
    db.Column('placement', db.Integer)
    )

tribe_castaway = db.Table('TribeCastaway',
    db.Column('castaway_id', db.Integer, db.ForeignKey('Castaways.id')),
    db.Column('tribe_id', db.Integer, db.ForeignKey('Tribes.id'))
    )

# main tables
class Castaways(db.Model):
    __tablename__ = "Castaways"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    hometown = db.Column(db.String(50))
    days_lasted = db.Column(db.Integer)
    challenge_wins = db.Column(db.Integer)
    seasons = db.relationship('Seasons', secondary=season_castaway, backref=db.backref('castaways_in_season', lazy='dynamic'))
    tribes = db.relationship('Tribes', secondary=tribe_castaway, backref=db.backref('castaways_in_tribe', lazy='dynamic'))     

class Seasons(db.Model):
    __tablename__ = "Seasons"
    season_number = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(40))
    location = db.Column(db.String(50))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    num_episodes = db.Column(db.Integer)
    num_castaways = db.Column(db.Integer)
    tribes = db.relationship("Tribes", cascade="all,delete")

class Tribes(db.Model):
    __tablename__ = "Tribes"
    id = db.Column(db.Integer, primary_key=True)
    tribe_name = db.Column(db.String(40))
    tribe_type = db.Column(db.String(30))
    season = db.Column(db.Integer, db.ForeignKey("Seasons.season_number"))
    challenge_wins = db.Column(db.String(10))





# if __name__ == "__main__":
    # app.run(debug=True)