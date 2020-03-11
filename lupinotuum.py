
import discord

from data import datamanager

from usable import group
from usable import time_difference
from usable import utils

from game import roles
from game import scheduler
from game import presets
from game import game


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        await client.change_presence(activity=discord.Game(name='Write $setup to start a game'))
        self.state_map = {} #Map channel to state
        self.react_map = {} #Map channel to react message
        self.role_list = {} #Map channel to role list
        self.count_map = {} #Map channel to count
        self.game_map  = {} #Map channel to game
        self.sched_map = {} #Map channel to scheduler (PROBALBY NOT NEEDED AFTER DEBUG)
        self.player_map= {} #Map channel to player list
        self.time_map  = {} #Map channel to time object

    async def on_message(self, message):
        # Don't react to bots
        if message.author.bot:
            return

        if message.channel.id in self.state_map:
            print(message.content[:10] + "" + str(self.state_map[message.channel.id]))

        # Game setup
        if message.channel.id not in self.state_map or self.state_map[message.channel.id] < 3:
            await self.setup(message)

        # User writes $setup while a game in runnning
        elif (message.content == "$setup"):
            await message.channel.send('Game is already running. There can only be ohne game per text channel.')

        # User uses "info"
        await self.information_calls(message)

        # Debug
        await self.debugCommands(message)


    # Handles Game setup such as "setup, continue, reset, listpresets, addrole, delrole, current, done"
    async def setup(self, message):
        # GAME SETUP

        # User writes $setup, game to be started
        if not message.channel.id in self.state_map:
            if message.content == "$setup":
                #TODO SETUP
                print("Setting up")
                self.state_map[message.channel.id] = 0
                self.react_map[message.channel.id] = await message.channel.send('Setting up game. To reset, write `$reset`. If you want to participate, react with :wolf: under this message. After all players have reacted, write `$continue`')
                await self.react_map[message.channel.id].add_reaction('🐺')

        # User writes continue after reacting
        elif (self.state_map[message.channel.id] == 0 and message.content == '$continue'):
            print("Continue")
            self.state_map[message.channel.id] = 1
            message = await message.channel.fetch_message(self.react_map[message.channel.id].id)
            count = list(filter(lambda x: x.emoji == '🐺', message.reactions))[0].count - 1
            if count < 0: ## TODO:  Enable this filter again (set on 4)
                count = max(4, count) ## TODO:  Remove this after debug phase
                await message.channel.send("Not enough players. There should be at least 4")
                self.state_map.pop(message.channel.id)
                return
            self.count_map[message.channel.id] = count
            self.player_map[message.channel.id] = set(map(lambda x: x.id,await list(filter(lambda x: x.emoji == '🐺', message.reactions))[0].users().flatten()))
            self.player_map[message.channel.id].remove(685910279070285877)
            print(self.player_map[message.channel.id]) #DEBUG
            await message.channel.send(str(count) + " players have entered.\n" + 'Add roles to the role list by typing `$addrole ROLE`. For example `$addrole ORACLE`. There should be at least one role more than there are players. To see all roles type `$rolelist`. To remove a role type `$delrole ROLE`. To look at your current role list, type `$current`. \nTo choose a preset type `$preset PRESET` and to view all presets use `$presetlist`.\nType `$done` when you are finished or `$reset` to start over')

        # Set a preset
        elif (self.state_map[message.channel.id] == 1 and message.content[:8] == '$preset '):
            self.role_list[message.channel.id] = presets.Preset.get_preset(message.content[8:], self.count_map[message.channel.id] + 1)
            await message.channel.send("Set preset to "+message.content[8:])

        # Get all presets
        elif (self.state_map[message.channel.id] == 1 and message.content == '$presetlist'):
            tmessage = 'There are the following presets: ```'
            for preset in presets.Preset:
                tmessage += "\n - " + preset.name
            await message.channel.send(tmessage + "``` Use `$presetinfo PRESET` to get a list of roles for the given preset")

        # Get a certain preset
        elif (self.state_map[message.channel.id] == 1 and message.content[:12]== '$presetinfo '):
            tmessage = 'Preset '+message.content[12:]+' contains: ```'
            for role in presets.Preset.get_preset(message.content[12:], self.count_map[message.channel.id] + 1):
                tmessage += "\n - " + role.__name__
            await message.channel.send(tmessage + "```")

        # User writes $reset before completing setup
        elif (self.state_map[message.channel.id] <= 1 and message.content == '$reset'):
            self.state_map.pop(message.channel.id)
            await message.channel.send("Game has been cancelled. Type $setup to start a new game.")

        # User adds a role using '$addrole ...'
        elif (self.state_map[message.channel.id] == 1 and message.content[0:9] == '$addrole '):
                role = next(obj for obj in roles.all_roles if obj.__name__.lower()==message.content[9:].lower())
                #role = Roles.get_role(message.content[9:])
                if role is None:
                    await message.channel.send('Invalid role. Use `$list` to see all roles')
                    return

                if not message.channel.id in self.role_list:
                    self.role_list[message.channel.id] = []
                self.role_list[message.channel.id].append(role)
                await message.channel.send('Added '+message.content[9:].title()+' to role list')

        # User removes a role using '$delrole ...'
        elif (self.state_map[message.channel.id] == 1 and message.content[0:9] == '$delrole '):
                role = next(obj for obj in roles.all_roles if obj.__name__.lower()==message.content[9:].lower())
                #role = Roles.get_role(message.content[9:])
                if role is None:
                    await message.channel.send('Invalid role. Use `$current` to see the role list')
                    return

                if not message.channel.id in self.role_list:
                    self.role_list[message.channel.id] = []
                if role not in self.role_list[message.channel.id]:
                    await message.channel.send(message.content[9:].title()+' not in role list')
                    return
                self.role_list[message.channel.id].remove(role)
                await message.channel.send('Removed '+message.content[9:].title()+' from role list')

        # User removes a role using '$current ...'
        elif (self.state_map[message.channel.id] == 1 and message.content == '$current'):
                if not message.channel.id in self.role_list or len(self.role_list[message.channel.id]) == 0:
                    await message.channel.send('Role list is empty.')
                    return
                await message.channel.send('The following roles are in the role list:' + utils.format_role_list(self.role_list[message.channel.id]))

        # User writes $done before adding enough roles
        elif (self.state_map[message.channel.id] == 1 and message.content == '$done' and (message.channel.id not in self.role_list or len(self.role_list[message.channel.id]) <= self.count_map[message.channel.id])):
            await message.channel.send('There are not enough roles. There should be at least '+str(self.count_map[message.channel.id] + 1)+' roles.')

        # User writes $done after adding enough roles
        elif (self.state_map[message.channel.id] == 1 and message.content == '$done' and len(self.role_list[message.channel.id]) > self.count_map[message.channel.id]):
            if roles.good_roles & set(self.role_list[message.channel.id]) == set():
                await message.channel.send('There should be at least one town alligned role')
                return
            if roles.evil_roles & set(self.role_list[message.channel.id]) == set():
                await message.channel.send('There should be at least one evil alligend role')
                return
            await message.channel.send('The following roles will be distributed:' + utils.format_role_list(self.role_list[message.channel.id]))
            #with open('config.json') as configfile:
            #    data = json.load(configfile)
            await message.channel.send('Please join https://discord.gg/'+ datamanager.get_config('invite_link') +' for private communications\nGame with ID '+str(message.channel.id)+' will start at INSERT TIME on INSERT DATE')
            await message.channel.send('Enter your timezone using `$timezone TIMEZONE`. Common timezones may be UTC, CET, Europe/Berlin, America/New_York, Asia/Dubai. For a list of all accepted timezones visit https://en.wikipedia.org/wiki/List_of_tz_database_time_zones and search the third column.')

            self.state_map[message.channel.id] = 2


            #TODO INITIALIZE GAME HERE
            ## TODO: ENTER TIME ZONE
            #self.game_map[message.channel.id] = game.Game(self, self.player_map[message.channel.id], message.channel.id, self.role_list[message.channel.id], 'Europe/Berlin')
            #await self.game_map[message.channel.id].time_scheduler();


        elif (self.state_map[message.channel.id] == 2 and message.content[:10] == '$timezone '):
            print("Entered Timezone")
            #try:
            self.time_map[message.channel.id] = time_difference.Time(message.content[10:])

            print(2)
            self.game_map[message.channel.id] = game.Game(self, self.player_map[message.channel.id], message.channel.id, self.role_list[message.channel.id], self.time_map[message.channel.id])
            print(2.5)
            self.sched_map[message.channel.id] = scheduler.Scheduler(self, self.time_map[message.channel.id], self.game_map[message.channel.id])
            print(3)
            self.state_map[message.channel.id] = 3
            print(4)
            await self.sched_map[message.channel.id].initialize()

            await message.channel.send('The game has ended. Thank you for playing :)')
            self.state_map.pop(message.channel.id)


            #except:
            #    await message.channel.send('Unknown timezone. Enter your timezone using `$timezone TIMEZONE`. Common timezones may be UTC, CET, Europe/Berlin, America/New_York, Asia/Dubai. For a list of all accepted timezones visit https://en.wikipedia.org/wiki/List_of_tz_database_time_zones and search the third column.')



    # Debug stuff
    async def debugCommands(self, message):

        if message.content == 'create':
            print("Create")
            self.c = group.Group(self, 'test_hi1')
            await self.c.instantiate_channel()

        if message.content == 'ref':
            print("refresh")
            await self.c.refresh_members()

        if message.content == 'add':
            print("add")
            self.c.add_user(298488132255350784)

        if message.content == 'remove':
            print("remove")
            self.c.remove_user(298488132255350784)

        if message.content == 'del':
            print("deleting")
            await self.c.delete_channel()

        if message.content == '.next':
            print("Next")
            self.sched_map[message.channel.id].debug = 1

        if message.content == 'berlin':
            print("start debug berlin...")
            self.game_map[message.channel.id] = game.Game(self, None, message.channel.id, None, 'Europe/Berlin')
            await self.game_map[message.channel.id].time_scheduler();

        if message.content == 'new_york':
            print("start debug york...")
            self.game_map[message.channel.id] = game.Game(self, None, message.channel.id, None, 'America/New_York')
            await self.game_map[message.channel.id].time_scheduler();

        if message.content == 'onservermou':
            await message.channel.send("Result: "+ str(utils.check_all_players_joined(self, [298488132255350784])))

        if message.content == 'onservernon':
            await message.channel.send("Result: "+ str(utils.check_all_players_joined(self, [270240574748098561])))

    # Get information about roles or presets
    async def information_calls(self, message):
        # User writes $list and gets a display of all roles
        if (message.content == '$rolelist'):
            print("List")
            tmessage = 'The following roles exist'
            tmessage += "\nTown alligned roles:```"
            for role in roles.good_roles:
                tmessage += ("\n - " + role.__name__)
            tmessage += "```Evil alligned roles: ```"
            for role in roles.evil_roles:
                tmessage += ("\n - " + role.__name__)
            tmessage += "```Neutral alligned roles: ```"
            for role in roles.neutral_roles:
                tmessage += ("\n - " + role.__name__)

            await message.channel.send(tmessage + "```")

        elif (message.content[:6] == "$info "):
            print("AM HERE")
            if message.content[6:].lower() not in set(map(lambda x: x.__name__.lower(), roles.all_roles)):
                await message.channel.send('Invalid role. Use `$rolelist` to see all roles')
                return

            data = datamanager.get_description()
            if message.content[6:].upper() not in data:
                await message.channel.send('No role description available :(')
                return
            stats = data[message.content[6:].upper()]
            #color = (10066176 if role.value == -1 else (color = 52224 if role.value < 100 else (7829367 if role.value >= 200 else 16711680)))
            if message.content[6:].lower() == 'narrator':
                color = 10066176
            elif message.content[6:].lower() in set(map(lambda x: x.__name__.lower(), roles.good_roles)):
                color = 52224
            elif message.content[6:].lower() in set(map(lambda x: x.__name__.lower(), roles.evil_roles)):
                color = 16711680
            else:
                color = 7829367

            embed = discord.Embed(color = color ,title = stats['name'], type = 'rich', description = "Role card")
            embed.add_field(name = "Description", value = stats['description'], inline = False)
            embed.add_field(name = "Abilities", value = stats['abilities'], inline = True)
            embed.add_field(name = 'Alligment', value = stats['allignment'], inline = True)
            embed.add_field(name = 'Usage', value = stats['usage'], inline = False)
            await message.channel.send("", embed = embed)



    # Send a message to a game channel
    async def game_broadcast(self, game_id, message):
        await self.get_channel(game_id).send(message)

    # Send a message to a user
    async def game_direct(self, user_id, message):
        await self.get_user(user_id).dm_channel.send()

    # End the game
    def end_game(id):
        self.game_broadcast(id, "The game has ended. Use `$setup` to start another game")
        self.state_map.pop(id)


if not datamanager.check_json():
    print("Multiple errors have occured. Bot has not been started")
    quit()

client = MyClient(activity = discord.Activity(name = 'Write $setup to start a game' , type = discord.ActivityType.custom))

#with open('config.json') as configfile:
#    data = json.load(configfile)

try:
    client.run(datamanager.get_config('token'))
except discord.errors.LoginFailure as exception:
    if str(exception) == 'Improper token has been passed.':
        print('Error: an improper token has been passed. Make sure that you added the correct token to config.json')
    else:
        print(exception)
