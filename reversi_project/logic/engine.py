from logic.board import (
    BLACK,
    BOARD_SIZE,
    EMPTY,
    WHITE,
    copy_board,
    get_opponent,
    is_board_full,
)
from models.game_state import GameState
from models.move import Move


class ReversiEngine:
    DIRECTIONS = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]

    def is_on_board(self, row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE

    def find_flips_for_move(
        self,
        board: list[list[int]],
        move: Move,
        player: int
    ) -> list[tuple[int, int]]:
        if not self.is_on_board(move.row, move.col):
            return []

        if board[move.row][move.col] != EMPTY:
            return []

        opponent = get_opponent(player)
        all_flips: list[tuple[int, int]] = []

        for row_direction, col_direction in self.DIRECTIONS:
            flips_in_direction: list[tuple[int, int]] = []

            current_row = move.row + row_direction
            current_col = move.col + col_direction

            while self.is_on_board(current_row, current_col):
                current_cell = board[current_row][current_col]

                if current_cell == opponent:
                    flips_in_direction.append((current_row, current_col))
                elif current_cell == player:
                    if flips_in_direction:
                        all_flips.extend(flips_in_direction)
                    break
                else:
                    break

                current_row += row_direction
                current_col += col_direction

        return all_flips

    def is_valid_move(
        self,
        board: list[list[int]],
        move: Move,
        player: int
    ) -> bool:
        return len(self.find_flips_for_move(board, move, player)) > 0

    def get_valid_moves(
        self,
        board: list[list[int]],
        player: int
    ) -> list[Move]:
        valid_moves: list[Move] = []

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                move = Move(row, col)

                if self.is_valid_move(board, move, player):
                    valid_moves.append(move)

        return valid_moves

    def apply_move(
        self,
        game_state: GameState,
        move: Move
    ) -> GameState:
        board = game_state.board
        player = game_state.current_player

        flips = self.find_flips_for_move(board, move, player)

        if not flips:
            raise ValueError("Nieprawidłowy ruch.")

        new_board = copy_board(board)
        new_board[move.row][move.col] = player

        for row, col in flips:
            new_board[row][col] = player

        return self.create_next_state(new_board, player)

    def create_next_state(
        self,
        board: list[list[int]],
        player_who_moved: int
    ) -> GameState:
        opponent = get_opponent(player_who_moved)

        opponent_moves = self.get_valid_moves(board, opponent)
        current_player_moves = self.get_valid_moves(board, player_who_moved)

        if is_board_full(board) or (not opponent_moves and not current_player_moves):
            return GameState(
                board=board,
                current_player=player_who_moved,
                game_over=True,
                winner=self.get_winner(board)
            )

        if opponent_moves:
            next_player = opponent
        else:
            next_player = player_who_moved

        return GameState(
            board=board,
            current_player=next_player,
            game_over=False,
            winner=None
        )

    def get_winner(self, board: list[list[int]]) -> int | None:
        black_count = 0
        white_count = 0

        for row in board:
            for cell in row:
                if cell == BLACK:
                    black_count += 1
                elif cell == WHITE:
                    white_count += 1

        if black_count > white_count:
            return BLACK

        if white_count > black_count:
            return WHITE

        return None