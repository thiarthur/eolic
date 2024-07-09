"""Module that contains example of usage of Eolic class - Game Events."""

from enum import Enum
from eolic import Eolic


# Defining all events on a enum (not required but it's a good pratice)
class GameEvents(Enum):
    """Enum for events that can be emitted in the game."""

    ON_PLAYER_JOIN = "ON_PLAYER_JOIN"
    ON_PLAYER_ATTACK = "ON_PLAYER_ATTACK"
    ON_MONSTER_DEFEATED = "ON_MONSTER_DEFEATED"
    ON_GAME_OVER = "ON_GAME_OVER"


# Instancing Eventypy class defining a webhook as remote_target
# for "ON_MONSTER_DEFEATED" event
handler = Eolic(
    remote_targets=[
        {
            "type": "url",
            "address": "https://mysite.site/api/game/hooks",
            "headers": {"X-Game-Event": "RPGSecretKey"},
            "events": [GameEvents.ON_MONSTER_DEFEATED],
        }
    ]
)


# Defining hooks that will be executed locally
@handler.on(GameEvents.ON_PLAYER_JOIN)
def handle_player_join(player_name):
    """Handle player join event."""
    print(f"{player_name} has joined the game!")


@handler.on(GameEvents.ON_PLAYER_ATTACK)
def handle_player_attack(player_name, monster_name, damage):
    """Handle on player attack event."""
    print(f"{player_name} attacked {monster_name} for {damage} damage!")


@handler.on(GameEvents.ON_MONSTER_DEFEATED)
def handle_monster_defeated(player_name, monster_name):
    """Handle on monster defeated event."""
    print(f"{player_name} has defeated {monster_name}!")


@handler.on(GameEvents.ON_GAME_OVER)
def handle_game_over():
    """Handle on game over event."""
    print("Game Over! Thanks for playing.")


# Emitting player join event
handler.emit(GameEvents.ON_PLAYER_JOIN, "Archer")

# Emitting player attack event
handler.emit(GameEvents.ON_PLAYER_ATTACK, "Archer", "Goblin", 30)

# Emitting monster defeated event
handler.emit(GameEvents.ON_MONSTER_DEFEATED, "Archer", "Goblin")

# Emitting game over event
handler.emit(GameEvents.ON_GAME_OVER)
