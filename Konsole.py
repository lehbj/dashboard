from datetime import date

from rich.console import Console
from rich.table import Table

from Datenbank import Datenbank
from Diagramm import Diagramm
from Modul import Modul
from Pruefung import Pruefung
from Semester import Semester
from Studium import Studium
from StudiumService import StudiumService

import os


def studium_erstellen() -> Studium:
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


class Konsole:
    def __init__(self, console: Console, studium: Studium, service: StudiumService) -> None:
        self._console = console
        self._studium = studium
        self._service = service

    def _clear(self):
        if os.name == 'nt':
            os.system("cls")
        else:
            self._console.clear()

    def _studium_ausgeben(self, titel: str):
        """Gibt eine Tabelle mit Informationen zum Studium aus."""
        table = Table(title=titel)
        table.add_column('Studiengang')
        table.add_column('Hochschule')
        table.add_column('Beginn')
        table.add_column('Geplantes Ende')
        table.add_column('Tage verbleibend', justify='right')
        table.add_column('Notendurchschnitt', justify='right')

        table.add_row(
            self._studium.studiengang,
            self._studium.hochschule,
            self._service.datum_formatieren(self._studium.start_datum),
            self._service.datum_formatieren(self._studium.geplantes_end_datum),
            str(self._service.tage_uebrig_berechnen()),
            str(self._service.gesamten_notendurchschnitt_berechnen() if self._service.gesamten_notendurchschnitt_berechnen() is not None else '-'),
        )

        self._clear()
        self._console.print(table)

    def _semester_ausgeben(self):
        """Gibt eine Tabelle mit allen Semestern aus."""
        table = Table(title='Semester verwalten')
        table.add_column('Semester', justify='right')
        table.add_column('Anzahl Module', justify='right')
        table.add_column('Notendurchschnitt', justify='right')

        for semester in self._studium.semester:
            table.add_row(
                str(semester.nummer),
                str(len(semester.module)),
                str(semester.get_noten_durchschnitt() if semester.get_noten_durchschnitt() is not None else '-'),
            )

        self._clear()
        self._console.print(table)

    def _module_ausgeben(self, titel: str):
        """Gibt eine Tabelle mit allen Modulen aus."""
        table = Table(title=titel)
        table.add_column('Kuerzel')
        table.add_column('Name')
        table.add_column('ETCs', justify='right')
        table.add_column('Semester', justify='right')
        table.add_column('Note', justify='right')
        table.add_column('Bestanden', justify='right')

        for semester in self._studium.semester:
            print(f'Semester {semester.nummer}:')
            for modul in semester.module:
                table.add_row(
                    modul.kuerzel,
                    modul.name,
                    str(modul.etcs),
                    str(semester.nummer),
                    str('-' if modul.get_note() is None else modul.get_note()),
                    'Ja' if modul.ist_bestanden() else 'Nein'
                )

        self._clear()
        self._console.print(table)

    def _studiengang_aendern(self):
        """Der Benutzer kann durch die Eingabeaufforderung den Namen des Studienganges ändern."""
        studiengang = input('Name des neuen Studienganges: ')

        self._studium.studiengang = studiengang
        input(f'Studiengang zu "{studiengang}" geändert. [OK]')

        # Änderung in Datenbank speichern
        self._service.studium_speichern()

    def _hochschule_aendern(self):
        """Der Benutzer kann durch die Eingabeaufforderung den Namen der Hochschule ändern."""
        hochschule = input('Name der neuen Hochschule: ')

        self._studium.hochschule = hochschule
        input(f'Hochschule zu "{hochschule}" geändert. [OK]')

        # Änderung in Datenbank speichern
        self._service.studium_speichern()

    def _startdatum_aendern(self):
        """Der Benutzer kann durch die Eingabeaufforderung das Startdatum des Studiums ändern."""
        start_datum = input('Neues Startdatum eingeben (TT.MM.JJJJ): ')

        try:
            start_datum = date.strptime(start_datum, '%d.%m.%Y')
        except ValueError:
            input('Ungültiges Datum. [OK]')
            return

        self._studium.start_datum = start_datum
        input(f'Startdatum zum {start_datum.strftime('%d.%m.%Y')} geändert. [OK]')

        # Änderung in Datenbank speichern
        self._service.studium_speichern()

    def _enddatum_aendern(self):
        """Der Benutzer kann durch die Eingabeaufforderung das geplante Enddatum des Studiums ändern."""
        end_datum = input('Neues Enddatum eingeben (TT.MM.JJJJ): ')

        try:
            end_datum = date.strptime(end_datum, '%d.%m.%Y')
        except ValueError:
            input('Ungültiges Datum. [OK]')
            return

        self._studium.geplantes_end_datum = end_datum
        input(f'Enddatum zum {end_datum.strftime('%d.%m.%Y')} geändert. [OK]')

        # Änderung in Datenbank speichern
        self._service.studium_speichern()

    def _semester_hinzufuegen(self):
        """Lässt den Benutzer eine Nummer eingeben, daraus wird ein Semester mit der Nummer erstellt."""
        try:
            nummer = int(input('Semesternummer eingeben: '))
        except ValueError:
            input('Ungültige Nummer. [OK]')
            return

        # Neues Semester nur erstellen, wenn es noch keines mit der eingegebenen Nummer gibt
        if self._studium.get_semester(nummer) is not None:
            input(f'Es gibt bereits in Semester mit der Nummer {nummer}. [OK]')
            return

        semester = Semester(nummer=nummer)
        self._studium.semester_hinzufuegen(semester=semester)

        # Semester in Datenbank hinzufügen
        with Datenbank() as db:
            db.write(query=f'INSERT INTO semester (studium_id, nummer) VALUES (1, "{semester.nummer}");')

    def _semester_loeschen(self):
        """Ein Semester mit gewünschter Nummer kann gelöscht werden."""
        try:
            nummer = int(input('Semesternummer eingeben: '))
        except ValueError:
            input('Ungültige Nummer. [OK]')
            return

        if self._studium.get_semester(nummer=nummer) is None:
            input(f'Kein Semester mit der Nummer {nummer} gefunden. [OK]')
            return

        self._studium.semester_entfernen(nummer=nummer)

        # Aus Datenbank löschen
        with Datenbank() as db:
            db.write(query=f'DELETE FROM semester WHERE nummer = "{nummer}";')

        input(f'Semester mit der Nummer {nummer} wurde gelöscht.')

    def _modul_hinzufuegen(self):
        """Neues Modul mit gewünschten Eigenschaft wird erstellt."""
        print('Neues Modul erstellen')
        kuerzel = input('Kürzel: ').upper()

        # Überprüfung, ob es bereits ein Modul mit dem gewünschtem Kürzel gibt
        if self._studium.get_modul(kuerzel=kuerzel) is not None:
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

        try:
            gewaeltes_semester = int(input())
        except ValueError:
            input('Ungültige Nummer. [OK]')
            return

        if self._studium.get_semester(nummer=gewaeltes_semester) is None:
            input('Gewähltes Semester existiert nicht. [OK]')
            return

        semester = self._studium.get_semester(nummer=gewaeltes_semester)
        if semester is not None:
            semester.modul_hinzufuegen(modul=neues_modul)

            # Zu Datenbank hinzufügen
            with Datenbank() as db:
                db.write(
                    query=f'INSERT INTO modul (semester_id, kuerzel, name, etcs) VALUES ((SELECT id FROM semester WHERE nummer = {semester.nummer}), "{neues_modul.kuerzel}", "{neues_modul.name}", "{neues_modul.etcs}");')

    def _modul_loeschen(self):
        """Modul mit gewünschten Kürzel löschen."""
        kuerzel = input('\nKürzel des zu löschenden Moduls eingeben: ').upper()
        ergebnis = self._studium.get_modul(kuerzel=kuerzel)

        if ergebnis is None:
            input(f'Kein Modul mit dem Kürzel "{kuerzel}" gefunden. [OK]')
            return

        semester, modul = ergebnis
        semester.modul_entfernen(kuerzel=kuerzel)

        input(f'Das Modul mit dem Kürzel {modul.kuerzel} wurde entfernt. [OK]')

        # Aus Datenbank löschen
        with Datenbank() as db:
            db.write(query=f'DELETE FROM modul WHERE id = (SELECT id FROM modul WHERE kuerzel = "{modul.kuerzel}");')

    def _pruefung_hinzufuegen(self):
        """Prüfungsergebnis zu Modul hinzufügen."""
        kuerzel = input('\nKürzel des Moduls eingeben, bei welchem eine Prüfung hinzugefügt werden soll: ').upper()

        # Modul mit eingegebenen Kürzel suchen
        ergebnis = self._studium.get_modul(kuerzel=kuerzel)
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
            db.write(
                query=f'INSERT INTO pruefung (modul_id, note) VALUES ((SELECT id FROM modul WHERE kuerzel = "{modul.kuerzel}"), "{pruefung.note}");')

    def _pruefung_loeschen(self):
        """Prüfung von Modul mit gewünschtem Kürzel löschen."""
        kuerzel = input('\nKürzel des Moduls eingeben, bei welchem die Prüfung gelöscht werden soll: ').upper()
        ergebnis = self._studium.get_modul(kuerzel=kuerzel)

        if ergebnis is None:
            input(f'Kein Modul mit dem Kürzel "{kuerzel}" gefunden. [OK]')
            return

        semester, modul = ergebnis

        # Bewertung nur löschen, wenn Modul bewertet ist
        if not modul.ist_bewertet():
            input(
                f'Prüfung konnte nicht gelöscht werden. Das Modul mit dem Kürzel "{kuerzel}" ist noch nicht bewertet worden. [OK]')
            return

        modul.pruefung_entfernen()
        input(f'Prüfung von Modul {modul.kuerzel} wurde entfernt. [OK]')

        # Aus Datenbank löschen
        with Datenbank() as db:
            db.write(
                query=f'DELETE FROM pruefung WHERE modul_id = (SELECT id FROM modul WHERE kuerzel = "{modul.kuerzel}");')

    def menu(self):
        """Regelt Benutzereingabe in Haupt- und Untermenüs."""
        eingabe_hauptmenue = ''
        while eingabe_hauptmenue != '0':  # Programm läuft bis der Benutzer im Hauptmenü "0" eingibt
            # Hauptmenü
            self._studium_ausgeben(titel='Studium-Verwaltungs-Dashboard')

            print('\n[1] - Studium bearbeiten')
            print('[2] - Semester verwalten')
            print('[3] - Module verwalten')
            print('[4] - Prüfungen verwalten')
            print('[5] - Notenübersicht öffnen')
            print('[0] - Beenden\n')
            eingabe_hauptmenue = input()

            if eingabe_hauptmenue == '1':  # Studium bearbeiten
                eingabe_untermenue = ''
                while eingabe_untermenue != '0':
                    # Studium bearbeiten Menü
                    self._studium_ausgeben(titel='Studium bearbeiten')

                    print('\n[1] - Studiengang ändern')
                    print('[2] - Hochschule ändern')
                    print('[3] - Startdatum ändern')
                    print('[4] - Enddatum ändern')
                    print('[0] - Zurück\n')
                    eingabe_untermenue = input()

                    if eingabe_untermenue == '1':  # Studiengang ändern
                        self._studiengang_aendern()
                    elif eingabe_untermenue == '2':  # Hochschule ändern
                        self._hochschule_aendern()
                    elif eingabe_untermenue == '3':  # Startdatum ändern
                        self._startdatum_aendern()
                    elif eingabe_untermenue == '4':  # Enddatum ändern
                        self._enddatum_aendern()

            elif eingabe_hauptmenue == '2':  # Semester verwalten
                eingabe_untermenue = ''
                while eingabe_untermenue != '0':
                    # Semester verwalten Menü
                    self._semester_ausgeben()

                    print('\n[1] - Semester hinzufügen')
                    print('[2] - Semester löschen')
                    print('[0] - Zurück\n')
                    eingabe_untermenue = input()

                    if eingabe_untermenue == '1':  # Semester hinzufügen
                        self._semester_hinzufuegen()
                    elif eingabe_untermenue == '2':  # Semester löschen
                        self._semester_loeschen()

            elif eingabe_hauptmenue == '3':  # Module verwalten
                eingabe_untermenue = ''
                while eingabe_untermenue != '0':
                    # Module verwalten Menü
                    self._module_ausgeben(titel='Module verwalten')

                    print('\n[1] - Modul hinzufügen')
                    print('[2] - Modul löschen')
                    print('[0] - Zurück\n')
                    eingabe_untermenue = input()

                    if eingabe_untermenue == '1':  # Modul hinzufügen
                        self._modul_hinzufuegen()
                    elif eingabe_untermenue == '2':  # Modul löschen
                        self._modul_loeschen()

            elif eingabe_hauptmenue == '4':  # Prüfungen verwalten
                eingabe_untermenue = ''
                while eingabe_untermenue != '0':
                    # Prüfungen verwalten Menü
                    self._module_ausgeben(titel='Prüfungen verwalten')

                    print('\n[1] - Prüfung hinzufügen')
                    print('[2] - Prüfung löschen')
                    print('[0] - Zurück\n')
                    eingabe_untermenue = input()

                    if eingabe_untermenue == '1':  # Prüfung hinzufügen
                        self._module_ausgeben(titel='Prüfung hinzufügen')
                        self._pruefung_hinzufuegen()
                    elif eingabe_untermenue == '2':  # Prüfung löschen
                        self._module_ausgeben(titel='Prüfung löschen')
                        self._pruefung_loeschen()

            elif eingabe_hauptmenue == '5':  # Notenübersicht
                diagramm = Diagramm(studium=self._studium)
                diagramm.notenuebersicht()
