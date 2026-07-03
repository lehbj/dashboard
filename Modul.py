from typing import Optional

from Pruefung import Pruefung


class Modul:
    def __init__(self, kuerzel: str, name: str, etcs: int) -> None:
        self._kuerzel: str = kuerzel
        self._name: str = name
        self._etcs: int = etcs
        self._pruefung: Optional[Pruefung] = None  # Komposition

    @property
    def kuerzel(self) -> str:
        return self._kuerzel

    @property
    def name(self) -> str:
        return self._name

    @property
    def etcs(self) -> int:
        return self._etcs

    @property
    def pruefung(self) -> Optional[Pruefung]:
        return self._pruefung

    @kuerzel.setter
    def kuerzel(self, kuerzel: str) -> None:
        self._kuerzel = kuerzel

    def pruefung_hinzufuegen(self, pruefung: Pruefung) -> None:
        """Weist dem Modul eine Prüfung zu"""
        self._pruefung = pruefung

    def pruefung_entfernen(self) -> None:
        """Entfernt die Prüfung des Moduls."""
        self._pruefung = None

    def get_note(self) -> Optional[float]:
        """Gibt die Note zurück, oder None wenn keine Prüfung vorhanden."""
        if self._pruefung is None:
            return None
        return self._pruefung.note

    def ist_bewertet(self) -> bool:
        """True, wenn es eine Prüfung mit Ergebnis gibt."""
        return self._pruefung is not None

    def ist_bestanden(self) -> bool:
        """Modul gilt als bestanden, wenn die Note besser als 4,0 ist."""
        if self.ist_bewertet():
            return self.get_note() <= 4.0
        return False

    def __repr__(self) -> str:
        return (
            f'[{self.kuerzel}] {self._name} ({self._etcs} ETCS) Note: {self.get_note()}, Bestanden: {self.ist_bestanden()}'
        )
