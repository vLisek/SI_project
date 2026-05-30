from reversi_project.gui.app import ReversiApp

"""
PLIK: main.py
OPIS: Główny plik uruchamiający aplikację gry Reversi.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten plik jest punktem startowym programu.

Nie zawiera logiki gry, algorytmu AI ani kodu odpowiedzialnego za reguły Reversi.
Jego zadaniem jest utworzenie obiektu aplikacji GUI oraz uruchomienie
głównej pętli programu.

MECHANIZMY:
1. Import klasy ReversiApp z modułu GUI
2. Utworzenie aplikacji
3. Uruchomienie głównej pętli Tkinter
"""


def main():
    """
    --- PUNKT STARTOWY PROGRAMU ---
    Tworzy instancję aplikacji ReversiApp i uruchamia jej główną pętlę.
    """
    app = ReversiApp()
    app.run()


if __name__ == "__main__":
    main()