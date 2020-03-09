from enum import Enum
from game.roles import Roles
import random

class Preset(Enum):
    CLASSIC = [Roles.SEER, Roles.GUARDIAN_ANGEL, Roles.WEREWOLF, Roles.VILLAGER, Roles.CUPID, Roles.WEREWOLF, Roles.HUNTER, Roles.ALCHEMIST, Roles.WEREWOLF, Roles.MAYOR, Roles.APPRENTICE_SEER, Roles.WEREWOLF, Roles.KNIGHT, Roles.HUNTER, Roles.WEREWOLF, Roles.RESURRECTIONIST] # Enter more
    CHAOS = [Roles.SEER, Roles.WEREWOLF, Roles.PRIEST, Roles.CULTIST, Roles.RESURRECTIONIST, Roles.BOMB, Roles.TEENAGE_WEREWOLF, Roles.ALPHA, Roles.ALCHEMIST, Roles.UNIVERSAL, Roles.JESTER, Roles.EXECUTIONER]
    RANDOM = []

    def get_preset(str, count):
        if str == "RANDOM": #Game with random roles

            ###### DEBUG ONLY
            if count < 2:
                return list(map(lambda x:random.choice(list(Roles)),range(count)))
            ###### DEBUG ONLY

            preset =  list(map(lambda x:random.choice(list(Roles)),range(count)))
            while len(list(filter(lambda x:x.value < 100, preset))) == 0 or len(list(filter(lambda x:100 <= x.value < 200, preset))) == 0:
                print("Incorrect ")
                print(preset)
                preset = list(map(lambda x:random.choice(list(Roles)),range(count)))
            return preset
        for preset in Preset:
            if preset.name == str:
                return preset.value[:count]
        return None
