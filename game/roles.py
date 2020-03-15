from game import role
from game.flags import Flags
from game import player


# Good Roles

class Good(role.Role):
    alive_alignment = "Village"
    pass


class Hunter(Good):
    pass


class Guardian_Angel(Good):
    guarded: int

    async def on_private_message(self, game, channel, message: str):
        await super(Guardian_Angel, self).on_private_message(game, channel, message)
        if message.split(' ')[0] == 'guard':
            try:

                if game.get_player_obj_at(int(message.split(' ')[1])).is_alive:
                    self.guarded = int(message.split(' ')[1])
                    await channel.send('You chose to guard ' + game.get_player_obj_at(int(message.split(' ')[1])).name)
                else:
                    await channel.send("Chosen player is not alive.")
            except:
                await channel.send("Incorrect command usage. Use `$info Guardian_Angel` to see an explanation.")

    async def on_nightfall(self, game):
        await super(Guardian_Angel, self).on_nightfall(game)
        self.flags.add(Flags.ABILITY_READY)
        await game.interface.game_direct(self.player.player_id, "You can use your ability until " + game.time.get_next_time_string(23, 0) + ".")

    async def on_postnight(self, game):
        await super(Guardian_Angel, self).on_postnight(game)
        self.flags.remove(Flags.ABILITY_READY)
        player_to_guard = game.get_player_obj_at(self.guarded)
        player_to_guard.role.flags.add(Flags.GUARDED)
        player_to_guard.role.guarded_from = self.player


class Villager(Good):
    pass


class Vigilante(Good):
    pass


class Seer(Good):
    see_player: player.Player

    async def on_private_message(self, game, channel, message: str):
        await super(Seer, self).on_private_message(game, channel, message)
        if message.split(' ')[0] == 'see':
            try:
                if game.get_player_obj_at(int(message.split(' ')[1])).is_alive:
                    self.see_player = game.get_player_obj_at(int(message.split(' ')[1]))
                    await channel.send('You chose to look at ' + self.see_player.name + '\'s alignment.')
                else:
                    await channel.send("Chosen player is not alive.")
            except:
                await channel.send("Incorrect command usage. Use `$info Seer` to see an explanation.")

    async def on_nightfall(self, game):
        await super(Seer, self).on_nightfall(game)
        self.flags.add(Flags.ABILITY_READY)
        await game.interface.game_direct(self.player.player_id, "You can use your ability until " + game.time.get_next_time_string(23, 0) + ".")

    async def on_postnight(self, game):
        await super(Seer, self).on_postnight(game)
        self.flags.remove(Flags.ABILITY_READY)

    async def on_sunrise(self, game):
        await super(Seer, self).on_sunrise(game)
        if self.see_player is not None:
            await game.interface.game_direct(self.player.player_id, self.see_player.name + '\'s alignment is ' + str(
                self.see_player.role.alive_alignment))


class Resurrectionist(Good):
    pass


class Priest(Good):
    pass


class Oracle(Good):
    pass


class Mayor(Good):
    pass


class Mason(Good):
    pass


class Mailman(Good):
    pass


class Knight(Good):
    pass


class Cupid(Good):
    pass


class Brother(Good):
    pass


class Bombshell(Good):
    pass


class Apprentice_Seer(Good):
    pass


class Alchemist(Good):
    pass


class Fox(Good):
    pass


class Teacher(Good):
    pass


class Lord(Good):
    pass


# Evil Roles

class Evil(role.Role):
    pass


class Alpha(Evil):
    pass


class Ancient(Evil):
    pass


class Cultist(Evil):
    pass


class Mafiosi(Evil):
    pass


class Serial_Killer(Evil):
    pass


class Teenage_Werewolf(Evil):
    pass


class Vampire(Evil):
    pass


