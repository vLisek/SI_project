import time
from dataclasses import dataclass
from math import inf
from typing import Optional

from reversi_project.ai.evaluation import ReversiEvaluator
from reversi_project.logic.board import BLACK, count_discs, get_opponent, move_to_notation
from reversi_project.logic.engine import ReversiEngine
from reversi_project.models.game_state import GameState
from reversi_project.models.move import Move

"""
PLIK: agent.py
OPIS: Implementacja inteligentnego agenta gry Reversi opartego na algorytmie Minimax.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten moduł odpowiada za proces "myślenia" AI. Wykorzystuje przeszukiwanie 
drzewa stanów gry, aby przewidzieć ruchy przeciwnika i wybrać optymalne 
zagranie dla siebie.

MECHANIZMY:
1. Algorytm Minimax - symuluje grę obu stron, zakładając, że każda gra optymalnie.
2. Odcięcia Alfa-Beta - optymalizacja, która pozwala pominąć gałęzie drzewa, które nie mają wpływu na ostateczną decyzję
3. Zarządzanie głębokośćią - AI patrzy na określoną liczbę ruchów w przód
4. Heurystyka - wykorzystuje implementację z evaluation.py do oceny liści drzewa gry
"""

@dataclass
class MinimaxStats:
    """
    Klasa do monitorowania wydajności algorytmu.
    Pozwala ocenić jak bardzo optymalizacja pomaga w obliczeniach
    """
    evaluated_states: int = 0           # wszystkie sprawdzone ustawienia planszy
    alpha_beta_cutoffs: int = 0         # liczba pominiętych gałęzi dzięki odcinaniu
    search_time_seconds: float = 0.0    # całkowity czas myślenia AI


@dataclass
class MinimaxResult:
    """
    Struktura przechowująca finalny wynik działania algorytmu
    """
    move: Optional[Move]        # najlepszy wybranych ruch
    score: int                  # ocena punktowa tego ruchu
    stats: MinimaxStats         # statystyki zebrane podczas obliczeń


