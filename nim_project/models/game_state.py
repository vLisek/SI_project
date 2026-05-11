from dataclasses import dataclass

"""
PLIK: game_state.py
OPIS: Model aktualnego stanu gry Nim.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten plik przechowuje dane opisujące aktualną sytuację w rozgrywce.

GameState nie wykonuje żadnej logiki gry.
Jest prostą strukturą danych, która jest przekazywana między silnikiem gry,
agentem AI oraz interfejsem graficznym.

PRZECHOWYWANE DANE:
1. Aktualny stan stert
2. Informacja, który gracz wykonuje ruch
3. Informacja, czy gra została zakończona
4. Informacja, kto wygrał partię
"""


@dataclass
class GameState:
    """
    Klasa reprezentująca pełny stan jednej rozgrywki.

    piles - lista stert, gdzie każda liczba oznacza liczbę żetonów w danej stercie
    current_player - aktualny gracz: "human" albo "ai"
    game_over - informacja czy gra została zakończona
    winner - zwycięzca gry albo None, jeśli gra jeszcze trwa
    """

    piles: list[int]
    current_player: str
    game_over: bool = False
    winner: str | None = None