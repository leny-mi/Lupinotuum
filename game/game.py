from game.roles import Roles
from usable.time_difference import Time
from threading import Timer
from datetime import timedelta, datetime
import asyncio

class Game:

    def __init__(self, interface, player_list, id, character_list, timezone):
        self.channels = []
        self.interface = interface
        self.player_list = player_list
        self.id = id
        self.character_list = character_list
        self.time = Time(timezone)

    async def commence_inital(self):
        await self.interface.game_broadcast(self.id, "Initializing game")

    async def commence_day(self):
        #TODO Day stuff
        #asyncio.set_event_loop(asyncio.new_event_loop())
        print(str(self.id) + " // 1")
        #asyncio.get_event_loop().create_task(self.interface.game_broadcast(self.id, "Day has started"))
        await self.interface.game_broadcast(self.id, "Day has started")
        #await self.schedule_event(0, 46, self.commence_vote)

    async def commence_vote(self):
        #TODO Vote stuff
        #asyncio.set_event_loop(asyncio.new_event_loop())
        print(str(self.id) + " // 2")
        #asyncio.get_event_loop().create_task(self.interface.game_broadcast(self.id, "Vote has started"))
        await self.interface.game_broadcast(self.id, "Vote has started")
        #await self.schedule_event(0, 47, self.commence_defense)

    async def commence_defense(self):
        #TODO Defense stuff

        await self.interface.game_broadcast(self.id, "Defense has started")
        #await self.schedule_event(0, 11, self.commence_tiebreaker)

    async def commence_tiebreaker(self):
        #TODO Tiebreaker stuff

        await self.interface.game_broadcast(self.id, "Tiebreaker has started")
        #await self.schedule_event(0, 3, self.commence_night)

    async def commence_night(self):
        #TODO Night stuff

        await self.interface.game_broadcast(self.id, "Night has started")
        #await self.schedule_event(0, 4, self.commence_day)

    async def time_scheduler(self):
        if time.seconds_until(19, 0) < 3600:
            ## TODO: Announce game start in 1h
            await asyncio.sleep(3600)
        else:
            ## TODO: Annouce game start at 19:00
            await sleep_until(19, 0)

        await commence_inital()
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
        secs = time.seconds_until(hour, minute)
        print("Seconds to next event "+str(secs))
        await asyncio.sleep(secs)
