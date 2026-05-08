import time
from dataclasses import dataclass
from math import inf
from typing import Optional

from ai.evaluation import ReversiEvaluator
from logic.board import BLACK, count_discs, get_opponent, move_to_notation
from logic.engine import ReversiEngine
from models.game_state import GameState
from models.move import Move


@dataclass
class MinimaxStats:
    evaluated_states: int = 0
    alpha_beta_cutoffs: int = 0
    search_time_seconds: float = 0.0


@dataclass
class MinimaxResult:
    move: Optional[Move]
    score: int
    stats: MinimaxStats


class ReversiAI:
    WIN_SCORE = 1_000_000
    LOSS_SCORE = -1_000_000

    def __init__(self):
        self.engine = ReversiEngine()
        self.evaluator = ReversiEvaluator()
        self.stats = MinimaxStats()

    def choose_best_move(
        self,
        board: list[list[int]],
        current_player: int,
        ai_player: int,
        depth: int
    ) -> MinimaxResult:
        start_time = time.perf_counter()

        self.stats = MinimaxStats()

        valid_moves = self.engine.get_valid_moves(board, current_player)

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

        if current_player == ai_player:
            best_score = -inf

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

        if depth <= 0 or (not ai_moves and not opponent_moves):
            self.stats.evaluated_states += 1
            return self.evaluate_terminal_or_heuristic(board, ai_player)

        valid_moves = self.engine.get_valid_moves(board, current_player)

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

                if beta <= alpha:
                    self.stats.alpha_beta_cutoffs += 1
                    break

            return int(best_score)

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

    def evaluate_terminal_or_heuristic(
        self,
        board: list[list[int]],
        ai_player: int
    ) -> int:
        ai_valid_moves = self.engine.get_valid_moves(board, ai_player)
        opponent_valid_moves = self.engine.get_valid_moves(board, get_opponent(ai_player))

        if not ai_valid_moves and not opponent_valid_moves:
            return self.evaluate_final_position(board, ai_player)

        return self.evaluator.evaluate_board(board, ai_player)

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

        if disc_difference > 0:
            return self.WIN_SCORE + disc_difference

        if disc_difference < 0:
            return self.LOSS_SCORE + disc_difference

        return 0

    def order_moves(self, moves: list[Move]) -> list[Move]:
        corners = {
            (0, 0),
            (0, 7),
            (7, 0),
            (7, 7),
        }

        return sorted(
            moves,
            key=lambda move: 0 if (move.row, move.col) in corners else 1
        )

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