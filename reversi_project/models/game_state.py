from dataclasses import dataclass

"""
PLIK: game_state.py
OPIS: Model aktualnego stanu gry Reversi.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten plik przechowuje dane opisujące aktualną sytuację w rozgrywce.

GameState nie wykonuje żadnej logiki gry.
Jest prostą strukturą danych, która jest przekazywana między silnikiem gry,
agentem AI oraz interfejsem graficznym.

PRZECHOWYWANE DANE:
1. Aktualny stan planszy
2. Informacja, który gracz wykonuje ruch
3. Informacja, czy gra została zakończona
4. Informacja, kto wygrał partię
"""


@dataclass
class GameState:
    """
    Klasa reprezentująca pełny stan jednej rozgrywki.

    board - aktualna plansza gry zapisana jako lista list
    current_player - aktualny gracz: "human", "ai", "ai_1" albo "ai_2"
    game_over - informacja czy gra została zakończona
    winner - zwycięzca gry albo None, jeśli gra jeszcze trwa lub zakończyła się remisem
    """

    board: list[list[int]]
    current_player: int
    game_over: bool = False
    winner: int | None = None