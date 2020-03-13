import json


def check_json():
    try:
        with open('data/config.json') as configfile:
            data = json.load(configfile)
            needed_attributes = ['token', 'covert_server', 'invite_link']  # Enter all needed attributes in json here
            correct = True
            for attribute in needed_attributes:
                if attribute not in data:
                    correct = False
                    print("Error: Attribute " + attribute + " not found. Please enter " + attribute + " in config.json")
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
