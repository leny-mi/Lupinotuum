import discord

from data import datamanager


class Group:

    def __init__(self, client, master, name='text_channel'):
        self.client = client
        self.members = []
        self.guild = client.get_guild(datamanager.get_config('covert_server'))  # insert guild ID
        self.name = name
        self.channel = None
        self.master = master
        self.votes = {}  # Dict of votes
        self.most_voted = None

    async def instantiate_channel(self, game):
        category = self.client.get_channel(self.client.category_id)
        overwrites = {
            self.guild.default_role: discord.PermissionOverwrite(read_messages=False),
            self.guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        self.channel = await self.guild.create_text_channel(self.name, overwrites=overwrites, category=category)
        self.client.group_game[self.channel.id] = game

    def add_user(self, user_id):
        user = self.client.get_user(user_id)
        self.members.append(user)

    def remove_user(self, user_id):
        user = self.client.get_user(user_id)
        self.members.remove(user)

    async def refresh_members(self):
        for user in self.channel.members:
            #print("Debug: Removed " + user.name + " from secret channel")
            await self.channel.set_permissions(user, overwrite=None)
        for user in self.members:
            #print("Debug: Added " + user.name + " to secret channel")
            await self.channel.set_permissions(user, read_messages=True, send_messages=True)

    async def delete_channel(self):
        await self.channel.delete()

    def get_id(self):
        return self.channel.id

    def add_vote(self, player, count):
        if player not in self.votes:
            self.votes[player] = 0
        self.votes[player] += count
        self.most_voted = list(filter(lambda x: self.votes.get(x, 0) == max(self.votes.values()), self.votes.keys()))
