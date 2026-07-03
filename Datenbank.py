import sqlite3

from Studium import Studium


class Datenbank:
    def __init__(self, pfad: str='dashboard.db') -> None:
        self._pfad = pfad
        self._connection: sqlite3.Connection = sqlite3.connect(pfad)
        self._connection.row_factory = sqlite3.Row  # Zugriff per Spaltenname
        self._connection.execute('PRAGMA foreign_keys = ON')  # Fremdschlüssel aktivieren
        self._tabellen_erstellen()

    def __enter__(self) -> Datenbank:
        return self

    def __exit__(self, *args) -> None:
        self._connection.close()

    def _tabellen_erstellen(self) -> None:
        """Erstellt Tabellen in Datenbank, falls diese noch nicht existieren"""
        with self._connection:
            self._connection.executescript('CREATE TABLE IF NOT EXISTS studium(id INTEGER PRIMARY KEY AUTOINCREMENT, studiengang TEXT NOT NULL, hochschule TEXT NOT NULL, start_datum date NOT NULL, geplantes_end_datum date NOT NULL);')
            self._connection.executescript('CREATE TABLE IF NOT EXISTS semester (id INTEGER PRIMARY KEY AUTOINCREMENT, studium_id INTEGER NOT NULL, nummer INTEGER NOT NULL, FOREIGN KEY (studium_id) REFERENCES studium(id) ON DELETE CASCADE);')
            self._connection.executescript('CREATE TABLE IF NOT EXISTS modul (id INTEGER PRIMARY KEY AUTOINCREMENT, semester_id INTEGER NOT NULL, kuerzel TEXT NOT NULL, name TEXT NOT NULL, etcs INTEGER NOT NULL, FOREIGN KEY (semester_id) REFERENCES semester(id) ON DELETE CASCADE);')
            self._connection.executescript('CREATE TABLE IF NOT EXISTS pruefung (id INTEGER PRIMARY KEY AUTOINCREMENT, modul_id INTEGER NOT NULL UNIQUE, note FLOAT(1,2) NOT NULL, FOREIGN KEY (modul_id) REFERENCES modul(id) ON DELETE CASCADE);')


    def read_one(self, query: str) -> sqlite3.Row | None:
        """Erhält eine SQL-Query als string und gibt ein oder kein Ergebnis zurück"""
        return self._connection.execute(query).fetchone()

    def read_all(self, query: str) -> list[sqlite3.Row] | None:
        """Erhält eine SQL-Query als string und gibt eine Liste von Ergebnissen oder gar keines zurück."""
        return self._connection.execute(query).fetchall()

    def write(self, query: str) -> None:
        """
        Erhält eine SQL-Query und führt diese aus.
        Dient nur zu Schreib-Zwecken, ein Ergebnis wird nie zurückgegeben.
        """
        with self._connection:
            self._connection.execute(query)

    def studium_aendern(self, studium: Studium) -> None:
        """
        Speichert Studium-Objekt in der Datenbank.
        Extra-Methode, weil es mehrere Aufrufe gibt.
        """
        self.write(f'UPDATE studium SET studiengang="{studium.studiengang}", hochschule="{studium.hochschule}", start_datum="{studium.start_datum}", geplantes_end_datum="{studium.geplantes_end_datum}";')