from logic.board import BLACK, BOARD_SIZE, EMPTY, count_discs, get_opponent
from logic.engine import ReversiEngine


POSITION_WEIGHTS = [
    [120, -20, 20, 5, 5, 20, -20, 120],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [5, -5, 3, 3, 3, 3, -5, 5],
    [20, -5, 15, 3, 3, 15, -5, 20],
    [-20, -40, -5, -5, -5, -5, -40, -20],
    [120, -20, 20, 5, 5, 20, -20, 120],
]


class ReversiEvaluator:
    CORNER_WEIGHT = 1000
    MOBILITY_WEIGHT = 100
    POSITIONAL_WEIGHT = 40
    DISC_DIFFERENCE_WEIGHT = 20
    RISKY_SQUARE_WEIGHT = 80

    CORNERS = [
        (0, 0),
        (0, 7),
        (7, 0),
        (7, 7),
    ]

    RISKY_SQUARES_BY_CORNER = {
        (0, 0): [(0, 1), (1, 0), (1, 1)],
        (0, 7): [(0, 6), (1, 7), (1, 6)],
        (7, 0): [(6, 0), (7, 1), (6, 1)],
        (7, 7): [(6, 7), (7, 6), (6, 6)],
    }

    def __init__(self):
        self.engine = ReversiEngine()

    def evaluate_board(self, board: list[list[int]], ai_player: int) -> int:
        components = self.evaluate_components(board, ai_player)

        return (
            self.CORNER_WEIGHT * components["corner_score"]
            + self.MOBILITY_WEIGHT * components["mobility_score"]
            + self.POSITIONAL_WEIGHT * components["positional_score"]
            + self.DISC_DIFFERENCE_WEIGHT * components["disc_difference"]
            - self.RISKY_SQUARE_WEIGHT * components["risky_square_penalty"]
        )

    def evaluate_components(self, board: list[list[int]], ai_player: int) -> dict[str, int]:
        opponent = get_opponent(ai_player)

        return {
            "corner_score": self.calculate_corner_score(board, ai_player, opponent),
            "mobility_score": self.calculate_mobility_score(board, ai_player, opponent),
            "positional_score": self.calculate_positional_score(board, ai_player, opponent),
            "disc_difference": self.calculate_disc_difference(board, ai_player, opponent),
            "risky_square_penalty": self.calculate_risky_square_penalty(board, ai_player, opponent),
        }

    def calculate_corner_score(
        self,
        board: list[list[int]],
        ai_player: int,
        opponent: int
    ) -> int:
        ai_corners = 0
        opponent_corners = 0

        for row, col in self.CORNERS:
            if board[row][col] == ai_player:
                ai_corners += 1
            elif board[row][col] == opponent:
                opponent_corners += 1

        return ai_corners - opponent_corners

    def calculate_mobility_score(
        self,
        board: list[list[int]],
        ai_player: int,
        opponent: int
    ) -> int:
        ai_moves = len(self.engine.get_valid_moves(board, ai_player))
        opponent_moves = len(self.engine.get_valid_moves(board, opponent))

        return ai_moves - opponent_moves

    def calculate_positional_score(
        self,
        board: list[list[int]],
        ai_player: int,
        opponent: int
    ) -> int:
        score = 0

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == ai_player:
                    score += POSITION_WEIGHTS[row][col]
                elif board[row][col] == opponent:
                    score -= POSITION_WEIGHTS[row][col]

        return score

    def calculate_disc_difference(
        self,
        board: list[list[int]],
        ai_player: int,
        opponent: int
    ) -> int:
        black_count, white_count = count_discs(board)

        if ai_player == BLACK:
            ai_count = black_count
            opponent_count = white_count
        else:
            ai_count = white_count
            opponent_count = black_count

        return ai_count - opponent_count

    def calculate_risky_square_penalty(
        self,
        board: list[list[int]],
        ai_player: int,
        opponent: int
    ) -> int:
        ai_risky_squares = 0
        opponent_risky_squares = 0

        for corner, risky_squares in self.RISKY_SQUARES_BY_CORNER.items():
            corner_row, corner_col = corner

            if board[corner_row][corner_col] != EMPTY:
                continue

            for row, col in risky_squares:
                if board[row][col] == ai_player:
                    ai_risky_squares += 1
                elif board[row][col] == opponent:
                    opponent_risky_squares += 1

        return ai_risky_squares - opponent_risky_squares