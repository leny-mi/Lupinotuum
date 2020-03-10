import game.scheduler


class Scheduler:
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
