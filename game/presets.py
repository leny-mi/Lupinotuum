import enum
import random

from game import roles


class Preset(enum.Enum):
    CLASSIC = [roles.Seer, roles.Guardian_Angel, roles.Werewolf, roles.Villager, roles.Cupid, roles.Werewolf, roles.Hunter, roles.Alchemist, roles.Werewolf, roles.Mayor, roles.Apprentice_Seer, roles.Werewolf, roles.Knight, roles.Hunter, roles.Werewolf, roles.Resurrectionist]
    CHAOS = [roles.Seer, roles.Werewolf, roles.Priest, roles.Cultist, roles.Resurrectionist, roles.Bombshell, roles.Teenage_Werewolf, roles.Alpha, roles.Alchemist, roles.Universal, roles.Jester, roles.Executioner]
    RANDOM = []

    def get_preset(str, count):
        if str == "RANDOM":  # Game with random roles
            preset = list(map(lambda x: random.choice(list(roles.all_roles)), range(count - 2)))
            preset.append(random.choice(list(roles.good_roles)))
            preset.append(random.choice(list(roles.evil_roles)))
            return preset

        for preset in Preset:
            if preset.name == str:
                return preset.value[:count]
        return None
