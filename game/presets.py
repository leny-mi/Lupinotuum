from enum import Enum
#from game.roles import Roles
from game.all_roles import *
import random

class Preset(Enum):
    CLASSIC = [Seer, Guardian_Angel, Werewolf, Villager, Cupid, Werewolf, Hunter, Alchemist, Werewolf, Mayor, Apprentice_Seer, Werewolf, Knight, Hunter, Werewolf, Ressurectionist]
    #CLASSIC = [Roles.SEER, Roles.GUARDIAN_ANGEL, Roles.WEREWOLF, Roles.VILLAGER, Roles.CUPID, Roles.WEREWOLF, Roles.HUNTER, Roles.ALCHEMIST, Roles.WEREWOLF, Roles.MAYOR, Roles.APPRENTICE_SEER, Roles.WEREWOLF, Roles.KNIGHT, Roles.HUNTER, Roles.WEREWOLF, Roles.RESURRECTIONIST] # Enter more
    CHAOS = [Seer, Werewolf, Priest, Cultist, Ressurectionist, Bombshell, Teenage_Werewolf, Alpha, Alchemist, Universal, Jester, Executioner]
    #CHAOS = [Roles.SEER, Roles.WEREWOLF, Roles.PRIEST, Roles.CULTIST, Roles.RESURRECTIONIST, Roles.BOMBSHELL, Roles.TEENAGE_WEREWOLF, Roles.ALPHA, Roles.ALCHEMIST, Roles.UNIVERSAL, Roles.JESTER, Roles.EXECUTIONER]
    RANDOM = []

    def get_preset(str, count):
        if str == "RANDOM": #Game with random roles
            preset = list(map(lambda x:random.choice(list(all_roles)),range(count - 2)))
            preset.append(random.choice(list(good_roles)))
            preset.append(random.choice(list(evil_roles)))
            return preset
            ###### DEBUG ONLY
            #if count < 2:
            #    return list(map(lambda x:random.choice(all_roles),range(count)))
            ###### DEBUG ONLY
#
            #preset =  list(map(lambda x:random.choice(list(Roles)),range(count)))
            #while len(list(filter(lambda x:x.value < 100, preset))) == 0 or len(list(filter(lambda x:100 <= x.value < 200, preset))) == 0:
            #    print("Incorrect ")
            #    print(preset)
        #        preset = list(map(lambda x:random.choice(list(Roles)),range(count)))
            #return preset
        for preset in Preset:
            if preset.name == str:
                return preset.value[:count]
        return None
