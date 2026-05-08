from dataclasses import dataclass


@dataclass
class GameState:
    piles: list[int]
    current_player: str
    game_over: bool = False
    winner: str | None = None