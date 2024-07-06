# Eventipy

Eventipy is an event-driven library for Python that supports event emission, remote target handling, and listener registration with a simple and intuitive API.

The main purpose be an effective way to trigger hooks based on events and allow communication to another systems based on most common protocols.

## Documentation

Read more about the usage with our [Documentation](https://linktodocumentation) / [Examples](https://linktodocumentation)

## Installation

To install Eventipy, clone this repository and run:

```bash
pip install eventipy
```

## Usage/Examples

```python
from enum import Enum
from eventipy import Eventipy

# Defining all events on a enum (not required but it's a good pratice)
class GameEvents(Enum):
    ON_PLAYER_JOIN = "ON_PLAYER_JOIN"
    ON_PLAYER_ATTACK = "ON_PLAYER_ATTACK"
    ON_MONSTER_DEFEATED = "ON_MONSTER_DEFEATED"
    ON_GAME_OVER = "ON_GAME_OVER"

# Instancing Eventypy class defining a webhook as remote_target for "ON_MONSTER_DEFEATED" event
handler = Eventipy(remote_targets=[
    {
        "type": "url",
        "address": "https://mysite.site/api/game/hooks",
        "headers": {"X-Game-Event":"RPGSecretKey"},
        "events": [GameEvents.ON_MONSTER_DEFEATED]
    }
])

# Defining hooks that will be executed locally
@game_event_handler.on(GameEvents.ON_PLAYER_JOIN)
def handle_player_join(player_name):
    print(f"{player_name} has joined the game!")

@game_event_handler.on(GameEvents.ON_PLAYER_ATTACK)
def handle_player_attack(player_name, monster_name, damage):
    print(f"{player_name} attacked {monster_name} for {damage} damage!")

@game_event_handler.on(GameEvents.ON_MONSTER_DEFEATED)
def handle_monster_defeated(player_name, monster_name):
    print(f"{player_name} has defeated {monster_name}!")

@game_event_handler.on(GameEvents.ON_GAME_OVER)
def handle_game_over():
    print("Game Over! Thanks for playing.")

# Emitting player join event
game_event_handler.emit(GameEvents.ON_PLAYER_JOIN, "Archer")

# Emitting player attack event
game_event_handler.emit(GameEvents.ON_PLAYER_ATTACK, "Archer", "Goblin", 30)

# Emitting monster defeated event
game_event_handler.emit(GameEvents.ON_MONSTER_DEFEATED, "Archer", "Goblin")

# Emitting game over event
game_event_handler.emit(GameEvents.ON_GAME_OVER)
```

## Roadmap

-   Implement integration for celery backend (RabbitMQ, Redis)
-   Implement Direct RabbitMQ
-   Allow Emit Async and Sync options

## License

[MIT](https://choosealicense.com/licenses/mit/)
