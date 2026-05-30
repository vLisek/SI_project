def find_optimal_move(self, piles: list[int]) -> Move:
    nim_sum = self.engine.calculate_nim_sum(piles)

    if nim_sum == 0:
        return self.find_fallback_move(piles)

    for index, pile in enumerate(piles):
        target = pile ^ nim_sum

        if target < pile:
            amount = pile - target
            return Move(index, amount)

    return self.find_fallback_move(piles)