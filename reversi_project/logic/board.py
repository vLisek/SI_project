EMPTY = 0
BLACK = 1
WHITE = -1

BOARD_SIZE = 8


def create_initial_board() -> list[list[int]]:
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    board[3][3] = WHITE
    board[3][4] = BLACK
    board[4][3] = BLACK
    board[4][4] = WHITE

    return board


def copy_board(board: list[list[int]]) -> list[list[int]]:
    return [row.copy() for row in board]


def get_opponent(player: int) -> int:
    return -player


def count_discs(board: list[list[int]]) -> tuple[int, int]:
    black_count = 0
    white_count = 0

    for row in board:
        for cell in row:
            if cell == BLACK:
                black_count += 1
            elif cell == WHITE:
                white_count += 1

    return black_count, white_count


def is_board_full(board: list[list[int]]) -> bool:
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False

    return True

def move_to_notation(row: int, col: int) -> str:
    column_letter = chr(ord("A") + col)
    row_number = row + 1
    return f"{column_letter}{row_number}"