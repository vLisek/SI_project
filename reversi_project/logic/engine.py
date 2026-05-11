from reversi_project.logic.board import (
    BLACK,
    BOARD_SIZE,
    EMPTY,
    WHITE,
    copy_board,
    get_opponent,
    is_board_full,
)
from reversi_project.models.game_state import GameState
from reversi_project.models.move import Move

"""
PLIK: engine.py
OPIS: Silnik zasad gry Reversi.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten moduł odpowiada za pełną logikę rozgrywki w Reversi.
Nie podejmuje decyzji za AI, tylko sprawdza zasady gry,
legalność ruchów, odwracanie pionków oraz zakończenie partii.

Silnik jest wykorzystywany zarówno przez GUI, jak i przez agenta AI.
Dzięki temu reguły gry są w jednym miejscu i nie trzeba ich powielać.

MECHANIZMY:
1. Sprawdzanie, czy pole znajduje się na planszy
2. Wyszukiwanie pionków do odwrócenia w 8 kierunkach
3. Sprawdzanie legalności ruchu
4. Generowanie listy wszystkich legalnych ruchów
5. Wykonanie ruchu i odwrócenie pionków
6. Obsługa pomijania tury
7. Wykrycie końca gry i zwycięzcy
"""


class ReversiEngine:
    # Wszystkie możliwe kierunki sprawdzania ruchu.
    # W Reversi pionki mogą być odwracane poziomo, pionowo oraz po skosach.
    DIRECTIONS = [
        (-1, -1), (-1, 0), (-1, 1),
        (0, -1),           (0, 1),
        (1, -1),  (1, 0),  (1, 1),
    ]


    """
    --- SPRAWDZENIE GRANIC PLANSZY ---
    Funkcja sprawdza, czy podane współrzędne mieszczą się na planszy 8x8.
    Jest używana przy analizie ruchów w różnych kierunkach.
    """
    def is_on_board(self, row: int, col: int) -> bool:
        return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


    """
    --- SZUKANIE PIONKÓW DO ODWRÓCENIA ---
    Najważniejsza funkcja reguł Reversi.
    Sprawdza, które pionki przeciwnika zostaną odwrócone po wykonaniu danego ruchu.

    Legalny ruch musi spełniać układ:
    nowy pionek -> pionki przeciwnika -> własny pionek

    Funkcja sprawdza ten warunek we wszystkich 8 kierunkach.
    """
    def find_flips_for_move(
        self,
        board: list[list[int]],
        move: Move,
        player: int
    ) -> list[tuple[int, int]]:
        # Jeśli ruch wychodzi poza planszę, nie można nic odwrócić
        if not self.is_on_board(move.row, move.col):
            return []

        # Ruch można wykonać tylko na pustym polu
        if board[move.row][move.col] != EMPTY:
            return []

        opponent = get_opponent(player)
        all_flips: list[tuple[int, int]] = []

        # Przechodzimy przez każdy z 8 kierunków
        for row_direction, col_direction in self.DIRECTIONS:
            flips_in_direction: list[tuple[int, int]] = []

            current_row = move.row + row_direction
            current_col = move.col + col_direction

            # Idziemy w danym kierunku tak długo, jak jesteśmy na planszy
            while self.is_on_board(current_row, current_col):
                current_cell = board[current_row][current_col]

                # Jeżeli trafiamy na pionek przeciwnika, może on zostać odwrócony
                if current_cell == opponent:
                    flips_in_direction.append((current_row, current_col))

                # Jeżeli po pionkach przeciwnika trafimy na własny pionek,
                # to cała zebrana linia pionków jest do odwrócenia
                elif current_cell == player:
                    if flips_in_direction:
                        all_flips.extend(flips_in_direction)
                    break

                # Puste pole przerywa sprawdzanie w danym kierunku
                else:
                    break

                current_row += row_direction
                current_col += col_direction

        return all_flips


    """
    --- WALIDACJA RUCHU ---
    Ruch jest legalny wtedy, gdy powoduje odwrócenie przynajmniej jednego
    pionka przeciwnika.
    """
    def is_valid_move(
        self,
        board: list[list[int]],
        move: Move,
        player: int
    ) -> bool:
        return len(self.find_flips_for_move(board, move, player)) > 0


    """
    --- GENEROWANIE LEGALNYCH RUCHÓW ---
    Funkcja przechodzi po całej planszy i sprawdza każde pole.
    Jeśli ruch na danym polu jest legalny, zostaje dodany do listy.
    """
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


    """
    --- WYKONANIE RUCHU ---
    Funkcja wykonuje ruch aktualnego gracza:
    1. sprawdza pionki do odwrócenia
    2. tworzy kopię planszy
    3. stawia nowy pionek
    4. odwraca pionki przeciwnika
    5. tworzy następny stan gry
    """
    def apply_move(
        self,
        game_state: GameState,
        move: Move
    ) -> GameState:
        board = game_state.board
        player = game_state.current_player

        flips = self.find_flips_for_move(board, move, player)

        # Jeśli nie ma pionków do odwrócenia, ruch jest nielegalny
        if not flips:
            raise ValueError("Nieprawidłowy ruch.")

        # Nie modyfikujemy starej planszy bezpośrednio.
        # Tworzymy kopię, aby symulacje AI i GUI nie nadpisywały poprzedniego stanu.
        new_board = copy_board(board)
        new_board[move.row][move.col] = player

        # Odwrócenie wszystkich pionków znalezionych przez find_flips_for_move
        for row, col in flips:
            new_board[row][col] = player

        return self.create_next_state(new_board, player)


    """
    --- TWORZENIE NASTĘPNEGO STANU GRY ---
    Po wykonaniu ruchu trzeba ustalić:
    1. czy gra się zakończyła
    2. czy przeciwnik ma legalny ruch
    3. czy należy pominąć turę przeciwnika
    4. kto będzie następnym graczem
    """
    def create_next_state(
        self,
        board: list[list[int]],
        player_who_moved: int
    ) -> GameState:
        opponent = get_opponent(player_who_moved)

        opponent_moves = self.get_valid_moves(board, opponent)
        current_player_moves = self.get_valid_moves(board, player_who_moved)

        # Gra kończy się gdy plansza jest pełna albo żaden gracz nie ma ruchu
        if is_board_full(board) or (not opponent_moves and not current_player_moves):
            return GameState(
                board=board,
                current_player=player_who_moved,
                game_over=True,
                winner=self.get_winner(board)
            )

        # Jeśli przeciwnik ma ruch, tura przechodzi na niego.
        # Jeśli nie ma ruchu, jego tura zostaje pominięta i gra dalej ten sam gracz.
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


    """
    --- WYZNACZANIE ZWYCIĘZCY ---
    Funkcja zlicza pionki obu graczy.
    Wygrywa ten, kto ma więcej pionków na planszy.
    Przy równej liczbie pionków zwracany jest remis, czyli None.
    """
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