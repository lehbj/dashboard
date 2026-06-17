from typing import Optional

from Modul import Modul


class Semester:
    def __init__(self, id: int, nummer: int):
        self._id: int = id
        self._nummer: int = nummer
        self._module: list[Modul] = [] # Komposition

    @property
    def id(self) -> int:
        return self._id

    @property
    def nummer(self) -> int:
        return self._nummer

    @property
    def module(self) -> list[Modul]:
        return list(self._module)

    def modul_hinzufuegen(self, modul: Modul) -> None:
        """Fügt ein Modul zum Semester hinzu"""
        self._module.append(modul)

    def modul_entfernen(self, kuerzel: str) -> None:
        """Entfernt ein Modul anhand des Kürzels"""
        self._module = [m for m in self._module if m.kuerzel != kuerzel]

    def get_noten_durchschnitt(self) -> Optional[float]:
        """
        Berechnet den Notendurchschnitt aller bewerteten Module
        Gibt None zurück, wenn noch kein Modul bewertet wurde
        """
        noten = [m.get_note() for m in self._module if m.ist_bewertet()]
        if not noten:
            return None
        return round(sum(noten) / len(noten), 2)

    def get_modul(self, kuerzel: str) -> Optional[Modul]:
        """Sucht ein Modul nach Kürzel und gibt es zurück"""
        for modul in self._module:
            if modul.kuerzel == kuerzel:
                return modul
        return None

    def __repr__(self) -> str:
        return (
            f'Semester {self._nummer}: '
            f'({len(self._module)} Module) '
            f'Durchschnitt: {self.get_noten_durchschnitt()}'
        )