from sqlite3 import Connection as SQLite3Connection
from sqlalchemy import event
from sqlalchemy.engine import Engine
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, request, jsonify
from datetime import date
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

@app.route("/castaways/challenge_wins", methods=["GET"])
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

@app.route("/castaways/challenge_wins/<num>", methods=["GET"])
def number_of_challenge_wins(num):
    '''
    Purpose:
        Presents data about the castaways who have won a certain number of challenges (num).
    Input Parameter(s):
        num- 
            A specified number of challenges won. /castaways/challenges/4 will return all of the castaways who have won exactly 4 challenges throughout all of their time on survivor.
    Return Value:
        JSONified version of the data.
    '''
    castaways = Castaways.query.filter_by(challenge_wins=int(num)).all()
    # print(castaways)

    if not castaways:
        return jsonify({
            "message": "No castaways found with that amount of challenge wins."
        }), 400
    
    json_body = []
    
    for castaway in castaways:
        json_body.append({
            "name": castaway.name,
            "challenge_wins": castaway.challenge_wins
        })
    
    return jsonify(json_body), 200

@app.route("/castaways/days_lasted", methods=["GET"])
def castaways_ordered_by_days_lasted():
    '''
    Purpose:
        Order the castaways by the total number of days they've lasted on survivor. This total rolls over to any new season a castaway is on. Highest is at the top of list, and it goes down from there.
    Input Parameter(s):
        None
    Return Value:
        JSONified version of the data
    '''
    castaways = Castaways.query.order_by(Castaways.days_lasted).all()
    castaways.reverse()

    json_body = []

    for castaway in castaways:
        json_body.append({
            "name": castaway.name,
            "total_days_lasted": castaway.days_lasted
        })
    
    return jsonify(json_body), 200

@app.route("/castaways/age/ascending", methods=["GET"])
def castaways_ordered_by_ascending_age():
    '''
    Purpose:
        Order the castaways by age in ascending order. i.e The first castaway will be the youngest, and they will get older as we go down the list.
    Input Parameter(s):
        None
    Return Value:
        JSONified version of the data
    '''
    castaways = Castaways.query.order_by(Castaways.age_at_recording).all()

    json_body = []
    for castaway in castaways:
        json_body.append({
            "name": castaway.name,
            "age_on_first_season": castaway.age_at_recording
        })
    
    return jsonify(json_body), 200

@app.route("/castways/age/descending", methods=["GET"])
def castaways_ordered_by_descending_age():
    '''
    Purpose:
        Order the castaways by age in descending order. i.e The first castaway will be the oldest, and they will get younger as we go down the list.
    Input Parameter(s):
        None
    Return Value:
        JSONified version of the data
    '''
    castaways = Castaways.query.order_by(Castaways.age_at_recording).all()
    castaways.reverse()

    json_body = []
    for castaway in castaways:
        json_body.append({
            "name": castaway.name,
            "age_on_first_season": castaway.age_at_recording
        })
    
    return jsonify(json_body), 200

@app.route("/castaways/winners", methods=["GET"])
def get_all_winners():
    '''
    Purpose:
        Display data on the winners of all seasons. Castaway name, season name, season number
    Input Parameter(s):
        None
    Return Value:
        JSONified version of the data
    '''
    winners = SeasonCastaway.query.filter_by(placement=1)

    json_body = []

    for winner in winners:
        castaway = Castaways.query.filter_by(id=winner.castaway_id).first()
        season = Seasons.query.filter_by(season_number=winner.season_number).first()
        json_body.append({
            "name": castaway.name,
            "season_number": winner.season_number,
            "season_name": season.name
        })

    return jsonify(json_body), 200

@app.route("/castaways/create", methods=["POST"])
def create_castaway():
    '''
    Purpose:
        Create a new castaway and store it in the database. This is for a NEW castaway, not a returning player. For updating a returning player's statistics, look to update_castaway().
    Input Parameter(s):
        None, but the body of the request should include JSON of the following castaway attributes:
            -Name of castaway
            -Hometown
            -Age
            -Total days lasted
            -Number of challenge wins
    Return Value:
        Successful creation message
    '''
    data = request.get_json()
    print(data["name"])
    new_castaway = Castaways(
        name=data["name"],
        hometown=data["hometown"],
        age_at_recording=data["age_at_recording"],
        days_lasted=data["days_lasted"],
        challenge_wins=data["challenge_wins"]
    )
    db.session.add(new_castaway)
    db.session.commit()
    return jsonify({"message": "castaway created successfully"})

@app.route("/castaways/delete/<castaway_name>", methods=["DELETE"])
def delete_castaway(castaway_name):
    '''
    Purpose:
        Delete a castaway from the database.
    Input Parameter(s):
        The name of the castaway to remove.
    Return Value:
        Successful deletion message.
    '''
    castaway_name = remove_underscores(castaway_name)
    castaway = Castaways.query.filter_by(name=castaway_name).first()
    if not castaway:
        return jsonify(castaway_not_found), 400
    db.session.delete(castaway)
    db.session.commit()

    return jsonify({"message": "castaway deleted successfully"})

# season endpoints

