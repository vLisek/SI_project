"""
PLIK: board.py
OPIS: Funkcje pomocnicze oraz stałe opisujące planszę gry Reversi.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten moduł przechowuje podstawowe informacje o planszy oraz pionkach.

Nie odpowiada za wykonywanie ruchów ani za decyzje AI.
Dostarcza wspólne stałe i funkcje pomocnicze wykorzystywane przez silnik gry,
algorytm AI oraz interfejs graficzny.

MECHANIZMY:
1. Definicja pustego pola oraz pionków graczy
2. Tworzenie początkowej planszy 8x8
3. Kopiowanie planszy
4. Pobieranie przeciwnika aktualnego gracza
5. Liczenie pionków na planszy
6. Sprawdzanie, czy plansza jest pełna
7. Zamiana współrzędnych ruchu na notację typu D3
"""

EMPTY = 0
BLACK = 1
WHITE = -1

BOARD_SIZE = 8


"""
--- TWORZENIE PLANSZY STARTOWEJ ---
Funkcja tworzy pustą planszę 8x8 i ustawia cztery początkowe pionki
zgodnie z klasycznymi zasadami Reversi.
"""
def create_initial_board() -> list[list[int]]:
    board = [[EMPTY for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    board[3][3] = WHITE
    board[3][4] = BLACK
    board[4][3] = BLACK
    board[4][4] = WHITE

    return board


"""
--- KOPIOWANIE PLANSZY ---
Tworzy niezależną kopię planszy.

Jest to szczególnie ważne dla algorytmu AI,
ponieważ Minimax wykonuje wiele symulowanych ruchów
i nie powinien nadpisywać prawdziwego stanu gry.
"""
def copy_board(board: list[list[int]]) -> list[list[int]]:
    return [row.copy() for row in board]


"""
--- POBRANIE PRZECIWNIKA ---
W projekcie gracze są oznaczeni jako 1 oraz -1.
Dzięki temu przeciwnik aktualnego gracza to po prostu wartość przeciwna.
"""
def get_opponent(player: int) -> int:
    return -player


"""
--- LICZENIE PIONKÓW ---
Funkcja zlicza pionki czarne i białe znajdujące się aktualnie na planszy.
Wynik jest używany między innymi do wyświetlania punktów oraz ustalenia zwycięzcy.
"""
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


"""
--- SPRAWDZENIE PEŁNEJ PLANSZY ---
Gra może zakończyć się wtedy, gdy na planszy nie ma już pustych pól.
"""
def is_board_full(board: list[list[int]]) -> bool:
    for row in board:
        for cell in row:
            if cell == EMPTY:
                return False

    return True


"""
--- NOTACJA RUCHU ---
Zamienia współrzędne planszy na zapis czytelny dla użytkownika.

Przykład:
row = 2, col = 3 -> D3
"""
def move_to_notation(row: int, col: int) -> str:
    column_letter = chr(ord("A") + col)
    row_number = row + 1
    return f"{column_letter}{row_number}"