from enum import Enum
from game.roles import *
import random

class Preset(Enum):
    CLASSIC = [Seer, Guardian_Angel, Werewolf, Villager, Cupid, Werewolf, Hunter, Alchemist, Werewolf, Mayor, Apprentice_Seer, Werewolf, Knight, Hunter, Werewolf, Ressurectionist]
    CHAOS = [Seer, Werewolf, Priest, Cultist, Ressurectionist, Bombshell, Teenage_Werewolf, Alpha, Alchemist, Universal, Jester, Executioner]
    RANDOM = []

    def get_preset(str, count):
        if str == "RANDOM": #Game with random roles
            preset = list(map(lambda x:random.choice(list(all_roles)),range(count - 2)))
            preset.append(random.choice(list(good_roles)))
            preset.append(random.choice(list(evil_roles)))
            return preset

        for preset in Preset:
            if preset.name == str:
                return preset.value[:count]
        return None
