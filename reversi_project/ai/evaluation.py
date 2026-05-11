from reversi_project.logic.board import BLACK, BOARD_SIZE, EMPTY, count_discs, get_opponent
from reversi_project.logic.engine import ReversiEngine

"""
PLIK: evaluation.py
OPIS: Moduł heurystycznej oceny stanu planszy dla gry Reversi.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten plik posługuje za decyzyjność AI. 
W grze Reversi liczba ruchów jest na tyle duża, 
że algorym musi w pewnym momencie zastanowić się i ocenić,
jak dobra jest sytuacja na planszy.

LOGIKA OCENY:
Algorytm nie może patrzeć tylko na liczbę pionków którą może uzyskać, bo bywa to mylące.
W tym celu mamy 5 aspektów które musi wziąć pod uwagę:
1. Kontrola rogów planszy - rogi są nie do przejęcia przez przeciwnika
2. Blokowanie ruchów przeciwnika
3. Wartość pól na planszy - macierz: POSITION_WEIGHTS
4. Różnica w liczbie pionków
5. Unikanie pól dających możliwość wyboru rogów przeciwnikowi

Wszystkie te czynniki są mnożone przez wagi, tworząc ostateczny wynik punktowy. Wynik dodatni oznacza przewagę AI.
"""

# --- TABELA WAG POZYCYJNYCH ---
# Każda liczba odpowiada polu na planszy 8x8.
# Wysokie wartości (120) to pola pożądane (rogi).
# Wartości ujemne (-20, -40) to pola niebezpieczne, których zajęcie ułatwia przeciwnikowi przejęcie rogów.

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

# --- MNOŻNIKI (WAGI) KOMPONENTÓW ---
# Określają, jak ważny jest dany aspekt gry dla AI.
# Przyjęcie tych wag pokazuje, że AI woli stracić pionki w celu zdobycia rogów
class ReversiEvaluator:
    CORNER_WEIGHT = 1000                # premia za posiadanie rogu
    MOBILITY_WEIGHT = 100               # premia za większą liczbę możliwych ruchów
    POSITIONAL_WEIGHT = 40              # premia za zajmowanie pól
    DISC_DIFFERENCE_WEIGHT = 20         # premia za różnicę w liczbie pionków
    RISKY_SQUARE_WEIGHT = 80            # kara za zajmowanie pól przy pustych rogach


# --- KLUCZOWE POLA STRATEGICZNE ---
# współrzędne rogów planszy
# rogów nie da się przejąć, co daje ogromną przewagę
    CORNERS = [
        (0, 0),
        (0, 7),
        (7, 0),
        (7, 7),
    ]

