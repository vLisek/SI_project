from nim_project.models.game_state import GameState
from nim_project.models.move import Move

"""
PLIK: engine.py
OPIS: Silnik zasad gry Nim.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten moduł odpowiada za podstawową logikę rozgrywki.
Nie podejmuje decyzji za AI, tylko pilnuje poprawności zasad gry.

Silnik sprawdza poprawność ruchów, aktualizuje stan stert,
zmienia aktualnego gracza oraz wykrywa koniec gry.

MECHANIZMY:
1. Obliczanie Nim-Sum - XOR wszystkich stert
2. Sprawdzanie zakończenia gry
3. Walidacja ruchu gracza lub AI
4. Wykonanie ruchu na kopii aktualnego stanu
5. Ustalenie następnego gracza i zwycięzcy
6. Obsługa dwóch trybów rozgrywki: Człowiek vs AI oraz AI vs AI
"""


class NimEngine:
    """
    --- OBLICZANIE NIM-SUM ---
    Nim-Sum to wynik operacji XOR wykonanej na wszystkich stertach.
    Jest to kluczowa wartość matematyczna w grze Nim.

    Jeśli Nim-Sum = 0, pozycja jest przegrywająca dla gracza wykonującego ruch,
    zakładając optymalną grę przeciwnika.

    Jeśli Nim-Sum != 0, pozycja jest wygrywająca i istnieje ruch,
    który sprowadza Nim-Sum do wartości 0.
    """
    def calculate_nim_sum(self, piles: list[int]) -> int:
        nim_sum = 0

        # XOR kolejnych stert daje wartość Nim-Sum dla całej pozycji
        for pile in piles:
            nim_sum ^= pile

        return nim_sum


    """
    --- SPRAWDZENIE KOŃCA GRY ---
    W wariancie normalnym gra kończy się wtedy, gdy wszystkie sterty są puste.
    Wygrywa gracz, który zabrał ostatni żeton.
    """
    def is_game_over(self, piles: list[int]) -> bool:
        return all(pile == 0 for pile in piles)


    """
    --- WALIDACJA RUCHU ---
    Funkcja sprawdza, czy wybrany ruch jest zgodny z zasadami gry Nim.

    Poprawny ruch musi spełniać warunki:
    1. wybrana sterta musi istnieć
    2. trzeba zabrać co najmniej jeden żeton
    3. nie można zabrać więcej żetonów niż znajduje się w stercie
    """
    def is_valid_move(self, piles: list[int], move: Move) -> bool:
        # Sprawdzenie czy indeks sterty mieści się w zakresie listy stert
        if move.pile_index < 0 or move.pile_index >= len(piles):
            return False

        # Nie można wykonać ruchu zabierającego 0 lub ujemną liczbę żetonów
        if move.amount <= 0:
            return False

        # Nie można zabrać więcej żetonów niż znajduje się w wybranej stercie
        if move.amount > piles[move.pile_index]:
            return False

        return True


    """
    --- WYKONANIE RUCHU ---
    Funkcja aktualizuje stan gry po poprawnym ruchu.

    Nie modyfikuje starej listy stert bezpośrednio.
    Tworzy kopię aktualnego stanu, zmniejsza wybraną stertę,
    sprawdza koniec gry i ustala następnego gracza.
    """
    def apply_move(self, game_state: GameState, move: Move) -> GameState:
        if not self.is_valid_move(game_state.piles, move):
            raise ValueError("Nieprawidłowy ruch.")

        # Tworzymy kopię stert, aby nie nadpisywać poprzedniego stanu gry
        new_piles = game_state.piles.copy()
        new_piles[move.pile_index] -= move.amount

        # Po wykonaniu ruchu sprawdzamy, czy wszystkie sterty są już puste
        game_over = self.is_game_over(new_piles)
        winner = game_state.current_player if game_over else None

        next_player = game_state.current_player

        # Jeśli gra się nie skończyła, tura przechodzi na drugiego gracza.
        # Silnik obsługuje dwa tryby:
        # human <-> ai dla gry człowieka z komputerem
        # ai_1 <-> ai_2 dla automatycznej symulacji AI vs AI
        if not game_over:
            if game_state.current_player == "human":
                next_player = "ai"
            elif game_state.current_player == "ai":
                next_player = "human"
            elif game_state.current_player == "ai_1":
                next_player = "ai_2"
            elif game_state.current_player == "ai_2":
                next_player = "ai_1"

        return GameState(
            piles=new_piles,
            current_player=next_player,
            game_over=game_over,
            winner=winner
        )