
#from game.roles import *
class Player:

    def __init__(self, id, role, name = "No Name"):
        self.role = Role(self)
        self.alive = True
        self.id = id
        self.name = name
        print("Loaded player "+str(id) + " with Role " + role.__name__)
