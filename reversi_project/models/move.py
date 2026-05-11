from dataclasses import dataclass

"""
PLIK: move.py
OPIS: Model pojedynczego ruchu w grze Reversi.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten plik przechowuje dane opisujące ruch wykonany przez gracza lub AI.

Move nie wykonuje żadnej logiki gry.
Jest prostą strukturą danych, która informuje silnik gry,
w którym miejscu na planszy ma zostać postawiony pionek.

PRZECHOWYWANE DANE:
1. Numer wiersza planszy
2. Numer kolumny planszy
"""


@dataclass(frozen=True)
class Move:
    """
    Klasa reprezentująca pojedynczy ruch w grze Reversi.

    row - indeks wiersza planszy
    col - indeks kolumny planszy
    """

    row: int
    col: int