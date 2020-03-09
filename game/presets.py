from enum import Enum
from game.roles import Role
import random

class Preset(Enum):
    CLASSIC = [Role.SEER, Role.GUARDIAN_ANGEL, Role.WEREWOLF, Role.VILLAGER, Role.CUPID, Role.WEREWOLF, Role.HUNTER, Role.WITCH, Role.WEREWOLF, Role.MAYOR, Role.APPRENTICE_SEER, Role.WEREWOLF, Role.KNIGHT, Role.HUNTER, Role.WEREWOLF, Role.RESURRECTIONIST] # Enter more
    CHAOS = [Role.SEER, Role.WEREWOLF, Role.PRIEST, Role.CULTIST, Role.RESURRECTIONIST, Role.BOMB, Role.TEENAGE_WEREWOLF, Role.ALPHA, Role.WITCH, Role.UNIVERSAL, Role.JESTER, Role.EXECUTIONER]
    RANDOM = []

    def get_preset(str, count):
        if str == "RANDOM": #Game with random roles

            ###### DEBUG ONLY
            if count < 2:
                return list(map(lambda x:random.choice(list(Role)),range(count)))
            ###### DEBUG ONLY

            preset =  list(map(lambda x:random.choice(list(Role)),range(count)))
            while len(list(filter(lambda x:x.value < 100, preset))) == 0 or len(list(filter(lambda x:100 <= x.value < 200, preset))) == 0:
                print("Incorrect ")
                print(preset)
                preset = list(map(lambda x:random.choice(list(Role)),range(count)))
            return preset
        for preset in Preset:
            if preset.name == str:
                return preset.value[:count]
        return None
