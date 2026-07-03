from datetime import date
import sys

from Studium import Studium
from Semester import Semester
from Modul import Modul
from Pruefung import Pruefung
from Datenbank import Datenbank
from Diagramm import Diagramm


def clear():
    """Leert das Konsolenfenster."""
    sys.stdout.write('\033[2J\033[H') # ANSI-Escape-Code zum Bildschirm leeren und Cursor an den Anfang setzen
    sys.stdout.flush()

def moduluebersicht(studium: Studium):
    """Gibt alle Module des übergebenen Studium-Objektes nach Semester sortiert aus."""
    clear()
    for semester in studium.semester:
        print(f'Semester {semester.nummer}:')
        for modul in semester.module:
            print(modul)


def studium_laden_oder_erstellen() -> Studium:
    """
    In der Datenbank wird nach einem Studium gesucht.
    Wenn keines gefunden wird, wird der Benutzer dazu aufgefordert, ein neues zu erstellen,
    wenn in der Datenbank bereits existiert wird daraus ein Studium-Objekt erstellt.
    """
    with Datenbank() as db:
        ergebnis = db.read_one(query='SELECT * FROM studium')

    # Kein Studium in der Datenbank gefunden, neues erstellen
    if ergebnis is None:
        studiengang = input('Kein Studium gefunden. Um ein neues zu erstellen, Name des Studienganges eingeben: ')
        hochschule = input('Hochschule: ')

        while True:
            start_datum = input('Startdatum (TT.MM.JJJJ): ')
            try:
                start_datum = date.strptime(start_datum, '%d.%m.%Y')
                break
            except ValueError:
                print('Ungültiges Datum.')

        while True:
            geplantes_end_datum = input('Geplantes Enddatum (TT.MM.JJJJ): ')
            try:
                geplantes_end_datum = date.strptime(geplantes_end_datum, '%d.%m.%Y')
                break
            except ValueError:
                print('Ungültiges Datum.')

        # Studium erstellen
        studium = Studium(studiengang=studiengang, hochschule=hochschule, start_datum=start_datum, geplantes_end_datum=geplantes_end_datum)
        with Datenbank() as db:
            db.write(query=f'INSERT INTO studium (studiengang, hochschule, start_datum, geplantes_end_datum) VALUES ("{studium.studiengang}", "{studium.hochschule}", "{studium.start_datum}", "{studium.geplantes_end_datum}");')
        return studium

    # Bestehendes Studium aus der Datenbank laden
    return Studium(studiengang=ergebnis['studiengang'], hochschule=ergebnis['hochschule'], start_datum=date.strptime(ergebnis['start_datum'], '%Y-%m-%d'), geplantes_end_datum=date.strptime(ergebnis['geplantes_end_datum'], '%Y-%m-%d'))


def studiengang_aendern(studium: Studium):
    """Der Benutzer kann durch die Eingabeaufforderung den Namen des Studienganges ändern."""
    clear()
    studiengang = input('Name des neuen Studienganges: ')

    studium.studiengang = studiengang
    input(f'Studiengang zu "{studiengang}" geändert. [OK]')

    # Änderung in Datenbank speichern
    with Datenbank() as db:
        db.studium_aendern(studium)


def hochschule_aendern(studium: Studium):
    """Der Benutzer kann durch die Eingabeaufforderung den Namen der Hochschule ändern."""
    clear()
    hochschule = input('Name der neuen Hochschule: ')

    studium.hochschule = hochschule
    input(f'Hochschule zu "{hochschule}" geändert. [OK]')

    # Änderung in Datenbank speichern
    with Datenbank() as db:
        db.studium_aendern(studium)


def startdatum_aendern(studium: Studium):
    """Der Benutzer kann durch die Eingabeaufforderung das Startdatum des Studiums ändern."""
    clear()
    start_datum = input('Neues Startdatum eingeben (TT.MM.JJJJ): ')

    try:
        start_datum = date.strptime(start_datum, '%d.%m.%Y')
    except ValueError:
        input('Ungültiges Datum. [OK]')
        return

    studium.start_datum = start_datum
    input(f'Startdatum zum {start_datum.strftime('%d.%m.%Y')} geändert. [OK]')

    # Änderung in Datenbank speichern
    with Datenbank() as db:
        db.studium_aendern(studium)


def enddatum_aendern(studium: Studium):
    """Der Benutzer kann durch die Eingabeaufforderung das geplante Enddatum des Studiums ändern."""
    clear()
    end_datum = input('Neues Enddatum eingeben (TT.MM.JJJJ): ')

    try:
        end_datum = date.strptime(end_datum, '%d.%m.%Y')
    except ValueError:
        input('Ungültiges Datum. [OK]')
        return

    studium.geplantes_end_datum = end_datum
    input(f'Enddatum zum {end_datum.strftime('%d.%m.%Y')} geändert. [OK]')

    # Änderung in Datenbank speichern
    with Datenbank() as db:
        db.studium_aendern(studium)


