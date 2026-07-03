from datetime import date


class StudiumService:
    def __init__(self, studium) -> None:
        self._studium = studium

    def tage_uebrig_berechnen(self) -> int:
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
