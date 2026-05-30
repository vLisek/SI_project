if current_player == ai_player:
    best_score = -inf

    for move in self.order_moves(valid_moves):
        next_state = self.engine.apply_move(
            GameState(board=board, current_player=current_player),
            move
        )

        score = self.minimax(
            next_state.board,
            depth - 1,
            alpha,
            beta,
            next_state.current_player,
            ai_player
        )

        best_score = max(best_score, score)
        alpha = max(alpha, best_score)

        if beta <= alpha:
            self.stats.alpha_beta_cutoffs += 1
            break

    return int(best_score)

best_score = inf

for move in self.order_moves(valid_moves):
    next_state = self.engine.apply_move(
        GameState(board=board, current_player=current_player),
        move
    )

    score = self.minimax(
        next_state.board,
        depth - 1,
        alpha,
        beta,
        next_state.current_player,
        ai_player
    )

    best_score = min(best_score, score)
    beta = min(beta, best_score)

    if beta <= alpha:
        self.stats.alpha_beta_cutoffs += 1
        break

return int(best_score)