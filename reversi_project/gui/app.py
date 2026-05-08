import tkinter as tk
from typing import Optional

from ai.agent import ReversiAI
from logic.board import (
    BLACK,
    BOARD_SIZE,
    WHITE,
    count_discs,
    create_initial_board,
    move_to_notation,
)
from logic.engine import ReversiEngine
from models.game_state import GameState
from models.move import Move


class ReversiApp:
    DEPTH_OPTIONS = {
        "Łatwy - głębokość 2": 2,
        "Średni - głębokość 3": 3,
        "Trudny - głębokość 4": 4,
    }

    HINT_LIMITS = {
        "Łatwy - głębokość 2": 1,
        "Średni - głębokość 3": 3,
        "Trudny - głębokość 4": 5,
    }

    CELL_SIZE = 78
    BOARD_PIXEL_SIZE = BOARD_SIZE * CELL_SIZE

    LEFT_LABEL_SPACE = 44
    TOP_LABEL_SPACE = 36
    OUTER_PADDING = 12

    CANVAS_WIDTH = LEFT_LABEL_SPACE + BOARD_PIXEL_SIZE + OUTER_PADDING
    CANVAS_HEIGHT = TOP_LABEL_SPACE + BOARD_PIXEL_SIZE + OUTER_PADDING

    BOARD_X0 = LEFT_LABEL_SPACE
    BOARD_Y0 = TOP_LABEL_SPACE

    DARK_GREEN = "#2e7d32"
    LIGHT_GREEN = "#49a84d"
    HINT_COLOR = "#f9c74f"
    GRID_COLOR = "#1b5e20"
    BG_COLOR = "#f3f1ed"
    SIDEBAR_COLOR = "#1f2933"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Reversi - człowiek vs AI")
        self.root.geometry("1420x920")
        self.root.minsize(1220, 820)
        self.root.configure(bg=self.BG_COLOR)

        self.engine = ReversiEngine()
        self.ai = ReversiAI()

        self.human_player = BLACK
        self.ai_player = WHITE

        self.game_state = GameState(
            board=create_initial_board(),
            current_player=BLACK
        )

        self.ai_thinking = False
        self.ai_after_id: Optional[str] = None

        self.last_ai_explanation = "AI nie wykonała jeszcze ruchu."
        self.move_history: list[str] = []

        self.depth_var = tk.StringVar(value="Średni - głębokość 3")

        self.hints_remaining = self.get_hint_limit()
        self.hint_move: Optional[Move] = None
        self.hint_button: Optional[tk.Button] = None

        self.status_label: Optional[tk.Label] = None
        self.black_score_canvas: Optional[tk.Canvas] = None
        self.white_score_canvas: Optional[tk.Canvas] = None
        self.board_canvas: Optional[tk.Canvas] = None

        self.show_game_screen()

    def run(self):
        self.root.mainloop()

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_game_screen(self):
        self.clear_window()

        main_container = tk.Frame(self.root, bg=self.BG_COLOR)
        main_container.pack(fill="both", expand=True)

        sidebar = tk.Frame(main_container, bg=self.SIDEBAR_COLOR, width=260)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        content = tk.Frame(main_container, bg=self.BG_COLOR, padx=28, pady=24)
        content.pack(side="right", fill="both", expand=True)

        self.build_sidebar(sidebar)
        self.build_content(content)

        self.render_game()

    def build_sidebar(self, sidebar: tk.Frame):
        title = tk.Label(
            sidebar,
            text="REVERSI",
            font=("Arial", 24, "bold"),
            bg=self.SIDEBAR_COLOR,
            fg="white"
        )
        title.pack(pady=(32, 6))

        subtitle = tk.Label(
            sidebar,
            text="Minimax + alfa-beta",
            font=("Arial", 10),
            bg=self.SIDEBAR_COLOR,
            fg="#cfd8e3"
        )
        subtitle.pack(pady=(0, 26))

        difficulty_label = tk.Label(
            sidebar,
            text="Poziom AI",
            font=("Arial", 11, "bold"),
            bg=self.SIDEBAR_COLOR,
            fg="white"
        )
        difficulty_label.pack(anchor="w", padx=20, pady=(0, 6))

        difficulty_menu = tk.OptionMenu(
            sidebar,
            self.depth_var,
            *self.DEPTH_OPTIONS.keys(),
            command=self.handle_difficulty_change
        )
        difficulty_menu.config(
            font=("Arial", 10),
            bg="#32414b",
            fg="white",
            activebackground="#3f505c",
            activeforeground="white",
            relief="flat",
            bd=0,
            highlightthickness=0
        )
        difficulty_menu["menu"].config(bg="white", fg="black")
        difficulty_menu.pack(fill="x", padx=18, pady=(0, 20))

        self.hint_button = self.create_sidebar_button(
            sidebar,
            self.get_hint_button_text(),
            self.show_hint
        )

        self.create_sidebar_button(sidebar, "Analiza AI", self.show_ai_explanation)
        self.create_sidebar_button(sidebar, "Historia ruchów", self.show_move_history)
        self.create_sidebar_button(sidebar, "Zasady i algorytm", self.show_rules)
        self.create_sidebar_button(sidebar, "Reset gry", self.reset_game)

        hint = tk.Label(
            sidebar,
            text=(
                "Jak grać?\n\n"
                "Kliknij dostępne pole\n"
                "na planszy.\n\n"
                "Żółte pole oznacza\n"
                "aktywną podpowiedź."
            ),
            font=("Arial", 10),
            bg=self.SIDEBAR_COLOR,
            fg="#cfd8e3",
            justify="left"
        )
        hint.pack(side="bottom", anchor="w", padx=22, pady=28)

    def build_content(self, content: tk.Frame):
        header = tk.Frame(content, bg=self.BG_COLOR)
        header.pack(fill="x", pady=(0, 18))

        title = tk.Label(
            header,
            text="Reversi",
            font=("Arial", 32, "bold"),
            bg=self.BG_COLOR,
            fg="#1f2933"
        )
        title.pack(side="left")

        self.status_label = tk.Label(
            content,
            text="",
            font=("Arial", 14, "bold"),
            bg=self.BG_COLOR,
            fg="#1f2933",
            anchor="w",
            justify="left",
            padx=16,
            pady=12
        )
        self.status_label.pack(fill="x", pady=(0, 16))

        board_holder = tk.Frame(content, bg=self.BG_COLOR)
        board_holder.pack(fill="both", expand=True)

        board_row = tk.Frame(board_holder, bg=self.BG_COLOR)
        board_row.pack(expand=True)

        self.black_score_canvas = tk.Canvas(
            board_row,
            width=100,
            height=185,
            bg=self.BG_COLOR,
            highlightthickness=0,
            bd=0
        )
        self.black_score_canvas.pack(side="left", padx=(0, 26))

        self.board_canvas = tk.Canvas(
            board_row,
            width=self.CANVAS_WIDTH,
            height=self.CANVAS_HEIGHT,
            bg=self.BG_COLOR,
            highlightthickness=0,
            bd=0
        )
        self.board_canvas.pack(side="left")
        self.board_canvas.bind("<Button-1>", self.handle_board_click)

        self.white_score_canvas = tk.Canvas(
            board_row,
            width=100,
            height=185,
            bg=self.BG_COLOR,
            highlightthickness=0,
            bd=0
        )
        self.white_score_canvas.pack(side="left", padx=(26, 0))

    def create_sidebar_button(self, parent: tk.Frame, text: str, command) -> tk.Button:
        button = tk.Button(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            bg="#32414b",
            fg="white",
            activebackground="#3f505c",
            activeforeground="white",
            relief="flat",
            bd=0,
            padx=12,
            pady=13,
            command=command
        )
        button.pack(fill="x", padx=18, pady=6)

        return button

    def render_game(self):
        self.render_status()
        self.redraw_board()
        self.update_hint_button()

    def render_status(self):
        black_count, white_count = count_discs(self.game_state.board)
        self.render_side_scores(black_count, white_count)

        if self.status_label is None:
            return

        if self.game_state.game_over:
            if self.game_state.winner is None:
                status = "Koniec gry - remis."
                bg_color = "#fff3cd"
                fg_color = "#7a4f00"
            elif self.game_state.winner == self.human_player:
                status = "Koniec gry - wygrał gracz."
                bg_color = "#e4f8df"
                fg_color = "#247a38"
            else:
                status = "Koniec gry - wygrała AI."
                bg_color = "#fde2e2"
                fg_color = "#a12b2b"

            self.status_label.config(
                text=status + "\nKliknij „Reset gry”, aby rozpocząć ponownie.",
                bg=bg_color,
                fg=fg_color
            )
            return

        if self.ai_thinking:
            self.status_label.config(
                text="Ruch wykonuje AI - komputer analizuje planszę.",
                bg="#fff3cd",
                fg="#7a4f00"
            )
            return

        if self.hint_move is not None:
            self.hint_button.config(state="disabled")
            return

        if self.game_state.current_player == self.human_player:
            self.status_label.config(
                text="Ruch gracza - wybierz jedno z możliwych pól na planszy.",
                bg="#e4f8df",
                fg="#247a38"
            )
            return

    def render_side_scores(self, black_count: int, white_count: int):
        if self.black_score_canvas is not None:
            self.black_score_canvas.delete("all")

            self.black_score_canvas.create_oval(
                20,
                16,
                80,
                76,
                fill="#111111",
                outline="#000000",
                width=2
            )

            self.black_score_canvas.create_text(
                50,
                46,
                text="TY",
                font=("Arial", 12, "bold"),
                fill="white"
            )

            self.black_score_canvas.create_text(
                50,
                126,
                text=str(black_count),
                font=("Arial", 32, "bold"),
                fill="#1f2933"
            )

        if self.white_score_canvas is not None:
            self.white_score_canvas.delete("all")

            self.white_score_canvas.create_oval(
                20,
                16,
                80,
                76,
                fill="#f8f8f8",
                outline="#d0d0d0",
                width=2
            )

            self.white_score_canvas.create_text(
                50,
                46,
                text="AI",
                font=("Arial", 12, "bold"),
                fill="#1f2933"
            )

            self.white_score_canvas.create_text(
                50,
                126,
                text=str(white_count),
                font=("Arial", 32, "bold"),
                fill="#1f2933"
            )

    def redraw_board(self):
        if self.board_canvas is None:
            return

        canvas = self.board_canvas
        canvas.delete("all")

        valid_positions = set()

        if (
            not self.game_state.game_over
            and not self.ai_thinking
            and self.game_state.current_player == self.human_player
        ):
            valid_moves = self.engine.get_valid_moves(
                self.game_state.board,
                self.human_player
            )
            valid_positions = {(move.row, move.col) for move in valid_moves}

        self.draw_labels(canvas)
        self.draw_cells(canvas, valid_positions)
        self.draw_grid(canvas)
        self.draw_discs(canvas)

    def draw_labels(self, canvas: tk.Canvas):
        for col in range(BOARD_SIZE):
            x = self.BOARD_X0 + col * self.CELL_SIZE + self.CELL_SIZE / 2
            y = self.TOP_LABEL_SPACE / 2

            canvas.create_text(
                x,
                y,
                text=chr(ord("A") + col),
                font=("Arial", 15, "bold"),
                fill="#1f2933"
            )

        for row in range(BOARD_SIZE):
            x = self.LEFT_LABEL_SPACE / 2
            y = self.BOARD_Y0 + row * self.CELL_SIZE + self.CELL_SIZE / 2

            canvas.create_text(
                x,
                y,
                text=str(row + 1),
                font=("Arial", 15, "bold"),
                fill="#1f2933"
            )

    def draw_cells(self, canvas: tk.Canvas, valid_positions: set[tuple[int, int]]):
        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                x1 = self.BOARD_X0 + col * self.CELL_SIZE
                y1 = self.BOARD_Y0 + row * self.CELL_SIZE
                x2 = x1 + self.CELL_SIZE
                y2 = y1 + self.CELL_SIZE

                is_hint_field = (
                    self.hint_move is not None
                    and self.hint_move.row == row
                    and self.hint_move.col == col
                )

                if is_hint_field:
                    fill_color = self.HINT_COLOR
                elif (row, col) in valid_positions:
                    fill_color = self.LIGHT_GREEN
                else:
                    fill_color = self.DARK_GREEN

                canvas.create_rectangle(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill_color,
                    outline=""
                )

    def draw_grid(self, canvas: tk.Canvas):
        x0 = self.BOARD_X0
        y0 = self.BOARD_Y0
        x1 = x0 + self.BOARD_PIXEL_SIZE
        y1 = y0 + self.BOARD_PIXEL_SIZE

        canvas.create_rectangle(
            x0,
            y0,
            x1,
            y1,
            outline=self.GRID_COLOR,
            width=5
        )

        for index in range(1, BOARD_SIZE):
            x = x0 + index * self.CELL_SIZE
            y = y0 + index * self.CELL_SIZE

            canvas.create_line(
                x,
                y0,
                x,
                y1,
                fill=self.GRID_COLOR,
                width=2
            )

            canvas.create_line(
                x0,
                y,
                x1,
                y,
                fill=self.GRID_COLOR,
                width=2
            )

    def draw_discs(self, canvas: tk.Canvas):
        padding = 10

        for row in range(BOARD_SIZE):
            for col in range(BOARD_SIZE):
                cell_value = self.game_state.board[row][col]

                if cell_value == 0:
                    continue

                x1 = self.BOARD_X0 + col * self.CELL_SIZE + padding
                y1 = self.BOARD_Y0 + row * self.CELL_SIZE + padding
                x2 = self.BOARD_X0 + (col + 1) * self.CELL_SIZE - padding
                y2 = self.BOARD_Y0 + (row + 1) * self.CELL_SIZE - padding

                if cell_value == BLACK:
                    fill_color = "#111111"
                    outline_color = "#000000"
                elif cell_value == WHITE:
                    fill_color = "#f8f8f8"
                    outline_color = "#d9d9d9"
                else:
                    continue

                canvas.create_oval(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill=fill_color,
                    outline=outline_color,
                    width=2
                )

    def handle_board_click(self, event: tk.Event):
        if self.game_state.game_over or self.ai_thinking:
            return

        if self.game_state.current_player != self.human_player:
            return

        row, col = self.pixel_to_board_position(event.x, event.y)

        if row is None or col is None:
            return

        move = Move(row, col)

        if not self.engine.is_valid_move(
            self.game_state.board,
            move,
            self.human_player
        ):
            return

        self.hint_move = None

        self.game_state = self.engine.apply_move(self.game_state, move)
        self.move_history.append(f"Gracz: {move_to_notation(row, col)}")

        if self.game_state.game_over:
            self.render_game()
            return

        if self.game_state.current_player == self.ai_player:
            self.ai_thinking = True
            self.render_game()
            self.ai_after_id = self.root.after(700, self.perform_ai_move)
        else:
            self.move_history.append(
                "AI: brak legalnego ruchu - ruch został pominięty."
            )
            self.render_game()

    def pixel_to_board_position(self, x: int, y: int) -> tuple[Optional[int], Optional[int]]:
        board_x = x - self.BOARD_X0
        board_y = y - self.BOARD_Y0

        if board_x < 0 or board_y < 0:
            return None, None

        col = board_x // self.CELL_SIZE
        row = board_y // self.CELL_SIZE

        if not (0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE):
            return None, None

        return int(row), int(col)

    def perform_ai_move(self):
        self.ai_after_id = None

        if self.game_state.game_over:
            self.ai_thinking = False
            self.render_game()
            return

        if self.game_state.current_player != self.ai_player:
            self.ai_thinking = False
            self.render_game()
            return

        depth = self.get_selected_depth()

        result = self.ai.choose_best_move(
            board=self.game_state.board,
            current_player=self.ai_player,
            ai_player=self.ai_player,
            depth=depth
        )

        self.last_ai_explanation = self.ai.build_result_explanation(result, depth)

        if result.move is None:
            self.move_history.append(
                "AI: brak legalnego ruchu - ruch został pominięty."
            )

            self.game_state = self.engine.create_next_state(
                self.game_state.board,
                self.ai_player
            )

            self.ai_thinking = False
            self.render_game()
            return

        notation = move_to_notation(result.move.row, result.move.col)

        self.game_state = self.engine.apply_move(self.game_state, result.move)

        self.move_history.append(
            f"AI: {notation} | ocena: {result.score} | "
            f"stany: {result.stats.evaluated_states} | "
            f"odcięcia: {result.stats.alpha_beta_cutoffs} | "
            f"czas: {result.stats.search_time_seconds:.3f}s"
        )

        if (
            not self.game_state.game_over
            and self.game_state.current_player == self.ai_player
        ):
            self.move_history.append(
                "Gracz: brak legalnego ruchu - ruch został pominięty."
            )

            self.render_game()
            self.ai_after_id = self.root.after(700, self.perform_ai_move)
            return

        self.ai_thinking = False
        self.render_game()

    def get_selected_depth(self) -> int:
        return self.DEPTH_OPTIONS.get(self.depth_var.get(), 3)

    def get_hint_limit(self) -> int:
        return self.HINT_LIMITS.get(self.depth_var.get(), 3)

    def get_hint_button_text(self) -> str:
        return f"Podpowiedź ({self.hints_remaining})"

    def update_hint_button(self):
        if self.hint_button is None:
            return

        self.hint_button.config(text=self.get_hint_button_text())

        if self.game_state.game_over:
            self.hint_button.config(state="disabled")
            return

        if self.ai_thinking:
            self.hint_button.config(state="disabled")
            return

        if self.game_state.current_player != self.human_player:
            self.hint_button.config(state="disabled")
            return

        if self.hints_remaining <= 0:
            self.hint_button.config(state="disabled")
            return

        valid_moves = self.engine.get_valid_moves(
            self.game_state.board,
            self.human_player
        )

        if not valid_moves:
            self.hint_button.config(state="disabled")
            return

        self.hint_button.config(state="normal")

    def show_hint(self):
        if self.game_state.game_over:
            return

        if self.ai_thinking:
            return

        if self.game_state.current_player != self.human_player:
            return

        if self.hint_move is not None:
            return

        if self.hints_remaining <= 0:
            return

        valid_moves = self.engine.get_valid_moves(
            self.game_state.board,
            self.human_player
        )

        if not valid_moves:
            return

        depth = self.get_selected_depth()

        result = self.ai.choose_best_move(
            board=self.game_state.board,
            current_player=self.human_player,
            ai_player=self.human_player,
            depth=depth
        )

        if result.move is None:
            return

        self.hint_move = result.move
        self.hints_remaining -= 1

        notation = move_to_notation(result.move.row, result.move.col)

        self.last_ai_explanation = (
            "Podpowiedź dla gracza - Minimax alfa-beta\n"
            "=======================================\n\n"
            f"Sugerowany ruch: {notation}\n"
            f"Głębokość analizy: {depth}\n"
            f"Ocena ruchu: {result.score}\n\n"
            "Statystyki:\n"
            f"Ocenione stany: {result.stats.evaluated_states}\n"
            f"Odcięcia alfa-beta: {result.stats.alpha_beta_cutoffs}\n"
            f"Czas decyzji: {result.stats.search_time_seconds:.4f} s\n\n"
            "Interpretacja:\n"
            "Podpowiedź została wyznaczona tym samym algorytmem Minimax alfa-beta, "
            "ale z perspektywy gracza."
        )

        self.render_game()

    def handle_difficulty_change(self, _selected_value=None):
        self.reset_game()

    def reset_game(self):
        if self.ai_after_id is not None:
            try:
                self.root.after_cancel(self.ai_after_id)
            except tk.TclError:
                pass

            self.ai_after_id = None

        self.game_state = GameState(
            board=create_initial_board(),
            current_player=BLACK
        )

        self.ai_thinking = False
        self.last_ai_explanation = "AI nie wykonała jeszcze ruchu."
        self.move_history = []

        self.hints_remaining = self.get_hint_limit()
        self.hint_move = None

        self.render_game()

    def show_ai_explanation(self):
        self.open_text_dialog("Analiza AI", self.last_ai_explanation)

    def show_move_history(self):
        if not self.move_history:
            content = "Brak wykonanych ruchów."
        else:
            content = "\n\n".join(
                f"{index + 1}. {entry}"
                for index, entry in enumerate(self.move_history)
            )

        self.open_text_dialog("Historia ruchów", content)

    def show_rules(self):
        content = (
            "Reversi - zasady i algorytm AI\n"
            "===============================\n\n"
            "Zasady gry:\n"
            "- Plansza ma rozmiar 8x8.\n"
            "- Gracz i AI wykonują ruchy naprzemiennie.\n"
            "- Legalny ruch musi odwrócić co najmniej jeden pionek przeciwnika.\n"
            "- Pionki są odwracane w 8 kierunkach.\n"
            "- Jeśli gracz nie ma legalnego ruchu, traci turę.\n"
            "- Gra kończy się, gdy plansza jest pełna albo żaden gracz nie ma ruchu.\n"
            "- Wygrywa strona z większą liczbą pionków.\n\n"
            "Algorytm AI:\n"
            "- AI wykorzystuje Minimax z odcięciami alfa-beta.\n"
            "- Minimax zakłada optymalną grę obu stron.\n"
            "- Alfa-beta ogranicza liczbę analizowanych stanów bez zmiany wyniku.\n\n"
            "Heurystyka oceny planszy uwzględnia:\n"
            "- rogi,\n"
            "- mobilność,\n"
            "- macierz pozycyjną,\n"
            "- różnicę pionków,\n"
            "- karę za pola ryzykowne obok pustych rogów.\n\n"
            "Podpowiedzi:\n"
            "- Przycisk „Podpowiedź” wskazuje sugerowany ruch gracza.\n"
            "- Podpowiedź jest liczona tym samym algorytmem Minimax alfa-beta.\n"
            "- Liczba podpowiedzi zależy od poziomu trudności:\n"
            "  * Łatwy: 1 podpowiedź,\n"
            "  * Średni: 3 podpowiedzi,\n"
            "  * Trudny: 5 podpowiedzi."
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
            fg="#1f2933",
            bd=0
        )
        text_area.pack(fill="both", expand=True)

        text_area.insert("1.0", content)
        text_area.config(state="disabled")

        close_button = tk.Button(
            dialog,
            text="Zamknij",
            font=("Arial", 11),
            bg="#32414b",
            fg="white",
            activebackground="#3f505c",
            activeforeground="white",
            bd=0,
            padx=18,
            pady=8,
            command=dialog.destroy
        )
        close_button.pack(pady=10)