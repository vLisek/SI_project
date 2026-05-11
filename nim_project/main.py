from gui.app import NimApp

"""
PLIK: main.py
OPIS: Główny plik uruchamiający aplikację gry Nim.
-------------------------------------------------------------
ZASTOSOWANIE:
Ten plik jest punktem startowym programu.

Nie zawiera logiki gry ani algorytmu AI.
Jego zadaniem jest utworzenie obiektu aplikacji GUI oraz uruchomienie
głównej pętli programu.

MECHANIZMY:
1. Import klasy NimApp z modułu GUI
2. Utworzenie aplikacji
3. Uruchomienie głównej pętli Tkinter
"""


def main():
    """
    --- PUNKT STARTOWY PROGRAMU ---
    Tworzy instancję aplikacji NimApp i uruchamia jej główną pętlę.
    """
    app = NimApp()
    app.run()


if __name__ == "__main__":
    main()