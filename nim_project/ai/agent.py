from logic.engine import NimEngine
from models.move import Move


class NimAI:
    def __init__(self):
        self.engine = NimEngine()

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

    def find_fallback_move(self, piles: list[int]) -> Move:
        for index, pile in enumerate(piles):
            if pile > 0:
                return Move(index, 1)

        raise ValueError("Brak możliwych ruchów.")

    def explain_move(self, piles_before: list[int], move: Move) -> str:
        nim_sum_before = self.engine.calculate_nim_sum(piles_before)

        piles_after = piles_before.copy()
        pile_before = piles_before[move.pile_index]
        pile_after = pile_before - move.amount
        piles_after[move.pile_index] = pile_after

        nim_sum_after = self.engine.calculate_nim_sum(piles_after)

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

    def get_binary_width(self, piles: list[int]) -> int:
        max_value = max(piles) if piles else 0
        return max(1, max_value.bit_length())