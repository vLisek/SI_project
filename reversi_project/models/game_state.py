from dataclasses import dataclass
from typing import Optional


@dataclass
class GameState:
    board: list[list[int]]
    current_player: int
    game_over: bool = False
    winner: Optional[int] = None