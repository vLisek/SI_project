def calculate_nim_sum(self, piles: list[int]) -> int:
    nim_sum = 0

    for pile in piles:
        nim_sum ^= pile

    return nim_sum