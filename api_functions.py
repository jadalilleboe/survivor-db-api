# This file is for all of the repetitive functions/variables within my server.py file.

castaway_not_found = {"Message" : "We couldn't find the castaway you're looking for. Please make sure you're spelling the name correctly with the first and last name starting with an uppercase letter.", "example" : "Parvati_Shallow"}

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

def remove_underscores(string):
    name_without_underscore = ''
    for char in string:
        if char == '_':
            name_without_underscore += ' '
        else:
            name_without_underscore += char

    return name_without_underscore

