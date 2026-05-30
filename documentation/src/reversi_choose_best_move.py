best_move = None
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