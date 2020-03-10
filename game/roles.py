from game import role

# Good Roles

class Good(role.Role):
    pass

class Hunter(Good):
    pass

class Guardian_Angel(Good):
    pass

class Villager(Good):
    pass

class Vigilante(Good):
    pass

class Seer(Good):
    pass

class Ressurectionist(Good):
    pass

class Priest(Good):
    pass

class Oracle(Good):
    pass

class Mayor(Good):
    pass

class Mason(Good):
    pass

class Mailman(Good):
    pass

class Knight(Good):
    pass

class Cupid(Good):
    pass

class Brother(Good):
    pass

class Bombshell(Good):
    pass

class Apprentice_Seer(Good):
    pass

class Alchemist(Good):
    pass

class Fox(Good):
    pass

class Teacher(Good):
    pass

class Lord(Good):
    pass

# Evil Roles

class Evil(role.Role):
    pass

class Alpha(Evil):
    pass

class Ancient(Evil):
    pass

class Cultist(Evil):
    pass

class Mafiosi(Evil):
    pass

class Serial_Killer(Evil):
    pass

class Teenage_Werewolf(Evil):
    pass

class Vampire(Evil):
    pass

class Werewolf(Evil):
    pass

class Witch(Evil):
    pass

class White(Evil):
    pass


# Neutral Roles

class Neutral(role.Role):
    pass

class Universal(Neutral):
    pass

class Survivor(Neutral):
    pass

class Protector(Neutral):
    pass

class Jester(Neutral):
    pass

class Executioner(Neutral):
    pass

class Copycat(Neutral):
    pass

class Actor(Neutral):
    pass


good_roles    = {Villager, Seer, Guardian_Angel, Alchemist, Hunter, Cupid, Mayor, Apprentice_Seer, Knight, Vigilante, Bombshell, Ressurectionist, Mailman, Oracle, Priest, Brother, Mason, Fox, Teacher, Lord}
evil_roles    = {Mafiosi, Werewolf, Alpha, Teenage_Werewolf, Vampire, Serial_Killer, Cultist, Ancient, Witch, White}
neutral_roles = {Survivor, Executioner, Protector, Jester, Universal, Copycat, Actor}

all_roles = good_roles.union(evil_roles).union(neutral_roles)
role_order = [Witch, Villager, Seer, Guardian_Angel, Alchemist, Hunter, Cupid, Mayor, Apprentice_Seer, Knight, Vigilante, Bombshell, Ressurectionist, Mailman, Oracle, Priest, Brother, Mason, Fox, Teacher, Lord, Mafiosi, Werewolf, Alpha, Teenage_Werewolf, Vampire, Serial_Killer, Cultist, Ancient, White, Survivor, Executioner, Protector, Jester, Universal, Copycat, Actor]
