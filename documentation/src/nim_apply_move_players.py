next_player = game_state.current_player

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