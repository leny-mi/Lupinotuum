
#from game.roles import *

class Player:

    def __init__(self, id, role, name = "No Name"):
        self.role = role(self)
        self.alive = True
        self.id = id
        self.name = name

        self.group_id = None
        print("Loaded player "+str(id) + " with Role " + role.__name__)