@app.route("/seasons", methods=["GET"])
def get_all_seasons():
    '''
    Purpose:
        Fetches data on all of the seasons of survivor.
    Input Parameter(s):
        None
    Return Value:
        JSONified version of the data
    '''
    seasons = Seasons.query.all()
    json_body = []

    for season in seasons:
        json_body.append(get_season_info(season))
    
    return jsonify(json_body), 200

@app.route("/seasons/<season_number>/castaways", methods=["GET"])
def get_all_of_seasons_castaways(season_number):
    '''
    Purpose:
        Fetches all of the castaways in a given season
    Input Parameter(s):
        The season number
    Return Value:
        JSONified version of the data
    '''
    castaways = SeasonCastaway.query.filter_by(season_number=season_number).all()
    if not castaways:
        return jsonify(season_not_found), 400
    
    json_body = []

    for castaway in castaways:
        castaway_info = Castaways.query.filter_by(id=castaway.castaway_id).first()
        json_body.append({
            "castaway_name": castaway_info.name,
            "placement": castaway.placement 
        })
    return jsonify(json_body), 200

@app.route("/seasons/descending", methods=["GET"])
def get_all_seasons_descending():
    '''
    Purpose:
        Fetches all seasons in a descending order. The first season in the list is the latest season, and the seasons get earlier and earlier as we go down the list.
    Input Parameter(s):
        None
    Return Value:
        JSONified version of the data
    '''
    seasons = Seasons.query.all()
    json_body = []

    for season in seasons:
        json_body.append(get_season_info(season))
    json_body.reverse()
    
    return jsonify(json_body), 200

@app.route("/seasons/<season_number>", methods=["GET"])
def get_one_season_by_number(season_number):
    '''
    Purpose:
        Get data on one season by its season number.
    Input Parameter(s):
        Number of the season
    Return Value:
        JSONified version of the data
    '''
    season = Seasons.query.filter_by(season_number=season_number).first()
    if not season:
        return jsonify(season_not_found), 400
    
    return jsonify(get_season_info(season)), 200

@app.route("/seasons/name/<season_name>", methods=["GET"])
def get_one_season_by_name(season_name):
    '''
    Purpose:
        Get data on one season by its season name.
    Input Parameter(s):
        Name of the season
    Return Value:
        JSONified version of the data
    '''
    season = Seasons.query.filter_by(name=season_name).first()
    if not season:
        return jsonify(season_not_found), 400
    
    return jsonify(get_season_info(season)), 200

@app.route("/seasons/<season_number>/winner", methods=["GET"])
def get_one_seasons_winner(season_number):
    '''
    Purpose:
        Gets the winner of one season.
    Input Parameter(s):
        The number of the season.
    Return Value:
        JSONified version of the data
    '''
    seasoncastaway = SeasonCastaway.query.filter_by(season_number=season_number, placement=1).first()
    if not seasoncastaway:
        return jsonify(season_not_found), 400
    winner = Castaways.query.filter_by(id=seasoncastaway.castaway_id).first()

    return jsonify({
        "winner_name": winner.name,
        "season_number": season_number
        }), 200

@app.route("/seasons/<season_number>/tribes", methods=["GET"])
def get_one_seasons_tribes(season_number):
    '''
    Purpose:
        Get all of the tribes for a season.
    Input Parameter(s):
        The number of the season.
    Return Value:
        JSONified version of the data.
    '''
    tribes = Tribes.query.filter_by(season=season_number).all()
    if not tribes:
        return jsonify(season_not_found), 400
    
    json_body = []

    for tribe in tribes:
        json_body.append({
            "tribe_name": tribe.tribe_name,
            "tribe_type": tribe.tribe_type,
            "season": tribe.season,
            "challenge_wins": tribe.challenge_wins
        })

    return jsonify(json_body), 200

@app.route("/seasons/locations", methods=["GET"])
def get_all_locations():
    '''
    Purpose: 
        Gets all of the survivor locations for each season.
    Input Parameter(s):
        None
    Return Value:
        JSONified version of the data
    '''
    seasons = Seasons.query.all()
    json_body = []

    for season in seasons:
        json_body.append({
            "season_number": season.season_number,
            "location": season.location
        })

    return jsonify(json_body), 200

@app.route("/seasons/create", methods=["POST"])
def create_season():
    '''
    Purpose:
        Create a new season and add it to the database.
    Input Parameter(s):
        None
    Return Value:
        Successful creation message.
    '''
    data = request.get_json()

    new_season = Seasons(
        name = data["name"],
        location = data["location"],
        start_date = date(data["year"], data["start_month"], data["start_day"]),
        end_date = date(data["year"], data["end_month"], data["end_day"]),
        num_episodes = data["num_episodes"],
        num_castaways = data["num_castaways"]
    )
    db.session.add(new_season)
    db.session.commit()

    return jsonify({"message": "season created successfully"})

@app.route("/seasons/delete/<season_number>", methods=["DELETE"])
def delete_season(season_number):
    '''
    Purpose:
        Delete a season from the database.
    Input Parameter(s):
        The number of the season.
    Return Value:
        Successful deletion message.
    '''
    season = Seasons.query.filter_by(season_number=season_number).first()
    if not season:
        return jsonify(season_not_found), 400
    
    db.session.delete(season)
    db.session.commit()

    return jsonify({"message": "season deleted successfully"})

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