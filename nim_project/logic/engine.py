from models.game_state import GameState
from models.move import Move


class NimEngine:
    def calculate_nim_sum(self, piles: list[int]) -> int:
        nim_sum = 0

        for pile in piles:
            nim_sum ^= pile

        return nim_sum

    def is_game_over(self, piles: list[int]) -> bool:
        return all(pile == 0 for pile in piles)

    def is_valid_move(self, piles: list[int], move: Move) -> bool:
        if move.pile_index < 0 or move.pile_index >= len(piles):
            return False

        if move.amount <= 0:
            return False

        if move.amount > piles[move.pile_index]:
            return False

        return True

    def apply_move(self, game_state: GameState, move: Move) -> GameState:
        if not self.is_valid_move(game_state.piles, move):
            raise ValueError("Nieprawidłowy ruch.")

        new_piles = game_state.piles.copy()
        new_piles[move.pile_index] -= move.amount

        game_over = self.is_game_over(new_piles)
        winner = game_state.current_player if game_over else None

        next_player = game_state.current_player

        if not game_over:
            if game_state.current_player == "human":
                next_player = "ai"
            else:
                next_player = "human"

        return GameState(
            piles=new_piles,
            current_player=next_player,
            game_over=game_over,
            winner=winner
        )