from dataclasses import dataclass


@dataclass
class Move:
    pile_index: int
    amount: int