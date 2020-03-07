import json

import discord
from group import Group


class MyClient(discord.Client):
    async def on_ready(self):
        print('Logged on as', self.user)
        await client.change_presence(activity=discord.Game(name='Werewolf'))

    async def on_message(self, message):
        # don't respond to ourselves
        if message.author == self.user:
            return

        if message.content == 'create':
            print("Create")
            self.c = Group(self, 'test_hi1')
            await self.c.create()

        if message.content == 'ref':
            print("refresh")
            await self.c.refresh()

        if message.content == 'add':
            print("add")
            self.c.add_user(298488132255350784)

        if message.content == 'remove':
            print("remove")
            self.c.remove_user(298488132255350784)

        if message.content == 'del':
            print("deleting")
            await self.c.delete_channel()


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