def semester_hinzufuegen(studium: Studium):
    """Lässt den Benutzer eine Nummer eingeben, daraus wird ein Semester mit der Nummer erstellt."""
    try:
        nummer = int(input('Semesternummer eingeben: '))
    except ValueError:
        input('Ungültige Nummer. [OK]')
        return

    # Neues Semester nur erstellen, wenn es noch keines mit der eingegebenen Nummer gibt
    if studium.get_semester(nummer) is not None:
        input(f'Es gibt bereits in Semester mit der Nummer {nummer}. [OK]')
        return

    semester = Semester(nummer=nummer)
    studium.semester_hinzufuegen(semester=semester)

    # Semester in Datenbank hinzufügen
    with Datenbank() as db:
        db.write(query=f'INSERT INTO semester (studium_id, nummer) VALUES (1, "{semester.nummer}");')


def semester_loeschen(studium: Studium):
    """Ein Semester mit gewünschter Nummer kann gelöscht werden."""
    try:
        nummer = int(input('Semesternummer eingeben: '))
    except ValueError:
        input('Ungültige Nummer. [OK]')
        return

    if studium.get_semester(nummer=nummer) is None:
        input(f'Kein Semester mit der Nummer {nummer} gefunden. [OK]')
        return

    studium.semester_entfernen(nummer=nummer)

    # Aus Datenbank löschen
    with Datenbank() as db:
        db.write(query=f'DELETE FROM semester WHERE nummer = "{nummer}";')

    input(f'Semester mit der Nummer {nummer} wurde gelöscht.')


def modul_hinzufuegen(studium: Studium):
    """Neues Modul mit gewünschten Eigenschaft wird erstellt."""
    clear()
    print('Neues Modul erstellen')
    kuerzel = input('Kürzel: ').upper()

    # Überprüfung, ob es bereits ein Modul mit dem gewünschtem Kürzel gibt
    if studium.get_modul(kuerzel=kuerzel) is not None:
        input(f'Ein Modul mit dem Kürzel "{kuerzel}" existiert bereits. [OK]')
        return

    name = input('Name: ')
    etcs = input('ETCs: ')

    try:
        etcs = int(etcs)
    except ValueError:
        input('Ungültige ETCs. [OK]')
        return

    neues_modul = Modul(kuerzel=kuerzel, name=name, etcs=etcs)

    print('\nNummer eingeben, zu welchem Semester das Modul hinzugefügt werden soll: ')
    for semester in studium.semester:
        print(f'{semester}')

    try:
        gewaeltes_semester = int(input())
    except ValueError:
        input('Ungültige Nummer. [OK]')
        return

    if studium.get_semester(nummer=gewaeltes_semester) is None:
        input('Gewähltes Semester existiert nicht. [OK]')
        return

    semester = studium.get_semester(nummer=gewaeltes_semester)
    if semester is not None:
        semester.modul_hinzufuegen(modul=neues_modul)

        # Zu Datenbank hinzufügen
        with Datenbank() as db:
            db.write(query=f'INSERT INTO modul (semester_id, kuerzel, name, etcs) VALUES ((SELECT id FROM semester WHERE nummer = {semester.nummer}), "{neues_modul.kuerzel}", "{neues_modul.name}", "{neues_modul.etcs}");')


def modul_loeschen(studium: Studium):
    """Modul mit gewünschten Kürzel löschen."""
    moduluebersicht(studium=studium)

    kuerzel = input('\nKürzel des zu löschenden Moduls eingeben: ').upper()
    ergebnis = studium.get_modul(kuerzel=kuerzel)

    if ergebnis is None:
        input(f'Kein Modul mit dem Kürzel "{kuerzel}" gefunden. [OK]')
        return

    semester, modul = ergebnis
    semester.modul_entfernen(kuerzel=kuerzel)

    input(f'{modul} wurde entfernt. [OK]')

    # Aus Datenbank löschen
    with Datenbank() as db:
        db.write(query=f'DELETE FROM modul WHERE id = (SELECT id FROM modul WHERE kuerzel = "{modul.kuerzel}");')


