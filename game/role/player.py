
from game.roles import *
class Player:

    def __init__(self, id, role = None):
        self.role = Role(self)
        self.alive = True
        self.id = id
        print("Loaded player "+str(id) + " with Role " + role.__name__)
