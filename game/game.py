from game.roles import *
from usable.time_difference import Time
from threading import Timer
from datetime import timedelta, datetime
from game.role.player import Player
import asyncio
import random

class Game:



    def __init__(self, interface, player_list, id, character_list, timezone):
        self.channels = []
        self.interface = interface
        self.players_list = player_list
        self.players_alive = player_list
        self.id = id
        self.character_list = character_list
        self.time = Time(timezone)
        self.player_objs = []

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
            self.player_objs.append(Player(player_id, role))
        await self.interface.game_broadcast(self.id, "Initializing game")

    async def commence_day(self):
        #TODO Day stuff
        await self.interface.game_broadcast(self.id, "Day has started")

    async def commence_vote(self):
        #TODO Vote stuff
        await self.interface.game_broadcast(self.id, "Vote has started")

    async def commence_defense(self):
        #TODO Defense stuff

        await self.interface.game_broadcast(self.id, "Defense has started")

    async def commence_tiebreaker(self):
        #TODO Tiebreaker stuff

        await self.interface.game_broadcast(self.id, "Tiebreaker has started")

    async def commence_night(self):
        #TODO Night stuff

        await self.interface.game_broadcast(self.id, "Night has started")

    async def time_scheduler(self):
        if self.time.seconds_until(19, 0) < 3600:
            ## TODO: Announce game start in 1h
            await self.interface.game_broadcast(self.id, "Game will start at " + self.time.get_reverse_time(datetime.now()+timedelta(hour = 1)).strftime("%b %d %Y %H:%M:%S"))
            await asyncio.sleep(3600)
        else:
            ## TODO: EDIT FOR NEXXT DAY
            await self.interface.game_broadcast(self.id, "Game will start at " + datetime.now().replace(hour = 19, minute = 0, second = 0, microsecond = 0).strftime("%b %d %Y %H:%M:%S"))

            await self.sleep_until(19, 0)

        ## TODO: CHECK IF ALL PLAYERS JOINED

        await self.commence_inital()

        await self.sleep_until(20, 0)
        await self.commence_night()

        while True: #Edit to end at game end
            await self.sleep_until(8, 0)
            await self.commence_day()
            await self.sleep_until(17, 30)
            await self.commence_vote()
            await self.sleep_until(18, 40)
            await self.commence_defense()
            await self.sleep_until(19, 0)
            await self.commence_tiebreaker()
            await self.sleep_until(20, 0)
            await self.commence_night()

    async def sleep_until(self, hour, minute):
        secs = self.time.seconds_until(hour, minute)
        print("Seconds to next event "+str(secs))
        while self.debug == 0:
            await asyncio.sleep(1)
        self.debug = 0
        #await asyncio.sleep(secs)