def pruefung_hinzufuegen(studium: Studium):
    """Prüfungsergebnis zu Modul hinzufügen."""
    moduluebersicht(studium=studium)

    kuerzel = input('\nKürzel des Moduls eingeben, bei welchem eine Prüfung hinzugefügt werden soll: ').upper()

    # Modul mit eingegebenen Kürzel suchen
    ergebnis = studium.get_modul(kuerzel=kuerzel)
    if ergebnis is None:
        input(f'Kein Modul mit dem Kürzel "{kuerzel}" gefunden. [OK]')
        return

    semester, modul = ergebnis

    if modul.ist_bewertet():
        input('Dieses Modul ist bereits bewertet. [OK]')
        return

    note = input('Note: ')

    try:
        note = float(note)
    except ValueError:
        input('Ungültige Note. [OK]')
        return

    pruefung = Pruefung(note=note)
    modul.pruefung_hinzufuegen(pruefung=pruefung)

    # In Datenbank speichern
    with Datenbank() as db:
        db.write(query=f'INSERT INTO pruefung (modul_id, note) VALUES ((SELECT id FROM modul WHERE kuerzel = "{modul.kuerzel}"), "{pruefung.note}");')


def pruefung_loeschen(studium: Studium):
    """Prüfung von Modul mit gewünschtem Kürzel löschen."""
    moduluebersicht(studium=studium)

    kuerzel = input('\nKürzel des Moduls eingeben, bei welchem die Prüfung gelöscht werden soll: ').upper()
    ergebnis = studium.get_modul(kuerzel=kuerzel)

    if ergebnis is None:
        input(f'Kein Modul mit dem Kürzel "{kuerzel}" gefunden. [OK]')
        return

    semester, modul = ergebnis

    # Bewertung nur löschen, wenn Modul bewertet ist
    if not modul.ist_bewertet():
        input(f'Prüfung konnte nicht gelöscht werden. Das Modul mit dem Kürzel "{kuerzel}" ist noch nicht bewertet worden. [OK]')
        return

    modul.pruefung_entfernen()
    input(f'Prüfung von Modul {modul.kuerzel} wurde entfernt. [OK]')

    # Aus Datenbank löschen
    with Datenbank() as db:
        db.write(query=f'DELETE FROM pruefung WHERE modul_id = (SELECT id FROM modul WHERE kuerzel = "{modul.kuerzel}");')


def main():
    studium = studium_laden_oder_erstellen()

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

    i = ''
    while i != '0':
        clear()
        # Hauptmenü
        print(studium)
        print('\n[1] - Studium bearbeiten')
        print('[2] - Semester verwalten')
        print('[3] - Module verwalten')
        print('[4] - Prüfungen verwalten')
        print('[5] - Notenübersicht öffnen')
        print('[0] - Beenden\n')
        i = input()

        if i == '1': # Studium bearbeiten
            j = ''
            while j != '0':
                clear()
                # Studium bearbeiten Menü
                print(studium)
                print('\n[1] - Studiengang ändern')
                print('[2] - Hochschule ändern')
                print('[3] - Startdatum ändern')
                print('[4] - Enddatum ändern')
                print('[0] - Zurück\n')
                j = input()

                if j == '1': # Studiengang ändern
                    studiengang_aendern(studium=studium)
                elif j == '2': # Hochschule ändern
                    hochschule_aendern(studium=studium)
                elif j == '3': # Startdatum ändern
                    startdatum_aendern(studium=studium)
                elif j == '4': # Enddatum ändern
                    enddatum_aendern(studium=studium)

        elif i == '2': # Semester verwalten
            j = ''
            while j != '0':
                clear()
                # Semester verwalten Menü
                for semester in studium.semester:
                    print(semester)

                print('\n[1] - Semester hinzufügen')
                print('[2] - Semester löschen')
                print('[0] - Zurück\n')
                j = input()

                if j == '1': # Semester hinzufügen
                    semester_hinzufuegen(studium=studium)
                elif j == '2': # Semester löschen
                    semester_loeschen(studium=studium)

        elif i == '3': # Module verwalten
            j = ''
            while j != '0':
                # Module verwalten Menü
                moduluebersicht(studium=studium)
                print('\n[1] - Modul hinzufügen')
                print('[2] - Modul löschen')
                print('[0] - Zurück\n')
                j = input()

                if j == '1': # Modul hinzufügen
                    modul_hinzufuegen(studium=studium)
                elif j == '2': # Modul löschen
                    modul_loeschen(studium=studium)

        elif i == '4': # Prüfungen verwalten
            j = ''
            while j != '0':
                # Prüfungen verwalten Menü
                moduluebersicht(studium=studium)
                print('\n[1] - Prüfung hinzufügen')
                print('[2] - Prüfung löschen')
                print('[0] - Zurück\n')
                j = input()

                if j == '1': # Prüfung hinzufügen
                    pruefung_hinzufuegen(studium=studium)
                elif j == '2': # Prüfung löschen
                    pruefung_loeschen(studium=studium)

        elif i == '5': # Notenübersicht
            diagramm = Diagramm(studium=studium)
            diagramm.notenuebersicht()

if __name__ == '__main__':
    main()