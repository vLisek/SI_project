from nim_project.logic.engine import NimEngine
from nim_project.models.move import Move

"""
PLIK: agent.py
OPIS: Implementacja inteligentnego agenta gry Nim opartego na strategii Nim-Sum.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten moduł odpowiada za proces podejmowania decyzji przez AI. 
W przeciwieństwie do Reversi, tutaj nie używamy algorytmu Minimax,
ponieważ gra Nim posiada znane rozwiązanie matematyczne.

MECHANIZMY:
1. Nim-Sum - wartość XOR wszystkich stert
2. Rozpoznanie pozycji wygrywającej i przegrywającej
3. Wybór ruchu sprowadzającego Nim-Sum do 0
4. Ruch awaryjny - wykonywany wtedy, gdy AI nie ma ruchu gwarantującego zwycięstwo
"""


class NimAI:
    def __init__(self):
        # silnik gry odpowiada za obliczanie Nim-Sum oraz podstawową logikę zasad
        self.engine = NimEngine()


    """
    --- GŁÓWNA FUNKCJA AI ---
    Metoda wywoływana, gdy AI musi podjąć decyzję.
    Najpierw oblicza Nim-Sum, a następnie sprawdza czy pozycja jest wygrywająca.
    Jeśli tak, wybiera ruch sprowadzający Nim-Sum do 0.
    """
    def find_optimal_move(self, piles: list[int]) -> Move:
        nim_sum = self.engine.calculate_nim_sum(piles)

        # jeśli Nim-Sum wynosi 0, AI znajduje się w pozycji przegrywającej
        # przy optymalnej grze przeciwnika
        if nim_sum == 0:
            return self.find_fallback_move(piles)

        # Szukamy sterty, którą można zmniejszyć tak,
        # aby po ruchu całkowity Nim-Sum był równy 0.
        for index, pile in enumerate(piles):
            target = pile ^ nim_sum

            # Warunek target < pile oznacza, że dana sterta może zostać zmniejszona
            # do wartości target, co daje pozycję przegrywającą przeciwnikowi.
            if target < pile:
                amount = pile - target
                return Move(index, amount)

        # Teoretycznie nie powinno się wydarzyć dla pozycji z Nim-Sum != 0,
        # ale zostawiamy zabezpieczenie na wypadek nietypowego stanu gry.
        return self.find_fallback_move(piles)


    """
    --- RUCH AWARYJNY ---
    Wykonywany wtedy, gdy Nim-Sum wynosi 0.
    W takiej pozycji AI nie ma ruchu, który gwarantuje zwycięstwo,
    dlatego wybiera pierwszy możliwy poprawny ruch.
    """
    def find_fallback_move(self, piles: list[int]) -> Move:
        for index, pile in enumerate(piles):
            if pile > 0:
                return Move(index, 1)

        raise ValueError("Brak możliwych ruchów.")


    """
    --- WYJAŚNIENIE RUCHU AI ---
    Metoda przygotowuje opis decyzji pod GUI.
    Pokazuje stan przed ruchem, wybraną stertę, liczbę zabranych żetonów
    oraz Nim-Sum przed i po ruchu.
    """
    def explain_move(self, piles_before: list[int], move: Move) -> str:
        nim_sum_before = self.engine.calculate_nim_sum(piles_before)

        # Tworzymy pomocniczą kopię stert, aby policzyć stan po ruchu AI
        piles_after = piles_before.copy()
        pile_before = piles_before[move.pile_index]
        pile_after = pile_before - move.amount
        piles_after[move.pile_index] = pile_after

        nim_sum_after = self.engine.calculate_nim_sum(piles_after)

        # Szerokość zapisu binarnego dopasowana do największej wartości ze stert
        binary_width = self.get_binary_width(piles_before + piles_after)

        if nim_sum_before == 0:
            position_type = "przegrywająca przy optymalnej grze przeciwnika"
            strategy_info = (
                "AI nie ma ruchu gwarantującego zwycięstwo, ponieważ Nim-Sum przed ruchem wynosi 0.\n"
                "W takiej sytuacji AI wykonuje pierwszy dostępny poprawny ruch."
            )
        else:
            position_type = "wygrywająca"
            strategy_info = (
                "AI wybiera taką stertę, aby po zmniejszeniu jej wartości całkowity Nim-Sum wynosił 0.\n"
                "Dzięki temu przeciwnik otrzymuje pozycję przegrywającą przy optymalnej grze."
            )

        return (
            f"Wyjaśnienie ruchu AI\n"
            f"{'=' * 24}\n\n"
            f"Stan przed ruchem AI: {piles_before}\n"
            f"Nim-Sum przed ruchem: {nim_sum_before} = {nim_sum_before:0{binary_width}b}\n"
            f"Typ pozycji: {position_type}\n\n"
            f"Wybrana sterta: {move.pile_index + 1}\n"
            f"Wartość sterty przed ruchem: {pile_before}\n"
            f"Wartość sterty po ruchu: {pile_after}\n"
            f"Liczba zabranych żetonów: {move.amount}\n\n"
            f"Stan po ruchu AI: {piles_after}\n"
            f"Nim-Sum po ruchu: {nim_sum_after} = {nim_sum_after:0{binary_width}b}\n\n"
            f"{strategy_info}"
        )


    """
    --- FORMATOWANIE ZAPISU BINARNEGO ---
    Funkcja pomocnicza używana tylko do czytelnego wyświetlania Nim-Sum.
    Dzięki niej zapis binarny ma stałą szerokość i wygląda czytelnie w panelu wyjaśnienia.
    """
    def get_binary_width(self, piles: list[int]) -> int:
        max_value = max(piles) if piles else 0
        return max(1, max_value.bit_length())