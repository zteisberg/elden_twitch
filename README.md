# Tutorial: elden_twitch

This project creates an *interactive experience* by connecting Twitch stream events directly to the *Elden Ring game*. It acts as a bridge, listening for actions like channel point redemptions or bit donations on Twitch and translating them into *real-time effects* within the game, such as killing the player, granting temporary buffs, or altering character appearance. It also **silently monitors** persistent game states, like player deaths, and reacts to these changes.


## Visual Overview

```mermaid
flowchart TD
    A0["Twitch Event Listener
"]
    A1["Elden Ring Game API
"]
    A2["Twitch Event Handlers
"]
    A3["Memory Address Discovery
"]
    A4["Game State Monitor
"]
    A0 -- "Dispatches events to" --> A2
    A0 -- "Initiates monitoring" --> A4
    A2 -- "Invokes game actions" --> A1
    A1 -- "Utilizes for discovery" --> A3
    A4 -- "Reads game state" --> A1
```

## Chapters

1. [Twitch Event Handlers
](01_twitch_event_handlers_.md)
2. [Elden Ring Game API
](02_elden_ring_game_api_.md)
3. [Twitch Event Listener
](03_twitch_event_listener_.md)
4. [Game State Monitor
](04_game_state_monitor_.md)
5. [Memory Address Discovery
](05_memory_address_discovery_.md)

---