from typing import Dict

import discord

from data import datamanager
from game import game
from game import presets
from game import roles
from game import scheduler
from usable import time_difference
from usable import utils


class WerewolfBot(discord.Client):
    in_game_map: Dict[int, set]
    time_map: Dict[int, time_difference.Time]
    player_map: Dict[int, list]
    sched_map: Dict[int, scheduler.Scheduler]
    game_map: Dict[int, game.Game]
    count_map: Dict[int, int]
    role_list: Dict[int, list]
    react_map: Dict[int, discord.Message]
    state_map: Dict[int, int]
    group_map: Dict[int, list]
    group_game: Dict[int, game.Game]
    category_id: int

    async def on_ready(self):

        self.in_game_map = {}  # Map player_id to their game_ids
        self.time_map = {}  # Map channel to time object
        self.player_map = {}  # Map channel to player list
        self.sched_map = {}  # Map channel to scheduler (PROBABLY NOT NEEDED AFTER DEBUG)
        self.game_map = {}  # Map channel to game
        self.count_map = {}  # Map channel to count
        self.role_list = {}  # Map channel to role list
        self.react_map = {}  # Map channel to react message
        self.state_map = {}  # Map channel to state
        self.group_map = {}  # Map channel to list of group
        self.group_game = {}  # Map channel_id (group) to game
        self.category_id = 0  # Category channel id to spawn groups in

        if len(list(filter(lambda x: x.name == "WEREWOLF GAMES",
                           self.get_guild(datamanager.get_config('covert_server')).categories))) == 0:
            werewolf_channel = await self.get_guild(datamanager.get_config('covert_server')).create_category_channel(
                'WEREWOLF GAMES')
            self.category_id = werewolf_channel.id
        else:
            self.category_id = next(x for x in self.get_guild(datamanager.get_config('covert_server')).categories if
                                    x.name == "WEREWOLF GAMES").id

        # TODO: Move this to database or something (also move same code in group.py)
        for text_channel in self.get_channel(self.category_id).text_channels:
            await text_channel.delete()

        print('Logged on as', self.user)
        await client.change_presence(activity=discord.Game(name='Write $setup to start a game'))

    async def on_message(self, message: discord.Message):
        # Don't react to bots and only react to commands containing $ or .
        if message.author.bot or ('$' not in message.content and '.' not in message.content):
            return

        # User uses information calls, possible in every chat
        if await self.information_calls(message):
            return

        # Group message
        if message.channel.type == discord.ChannelType.text and message.channel.category_id == self.category_id:
            # TODO: Route to guild
            await self.group_game[message.channel.id].player_objs[message.author.id].role.on_group_message(
                self.group_game[message.channel.id], message.channel, message.content.split('$')[1])
            return

        # User starts game setup
        if message.channel.type == discord.ChannelType.text and (
                message.channel.id not in self.state_map or self.state_map[message.channel.id] < 2):
            await self.setup(message)

        # User uses $setup incorrectly
        elif message.channel.type == discord.ChannelType.text and message.content in ["$s",
                                                                                      "$setup"]:  # Send a message only on $setup to avoid confusion
            await message.channel.send('Game is already running. There can only be one game per text channel.')
            return

        elif message.channel.type == discord.ChannelType.text:  # Send a message only on $setup to avoid confusion
            await self.global_calls(message)

        # else: Route Message to role (io -> game -> player -> role -> on_message)
        if message.channel.type == discord.ChannelType.private:
            await self.parse_player_message(message)

        # Debug
        await self.debug_commands(message)

    # Handles Game setup such as "setup, continue, reset, listpresets, addrole, delrole, current, done"
    async def setup(self, message):
        # GAME SETUP

        # User writes $setup, game to be started
        if message.channel.id not in self.state_map:
            if message.content in ["$s", "$setup"]:
                # TODO SETUP
                print("Debug: Setup initialized")
                self.state_map[message.channel.id] = 0
                self.react_map[message.channel.id] = await message.channel.send(
                    'Setting up game. To reset, write `$reset`. If you want to participate, react with :wolf: under '
                    'this message. After all players have reacted, write `$continue`')
                await self.react_map[message.channel.id].add_reaction('🐺')

        # User writes continue after reacting
        elif self.state_map[message.channel.id] == 0 and message.content in ('$c', '$continue'):
            print("Debug: Continue has been called")
            self.state_map[message.channel.id] = 1
            message = await message.channel.fetch_message(self.react_map[message.channel.id].id)
            count = list(filter(lambda x: x.emoji == '🐺', message.reactions))[0].count - 1
            if count < 0:  # TODO:  Enable this filter again (set on 4)
                await message.channel.send("Not enough players. There should be at least 4")
                self.state_map.pop(message.channel.id)
                return
            self.count_map[message.channel.id] = count
            self.player_map[message.channel.id] = list(map(lambda x: x.id, await
            list(filter(lambda x: x.emoji == '🐺', message.reactions))[0].users().flatten()))
            self.player_map[message.channel.id].remove(self.user.id)

            print("Debug: The following players are participating:", self.player_map[message.channel.id])  # DEBUG
            await message.channel.send(str(
                count) + " players have entered.\n" + 'Add roles to the role list by typing `$addrole ROLE`. For '
                                                      'example `$addrole ORACLE`. There should be at least one role '
                                                      'more than there are players. To see all roles type '
                                                      '`$rolelist`. To remove a role type `$delrole ROLE`. To look at '
                                                      'your current role list, type `$current`. \nTo choose a preset '
                                                      'type `$preset PRESET` and to view all presets use '
                                                      '`$presetlist`.\nType `$done` when you are finished or `$reset` '
                                                      'to start over\nEnter your timezone using `$timezone TIMEZONE` '
                                                      '(default is UTC). Common timezones may be UTC, CET, '
                                                      'Europe/Berlin, America/New_York, Asia/Dubai. For a list of all '
                                                      'accepted timezones visit '
                                                      'https://en.wikipedia.org/wiki/List_of_tz_database_time_zones '
                                                      'and search the third column.')

        # Set a preset
        elif self.state_map[message.channel.id] == 1 and message.content.split(' ')[0] in ('$p', '$preset'):
            self.role_list[message.channel.id] = presets.get_preset(message.content.split(' ')[1],
                                                                    self.count_map[message.channel.id] + 1)
            await message.channel.send("Set preset to " + message.content.split(' ')[1])

        # Get all presets
        elif self.state_map[message.channel.id] == 1 and message.content in ['$pl', '$presetlist']:
            presets_message = 'There are the following presets: ```'
            for preset in presets.Preset:
                presets_message += "\n - " + preset.name
            await message.channel.send(
                presets_message + "``` Use `$presetinfo PRESET` to get a list of roles for the given preset")

        # Get a certain preset
        elif self.state_map[message.channel.id] == 1 and message.content.split(' ')[0] in ['$pi', '$presetinfo']:
            presets_message = 'Preset ' + message.content.split(' ')[1] + ' contains: ```'
            for role in presets.Preset.get_preset(message.content.split(' ')[1],
                                                  self.count_map[message.channel.id] + 1):
                presets_message += "\n - " + role.__name__
            await message.channel.send(presets_message + "```")

        # User writes $reset before completing setup
        elif self.state_map[message.channel.id] <= 1 and message.content in ['$r', '$reset']:
            self.state_map.pop(message.channel.id)
            await message.channel.send("Game has been cancelled. Type $setup to start a new game.")

        # User adds a role using '$addrole ...'
        elif self.state_map[message.channel.id] == 1 and message.content.split(' ')[0] in ['$ar', '$addrole']:
            role = next(obj for obj in roles.all_roles if obj.__name__.lower() == message.content.split(' ')[1].lower())
            # role = Roles.get_role(message.content[9:])
            if role is None:
                await message.channel.send('Invalid role. Use `$list` to see all roles')
                return

            if message.channel.id not in self.role_list:
                self.role_list[message.channel.id] = []
            self.role_list[message.channel.id].append(role)
            await message.channel.send('Added ' + message.content.split(' ')[1].title() + ' to role list')

        # User removes a role using '$delrole ...'
        elif self.state_map[message.channel.id] == 1 and message.content.split(' ')[0] in ['$dr', '$delrole ']:
            role = next(obj for obj in roles.all_roles if obj.__name__.lower() == message.content.split(' ')[1].lower())
            # role = Roles.get_role(message.content[9:])
            if role is None:
                await message.channel.send('Invalid role. Use `$current` to see the role list')
                return

            if message.channel.id not in self.role_list:
                self.role_list[message.channel.id] = []
            if role not in self.role_list[message.channel.id]:
                await message.channel.send(message.content.split(' ')[1].title() + ' not in role list')
                return
            self.role_list[message.channel.id].remove(role)
            await message.channel.send('Removed ' + message.content.split(' ')[1].title() + ' from role list')

        # User removes a role using '$current'
        elif self.state_map[message.channel.id] == 1 and message.content in ['$cr', '$current']:
            if message.channel.id not in self.role_list or len(self.role_list[message.channel.id]) == 0:
                await message.channel.send('Role list is empty.')
                return
            await message.channel.send('The following roles are in the role list:' + utils.format_role_list(
                self.role_list[message.channel.id]))

        # User sets timezone using 'timezone ...'
        elif self.state_map[message.channel.id] == 1 and message.content.split(' ')[0] in ['$tz', '$timezone ']:
            print("Debug: Entered Timezone", message.content.split(' ')[1])
            import pytz
            try:
                self.time_map[message.channel.id] = time_difference.Time(message.content.split(' ')[1])
                await message.channel.send(
                    "Entered timezone " + message.content.split(' ')[1] + ".")
            except pytz.exceptions.UnknownTimeZoneError:
                await message.channel.send(
                    "Invalid timezone. Visit https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for a list of all valid timezones (Enter the TZ database name).")
        # User writes $done before adding enough roles
        elif self.state_map[message.channel.id] == 1 and message.content in ['$d', '$done'] and (
                message.channel.id not in self.role_list or len(self.role_list[message.channel.id]) <= self.count_map[
            message.channel.id]):
            await message.channel.send('There are not enough roles. There should be at least ' + str(
                self.count_map[message.channel.id] + 1) + ' roles.')

        # User writes $done after adding enough roles
        elif self.state_map[message.channel.id] == 1 and message.content in ['$d', '$done'] and len(
                self.role_list[message.channel.id]) > self.count_map[message.channel.id]:
            if roles.good_roles & set(self.role_list[message.channel.id]) == set():
                await message.channel.send('There should be at least one town aligned role')
                return
            if roles.evil_roles & set(self.role_list[message.channel.id]) == set():
                await message.channel.send('There should be at least one evil aligned role')
                return

            for player_id in self.player_map[message.channel.id]:
                if player_id not in self.in_game_map:
                    self.in_game_map[player_id] = set()
                self.in_game_map[player_id].add(message.channel.id)

            await message.channel.send(
                'The following roles will be distributed:' + utils.format_role_list(self.role_list[message.channel.id]))
            # with open('config.json') as configfile:
            #    data = json.load(configfile)
            await message.channel.send('Please join https://discord.gg/' + datamanager.get_config(
                'invite_link') + ' for private communications\nGame with ID ' + str(
                message.channel.id) + ' will start at INSERT TIME on INSERT DATE')

            if message.channel.id not in self.time_map:
                self.time_map[message.channel.id] = time_difference.Time('UTC')

            self.game_map[message.channel.id] = game.Game(self, self.player_map[message.channel.id], message.channel.id,
                                                          self.role_list[message.channel.id],
                                                          self.time_map[message.channel.id])

            self.sched_map[message.channel.id] = scheduler.Scheduler(self, self.time_map[message.channel.id],
                                                                     self.game_map[message.channel.id])

            self.state_map[message.channel.id] = 2

            await self.sched_map[message.channel.id].initialize()

            await message.channel.send('Thank you for playing :)')
            for player_id in self.game_map[message.channel.id].players_list:
                self.in_game_map[player_id].remove(message.channel.id)

            for group in self.game_map[message.channel.id].groups:
                group.delete_channel()

            self.role_list.pop(message.channel.id)

            await self.game_broadcast(message.channel.id, "The game has ended. Use `$setup` to start another game")
            self.state_map.pop(message.channel.id)

        # TODO INITIALIZE GAME HERE
        # TODO: ENTER TIME ZONE
        # self.game_map[message.channel.id] = game.Game(self, self.player_map[message.channel.id], message.channel.id, self.role_list[message.channel.id], 'Europe/Berlin')
        # await self.game_map[message.channel.id].time_scheduler();

        # except:
        #    await message.channel.send('Unknown timezone. Enter your timezone using `$timezone TIMEZONE`. Common timezones may be UTC, CET, Europe/Berlin, America/New_York, Asia/Dubai. For a list of all accepted timezones visit https://en.wikipedia.org/wiki/List_of_tz_database_time_zones and search the third column.')

    # Debug stuff
    async def debug_commands(self, message):

        if message.content in ('.next', '.n'):
            print("Debug: Skip to next event")
            self.sched_map[message.channel.id].debug = 1

    # Get information about roles or presets
    async def information_calls(self, message):
        # User writes $list and gets a display of all roles
        if message.content in ('$rl', '$rolelist'):
            print("Debug: List all roles")
            role_list_message_content = 'The following roles exist'
            role_list_message_content += "\n\nTown aligned roles:```"
            role_list_message_content += "\n - ".join(map(lambda x: x.__name__, roles.good_roles))
            role_list_message_content += "```\nEvil aligned roles: ```"
            role_list_message_content += "\n - ".join(map(lambda x: x.__name__, roles.evil_roles))
            role_list_message_content += "```\nNeutral aligned roles: ```"
            role_list_message_content += "\n - ".join(map(lambda x: x.__name__, roles.neutral_roles))

            await message.channel.send(role_list_message_content + "```")
            return True

        if message.content.split(' ')[0] in ('$i', '$info'):
            print("Debug: Get info on", message.content.split(' ')[1].title())
            if message.content.split(' ')[1].lower() not in set(map(lambda x: x.__name__.lower(), roles.all_roles)) and \
                    message.content.split(' ')[1].lower() != 'narrator':
                await message.channel.send('Invalid role. Use `$rolelist` to see all roles')
                return True

            data = datamanager.get_description()
            if message.content.split(' ')[1].upper() not in data:
                await message.channel.send('No role description available :(')
                return True
            stats = data[message.content.split(' ')[1].upper()]
            if message.content.split(' ')[1].lower() == 'narrator':
                color = 10066176
            elif message.content.split(' ')[1].lower() in set(map(lambda x: x.__name__.lower(), roles.good_roles)):
                color = 52224
            elif message.content.split(' ')[1].lower() in set(map(lambda x: x.__name__.lower(), roles.evil_roles)):
                color = 16711680
            else:
                color = 7829367

            embed = discord.Embed(color=color, title=stats['name'], type='rich', description="Role card")
            embed.add_field(name="Description", value=stats['description'], inline=False)
            embed.add_field(name="Abilities", value=stats['abilities'], inline=True)
            embed.add_field(name='Alignment', value=stats['alignment'], inline=True)
            embed.add_field(name='Usage', value=stats['usage'], inline=False)
            await message.channel.send("", embed=embed)
            return True

        if message.content in ('$g', '$games'):
            print("Debug: Get games", message.content.split(' ')[1].title())
            if message.author.id not in self.in_game_map or len(self.in_game_map[message.author.id]) == 0:
                await message.channel.send("You don't have any games.")
            else:
                await message.channel.send('Your games are (ID | Server | Channel): \n - ' + "\n - ".join(
                    map(lambda x: str(x) + " (" + self.get_channel(x).guild.name + "/" + self.get_channel(x).name + ")",
                        self.in_game_map[message.author.id])))
            return True

        if message.content in ('$h', '$help'):
            await message.channel.send("Here is a list of all commands\n"
                                       "- $help, $h | Shows this message\n"
                                       "- $setup, $s | Starts a game\n"
                                       "- $continue, $c | Finalize Player signup\n"
                                       "- $presetlist, $pl | Show all presets\n"
                                       "- $preset PRESET, $p PRESET | Choose PRESET as current preset\n"
                                       "- $rolelist, $rl | Show all roles\n"
                                       "- $addrole ROLE, $ar ROLE | Add a role to the rolelist\n"
                                       "- $delrole ROLE, $dr ROLE | Remove a role from the rolelist\n"
                                       "- $current, $cr | List all roles currently in the rolelist\n"
                                       "- $info ROLE, $i ROLE | Show a roles rolecard\n"
                                       "- $done, $d | finalize rolelist\n"
                                       "- $timezone TIME, $tz TIME | sets the current timezone. View https://en.wikipedia.org/wiki/List_of_tz_database_time_zones for all timezones\n"
                                       "- $presetinfo, $pi | Show the roles a preset contains\n"
                                       "- $games, $g | Show the games you are part of\n"
                                       "- $player, $p | Show currently alive players\n")

        return False

    # Global game calls
    async def global_calls(self, message):
        if message.content == "$players":
            await message.channel.send(self.game_map[message.channel.id].get_player_list())

    # Parse direct messages
    async def parse_player_message(self, message):
        print("Debug: Start parsing private message")
        if message.channel.type != discord.ChannelType.private or '$' not in message.content or message.author.id not in self.in_game_map:
            return

        print("Debug: Message parsed")
        if message.content.startswith('$') and len(self.in_game_map[message.author.id]) > 1:
            await message.channel.send(
                "You are in multiple games. Please specify the game you are referring to by prepending it to your "
                "command. \nIf your game ID were 123456789 for example, you might write `123456789$info Villager` "
                "instead of `$info Villager`. You may use only a first part of your game ID as long as it's unique. "
                "If you had two games with the IDs 123456789 and 124567899, you might write `123$info Villager` but "
                "not `12$info Villager`. \nTo view a list of your games use `$games`. ")
            return

        games = list(
            filter(lambda x: str(x).startswith(message.content.split('$')[0]), self.in_game_map[message.author.id]))
        if len(games) > 1:
            await message.channel.send(
                "You are in multiple games. Please specify the game you are referring to by prepending it to your "
                "command. \nIf your game ID were 123456789 for example, you might write `123456789$info Villager` "
                "instead of `$info Villager`. You may use only a first part of your game ID as long as it's unique. "
                "If you had two games with the IDs 123456789 and 124567899, you might write `123$info Villager` but "
                "not `12$info Villager`. \nTo view a list of your games use `$games`. ")
            return

        if len(games) < 1:
            await message.channel.send(
                "Either none of your games match your ID or they have not yet started. Please specify the game you "
                "are referring to by prepending it to your command. \nIf your game ID were 123456789 for example, "
                "you might write `123456789$info Villager` instead of `$info Villager`. You may use only a first part "
                "of your game ID as long as it's unique. If you had two games with the IDs 123456789 and 124567899, "
                "you might write `123$info Villager` but not `12$info Villager`. \nTo view a list of your games use "
                "`$games`. ")
            return

        if message.author.id not in self.game_map[games[0]].player_objs:
            await message.channel.send("This game has not yet started.")
            return

        print("Debug: Relay private message")
        print("Debug: In Games:", games)
        print("Debug: Game has players:", self.game_map[games[0]].player_objs.keys())
        await self.game_map[games[0]].player_objs[message.author.id].role.on_private_message(self.game_map[games[0]],
                                                                                             message.channel,
                                                                                             message.content.split('$')[
                                                                                                 1])

    # Send a message to a game channel
    async def game_broadcast(self, game_id, message):
        await self.get_channel(game_id).send(message)

    # Send a message to a user
    async def game_direct(self, user_id, message):
        if self.get_user(user_id).dm_channel is None:
            await self.get_user(user_id).create_dm()
        await self.get_user(user_id).dm_channel.send(message)


if not datamanager.check_json():
    print("Error: Multiple errors have occurred. Bot has not been started")
    quit()

client = WerewolfBot(activity=discord.Activity(name='Write $setup to start a game', type=discord.ActivityType.custom))

try:
    client.run(datamanager.get_config('token'))
except discord.errors.LoginFailure as exception:
    if str(exception) == 'Improper token has been passed.':
        print('Error: an improper token has been passed. Make sure that you added the correct token to config.json')
    else:
        print(exception)