# Mapowanie: Róg -> Pola, które z nim bezpośrednio sąsiadują
# Logika: Jeśli róg jest pusty, to zajęcie pola obok niego to duży błąd
# taki ruch umożliwia przeciwnikowi zajęcie rogu w jego turze
    RISKY_SQUARES_BY_CORNER = {
        (0, 0): [(0, 1), (1, 0), (1, 1)],
        (0, 7): [(0, 6), (1, 7), (1, 6)],
        (7, 0): [(6, 0), (7, 1), (6, 1)],
        (7, 7): [(6, 7), (7, 6), (6, 6)],
    }

    def __init__(self):
        # silnik gry
        self.engine = ReversiEngine()

    """
    --- GŁÓWNA FUNKCJA OCENY (Heurystyka) ---
    Oblicza ostateczny wynik punktowy dla danego stanu planszy.
    Sumuje poszczególne komponenty strategiczne przemnożone przez ich wagi.
    """
    def evaluate_board(self, board: list[list[int]], ai_player: int) -> int:
        # Pobranie surowych danych o komponentach (np. ile mamy rogów, ile ruchów)
        components = self.evaluate_components(board, ai_player)

        # Łączymy wszystkie strategie w jeden wynik,
        # Przy risky_square_penalty widzimy minus, bo jest to komponent obniżający ocenę
        return (
            self.CORNER_WEIGHT * components["corner_score"]
            + self.MOBILITY_WEIGHT * components["mobility_score"]
            + self.POSITIONAL_WEIGHT * components["positional_score"]
            + self.DISC_DIFFERENCE_WEIGHT * components["disc_difference"]
            - self.RISKY_SQUARE_WEIGHT * components["risky_square_penalty"]
        )

    """
    --- AGREGATOR KOMPONENTÓW ---
    Zbiera cząstkowe wyniki dla wszystkich aspektów gry.
    Zwraca słownik, który ułatwia zarządzanie różnymi strategiami.
    """
    def evaluate_components(self, board: list[list[int]], ai_player: int) -> dict[str, int]:
        opponent = get_opponent(ai_player)

        # Wywołanie specyficznych funkcji liczących konkretne parametry gry
        return {
            "corner_score": self.calculate_corner_score(board, ai_player, opponent),
            "mobility_score": self.calculate_mobility_score(board, ai_player, opponent),
            "positional_score": self.calculate_positional_score(board, ai_player, opponent),
            "disc_difference": self.calculate_disc_difference(board, ai_player, opponent),
            "risky_square_penalty": self.calculate_risky_square_penalty(board, ai_player, opponent),
        }

    # --- CZYNNIK 1: KONTROLA ROGÓW ---
    # Funkcja zliczająca posiadane rogi
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

        # Zwracamy różnicę (przewaga AI w rogach)
        return ai_corners - opponent_corners

    # --- CZYNNIK 2: MOBILNOŚĆ (liczba ruchów możliwych) ---
    # Oblicza przewagę w liczbie dostępnych ruchów.
    # Wysoka mobilność pozwala AI kontrolować przebieg gry
    def calculate_mobility_score(
        self,
        board: list[list[int]],
        ai_player: int,
        opponent: int
    ) -> int:
        # Sprawdzenie ile legalnych ruchów ma AI, a ile przeciwnik
        ai_moves = len(self.engine.get_valid_moves(board, ai_player))
        opponent_moves = len(self.engine.get_valid_moves(board, opponent))

        # strategią jest ograniczyć ruchy przeciwnika, czyli dążyć do tego, aby nie miał ich wcale
        return ai_moves - opponent_moves

    # --- METRYKA 3: JAKOŚĆ POZYCJI (Macierz Wag) ---
    # Sumuje wartości pól zajętych przez graczy na podstawie tabeli POSITION_WEIGHTS.
    # Pozwala to AI ocenić, czy pionki stoją na "silnych" czy "słabych" polach.
    def calculate_positional_score(
        self,
        board: list[list[int]],
        ai_player: int,
        opponent: int
    ) -> int:
        score = 0

        # przejście przez całą planszę 8x8
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                if board[row][col] == ai_player:
                    score += POSITION_WEIGHTS[row][col]
                elif board[row][col] == opponent:
                    score -= POSITION_WEIGHTS[row][col]

        return score

    # --- METRYKA 4: RÓŻNICA PIONKÓW (Disc Difference) ---
    # Oblicza czystą przewagę liczbową pionków.
    # Niska waga, ze względu na to, że to jest kluczowe dopiero na końcu gry
    def calculate_disc_difference(
        self,
        board: list[list[int]],
        ai_player: int,
        opponent: int
    ) -> int:
        # całkowita liczba pionków
        black_count, white_count = count_discs(board)

        # liczniki przypisane do graczy
        if ai_player == BLACK:
            ai_count = black_count
            opponent_count = white_count
        else:
            ai_count = white_count
            opponent_count = black_count
        # Zwraca różnicę (dodatnia oznacza więcej pionków AI)
        return ai_count - opponent_count

    # --- METRYKA 5: KARA ZA POLA RYZYKOWNE ---
    # Oblicza karę za zajmowanie pól przy rogach
    def calculate_risky_square_penalty(
        self,
        board: list[list[int]],
        ai_player: int,
        opponent: int
    ) -> int:
        ai_risky_squares = 0
        opponent_risky_squares = 0

        # iterujemy przez wszystkie rogi i przypisane do niego ryzykowne pola
        for corner, risky_squares in self.RISKY_SQUARES_BY_CORNER.items():
            corner_row, corner_col = corner

            # Ważne: Jeśli róg nie jest pusty, pola obok niego przestają być ryzykowne!
            if board[corner_row][corner_col] != EMPTY:
                continue

            # Sprawdzenie czy przeciwnik lub AI zajęli puste pola obok rogu
            for row, col in risky_squares:
                if board[row][col] == ai_player:
                    ai_risky_squares += 1
                elif board[row][col] == opponent:
                    opponent_risky_squares += 1

        # różnica w ryzykownych ruchach
        return ai_risky_squares - opponent_risky_squares