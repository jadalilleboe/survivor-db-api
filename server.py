from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from api_functions import *

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
    placement = db.Column(db.Integer)

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
    '''
    Purpose:
        Fetches all of the castaways (and their information) from the database and turns it into a json body. It presents the most recent players first.
    Input Parameter(s):
        None
    Return Value:
        The JSONified json body, with all of the castaway info
    '''
    castaways = Castaways.query.all()
    json_body = []
    for castaway in castaways:
        json_body.append(get_castaway_info(castaway))
    json_body.reverse()
    
    return jsonify(json_body), 200

@app.route("/castaways/ascending", methods=["GET"])
def get_all_castaways_ascending():
    '''
    Purpose:
        Fetches all of the castaways (and their information) from the database and turns it into a json body. It presents the earliest players first.
    Input Parameter(s):
        None
    Return Value:
        The JSONified json body, with all of the castaway info
    '''
    castaways = Castaways.query.all()
    json_body = []
    for castaway in castaways:
        json_body.append(get_castaway_info(castaway))
    
    return jsonify(json_body), 200
        

@app.route("/castaways/<castaway_name>", methods=["GET"])
def get_one_castaway(castaway_name):
    '''
    Purpose: 
        Fetches one castaway's information and presents it.
    Input Parameter(s):
        The name of a castaway
    Return Value:
        JSONified version of the castaway's information
    '''
    name = remove_underscores(castaway_name)
    castaway = Castaways.query.filter_by(name=name).first()

    if not castaway:
        return jsonify(castaway_not_found), 400
    
    return jsonify(get_castaway_info(castaway)), 200
    

@app.route("/castaways/<castaway_name>/seasons", methods=["GET"])
def get_one_castaways_seasons(castaway_name):
    '''
    Purpose:
        Provides information about all of the seasons an individual castaway has made an appearance on. For example, if a castaway has been on 3 seasons, information about all 3 seasons (and that castaway's placement on those seasons) will be presented.
    Input Parameter(s):
        The name of a castaway
    Return Value:
        JSONified version of all that data
    '''
    name = remove_underscores(castaway_name)
    castaway = Castaways.query.filter_by(name=name).first()
    if not castaway:
        return jsonify(castaway_not_found), 400
    seasons = SeasonCastaway.query.filter_by(castaway_id=castaway.id)

    json_body = []
    castaway_occurences = 1

    for season in seasons:
        season_info = Seasons.query.filter_by(season_number=season.season_number).first()
        json_body.append({
            "name": castaway.name,
            "season_number": season.season_number,
            "season_name": season_info.name,
            "season_start_date": season_info.start_date,
            "castaways_placement": season.placement,
            "times_castaway_has_played": castaway_occurences
        })
        castaway_occurences += 1
    
    return jsonify(json_body), 200

    
@app.route("/castways/challenge_wins", methods=["GET"])
def castaways_ordered_by_challenge_wins():
    '''
    Purpose:
        Present all of the castaways ordered by how many challenges they've won. (HIghest number presented first)
    Input Parameter(s):
        None
    Return Value:
        JSONified version of the data.
    '''
    castaways = Castaways.query.order_by(Castaways.challenge_wins)
    json_body = []

    for castaway in castaways:
        json_body.append({
            "name": castaway.name,
            "challenge_wins": castaway.challenge_wins
        })
    json_body.reverse()

    return jsonify(json_body), 200

@app.route("/castways/challenge_wins/<num>", methods=["GET"])
def number_of_challenge_wins(num):
    '''
    Purpose:
        Presents data about the castaways who have won a certain number of challenges (num).
    Input Parameter(s):
        num- 
            A specified number of challenges won. /castaways/challenges/4 will return all of the castaways who have won exactly 4 challenges.
    Return Value:
        JSONified version of the data.
    '''
    castaways = Castaways.query.filter_by(challenge_wins=int(num))

    if not castaways:
        pass

@app.route("/castways/days_lasted", methods=["GET"])
def castaways_ordered_by_days_lasted():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/castways/age/ascending", methods=["GET"])
def castaways_ordered_by_ascending_age():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/castways/age/descending", methods=["GET"])
def castaways_ordered_by_descending_age():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/castaways/winners", methods=["GET"])
def get_all_winners():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/castaways/create", methods=["POST"])
def create_castaway():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/castaways/delete/<castaway_id>", methods=["DELETE"])
def delete_castaway(castaway_id):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

# season endpoints

@app.route("/seasons", methods=["GET"])
def get_all_seasons():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/seasons/<season_number>/castaways", methods=["GET"])
def get_all_of_seasons_castaways():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/seasons/descending", methods=["GET"])
def get_all_seasons_descending():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/seasons/<season_number>", methods=["GET"])
def get_one_season_by_number(season_number):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/seasons/<season_name>", methods=["GET"])
def get_one_season_by_name(season_name):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/seasons/<season_number>/winner", methods=["GET"])
def get_one_seasons_winner(season_number):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/seasons/<season_number>/tribes", methods=["GET"])
def get_one_seasons_tribes(season_number):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/seasons/locations", methods=["GET"])
def get_all_locations():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/seasons/create", methods=["POST"])
def create_season():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/seasons/delete/<season_number>", methods=["DELETE"])
def delete_season(season_number):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

# tribe endpoints

@app.route("/tribes", methods=["GET"])
def get_all_tribes():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/tribes/challenge_wins", methods=["GET"])
def order_tribes_by_challenge_wins():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/tribes/<tribe_name>", methods=["GET"])
def get_one_tribe(tribe_name):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/tribes/<season_number>", methods=["GET"])
def get_all_tribes_from_a_season(season_number):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/tribes/<tribe_name>/members", methods=["GET"])
def get_tribe_members(tribe_name):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/tribes/<tribe_name>/highest_placing", methods=["GET"])
def get_highest_placing_member(tribe_name):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/tribes/create", methods=["POST"])
def create_tribe():
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass

@app.route("/tribes/delete/<tribe_name>", methods=["GET"])
def delete_tribe(tribe_name):
    '''
    Purpose:
    Input Parameter(s):
    Return Value:
    '''
    pass






if __name__ == "__main__":
    app.run(debug=True)