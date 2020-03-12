import asyncio

from game.flags import Flags


class Role:

    def __init__(self, player):
        self.player = player  # Reference to this player
        self.flags = set()  # Set of this roles flags
        self.lovers = set()  # Set of this roles lovers

        self.vote_for = None  # Player INDEX to vote for

    async def on_message(self, game, message):
        print(self.player.name, ": ", message)

        if message == 'players':
            print("Debug: List Players")
            await game.interface.game_direct(self.player.id,
                                             "The following players are still in the game:\n" + game.get_player_list())

        if message.startswith('vote ') and Flags.VOTE_READY in self.flags:
            try:
                self.vote_for = int(message.split(' ')[1])
                await game.interface.game_direct(self.player.id,
                                                 "You have voted for " + game.get_player_obj_at(self.vote_for).name)
            except ValueError:
                await game.interface.game_direct(self.player.id,
                                                 "Incorrect command. Use `$vote NUMBER` to vote for a player. To vote for Player 2 use `$vote 2` for example")

    async def on_game_start(self, game):
        pass

    async def on_nightfall(self, game):
        pass

    async def on_postnight(self, game):
        pass

    async def on_sunrise(self, game):
        pass

    async def on_votestart(self, game):
        self.flags.add(Flags.VOTE_READY)

    async def on_voteend(self, game):
        self.flags.remove(Flags.VOTE_READY)
        if self.vote_for is not None:
            game.add_vote(game.get_player_id_at(self.vote_for), 1)
            self.vote_for = None

    async def on_defense(self, game, tied_players):
        if self.player in tied_players:
            await game.interface.game_direct(self.player.id,
                                             "You are on trial. You may defend yourself to escape death.")

    async def on_deathrow(self, game, player):
        # TODO: you are on trial
        if self.player == player:
            # await game.interface.game_broadcast(game.id, player.name + " is on death row.")
            pass
        # TODO: DO DEATH

    async def on_hang(self, game, player):
        # TODO: you have been hanged
        if self.player == player:
            if Flags.GRACED in self.flags:
                await game.interface.game_broadcast(game.id, self.player.name + " has been graced.")
            else:
                await game.interface.game_broadcast(game.id,
                                                    self.player.name + " has been hanged. They have been a " + self.player.role.__class__.__name__.title())
                self.player.alive = False
                await game.player_die(self.player, None)
            pass

    async def on_playerdeath(self, game, player, murderer):
        # game.players_alive.remove(player)
        if player in self.lovers:
            await game.interface.game_broadcast(game.id,
                                                self.player.name + " died because of their love to " + player.name)

            await game.player_die(self.player, None)

    async def on_resurrect(self, game):
        pass
        # TODO:

    async def on_changerole(self, game, role):
        self.player.role = role(self.player)
        await game.interface.game_direct(self.player.id,
                                         "Your role has been changed to " + self.player.role.__class__.__name__.title())

    async def on_inhibit(self, game):
        self.add(Flags.INHIBITED)

    async def on_inlove(self, game, player):
        self.lovers.add(player)

    async def on_attacked(self, game, attacker):
        await game.interface.game_broadcast(game.id,
                                            self.player.name + " has died because of an attack by a " + attacker.__class__.__name__.title())

    async def on_guard(self, game):
        # TODO: you have been guarded
        self.flags.add(Flags.GUARDED)

    async def on_grace(self, game):
        # TODO: you have been graced
        self.flags.add(Flags.GRACED)

    async def do_vote_action(self, game, message, flag=Flags.VOTE_READY):
        if message.startswith('vote ') and flag in self.flags:
            try:
                value = int(message.split(' ')[1])
                if not game.get_player_obj_at(value).alive:
                    await game.interface.game_direct(self.player.id,
                                                     "Chosen player is not alive. Please choose a player who is still in the game.")
                    return
                self.vote_for = value
            except ValueError:
                await game.interface.game_direct(self.player.id,
                                                 "Incorrect command. Use `$vote NUMBER` to vote for a player. To vote for Player 2 use `$vote 2` for example")
            except IndexError:
                await game.interface.game_direct(self.player.id, "Incorrect player index")

    # def do_choose(self, game, message, flag )
