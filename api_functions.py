# This file is for all of the repetitive functions/variables within my server.py file.

castaway_not_found = {"Message" : "We couldn't find the castaway you're looking for. Please make sure you're spelling the name correctly with the first and last name starting with an uppercase letter.", "example" : "Parvati_Shallow"}

season_not_found = {"message": "We couldn't find the season you're looking for. Please make sure it is a valid season number/name."}

def get_castaway_info(castaway):
    # This function takes a Castaway query as input. Must be a Castaway query so we can perform attribute calls.
    castaway_info = {
    "name": castaway.name,
    "hometown": castaway.hometown,
    "age_on_first_season": castaway.age_at_recording,
    "total_days_on_survivor": castaway.days_lasted,
    "total_challenge_wins": castaway.challenge_wins
    }
    return castaway_info

def get_season_info(season):
    # This function takes a Season query as input. Must be a Season query so we can perform attribute calls.
    season_info = {
            "season_number": season.season_number,
            "season_name": season.name,
            "location": season.location,
            "start_date": season.start_date,
            "end_date": season.end_date,
            "number_of_episodes": season.num_episodes,
            "number_of_castaways": season.num_castaways
        }
    return season_info

def remove_underscores(string):
    name_without_underscore = ''
    for char in string:
        if char == '_':
            name_without_underscore += ' '
        else:
            name_without_underscore += char

    return name_without_underscore



