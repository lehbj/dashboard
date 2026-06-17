import sqlite3
from typing import Optional, Any

from Studium import Studium
from Semester import Semester
from Modul import Modul
from Pruefung import Pruefung


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

    def naechste_id_finden(self, tabelle: str) -> int:
        """
        Findet die höchste id einer Tabelle und gibt diese+1 zurück
        Falls die Tabelle noch leer ist, wird 1 zurückgegeben
        """
        with self._connection:
            id = self._connection.execute(f'SELECT seq + 1 AS id FROM sqlite_sequence WHERE name = "{tabelle}";').fetchone()
            if id is not None:
                return id['id']
            return 1


    def studium_laden(self) -> Optional[Studium]:
        with self._connection:
            return self._connection.execute('SELECT * FROM studium').fetchone()

    def studium_erstellen(self, studium: Studium) -> None:
        with self._connection:
            self._connection.execute(f'INSERT INTO studium (studiengang, hochschule, start_datum, geplantes_end_datum) VALUES ("{studium.studiengang}", "{studium.hochschule}", "{studium.start_datum}", "{studium.geplantes_end_datum}");')

    def studium_aendern(self, studium: Studium) -> None:
        with self._connection:
            self._connection.execute(f'UPDATE studium SET studiengang="{studium.studiengang}", hochschule="{studium.hochschule}", start_datum="{studium.start_datum}", geplantes_end_datum="{studium.geplantes_end_datum}" WHERE id = {studium.id};')

    def semester_laden(self) -> Optional[list[Semester]]:
        with self._connection:
            return self._connection.execute('SELECT * FROM semester').fetchall()

    def semester_erstellen(self, studium: Studium, semester: Semester) -> None:
        with self._connection:
            self._connection.execute(f'INSERT INTO semester (studium_id, nummer) VALUES ("{studium.id}", "{semester.nummer}");')

    def semester_loeschen(self, nummer: int) -> None:
        with self._connection:
            self._connection.execute(f'DELETE FROM semester WHERE nummer = "{nummer}";')

    def modul_laden(self, semester: Semester) -> Optional[list[Modul]]:
        with self._connection:
            return self._connection.execute(f'SELECT * FROM modul WHERE semester_id = "{semester.id}"').fetchall()

    def modul_erstellen(self, semester: Semester, modul: Modul) -> None:
        with self._connection:
            self._connection.execute(f'INSERT INTO modul (semester_id, kuerzel, name, etcs) VALUES ("{semester.id}", "{modul.kuerzel}", "{modul.name}", "{modul.etcs}");')

    def modul_loeschen(self, modul: Modul) -> None:
        with self._connection:
            self._connection.execute(f'DELETE FROM modul WHERE id = "{modul.id}";')

    def pruefung_hinzufuegen(self, modul: Modul, pruefung: Pruefung) -> None:
        with self._connection:
            self._connection.execute(f'INSERT INTO pruefung (modul_id, note) VALUES ("{modul.id}", "{pruefung.note}");')

    def pruefung_laden(self, modul: Modul) -> list[Pruefung]:
        with self._connection:
            return self._connection.execute(f'SELECT * FROM pruefung WHERE modul_id = "{modul.id}"').fetchall()

    def pruefung_loeschen(self, modul: Modul) -> None:
        with self._connection:
            self._connection.execute(f'DELETE FROM pruefung WHERE modul_id = "{modul.id}";')