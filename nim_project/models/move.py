from dataclasses import dataclass

"""
PLIK: move.py
OPIS: Model pojedynczego ruchu w grze Nim.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten plik przechowuje dane opisujące ruch wykonany przez gracza lub AI.

Move nie wykonuje żadnej logiki gry.
Jest prostą strukturą danych, która informuje silnik gry,
z której sterty należy zabrać żetony oraz ile żetonów zabrać.

PRZECHOWYWANE DANE:
1. Indeks sterty, z której zabierane są żetony
2. Liczba żetonów zabieranych z tej sterty
"""


@dataclass
class Move:
    """
    Klasa reprezentująca pojedynczy ruch w grze Nim.

    pile_index - indeks sterty wybranej przez gracza lub AI
    amount - liczba żetonów do zabrania z wybranej sterty
    """

    pile_index: int
    amount: int