class Werewolf(Evil):
    alive_alignment = "Werewolf"

    async def on_group_message(self, game, channel, message):
        await super(Werewolf, self).on_group_message(game, channel, message)
        print("Debug: Got group message", message)
        await self.do_vote_action(game, channel, message, flag=Flags.ABILITY_READY)

    async def on_game_start(self, game):
        await super(Werewolf, self).on_game_start(game)
        if self.__class__.__name__ not in game.groups:
            game.groups[self.__class__.__name__] = await game.create_group(self.__class__.__name__, self)
            self.group_master.append(game.groups[self.__class__.__name__])
        game.groups[self.__class__.__name__].add_user(self.player.player_id)

    async def on_nightfall(self, game):
        await super(Werewolf, self).on_nightfall(game)
        self.flags.add(Flags.ABILITY_READY)
        if self == game.groups[self.__class__.__name__].master:
            game.groups[self.__class__.__name__].votes = {}
            await game.groups[self.__class__.__name__].channel.send(
                "The night has started. You may vote on a target using "
                "`$vote PLAYER`. Use `$players` to get a list of all "
                "living players. Vote by " +
                game.time.get_next_time_string(23, 0))

    async def on_postnight(self, game):
        await super(Werewolf, self).on_postnight(game)
        self.flags.remove(Flags.ABILITY_READY)
        if self.vote_for is not None:
            if self.vote_for not in game.groups[self.__class__.__name__].votes:
                game.groups[self.__class__.__name__].votes[game.get_player_obj_at(self.vote_for)] = 0
            game.groups[self.__class__.__name__].votes[game.get_player_obj_at(self.vote_for)] += 1
            self.vote_for = None

    async def on_sunrise(self, game):
        await super(Werewolf, self).on_sunrise(game)
        if self == game.groups[self.__class__.__name__].master:
            max_votes = max(game.groups[self.__class__.__name__].votes.values()) if len(
                game.groups[self.__class__.__name__].votes.values()) > 0 else 0
            print("Debug: max_votes =", max_votes)
            most_voted = list(
                filter(lambda x: game.groups[self.__class__.__name__].votes.get(x, 0) == max_votes,
                       game.sort_players(only_alive=True)))
            print("Debug: most_voted =", most_voted)
            # game.get_player_obj_at()
            if len(most_voted) > 1:
                await game.groups[self.__class__.__name__].channel.send("No majority reached.")
            else:
                await most_voted[0].role.on_attacked(game, self)


class Witch(Evil):
    pass


class White(Evil):
    pass


# Neutral Roles

class Neutral(role.Role):
    pass


class Universal(Neutral):
    pass


class Survivor(Neutral):
    pass


class Protector(Neutral):
    pass


class Jester(Neutral):
    pass


class Executioner(Neutral):
    pass


class Copycat(Neutral):
    pass


class Actor(Neutral):
    pass


good_roles = {Villager, Seer, Guardian_Angel, Alchemist, Hunter, Cupid, Mayor, Apprentice_Seer, Knight, Vigilante,
              Bombshell, Resurrectionist, Mailman, Oracle, Priest, Brother, Mason, Fox, Teacher, Lord}
evil_roles = {Mafiosi, Werewolf, Alpha, Teenage_Werewolf, Vampire, Serial_Killer, Cultist, Ancient, Witch, White}
neutral_roles = {Survivor, Executioner, Protector, Jester, Universal, Copycat, Actor}

all_roles = good_roles.union(evil_roles).union(neutral_roles)
role_order = [Witch, Villager, Seer, Guardian_Angel, Alchemist, Hunter, Cupid, Mayor, Apprentice_Seer, Knight,
              Vigilante, Bombshell, Resurrectionist, Mailman, Oracle, Priest, Brother, Mason, Fox, Teacher, Lord,
              Mafiosi, Werewolf, Alpha, Teenage_Werewolf, Vampire, Serial_Killer, Cultist, Ancient, White, Survivor,
              Executioner, Protector, Jester, Universal, Copycat, Actor]
