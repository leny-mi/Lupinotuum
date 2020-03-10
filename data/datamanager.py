import json

def check_json():
    try:
        with open('data/config.json') as configfile:
            data = json.load(configfile)
            neededAttributes = ['token', 'covert_server', 'invite_link'] # Enter all needed attributes in json here
            correct = True
            for attibute in neededAttributes:
                if attibute not in data:
                    correct = False
                    print("Error: Attribute "+attibute+" not found. Please enter "+attibute+" in config.json")
            return correct
    except FileNotFoundError:
        print('Error: config.json not found. Did you forget to add one?')
        return False

def get_config(attr):
    with open('data/config.json') as configfile:
        data = json.load(configfile)
        return data[attr]

def get_description():
    with open('data/descriptions.json') as descriptions:
        data = json.load(descriptions)
        return data
