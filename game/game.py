import random

from game import roles
from game import player

from usable import group

class Game:

    def __init__(self, interface, player_list, game_id, character_list, time):
        self.interface = interface  # IO interface
        self.players_list = player_list  # List of player IDs
        self.id = game_id  # Game ID
        self.character_list = character_list  # List of roles
        self.time = time  # Time Object

        # self.players_alive = player_list.copy() # Maybe not needed
        self.player_objs = {}  # Map IDs to Objects
        self.votes = {}  # Map IDs to Votes
        self.groups = {}  # Map role to channels

        self.day_n = 1
        self.tie = 0
        self.to_die = None

    async def commence_initial(self):
        print("Debug: Initialize on game")
        # Choose role list subset
        role_choice = random.sample(self.character_list, len(self.players_list))
        while roles.good_roles & set(role_choice) == set() or roles.evil_roles & set(role_choice) == set():
            role_choice = random.sample(self.character_list, len(self.players_list))

        # Distribute roles to players
        random.shuffle(role_choice)
        for role, player_id in zip(role_choice, self.players_list):
            username = self.interface.get_user(player_id).name
            self.player_objs[player_id] = (player.Player(player_id, role, name=username))
        await self.interface.game_broadcast(self.id, "Initializing game")
        for concrete_player in self.sort_players():
            await concrete_player.role.on_game_start(self)
        await self.refresh_groups()

    async def commence_day(self):
        # TODO Day stuff
        print("Debug: Day", self.day_n, "has started")

        await self.interface.game_broadcast(self.id, "Day " + str(self.day_n) + " has started")
        self.day_n += 1
        # TODO: CHECK IF TIE LIMIT REACHED
        self.to_die = None
        for concrete_player in self.sort_players(only_alive=True):
            await concrete_player.role.on_sunrise(self)
        await self.refresh_groups()

    async def commence_vote(self):
        # TODO Vote stuff
        print("Debug: Vote has started")
        self.votes = {}
        await self.interface.game_broadcast(self.id, "Vote has started")
        for concrete_player in self.sort_players(only_alive=True):
            await concrete_player.role.on_votestart(self)
        await self.refresh_groups()

    async def commence_voteend(self):
        # TODO Defense stuff
        print("Debug: Vote has ended")
        await self.interface.game_broadcast(self.id, "Vote has ended")
        for concrete_player in self.sort_players(only_alive=True):
            await concrete_player.role.on_voteend(self)

        max_votes = max(self.votes.values()) if len(self.votes.values()) > 0 else 0
        print("Debug: max_votes =", max_votes)
        print("Debug: votes =", self.votes)
        most_voted = list(filter(lambda x: self.votes.get(x.id, 0) == max_votes, self.sort_players(only_alive=True)))
        print("Debug: most_voted =", most_voted)

        if len(most_voted) > 1:
            await self.interface.game_broadcast(self.id, "There has been a tie between " + " and ".join(
                [", ".join(list(map(lambda x: x.name, most_voted[:-1]))),
                 most_voted[-1].name]) + "\nVote again on either of them by " + self.time.get_next_time_string(19, 0))
            for concrete_player in self.sort_players(only_alive=True):
                await concrete_player.role.on_defense(self, most_voted)
                await concrete_player.role.on_votestart(self)
            self.tie += 1

        else:
            # TODO: PRINT ALL VOTES
            await self.interface.game_broadcast(self.id, most_voted[
                0].name + " will die today. The hanging will be at " + self.time.get_next_time_string(19, 30))
            self.to_die = most_voted[0]
            self.tie = 0
            for concrete_player in self.sort_players(only_alive=True):
                await concrete_player.role.on_deathrow(self, self.to_die)

        await self.refresh_groups()

    async def commence_tiebreaker(self):
        # TODO Tiebreaker stuff
        print("Debug: Tiebreaker has started")
        if self.tie == 0:
            return

        await self.interface.game_broadcast(self.id, "Tiebreaker has started")

        self.votes = {}

        for concrete_player in self.sort_players(only_alive=True):
            await concrete_player.role.on_voteend(self)

        max_votes = max(self.votes.values()) if len(self.votes.values()) > 0 else 0
        print("Debug: max_votes =", max_votes)
        most_voted = list(filter(lambda x: self.votes.get(x.id, 0) == max_votes, self.sort_players(only_alive=True)))
        print("Debug: most_voted =", most_voted)

        if len(most_voted) > 1:
            await self.interface.game_broadcast(self.id, "There has been a tie between" + " and ".join(
                [", ".join(list(map(lambda x: x.name, most_voted[:-1]))),
                 most_voted[-1].name]) + "\nNo one will die today...")
            return

        else:
            # TODO: PRINT ALL VOTES
            await self.interface.game_broadcast(self.id, most_voted[
                0].name + " will die today. The hanging will be at " + self.time.get_next_time_string(19, 30))
            self.to_die = most_voted[0]
            self.tie = 0
            for concrete_player in self.sort_players(only_alive=True):
                await concrete_player.role.on_deathrow(self, self.to_die)

        await self.refresh_groups()

    async def commence_hanging(self):
        print("Debug: Hanging has started")
        if self.to_die is None:
            return
        for concrete_player in self.sort_players(only_alive=True):
            await concrete_player.role.on_hang(self, self.to_die)
        # await self.interface.game_broadcast(self.id, self.to_die.name + " has been hanged.")
        await self.refresh_groups()

    async def commence_night(self):
        # TODO Night stuff
        print("Debug: Night has started")
        await self.interface.game_broadcast(self.id, "Night has started")
        for concrete_player in self.sort_players(only_alive=True):
            await concrete_player.role.on_nightfall(self)
        await self.refresh_groups()

    #
    async def player_die(self, dead_player, murderer):
        for concrete_player in self.sort_players(only_alive=True):
            await concrete_player.role.on_playerdeath(self, dead_player, murderer)

    async def create_group(self, group_bind):
        g = group.Group(self.interface, name=group_bind + "_on_" + self.interface.get_channel(
            self.id).guild.name + "_" + self.interface.get_channel(self.id).name)
        await g.instantiate_channel()
        self.groups[group_bind] = g
        return g

    async def refresh_groups(self):
        for concrete_group in self.groups:
            concrete_group.refresh_members()

    def sort_players(self, only_alive=False):
        players = list(map(lambda y: self.player_objs[y], list(self.players_list)))
        players.sort(key=lambda x: roles.role_order.index(x.role.__class__))
        return list(filter(lambda x: not only_alive or x.is_alive, players))

    def add_vote(self, player_id, vote_count):
        if player_id not in self.votes:
            self.votes[player_id] = vote_count
        else:
            self.votes[player_id] += vote_count

    def get_player_list(self, only=True, alive=False):
        return "\n".join(map(lambda x: " ".join([str(x[0] + 1), '-', x[1].name]),
                             filter(lambda y: y[1].is_alive or not only != alive,
                                    enumerate(map(lambda z: self.player_objs[z], self.sort_players(only_alive=False))))))

    def get_player_id_at(self, n):
        return self.get_player_obj_at(n).id

    def get_player_obj_at(self, n):
        return self.sort_players(only_alive=False)[n - 1]
