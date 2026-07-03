from datetime import date

from Datenbank import Datenbank


class StudiumService:
    def __init__(self, studium) -> None:
        self._studium = studium

    def tage_uebrig_berechnen(self) -> int:
        """Berechnet die Anzahl der noch verbleibenden Tage bis zum geplanten Abschluss des Studiums."""
        return (self._studium.geplantes_end_datum - date.today()).days

    def gesamten_notendurchschnitt_berechnen(self) -> float | None:
        """
        Berechnet den Gesamtdurchschnitt.
        Gibt None zurück, wenn noch keine Note vorhanden ist.
        """
        alle_noten = []
        for semester in self._studium.semester:
            for modul in semester.module:
                note = modul.get_note()
                if note is not None:
                    alle_noten.append(note)
        if not alle_noten:
            return None
        return round(sum(alle_noten) / len(alle_noten), 2)

    def datum_formatieren(self, datum: date) -> str:
        return datum.strftime('%d.%m.%Y')

    def studium_speichern(self) -> None:
        """Speichert Studium-Objekt in der Datenbank."""
        with Datenbank() as db:
            db.write(
                query=f'UPDATE studium SET studiengang="{self._studium.studiengang}", hochschule="{self._studium.hochschule}", start_datum="{self._studium.start_datum}", geplantes_end_datum="{self._studium.geplantes_end_datum}";')