class ReversiAI:
    # Stałe definiujące krańcowe wartości dla zwycięstwa i porażki
    WIN_SCORE = 1_000_000
    LOSS_SCORE = -1_000_000

    def __init__(self):
        self.engine = ReversiEngine()
        self.evaluator = ReversiEvaluator()
        self.stats = MinimaxStats()


    """
    --- PUNKT WYJŚĆIA AI ---
    Metoda wywoływana, gdy AI musi podjąć decyzję
    Inicjuje proces przeszukiwania drzewa i mierzy jego czas
    """
    def choose_best_move(
        self,
        board: list[list[int]],
        current_player: int,
        ai_player: int,
        depth: int
    ) -> MinimaxResult:
        start_time = time.perf_counter()

        self.stats = MinimaxStats() # reset przed następnym ruchem

        valid_moves = self.engine.get_valid_moves(board, current_player)

        # jeśli AI nie ma ruchów, to sprawdza co się stanie dalej (czy koniec gry)
        if not valid_moves:
            score = self.minimax(
                board=board,
                depth=depth,
                alpha=-inf,
                beta=inf,
                current_player=get_opponent(current_player),
                ai_player=ai_player
            )

            self.stats.search_time_seconds = time.perf_counter() - start_time

            return MinimaxResult(
                move=None,
                score=score,
                stats=self.stats
            )

        best_move: Optional[Move] = None

        # Start symulacji dla każdego dostępnego ruchu z obecnej pozycji
        if current_player == ai_player:
            best_score = -inf

            for move in self.order_moves(valid_moves):
                # symulacja ruchu na wirtualnej planszy
                next_state = self.engine.apply_move(
                    GameState(board=board, current_player=current_player),
                    move
                )
                # rekurencja minmax, sprawdzenie odpowiedzi przecwinika
                score = self.minimax(
                    board=next_state.board,
                    depth=depth - 1,
                    alpha=-inf,
                    beta=inf,
                    current_player=next_state.current_player,
                    ai_player=ai_player
                )

                # analogiczna logika dla przeciwnika dążącego do minimaluzacji wyniku
                if score > best_score:
                    best_score = score
                    best_move = move

        else:
            best_score = inf

            for move in self.order_moves(valid_moves):
                next_state = self.engine.apply_move(
                    GameState(board=board, current_player=current_player),
                    move
                )

                score = self.minimax(
                    board=next_state.board,
                    depth=depth - 1,
                    alpha=-inf,
                    beta=inf,
                    current_player=next_state.current_player,
                    ai_player=ai_player
                )

                if score < best_score:
                    best_score = score
                    best_move = move

        self.stats.search_time_seconds = time.perf_counter() - start_time

        return MinimaxResult(
            move=best_move,
            score=int(best_score),
            stats=self.stats
        )

    """
    --- RDZEŃ ALGORYTMU: MINIMAX Z ALFA-BETA ---
    Rekurencja przeszukująca drzewo gry.
    alpha: najlepszy wynik gwarantowany dla gracza MAX (AI)
    beta: najlepszy wynik gwarantowany dla gracza MIN (przeciwnik)
    """
    def minimax(
        self,
        board: list[list[int]],
        depth: int,
        alpha: float,
        beta: float,
        current_player: int,
        ai_player: int
    ) -> int:
        ai_moves = self.engine.get_valid_moves(board, ai_player)
        opponent = get_opponent(ai_player)
        opponent_moves = self.engine.get_valid_moves(board, opponent)

        # Sprawdzenie, czy to koniec gry
        if depth <= 0 or (not ai_moves and not opponent_moves):
            self.stats.evaluated_states += 1
            return self.evaluate_terminal_or_heuristic(board, ai_player)

        valid_moves = self.engine.get_valid_moves(board, current_player)

        # jeśli gracz nie ma ruchu, oddaje ture
        if not valid_moves:
            next_player = get_opponent(current_player)

            return self.minimax(
                board=board,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                current_player=next_player,
                ai_player=ai_player
            )

        ordered_moves = self.order_moves(valid_moves)

        if current_player == ai_player:
            # FAZA MAX: AI chce maksymalizować swój wynik
            best_score = -inf

            for move in ordered_moves:
                next_state = self.engine.apply_move(
                    GameState(board=board, current_player=current_player),
                    move
                )

                score = self.minimax(
                    board=next_state.board,
                    depth=depth - 1,
                    alpha=alpha,
                    beta=beta,
                    current_player=next_state.current_player,
                    ai_player=ai_player
                )

                best_score = max(best_score, score)
                alpha = max(alpha, best_score)

                # --- ODCIĘCIE ALFA-BETA ---
                # Jeśli wynik w tej gałęzi jest gorszy niż to, co przeciwnik nam dał wcześniej, przestajemy szukać w tej gałęzi
                if beta <= alpha:
                    self.stats.alpha_beta_cutoffs += 1
                    break

            return int(best_score)

        # FAZA MIN: symlujemy optymalną grę przeciwnika (chce minimalizować wynik AI)
        best_score = inf

        for move in ordered_moves:
            next_state = self.engine.apply_move(
                GameState(board=board, current_player=current_player),
                move
            )

            score = self.minimax(
                board=next_state.board,
                depth=depth - 1,
                alpha=alpha,
                beta=beta,
                current_player=next_state.current_player,
                ai_player=ai_player
            )

            best_score = min(best_score, score)
            beta = min(beta, best_score)

            if beta <= alpha:
                self.stats.alpha_beta_cutoffs += 1
                break

        return int(best_score)

    """
    --- LOGIKA DECYZYJNA: KONIEC GRY VS PRZYSZŁOŚĆ ---
    Funkcja decyduje, czy ocenić planszę jako koniec gry, czy za pomocą heurystyki
    """
    def evaluate_terminal_or_heuristic(
        self,
        board: list[list[int]],
        ai_player: int
    ) -> int:
        ai_valid_moves = self.engine.get_valid_moves(board, ai_player)
        opponent_valid_moves = self.engine.get_valid_moves(board, get_opponent(ai_player))

        # jeżeli żaden gracz nie ma ruchu to gra się kończy
        if not ai_valid_moves and not opponent_valid_moves:
            return self.evaluate_final_position(board, ai_player)

        # w przeciwnym wypadku używamy ocen strategicznych
        return self.evaluator.evaluate_board(board, ai_player)


    """
    Ocena stanu końcowego.
    Liczymy kto faktycznie wygrał, zwracamy bardzo wysoki wynik (WIN_SCORE) lub bardzo niski (LOSS_SCORE)
    """
    def evaluate_final_position(
        self,
        board: list[list[int]],
        ai_player: int
    ) -> int:
        black_count, white_count = count_discs(board)

        if ai_player == BLACK:
            ai_count = black_count
            opponent_count = white_count
        else:
            ai_count = white_count
            opponent_count = black_count

        disc_difference = ai_count - opponent_count

        # Zwycięstwo: dodajemy przewagę pionków do miliona, by preferować wygrane większą różnicą
        if disc_difference > 0:
            return self.WIN_SCORE + disc_difference

        # Porażka: analogicznie odejmujemy różnicę od minus miliona
        if disc_difference < 0:
            return self.LOSS_SCORE + disc_difference

        return 0

    """
    --- OPTYMALIZACJA WYDAJNOŚCI - przegrupowanie ruchów ---
    Kluczowe dla efektywności Alfa-Beta. Jeśli najpierw sprawdzimy 
    najbardziej obiecujące ruchy (np. rogi), algorytm szybciej odetnie gorsze gałęzie.
    """
    def order_moves(self, moves: list[Move]) -> list[Move]:
        corners = {
            (0, 0),
            (0, 7),
            (7, 0),
            (7, 7),
        }
        # sortujemy, tak aby rogi miały priorytet 0 (były na początku listy)
        return sorted(
            moves,
            key=lambda move: 0 if (move.row, move.col) in corners else 1
        )

    # --- INTERFEJS UŻYTKOWNIKA ---
    def build_result_explanation(
        self,
        result: MinimaxResult,
        depth: int
    ) -> str:
        if result.move is None:
            move_text = "brak legalnego ruchu"
        else:
            move_text = move_to_notation(result.move.row, result.move.col)

        return (
            "Decyzja AI — Minimax alfa-beta\n"
            "==============================\n\n"
            f"Najlepszy ruch: {move_text}\n"
            f"Głębokość przeszukiwania: {depth}\n"
            f"Ocena ruchu: {result.score}\n\n"
            "Statystyki:\n"
            f"Ocenione stany: {result.stats.evaluated_states}\n"
            f"Odcięcia alfa-beta: {result.stats.alpha_beta_cutoffs}\n"
            f"Czas decyzji: {result.stats.search_time_seconds:.4f} s\n\n"
            "Interpretacja:\n"
            "Minimax zakłada optymalną grę obu stron.\n"
            "Odcięcia alfa-beta pomijają gałęzie, które nie mogą poprawić wyniku."
        )