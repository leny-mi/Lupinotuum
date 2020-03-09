import json
import discord
from usable import utils
from usable.group import Group
from game.roles import Role
from game.presets import Preset
from game.game import Game

class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        await client.change_presence(activity=discord.Game(name='Write $setup to start a game'))
        self.state_map = {} #Map channel to state
        self.react_map = {} #Map channel to react message
        self.role_list = {} #Map channel to role list
        self.count_map = {} #Map channel to count
        self.game_map  = {} #Map channel to game

    async def on_message(self, message):
        # Don't react to bots
        if message.author.bot:
            return

        # Game setup
        if message.channel.id not in self.state_map or self.state_map[message.channel.id] < 2:
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
            await message.channel.send(str(count) + " players have entered.\n" + 'Add roles to the role list by typing `$addrole ROLE`. For example `$addrole ORACLE`. There should be at least one role more than there are players. To see all roles type `$rolelist`. To remove a role type `$delrole ROLE`. To look at your current role list, type `$current`. \nTo choose a preset type `$preset PRESET` and to view all presets use `$presetlist`.\nType `$done` when you are finished or `$reset` to start over')

        # Set a preset
        elif (self.state_map[message.channel.id] == 1 and message.content[:8] == '$preset '):
            self.role_list[message.channel.id] = Preset.get_preset(message.content[8:], self.count_map[message.channel.id] + 1)
            await message.channel.send("Set preset to "+message.content[8:])


        # Get all presets
        elif (self.state_map[message.channel.id] == 1 and message.content == '$presetlist'):
            tmessage = 'There are the following presets: ```'
            for preset in Preset:
                tmessage += "\n - " + preset.name
            await message.channel.send(tmessage + "``` Use `$presetinfo PRESET` to get a list of roles for the given preset")

        # Get a certain preset
        elif (self.state_map[message.channel.id] == 1 and message.content[:12]== '$presetinfo '):
            tmessage = 'Preset '+message.content[12:]+' contains: ```'
            for role in Preset.get_preset(message.content[12:], self.count_map[message.channel.id] + 1):
                tmessage += "\n - " + role.name
            await message.channel.send(tmessage + "```")



        # User writes $reset before completing setup
        elif (self.state_map[message.channel.id] <= 1 and message.content == '$reset'):
            self.state_map.pop(message.channel.id)
            await message.channel.send("Game has been cancelled. Type $setup to start a new game.")

        # User adds a role using '$addrole ...'
        elif (self.state_map[message.channel.id] == 1 and message.content[0:9] == '$addrole '):
                role = Role.get_role(message.content[9:])
                if role is None:
                    await message.channel.send('Invalid role. Use `$list` to see all roles')
                    return

                if not message.channel.id in self.role_list:
                    self.role_list[message.channel.id] = []
                self.role_list[message.channel.id].append(role)
                await message.channel.send('Added '+message.content[9:]+' to role list')

        # User removes a role using '$delrole ...'
        elif (self.state_map[message.channel.id] == 1 and message.content[0:9] == '$delrole '):
                role = Role.get_role(message.content[9:])
                if role is None:
                    await message.channel.send('Invalid role. Use `$current` to see the role list')
                    return

                if not message.channel.id in self.role_list:
                    self.role_list[message.channel.id] = []
                if role not in self.role_list[message.channel.id]:
                    await message.channel.send(message.content[9:]+' not in role list')
                    return
                self.role_list[message.channel.id].remove(role)
                await message.channel.send('Removed '+message.content[9:]+' from role list')

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
            if min(map(lambda x:x.value, self.role_list[message.channel.id])) >= 100:
                await message.channel.send('There should be at least one town alligned role')
                return
            if max(map(lambda x:x.value%200, self.role_list[message.channel.id])) < 100:
                await message.channel.send('There should be at least one evil alligend role')
                return
            await message.channel.send('The following roles will be distributed:' + utils.format_role_list(self.role_list[message.channel.id]))
            with open('config.json') as configfile:
                data = json.load(configfile)
            await message.channel.send('Please join https://discord.gg/'+ data['invite_link'] +' for private communications\nGame with ID '+str(message.channel.id)+' will start at INSERT TIME on INSERT DATE')
            self.state_map[message.channel.id] = 2

            #TODO INITIALIZE GAME HERE

            #TODO Add list decoder
            #TODO Check list size

    # Debug stuff
    async def debugCommands(self, message):

        if message.content == 'create':
            print("Create")
            self.c = Group(self, 'test_hi1')
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

        if message.content == 'berlin':
            print("start debug berlin...")
            self.game_map[message.channel.id] = Game(self, None, message.channel.id, None, 'Europe/Berlin')
            await self.game_map[message.channel.id].time_scheduler();
        if message.content == 'new_york':
            print("start debug york...")
            self.game_map[message.channel.id] = Game(self, None, message.channel.id, None, 'America/New_York')
            await self.game_map[message.channel.id].commence_day();

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
            for role in Role:
                if role.value == 000:
                    tmessage += "\nTown alligned roles:```"
                elif role.value == 100:
                    tmessage += "```Evil alligned roles: ```"
                elif role.value == 200:
                    tmessage += "```Neutral alligned roles: ```"
                tmessage += ("\n - " + role.name)
            await message.channel.send(tmessage + "```")

        elif (message.content[:6] == "$info "):
            print("AM HERE")
            role = Role.get_role(message.content[6:])
            if role is None:
                await message.channel.send('Invalid role. Use `$list` to see all roles')
                return
            with open('game/descriptions.json') as configfile:
                print("am here")
                data = json.load(configfile)
                if message.content[6:] not in data:
                    await message.channel.send('No role description available :(')
                    return
                stats = data[message.content[6:]]
                embed = discord.Embed(color = 52224 if role.value < 100 else 7829367 if role.value >= 200 else 16711680,title = stats['name'], type = 'rich', description = "Role card")
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
        self.state_map.pop(id)


if not utils.checkJson():
    print("Multiple errors have occured. Bot has not been started")
    quit()

client = MyClient(activity = discord.Activity(name = 'Write $setup to start a game' , type = discord.ActivityType.custom))

with open('config.json') as configfile:
    data = json.load(configfile)

try:
    client.run(data['token'])
except discord.errors.LoginFailure as exception:
    if str(exception) == 'Improper token has been passed.':
        print('Error: an improper token has been passed. Make sure that you added the correct token to config.json')
    else:
        print(exception)
