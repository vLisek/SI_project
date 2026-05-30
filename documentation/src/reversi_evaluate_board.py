def evaluate_board(self, board: list[list[int]], ai_player: int) -> int:
    components = self.evaluate_components(board, ai_player)

    return (
        self.CORNER_WEIGHT * components["corner_score"]
        + self.MOBILITY_WEIGHT * components["mobility_score"]
        + self.POSITIONAL_WEIGHT * components["positional_score"]
        + self.DISC_DIFFERENCE_WEIGHT * components["disc_difference"]
        - self.RISKY_SQUARE_WEIGHT * components["risky_square_penalty"]
    )