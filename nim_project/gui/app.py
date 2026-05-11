import tkinter as tk
from typing import Optional

from nim_project.ai.agent import NimAI
from nim_project.logic.engine import NimEngine
from nim_project.models.game_state import GameState
from nim_project.models.move import Move

"""
PLIK: app.py
OPIS: Interfejs graficzny gry Nim.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten plik odpowiada za warstwę wizualną aplikacji.

GUI umożliwia rozpoczęcie gry, wybór ruchu przez kliknięcie patyczków,
wyświetlanie aktualnego stanu stert, historii ruchów oraz wyjaśnień AI.

Logika zasad gry i decyzje AI nie są implementowane bezpośrednio w tym pliku.
GUI korzysta z klas NimEngine oraz NimAI, dzięki czemu interfejs jest oddzielony
od właściwej logiki gry.

MECHANIZMY:
1. Budowanie ekranu startowego
2. Rysowanie stert i obsługa kliknięć użytkownika
3. Wywoływanie ruchu AI
4. Wyświetlanie statusu gry
5. Obsługa paneli informacyjnych w sidebarze
"""

class NimApp:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Gra Nim — człowiek vs AI")
        self.root.geometry("1450x900")
        self.root.minsize(1150, 720)
        self.root.configure(bg="#f3f1ed")

        self.engine = NimEngine()
        self.ai = NimAI()

        self.game_state: Optional[GameState] = None
        self.initial_piles: list[int] = []
        self.last_explanation = ""
        self.move_history: list[str] = []

        self.selected_pile_index: Optional[int] = None
        self.selected_stick_indexes: set[int] = set()

        self.ai_thinking = False
        self.ai_after_id: Optional[str] = None

        self.initial_piles_entry: Optional[tk.Entry] = None
        self.start_error_label: Optional[tk.Label] = None
        self.status_label: Optional[tk.Label] = None
        self.board_frame: Optional[tk.Frame] = None
        self.selection_label: Optional[tk.Label] = None
        self.execute_button: Optional[tk.Button] = None

        self.show_start_screen()

    def run(self):
        self.root.mainloop()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_start_screen(self):
        self.cancel_pending_ai_move()
        self.clear_window()

        container = tk.Frame(self.root, bg="#f3f1ed")
        container.pack(fill="both", expand=True)

        card = tk.Frame(
            container,
            bg="#fffaf3",
            padx=46,
            pady=40
        )
        card.place(relx=0.5, rely=0.5, anchor="center")

        title = tk.Label(
            card,
            text="Gra Nim",
            font=("Arial", 30, "bold"),
            bg="#fffaf3",
            fg="#2b2118"
        )
        title.pack(pady=(0, 8))

        subtitle = tk.Label(
            card,
            text="Człowiek vs AI",
            font=("Arial", 15),
            bg="#fffaf3",
            fg="#6b5542"
        )
        subtitle.pack(pady=(0, 24))

        info = tk.Label(
            card,
            text="Podaj początkowe sterty oddzielone spacją:",
            font=("Arial", 12),
            bg="#fffaf3",
            fg="#2b2118"
        )
        info.pack()

        self.initial_piles_entry = tk.Entry(
            card,
            font=("Arial", 17),
            justify="center",
            width=24,
            bd=1,
            relief="solid"
        )
        self.initial_piles_entry.insert(0, "3 4 5")
        self.initial_piles_entry.pack(pady=(14, 8), ipady=7)

        self.start_error_label = tk.Label(
            card,
            text="",
            font=("Arial", 11, "bold"),
            bg="#fffaf3",
            fg="#a12b2b",
            wraplength=420,
            justify="center"
        )
        self.start_error_label.pack(pady=(0, 10))

        start_button = tk.Button(
            card,
            text="Rozpocznij grę",
            font=("Arial", 13, "bold"),
            bg="#8b5e34",
            fg="white",
            activebackground="#714a27",
            activeforeground="white",
            bd=0,
            padx=24,
            pady=11,
            command=self.start_game
        )
        start_button.pack(pady=(6, 12))

        example = tk.Label(
            card,
            text="Przykłady: 3 4 5   |   1 2 3   |   7 5 3 1",
            font=("Arial", 10),
            bg="#fffaf3",
            fg="#8c7a68"
        )
        example.pack()

    def parse_initial_piles(self) -> list[int]:
        if self.initial_piles_entry is None:
            raise ValueError("Brak pola wejściowego.")

        user_input = self.initial_piles_entry.get().strip()

        if user_input == "":
            return [3, 4, 5]

        try:
            piles = [int(value) for value in user_input.split()]
        except ValueError:
            raise ValueError("Podaj tylko liczby całkowite oddzielone spacją.")

        if len(piles) < 2:
            raise ValueError("Gra powinna mieć co najmniej dwie sterty.")

        if any(pile < 0 for pile in piles):
            raise ValueError("Liczba żetonów nie może być ujemna.")

        if all(pile == 0 for pile in piles):
            raise ValueError("Przynajmniej jedna sterta musi mieć żetony.")

        return piles

    def start_game(self):
        try:
            piles = self.parse_initial_piles()
        except ValueError as error:
            if self.start_error_label is not None:
                self.start_error_label.config(
                    text=f"Błąd: {error}",
                    fg="#a12b2b"
                )
            return

        if self.start_error_label is not None:
            self.start_error_label.config(text="")

        self.game_state = GameState(
            piles=piles,
            current_player="human"
        )

        self.initial_piles = piles.copy()
        self.move_history = []
        self.last_explanation = self.build_initial_explanation(piles)
        self.selected_pile_index = None
        self.selected_stick_indexes = set()
        self.ai_thinking = False

        self.show_game_screen()



    def reset_current_game(self):
        self.cancel_pending_ai_move()

        if not self.initial_piles:
            self.show_start_screen()
            return

        piles = self.initial_piles.copy()

        self.game_state = GameState(
            piles=piles,
            current_player="human"
        )

        self.move_history = []
        self.last_explanation = self.build_initial_explanation(piles)
        self.selected_pile_index = None
        self.selected_stick_indexes = set()
        self.ai_thinking = False

        self.render_game()

    def build_initial_explanation(self, piles: list[int]) -> str:
        nim_sum = self.engine.calculate_nim_sum(piles)

        if nim_sum == 0:
            return (
                f"Początkowy stan stert: {piles}\n"
                f"Początkowy Nim-Sum: {nim_sum}\n\n"
                "Pozycja początkowa jest przegrywająca dla gracza rozpoczynającego,\n"
                "jeżeli przeciwnik będzie grał optymalnie."
            )

        return (
            f"Początkowy stan stert: {piles}\n"
            f"Początkowy Nim-Sum: {nim_sum}\n\n"
            "Pozycja początkowa jest wygrywająca dla gracza rozpoczynającego\n"
            "przy optymalnej grze."
        )

    def show_game_screen(self):
        self.clear_window()

        main_container = tk.Frame(self.root, bg="#f3f1ed")
        main_container.pack(fill="both", expand=True)

        sidebar = tk.Frame(main_container, bg="#2b2118", width=235)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        content = tk.Frame(main_container, bg="#f3f1ed", padx=42, pady=34)
        content.pack(side="right", fill="both", expand=True)

        sidebar_title = tk.Label(
            sidebar,
            text="NIM",
            font=("Arial", 24, "bold"),
            bg="#2b2118",
            fg="#f7eee3"
        )
        sidebar_title.pack(pady=(34, 8))

        sidebar_subtitle = tk.Label(
            sidebar,
            text="człowiek vs AI",
            font=("Arial", 10),
            bg="#2b2118",
            fg="#c9b8a5"
        )
        sidebar_subtitle.pack(pady=(0, 28))

        self.create_sidebar_button(sidebar, "Wyjaśnienie AI", self.show_explanation_dialog)
        self.create_sidebar_button(sidebar, "Historia ruchów", self.show_history_dialog)
        self.create_sidebar_button(sidebar, "Zasady i algorytm", self.show_rules_dialog)
        self.create_sidebar_button(sidebar, "Reset gry", self.reset_current_game)

        hint = tk.Label(
            sidebar,
            text=(
                "Kliknij konkretne\n"
                "patyczki w jednej\n"
                "stercie.\n\n"
                "Zaznaczone patyczki\n"
                "zostaną zabrane po\n"
                "kliknięciu przycisku."
            ),
            font=("Arial", 10),
            bg="#2b2118",
            fg="#d7c7b5",
            justify="left"
        )
        hint.pack(side="bottom", anchor="w", padx=22, pady=28)

        header = tk.Frame(content, bg="#f3f1ed")
        header.pack(fill="x", pady=(0, 18))

        title = tk.Label(
            header,
            text="Gra Nim",
            font=("Arial", 32, "bold"),
            bg="#f3f1ed",
            fg="#2b2118"
        )
        title.pack(side="left")

        self.status_label = tk.Label(
            content,
            text="",
            font=("Arial", 14, "bold"),
            bg="#f3f1ed",
            fg="#2b2118",
            anchor="w",
            justify="left",
            padx=18,
            pady=12
        )
        self.status_label.pack(fill="x", pady=(0, 8))

        self.board_frame = tk.Frame(content, bg="#f3f1ed")
        self.board_frame.pack(fill="both", expand=True, pady=(8, 0))

        bottom_bar = tk.Frame(content, bg="#f3f1ed")
        bottom_bar.pack(fill="x", pady=(22, 0))

        self.selection_label = tk.Label(
            bottom_bar,
            text="Zaznacz patyczki, które chcesz zabrać.",
            font=("Arial", 14),
            bg="#f3f1ed",
            fg="#4f4033",
            anchor="w"
        )
        self.selection_label.pack(side="left", fill="x", expand=True)

        self.execute_button = tk.Button(
            bottom_bar,
            text="Wykonaj ruch",
            font=("Arial", 14, "bold"),
            bg="#8b5e34",
            fg="white",
            activebackground="#714a27",
            activeforeground="white",
            bd=0,
            padx=28,
            pady=13,
            command=self.handle_human_move
        )
        self.execute_button.pack(side="right")

        self.render_game()

    def create_sidebar_button(self, parent: tk.Frame, text: str, command):
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            bg="#403126",
            fg="#f7eee3",
            activebackground="#5a4434",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=13,
            command=command
        )
        button.pack(fill="x", padx=18, pady=6)

    def render_game(self):
        if self.game_state is None:
            return

        self.render_status()
        self.render_piles()
        self.render_selection_state()
        self.update_execute_button_state()

    def render_status(self):
        if self.game_state is None or self.status_label is None:
            return

        if self.game_state.game_over:
            if self.game_state.winner == "human":
                status_text = (
                    "Koniec gry - wygrał człowiek.\n"
                    "Ostatni żeton został zabrany przez gracza."
                )
                bg_color = "#e4f8df"
                fg_color = "#247a38"
            else:
                status_text = (
                    "Koniec gry - wygrała AI.\n"
                    "Ostatni żeton został zabrany przez komputer."
                )
                bg_color = "#fde2e2"
                fg_color = "#a12b2b"

            self.status_label.config(
                text=status_text,
                bg=bg_color,
                fg=fg_color
            )
            return

        if self.ai_thinking:
            self.status_label.config(
                text=(
                    "Ruch wykonuje AI...\n"
                    "Komputer analizuje aktualny układ stert."
                ),
                bg="#fff3cd",
                fg="#7a4f00"
            )
            return

        nim_sum = self.engine.calculate_nim_sum(self.game_state.piles)

        if nim_sum == 0:
            status_text = (
                "Ocena pozycji: PRZEGRYWAJĄCA dla gracza wykonującego ruch.\n"
                f"Suma Nim, czyli XOR wszystkich stert = {nim_sum}. "
                "Przy optymalnej grze przeciwnika nie istnieje ruch gwarantujący wygraną."
            )
            bg_color = "#fde2e2"
            fg_color = "#a12b2b"
        else:
            status_text = (
                "Ocena pozycji: WYGRYWAJĄCA dla gracza wykonującego ruch.\n"
                f"Suma Nim, czyli XOR wszystkich stert = {nim_sum}. "
                "Istnieje ruch, który sprowadza pozycję do XOR = 0."
            )
            bg_color = "#e4f8df"
            fg_color = "#247a38"

        self.status_label.config(
            text=status_text,
            bg=bg_color,
            fg=fg_color
        )

    def render_piles(self):
        if self.game_state is None or self.board_frame is None:
            return

        for widget in self.board_frame.winfo_children():
            widget.destroy()

        for pile_index, pile_size in enumerate(self.game_state.piles):
            row = tk.Frame(self.board_frame, bg="#f3f1ed", height=132)
            row.pack(fill="x", pady=12)
            row.pack_propagate(False)

            label = tk.Label(
                row,
                text=f"Sterta {pile_index + 1}",
                font=("Arial", 24, "bold"),
                bg="#f3f1ed",
                fg="#2b2118",
                width=9,
                anchor="w"
            )
            label.pack(side="left", fill="y", padx=(0, 16))

            canvas = tk.Canvas(
                row,
                height=132,
                bg="#f3f1ed",
                highlightthickness=0,
                bd=0
            )
            canvas.pack(side="left", fill="x", expand=True)

            canvas.bind(
                "<Configure>",
                lambda event, c=canvas, p=pile_index, s=pile_size: self.draw_pile(c, p, s)
            )

            canvas.bind(
                "<Button-1>",
                lambda event, c=canvas, p=pile_index, s=pile_size: self.handle_stick_click(event, c, p, s)
            )

    def get_stick_positions(self, canvas_width: int, pile_size: int) -> list[float]:
        if pile_size <= 0:
            return []

        if pile_size == 1:
            return [canvas_width / 2]

        max_spacing = 46
        min_spacing = 22
        available_width = max(160, canvas_width - 120)

        spacing = min(max_spacing, available_width / max(1, pile_size - 1))
        spacing = max(min_spacing, spacing)

        total_width = spacing * (pile_size - 1)
        start_x = (canvas_width - total_width) / 2

        return [start_x + index * spacing for index in range(pile_size)]

    def draw_pile(self, canvas: tk.Canvas, pile_index: int, pile_size: int):
        canvas.delete("all")

        canvas_width = max(canvas.winfo_width(), 600)
        canvas_height = int(canvas["height"])

        if pile_size <= 0:
            canvas.create_text(
                canvas_width / 2,
                canvas_height / 2,
                text="—",
                font=("Arial", 28),
                fill="#b9aa99"
            )
            return

        positions = self.get_stick_positions(canvas_width, pile_size)

        baseline_y = canvas_height - 24
        top_y = 28

        for stick_index, x in enumerate(positions):
            is_selected = (
                self.selected_pile_index == pile_index
                and stick_index in self.selected_stick_indexes
            )

            stick_color = "#2d89ef" if is_selected else "#9b6a3e"
            shadow_color = "#d8c7b5"

            canvas.create_line(
                x + 3,
                top_y + 4,
                x + 3,
                baseline_y + 4,
                width=13,
                fill=shadow_color,
                capstyle=tk.ROUND
            )

            canvas.create_line(
                x,
                top_y,
                x,
                baseline_y,
                width=13,
                fill=stick_color,
                capstyle=tk.ROUND
            )

            canvas.create_oval(
                x - 5,
                top_y + 7,
                x + 5,
                top_y + 17,
                fill="#f1d29a" if not is_selected else "#bcd8ff",
                outline=""
            )

    def handle_stick_click(self, event: tk.Event, canvas: tk.Canvas, pile_index: int, pile_size: int):
        if self.game_state is None or self.game_state.game_over or self.ai_thinking:
            return

        if pile_size <= 0:
            return

        positions = self.get_stick_positions(max(canvas.winfo_width(), 600), pile_size)

        closest_index = min(
            range(len(positions)),
            key=lambda index: abs(positions[index] - event.x)
        )

        max_click_distance = 24

        if abs(positions[closest_index] - event.x) > max_click_distance:
            return

        self.toggle_stick_selection(pile_index, closest_index)

    def toggle_stick_selection(self, pile_index: int, stick_index: int):
        if self.selected_pile_index != pile_index:
            self.selected_pile_index = pile_index
            self.selected_stick_indexes = {stick_index}
        else:
            if stick_index in self.selected_stick_indexes:
                self.selected_stick_indexes.remove(stick_index)

                if not self.selected_stick_indexes:
                    self.selected_pile_index = None
            else:
                self.selected_stick_indexes.add(stick_index)

        self.render_game()

    def render_selection_state(self):
        if self.selection_label is None or self.game_state is None:
            return

        if self.game_state.game_over:
            self.selection_label.config(
                text="Gra zakończona."
            )
            return

        if self.ai_thinking:
            self.selection_label.config(
                text="AI wykonuje swój ruch..."
            )
            return

        selected_amount = len(self.selected_stick_indexes)

        if self.selected_pile_index is None or selected_amount == 0:
            self.selection_label.config(
                text="Zaznacz patyczki, które chcesz zabrać."
            )
            return

        self.selection_label.config(
            text=(
                f"Wybrany ruch: sterta {self.selected_pile_index + 1}, "
                f"do zabrania: {selected_amount}"
            )
        )

    def update_execute_button_state(self):
        if self.execute_button is None or self.game_state is None:
            return

        if self.game_state.game_over:
            self.execute_button.config(
                text="Nowa gra",
                state="normal",
                command=self.show_start_screen,
                bg="#8b5e34",
                fg="white"
            )
            return

        if self.ai_thinking:
            self.execute_button.config(
                text="AI wykonuje ruch...",
                state="disabled",
                command=self.handle_human_move,
                bg="#b8a99a",
                fg="white"
            )
            return

        self.execute_button.config(
            text="Wykonaj ruch",
            command=self.handle_human_move,
            bg="#8b5e34",
            fg="white"
        )

        if self.selected_pile_index is None or len(self.selected_stick_indexes) == 0:
            self.execute_button.config(state="disabled")
            return

        self.execute_button.config(state="normal")

    def handle_human_move(self):
        if self.game_state is None or self.game_state.game_over or self.ai_thinking:
            return

        selected_amount = len(self.selected_stick_indexes)

        if self.selected_pile_index is None or selected_amount == 0:
            return

        human_move = Move(
            pile_index=self.selected_pile_index,
            amount=selected_amount
        )

        if not self.engine.is_valid_move(self.game_state.piles, human_move):
            return

        piles_before_human_move = self.game_state.piles.copy()
        self.game_state = self.engine.apply_move(self.game_state, human_move)

        self.move_history.append(
            f"Gracz: sterta {human_move.pile_index + 1}, zabrano {human_move.amount}\n"
            f"{piles_before_human_move} → {self.game_state.piles}"
        )

        self.last_explanation = (
            f"Ruch gracza\n"
            f"===========\n\n"
            f"Wybrana sterta: {human_move.pile_index + 1}\n"
            f"Liczba zabranych żetonów: {human_move.amount}\n"
            f"Stan po ruchu gracza: {self.game_state.piles}"
        )

        self.selected_pile_index = None
        self.selected_stick_indexes = set()

        if self.game_state.game_over:
            self.render_game()
            return

        self.ai_thinking = True
        self.render_game()
        self.ai_after_id = self.root.after(1200, self.perform_ai_move)

    def perform_ai_move(self):
        self.ai_after_id = None

        if self.game_state is None or self.game_state.game_over:
            self.ai_thinking = False
            self.render_game()
            return

        piles_before_ai_move = self.game_state.piles.copy()

        ai_move = self.ai.find_optimal_move(self.game_state.piles)
        self.last_explanation = self.ai.explain_move(piles_before_ai_move, ai_move)
        self.game_state = self.engine.apply_move(self.game_state, ai_move)

        self.move_history.append(
            f"AI: sterta {ai_move.pile_index + 1}, zabrano {ai_move.amount}\n"
            f"{piles_before_ai_move} → {self.game_state.piles}"
        )

        self.ai_thinking = False
        self.render_game()

    def cancel_pending_ai_move(self):
        if self.ai_after_id is not None:
            try:
                self.root.after_cancel(self.ai_after_id)
            except tk.TclError:
                pass

            self.ai_after_id = None

        self.ai_thinking = False

    def show_explanation_dialog(self):
        content = self.last_explanation if self.last_explanation else "Brak wyjaśnienia."
        self.open_text_dialog("Wyjaśnienie AI", content)

    def show_history_dialog(self):
        if self.move_history:
            content = "\n\n".join(
                f"{index + 1}. {entry}" for index, entry in enumerate(self.move_history)
            )
        else:
            content = "Brak wykonanych ruchów."

        self.open_text_dialog("Historia ruchów", content)

    def show_rules_dialog(self):
        content = (
            "Gra Nim — zasady i algorytm AI\n"
            "================================\n\n"
            "Zasady gry:\n"
            "- Gra składa się z kilku stert żetonów.\n"
            "- Gracz w swojej turze wybiera dokładnie jedną stertę.\n"
            "- Z wybranej sterty zabiera co najmniej jeden żeton.\n"
            "- Można zabrać dowolną liczbę żetonów, ale tylko z jednej sterty.\n"
            "- W wariancie normalnym wygrywa gracz, który zabierze ostatni żeton.\n\n"
            "Obsługa GUI:\n"
            "- Kliknij konkretne patyczki w jednej stercie.\n"
            "- Każdy zaznaczony patyczek oznacza jeden żeton do zabrania.\n"
            "- Kliknięcie zaznaczonego patyczka odznacza go.\n"
            "- Kliknięcie patyczka w innej stercie czyści poprzedni wybór.\n"
            "- Następnie kliknij „Wykonaj ruch”.\n\n"
            "Algorytm AI:\n"
            "- AI nie używa minimaxa.\n"
            "- Wykorzystuje własność gry Nim opartą o operację XOR.\n"
            "- Obliczana jest wartość Nim-Sum.\n"
            "- Jeśli Nim-Sum != 0, AI znajduje ruch, który sprowadza Nim-Sum do 0.\n"
            "- Dzięki temu przeciwnik dostaje pozycję przegrywającą przy optymalnej grze."
        )

        self.open_text_dialog("Zasady i algorytm", content)

    def open_text_dialog(self, title: str, content: str):
        dialog = tk.Toplevel(self.root)
        dialog.title(title)
        dialog.geometry("760x520")
        dialog.minsize(600, 420)
        dialog.configure(bg="#fffaf3")

        text_area = tk.Text(
            dialog,
            font=("Consolas", 11),
            wrap="word",
            padx=15,
            pady=15,
            bg="#fffaf3",
            fg="#2b2118",
            bd=0
        )
        text_area.pack(fill="both", expand=True)

        text_area.insert("1.0", content)
        text_area.config(state="disabled")

        close_button = tk.Button(
            dialog,
            text="Zamknij",
            font=("Arial", 11),
            bg="#8b5e34",
            fg="white",
            activebackground="#714a27",
            activeforeground="white",
            bd=0,
            padx=18,
            pady=8,
            command=dialog.destroy
        )
        close_button.pack(pady=10)