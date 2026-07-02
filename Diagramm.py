import matplotlib.pyplot as plt

from Studium import Studium


class Diagramm:
    def __init__(self, studium: Studium) -> None:
        self._studium = studium

    @staticmethod
    def _notenfarbe(note: float) -> str:
        """Gibt je nach Note eine entsprechende Farbe zurück"""
        if note <= 1.5:
            return '#2ecc71' # Grün
        elif note <= 2.5:
            return '#3498db' # Blau
        elif note <= 3.5:
            return '#f39c12' # Orange
        elif note <= 4.0:
            return '#e67e22' # Dunkelorange
        else:
            return '#e74c3c' # Rot

    def notenuebersicht(self) -> None:
        """Notendiagramm erstellen und anzeigen"""
        semester_labels = []
        durchschnittsnoten = []
        farben = []

        for semester in self._studium.semester:
            durchschnitt = semester.get_noten_durchschnitt()
            if durchschnitt is not None:
                label = semester.nummer
                semester_labels.append(label)
                durchschnittsnoten.append(durchschnitt)
                farben.append(Diagramm._notenfarbe(durchschnitt))

        # Falls noch keine Noten eingespeichert sind
        if not durchschnittsnoten:
            input('Diagramm konnte nicht erstellt werden - Noch keine Prüfungen eingespeichert. [OK]')
            return

        fig, ax = plt.subplots(figsize=(10, 5))

        # Linie zeichnen
        ax.plot(range(len(semester_labels)), durchschnittsnoten, linewidth=2.5, color='#000000')

        # Semester auf x-Achse
        ax.set_xticks(range(len(semester_labels)))
        ax.set_xticklabels(semester_labels)

        # Datenpunkte
        for xi, (yi, farbe) in enumerate(zip(durchschnittsnoten, farben)):
            ax.scatter(xi, yi, color=farbe, s=100, zorder=3)

            # Beschriftung Punkte
            ax.annotate(f'{yi:.2f}', xy=(xi, yi), xytext=(0, 10), textcoords='offset points', ha='center', fontsize=10, color=farbe, fontweight='bold')

        # Linie Bestanden-Grenze
        ax.axhline(y=4.0, color='#e74c3c', alpha=0.5, label='Bestanden-Grenze (4.0)',)

        # Linie Gesamtdurchschnitt
        gesamt = self._studium.get_gesamten_durchschnitt()
        ax.axhline(y=gesamt, color='#7f8c8d', linewidth=1.2, linestyle=':',  alpha=0.5, label=f'Ø Gesamt: {gesamt:.2f}')

        # Invertieren, Abstände anpassen
        ax.set_ylim(5.2, 0.7)

        # Gitter
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)

        # Labels
        ax.set_title('Notenverlauf')
        ax.set_xlabel('Semester')
        ax.set_ylabel('Notenschnitt')

        # Legende Bestanden-Grenze und Durchschnitt gesamt
        ax.legend(loc='lower right')

        # Abstände optimieren und Ausgabe
        plt.tight_layout()
        plt.show()
