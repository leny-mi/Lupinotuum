from enum import Enum

class Role(Enum):
    # Town roles
    NARRATOR = -1

    VILLAGER = 0
    SEER = 1
    GUARDIAN_ANGEL = 2
    ALCHEMIST = 3
    HUNTER = 4
    CUPID = 5
    MAYOR = 6
    APPRENTICE_SEER = 7
    KNIGHT = 8
    VIGILANTE = 9
    RESURRECTIONIST = 10
    MAILMAN = 11
    ORACLE = 12
    PRIEST = 13
    BROTHER = 14
    MASON = 15
    BOMB = 16

    # Evil roles
    MAFIOSI = 100
    WEREWOLF = 101
    ALPHA = 102
    TEENAGE_WEREWOLF = 103
    VAMPIRE = 104
    SERIAL_KILLER = 105
    CULTIST = 106
    WITCH = 107

    # Neutral roles
    SURVIVOR = 200
    EXECUTIONER = 201
    PROTECTOR = 202
    JESTER = 203
    UNIVERSAL = 204

    def get_role(str):
        for role in Role:
            if role.name == str:
                return role
        return None
