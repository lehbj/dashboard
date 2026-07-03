from datetime import date
from rich.console import Console

from Datenbank import Datenbank
from Konsole import Konsole, studium_erstellen
from Modul import Modul
from Pruefung import Pruefung
from Semester import Semester
from Studium import Studium
from StudiumService import StudiumService


def studium_laden_oder_erstellen() -> Studium:
    """
    In der Datenbank wird nach einem Studium gesucht.
    Wenn keines gefunden wird, wird der Benutzer dazu aufgefordert, ein neues zu erstellen,
    wenn in der Datenbank bereits existiert wird daraus ein Studium-Objekt erstellt.
    """
    with Datenbank() as db:
        ergebnis = db.read_one(query='SELECT * FROM studium')

    if ergebnis is None:
        # Kein Studium in der Datenbank gefunden, neues erstellen
        return studium_erstellen()

    # Bestehendes Studium aus der Datenbank laden
    return Studium(studiengang=ergebnis['studiengang'], hochschule=ergebnis['hochschule'], start_datum=date.strptime(ergebnis['start_datum'], '%Y-%m-%d'), geplantes_end_datum=date.strptime(ergebnis['geplantes_end_datum'], '%Y-%m-%d'))

def main():
    studium = studium_laden_oder_erstellen()
    service = StudiumService(studium=studium)
    konsole = Konsole(console=Console(), studium=studium, service=service)

    # Semester aus Datenbank laden und zu Studium hinzufügen (Komposition)
    with Datenbank() as db:
        semesters = db.read_all(query='SELECT * FROM semester ORDER BY nummer')
        if semesters is not None:
            for semester in semesters:
                neues_semester = Semester(nummer=semester['nummer'])
                studium.semester_hinzufuegen(semester=neues_semester)

                # Module aus Datenbank laden und zu Semester hinzufügen (Komposition)
                with Datenbank() as db2:
                    module = db2.read_all(query=f'SELECT * FROM modul WHERE semester_id = (SELECT id FROM semester WHERE nummer = {neues_semester.nummer})')
                    if module is not None:
                        for modul in module:
                            neues_modul = Modul(kuerzel=modul['kuerzel'], name=modul['name'], etcs=modul['etcs'])
                            neues_semester.modul_hinzufuegen(modul=neues_modul)

                            # Prüfungen aus Datenbank laden und zu Modul zuweisen (Aggregation)
                            with Datenbank() as db3:
                                pruefungen = db3.read_all(query=f'SELECT * FROM pruefung WHERE modul_id = (SELECT id FROM modul WHERE kuerzel = "{neues_modul.kuerzel}")')
                                if pruefungen is not None:
                                    for pruefung in pruefungen:
                                        neue_pruefung = Pruefung(note=pruefung['note'])
                                        neues_modul.pruefung_hinzufuegen(pruefung=neue_pruefung)

    konsole.menu()


if __name__ == '__main__':
    main()
