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
class SeasonCastaway(db.Model):
    __tablename__ = "SeasonCastaway"
    id = db.Column(db.Integer, primary_key=True)
    season_number = db.Column(db.Integer, db.ForeignKey('Seasons.season_number'))
    castaway_id = db.Column(db.Integer, db.ForeignKey('Castaways.id'))
    placement = db.Column(db.String(40))

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
    age_at_recording = db.Column(db.Integer)
    days_lasted = db.Column(db.Integer)
    challenge_wins = db.Column(db.Integer)
    # seasons = db.relationship('Seasons', backref=db.backref('castaways_in_season', lazy='dynamic'))
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

# castaway endpoints

@app.route("/castaways", methods=["GET"])
def get_all_castaways():
    pass

@app.route("/castaways/<castaway_name>", methods=["GET"])
def get_one_castaway(castaway_name):
    pass

@app.route("/castaways/<castaway_name>/seasons", methods=["GET"])
def get_one_castaways_seasons(castaway_name):
    pass

@app.route("/castways/challenge_wins", methods=["GET"])
def castaways_ordered_by_challenge_wins():
    pass

@app.route("/castways/days_lasted", methods=["GET"])
def castaways_ordered_by_days_lasted():
    pass

@app.route("/castways/age/ascending", methods=["GET"])
def castaways_ordered_by_ascending_age():
    pass

@app.route("/castways/age/descending", methods=["GET"])
def castaways_ordered_by_descending_age():
    pass

@app.route("/castaways/winners", methods=["GET"])
def get_all_winners():
    pass

@app.route("/castaways/create", methods=["POST"])
def create_castaway():
    pass

@app.route("/castaways/delete/<castaway_id>", methods=["DELETE"])
def delete_castaway(castaway_id):
    pass

# season endpoints

@app.route("/seasons", methods=["GET"])
def get_all_seasons():
    pass

@app.route("/seasons/<season_number>/castaways", methods=["GET"])
def get_all_of_seasons_castaways():
    pass

@app.route("/seasons/descending", methods=["GET"])
def get_all_seasons_descending():
    pass

@app.route("/seasons/<season_number>", methods=["GET"])
def get_one_season(season_number):
    pass

@app.route("/seasons/<season_name>", methods=["GET"])
def get_one_season(season_name):
    pass

@app.route("/seasons/<season_number>/winner", methods=["GET"])
def get_one_seasons_winner(season_number):
    pass

@app.route("/seasons/<season_number>/tribes", methods=["GET"])
def get_one_seasons_tribes(season_number):
    pass

@app.route("/seasons/locations>", methods=["GET"])
def get_all_locations():
    pass

@app.route("/seasons/create>", methods=["POST"])
def create_season():
    pass

@app.route("/seasons/delete/<season_number>", methods=["DELETE"])
def delete_season(season_number):
    pass

# tribe endpoints

@app.route("/tribes", methods=["GET"])
def get_all_tribes():
    pass

@app.route("/tribes/challenge_wins", methods=["GET"])
def order_tribes_by_challenge_wins():
    pass

@app.route("/tribes/<tribe_name>", methods=["GET"])
def get_one_tribe(tribe_name):
    pass

@app.route("/tribes/<season_number>", methods=["GET"])
def get_all_tribes_from_a_season(season_number):
    pass

@app.route("/tribes/<tribe_name>/members", methods=["GET"])
def get_tribe_members(tribe_name):
    pass

@app.route("/tribes/<tribe_name>/highest_placing", methods=["GET"])
def get_highest_placing_member(tribe_name):
    pass

@app.route("/tribes/create", methods=["POST"])
def create_tribe():
    pass

@app.route("/tribes/delete/<tribe_name>", methods=["GET"])
def delete_tribe(tribe_name):
    pass






# if __name__ == "__main__":
    # app.run(debug=True)