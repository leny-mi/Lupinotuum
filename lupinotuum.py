import json
import discord
from group import Group
from roles import Role


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        await client.change_presence(activity=discord.Game(name='Werewolf'))
        self.state_map = {} #Map channel to state
        self.react_map = {} #Map channel to react message
        self.role_list = {} #Map channel to role list
        self.count_map = {} #Map channel to count

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        # GAME SETUP

        if not message.channel.id in self.state_map:
            if message.content == "$setup":
                #TODO SETUP
                print("Setting up")
                self.state_map[message.channel.id] = 0
                self.react_map[message.channel.id] = await message.channel.send('Setting up game. If you want to participate, react with :wolf: under this message')
                await self.react_map[message.channel.id].add_reaction('🐺')
                pass

        elif (self.state_map[message.channel.id] == 0 and message.content == '$continue'):
            print("Continue")
            self.state_map[message.channel.id] = 1
            message = await message.channel.fetch_message(self.react_map[message.channel.id].id)
            count = list(filter(lambda x: x.emoji == '🐺', message.reactions))[0].count - 1
            if count < 0: #TODO Enable this filter again (set on 4)
                await message.channel.send("Not enough players. There should be at least 4")
                self.state_map.pop(message.channel.id)
                return
            self.count_map[message.channel.id] = count
            await message.channel.send(str(count) + " players have entered.\n" + 'Add roles to the role list by typing `$role ROLE`. For example `$role ORACLE`. There should be at least one role more than there are players. To see all roles type `$list`. Type `$done` when you are finished or `$reset` to start over')

            #TODO Print character list

        elif (self.state_map[message.channel.id] == 1 and message.content == '$list'):
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

        elif (self.state_map[message.channel.id] == 1 and message.content == '$reset'):
            self.state_map.pop(message.channel.id)
            await message.channel.send("Game has been cancelled. Type $setup to start a new game.")

        elif (self.state_map[message.channel.id] == 1 and message.content[0:6] == '$role '):
            role = Role.getRole(message.content[6:])
            if role is None:
                await message.channel.send('Invalid role. Use `$list` to see all roles')
                return

            if not message.channel.id in self.role_list:
                self.role_list[message.channel.id] = []
            self.role_list[message.channel.id].append(role)
            await message.channel.send('Added '+message.content[6:]+' to role list')

        elif (self.state_map[message.channel.id] == 1 and message.content == '$done' and len(self.role_list[message.channel.id]) > self.count_map[message.channel.id]):

            messaget = await MyClient.printRoles(self.role_list[message.channel.id])
            await message.channel.send('The following roles will be distributed:' + messaget)
            await message.channel.send('Please join https://discord.gg/PzYPTdr for private communications\nGame with ID '+str(message.channel.id)+' will start at INSERT TIME on INSERT DATE')
            self.state_map[message.channel.id] = 2
            #TODO Add list decoder
            #TODO Check list size

        elif (message.content == "$setup"):
            await message.channel.send('Game is already running. There can only be ohne game per text channel.')













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

    async def broadcast(self, game_id, message):
        await self.get_channel(game_id).send(message)

    def end_game(id):
        self.state_map.pop(id)

    async def printRoles(roles):
        return "\n - " + ("\n - ".join(map(lambda x: str(roles.count(x)) + 'x ' + x.name, list(set(roles)))))

client = MyClient()

with open('config.json') as configfile:
    data = json.load(configfile)

try:
    client.run(data['token'])
except discord.errors.LoginFailure as exception:
    if str(exception) == 'Improper token has been passed.':
        print('Improper token has been passed. Did you forget to edit token.txt?')
    else:
        print(exception)
