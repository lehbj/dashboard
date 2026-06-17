from datetime import date
from typing import Optional

from Semester import Semester
from Modul import Modul


class Studium:
    def __init__(self, id: int, studiengang: str, hochschule: str, start_datum: date, geplantes_end_datum: date) -> None:
        self._id: int = id
        self._studiengang: str = studiengang
        self._hochschule: str = hochschule
        self._start_datum: date = start_datum
        self._geplantes_end_datum: date = geplantes_end_datum
        self._semester: list[Semester] = []  # Komposition

    @property
    def semester(self) -> list[Semester]:
        return list(self._semester)

    @property
    def id(self) -> int:
        return self._id

    @property
    def studiengang(self) -> str:
        return self._studiengang

    @studiengang.setter
    def studiengang(self, studiengang: str) -> None:
        self._studiengang = studiengang

    @property
    def hochschule(self) -> str:
        return self._hochschule

    @hochschule.setter
    def hochschule(self, hochschule: str) -> None:
        self._hochschule = hochschule

    @property
    def start_datum(self) -> date:
        return self._start_datum

    @start_datum.setter
    def start_datum(self, start_datum: date) -> None:
        self._start_datum = start_datum

    @property
    def geplantes_end_datum(self) -> date:
        return self._geplantes_end_datum

    @geplantes_end_datum.setter
    def geplantes_end_datum(self, geplantes_end_datum: date) -> None:
        self._geplantes_end_datum = geplantes_end_datum

    def semester_hinzufuegen(self, semester: Semester) -> None:
        self._semester.append(semester)

    def semester_entfernen(self, nummer: int) -> None:
        self._semester = [s for s in self._semester if s.nummer != nummer]

    def get_semester(self, nummer: int) -> Optional[Semester]:
        """Gibt ein Semester anhand der Nummer zurück"""
        for semester in self._semester:
            if semester.nummer == nummer:
                return semester
        return None

    def get_gesamten_durchschnitt(self) -> None | float:
        """
        Berechnet den Gesamtdurchschnitt
        Gibt None zurück, wenn noch keine Note vorhanden ist
        """
        alle_noten = []
        for semester in self._semester:
            for modul in semester.module:
                note = modul.get_note()
                if note is not None:
                    alle_noten.append(note)
        if not alle_noten:
            return None
        return round(sum(alle_noten) / len(alle_noten), 2)

    def get_modul(self, kuerzel: str) -> Optional[tuple[Semester, Modul]]:
        """
        Durchsucht alle Semester nach einem Modul mit dem gegebenen Kürze
        Gibt ein Tupel (Semester, Modul) zurück, oder None, wenn nicht gefunden
        """
        for semester in self._semester:
            modul = semester.get_modul(kuerzel)
            if modul is not None:
                return (semester, modul)
        return None

    def __repr__(self) -> str:
        start_datum = self._start_datum.strftime('%d.%m.%Y')
        end_datum = self._geplantes_end_datum.strftime('%d.%m.%Y')
        tage_uebrig = (self._geplantes_end_datum - date.today()).days

        return (
            f'Studiengang: {self._studiengang}\n'
            f'Hochschule: {self._hochschule}\n'
            f'Beginn: {start_datum}, '
            f'Geplantes Ende: {end_datum} '
            f'(noch {tage_uebrig} Tage)'
        )