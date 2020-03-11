import json
import discord

from data import datamanager
#from game import roles
#from game.role import role
# Check for correct json
def check_json():
    print("Debug: This should not happen. utils.py has been called where it shouldn't.")
    try:
        with open('config.json') as configfile:
            data = json.load(configfile)
            neededAttributes = ['token', 'covert_server', 'invite_link']
            correct = True
            for attibute in neededAttributes:
                if attibute not in data:
                    correct = False
                    print("Error: Attribute "+attibute+" not found. Please enter "+attibute+" in config.json")
            return correct
    except FileNotFoundError:
        print('Error: config.json not found. Did you forget to add one?')
        return False

# Print all roles in a readable way
def format_role_list(roles):
    return "\n - " + ("\n - ".join(map(lambda x: str(roles.count(x)) + 'x ' + x.__name__, list(set(roles)))))

def check_all_players_joined(client, player_list):
    s = set(map(lambda x: x.id, client.get_guild(datamanager.get_config('covert_server')).members))
    #rint(s)
    return set(player_list).issubset(s)
