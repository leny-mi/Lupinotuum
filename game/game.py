import game.roles
import usable.time_difference.Time
from threading import Timer
from datetime import timedelta, datetime
from game.role.player import Player
from usable import utils
import asyncio
import random

class Game:



    def __init__(self, interface, player_list, id, character_list, timezone):
        self.channels = {} # Created channels
        self.interface = interface # IO interface
        self.players_list = player_list # List of player IDs
        # self.players_alive = player_list.copy() # Maybe not needed
        self.id = id # Game ID
        self.character_list = character_list # List of roles
        self.time = Time(timezone) # Time Object
        self.player_objs = {} # Map IDs to Objects
        self.votes = {} # Map IDs to Votes

        self.tie = False
        self.to_die = None

        self.debug = 0 ## TODO: REMOVE LATER

    async def commence_inital(self):
        # Choose List subset
        rolechoice = random.sample(self.character_list, len(self.players_list))
        while good_roles & set(rolechoice) == set() or evil_roles & set(rolechoice) == set():
            print("Incorrect ")
            print(rolechoice)
            rolechoice = random.sample(self.character_list, len(self.players_list))

        # Distribute
        random.shuffle(rolechoice)
        for role, player_id in zip(rolechoice, self.players_list):
            self.player_objs[player_id] = (Player(player_id, role))
        await self.interface.game_broadcast(self.id, "Initializing game")
        for player in self.sort_players():
            player.role.on_gamestart(self)

    async def commence_day(self):
        #TODO Day stuff

        await self.interface.game_broadcast(self.id, "Day has started")
        self.tie = False
        self.to_die = None
        for player in self.sort_players(only_alive = True):
            player.role.on_sunrise(self)

    async def commence_vote(self):
        #TODO Vote stuff
        self.votes = {}
        await self.interface.game_broadcast(self.id, "Vote has started")
        for player in self.sort_players(only_alive = True):
            player.role.on_votestart(self)

    async def commence_voteend(self):
        #TODO Defense stuff

        await self.interface.game_broadcast(self.id, "Vote has ended")
        for player in self.sort_players(only_alive = True):
            player.role.on_voteend(self)

        max_votes = max(self.votes.values())
        most_voted = list(filter(lambda x: self.votes[x] == max_votes, self.sort_players(only_alive = True)))

        if len(most_voted) > 1:
            await self.interface.game_broadcast(self.id, "There has been a tie between" + ", ".join(list(map(lambda x: self.player_objs[x].name, most_voted))) + "\nVote again on either of them by "+self.time.get_next_time_string(19,0))
            for player in self.sort_players(only_alive = True):
                player.role.on_votestart(self)
            self.tie = True

        else:
            # TODO: PRINT ALL VOTES
            await self.interface.game_broadcast(self.id, self.player_objs[most_voted[0]].name + " will die today. The hanging will be at " +  self.time.get_next_time_string(19,30))
            to_die = most_voted[0]

    async def commence_tiebreaker(self):
        #TODO Tiebreaker stuff
        print("Tiebreaker start")
        if not self.tie:
            return

        await self.interface.game_broadcast(self.id, "Tiebreaker has started")

        self.votes = {}

        for player in self.sort_players(only = True):
            player.role.on_voteend()

        max_votes = max(self.votes.values())
        most_voted = list(filter(lambda x: self.votes[x] == max_votes, self.sort_players(only_alive = True)))

        if len(most_voted) > 1:
            await self.interface.game_broadcast(self.id, "There has been a tie between" + ", ".join(list(map(lambda x: self.player_objs[x].name, most_voted))) + "\nNo one will die today...")
            return

        else:
            # TODO: PRINT ALL VOTES
            await self.interface.game_broadcast(self.id, self.player_objs[most_voted[0]].name + " will die today. The hanging will be at " +  self.time.get_next_time_string(19,30))
            to_die = most_voted[0]


    async def commence_hanging(self):
        print("Hanging start")

        pass

    async def commence_night(self):
        #TODO Night stuff

        await self.interface.game_broadcast(self.id, "Night has started")

    async def time_scheduler(self):
        if self.time.seconds_until(19, 0) < 3600:
            ## TODO: Announce game start in 1h
            await self.interface.game_broadcast(self.id, "Game will start at " + self.time.get_time_in_string(1,0))
            await asyncio.sleep(3600)
        else:
            await self.interface.game_broadcast(self.id, "Game will start at " + self.time.get_next_time_string(19,0))
            await self.sleep_until(19, 0)

        ## TODO: CHECK IF ALL PLAYERS JOINED

        if not utils.check_all_players_joined(self.players_list):
            with open('../config.json') as configfile:
                data = json.load(configfile)
            await message.channel.send('Not all players have joined. Please join https://discord.gg/'+ data['invite_link'] +' for private communications\nGame with ID '+str(message.channel.id)+' will start at ' + self.time.get_next_time_string(20,0))

            await self.sleep_until(20,0)
            ## TODO: If game setups at 18:59, this won't be enough time for another join

            if not utils.check_all_players_joined(self.players_list):
                await self.interface.game_broadcast(self.id, "Not all players have joined. Your game has been cancelled. Use `$setup` to start a new game")


            await self.commence_inital()
            await self.sleep_until(20,15)

        else:


            await self.commence_inital()
            await self.sleep_until(20, 0)


        await self.commence_night()

        while True: #Edit to end at game end
            await self.sleep_until(8, 0)
            await self.commence_day()
            await self.sleep_until(17, 30)
            await self.commence_vote()
            await self.sleep_until(18, 40)
            await self.commence_voteend()
            await self.sleep_until(19, 0)
            await self.commence_tiebreaker()
            await self.sleep_until(19, 30)
            await self.commence_hanging()
            await self.sleep_until(20, 0)
            await self.commence_night()

    async def sleep_until(self, hour, minute):
        secs = self.time.seconds_until(hour, minute)
        print("Seconds to next event "+str(secs))
        while self.debug == 0:      # DEBUG:
            await asyncio.sleep(1)  # DEBUG:
        self.debug = 0              # DEBUG:
        #await asyncio.sleep(secs)

    def sort_players(self, only_alive = False):
        players = player_list.copy()
        players.sort(key = lambda x: role_order.index(x.role.__class__))
        return list(filter(lambda x: not only_alive or self.player_objs[x].alive, players))

    def add_vote(self, player_id, vote_count):
        if player_id not in self.votes:
            self.votes[player_id] = vote_count
        else:
            self.votes[player_id] += vote_count
