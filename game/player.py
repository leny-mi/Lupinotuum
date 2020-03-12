# from game.roles import *


class Player:

    def __init__(self, player_id, role, name="No Name"):
        self.role = role(self)
        self.is_alive = True
        self.player_id = player_id
        self.name = name

        # self.group_id = None
        print("Loaded player " + str(player_id) + " with Role " + role.__name__)
