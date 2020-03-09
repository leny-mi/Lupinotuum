


# Lupinotuum
A Bot to play Werewolf on Discord in real-time.

## Usage

To host this bot yourself clone this repository. You'll have to create a `config.json` in `Lupinotuum/` and enter your bot token and a covert_server. Then just run `lupinotuum.py`.

The covert_server should be a server where private communication is managed using text_channels. Here the bot need permissions to create and modify channels.

The invite link should be the last part of a generated invite link to your covert server. In the given case the link [https://discord.gg/PzYPTdr](https://discord.gg/PzYPTdr "https://discord.gg/PzYPTdr") has been generated which leads to `PzYPTdr` as the last part.

Your `config.json` might look like this

    {
      "token": "Dwa9aFW9saf68gwaf-faw80saf789fwa.fawXAawdfajigeoAIWZUk",
      "covert_server": 4201333712345678910
      "invite_link" : "PzYPTdr"
    }

## Task List

- [ ] Interface
	 - [x] Game Setup
	 - [ ] Ingame interaction
- [ ] Game logic
	 - [ ] Main game
	 - [ ] Usability
		 - [x] Group management
		 - [ ] Time management
- [ ] Database
	- [ ] Game state
		- [ ] Save game state
		- [ ] Recall game state
	- [ ] Game setup



## Roles
#### Town aligned roles

|Role                           |Ability                      |Special win condition
|-------------------------------|-----------------------------|---------|
|Villager|-|-|
|Seer|View a players alignment each night|-|
|Guardian Angel|Guard a player each night. Player cannot die|-|
|Alchemist|Save a player once each game. Kill a player once each game|-|
|Hunter|After death may kill a player|-|
|Cupid|Chooses two players at the start to have altered win conditions|Also wins with the couple|
|Mayor|Vote is worth twice as much|-|
|Apprentice Seer|Becomes a Seer when the Seer dies|-|
|Knight|Survives the first attack on him|-|
|Vigilante|May kill two players per game|-|
|Bomb|Kills their killer|-|
|Resurrectionist|May resurrect one player per game|-|
|Mailman|May write a Message each night to be shown to the Town|-|
|Oracle|May reveal a players role to another player but not themselves|-|
|Priest|Can throw Holy Water at another player. If target is a werewolf the target dies; otherwise the priest dies|-|
|Brothers|Knows the other Brothers|-|
|Mason|Knows the other Masons|-|
||||

#### Evil Roles
|Role                           |Ability                      |Special win condition
|-------------------------------|-----------------------------|---------|
|Mafiosi|Vote to kill a player at night|-|
|Werewolf|Vote to kill a player at night|-|
|Alpha|Vote to kill a player at night|Only wins if no other werewolf survives|
|Teenage Werewolf|Must say 'werewolf' once each day|-|
|Vampire|May bite a player every even night|Only Vampires left|
|Serial Killer|May kill a player every night|Has to be last survivor|
|Cultist|Is not part of werewolf chat|-|
|Ancient Werewolf|Once may convert someone to a werewolf instead of killing them|-|
|Witch|May inhibit a night activity each night|-|

#### Neutral Roles
|Role                           |Ability                      |Special win condition
|-------------------------------|-----------------------------|---------|
|Survivor|-|Wins if alive at the end|
|Executioner|-|Wins if target is killed by the end of the game|
|Guardian|-|Wins if target is alive by the end of the game|
|Jester|-|Wins if he is lynched|
|Universal|May choose a role on the first night|-|
|Copycat|Gets the role of the first player to die|-|
