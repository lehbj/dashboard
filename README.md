# Studiumsverwaltungs-Dashboard

Ein objektorientiertes Konsolenprogramm zur Verwaltung und Auswertung von Studienleistungen. 
Prüfungsergebnisse, Module und Semester werden in einer lokalen SQLite-Datenbank gespeichert.
Der Notenverlauf kann als Diagramm visualisiert werden.

---

## Voraussetzungen

- Python 3.14
- pip

---

## Installation

### 1. Repository klonen

```bash
git clone https://github.com/benutzername/studiumsverwaltung.git
cd studiumsverwaltung
```

### 2. Abhängigkeiten installieren

Zur Diagrammerstellung wird **matplotlib** verwendet. Falls es noch nich installiert ist, kann es mit pip installiert werden:

```bash
pip install matplotlib
```

### 3. Programm starten

```bash
python Main.py
```

Die SQLite-Datenbank (`studiumsverwaltung.db`) wird beim ersten Start automatisch im Projektverzeichnis angelegt.

---

## Bedienung

Das Programm wird vollständig über ein Konsolenmenü gesteuert. Einfach die gewünschte Zahl über die Eingabeaufforderung eingeben und mit Enter bestätigen.

### Datumseingabe

Alle Datumsfelder werden im Format `TT.MM.JJJJ` eingegeben, zum Beispiel:

```
Neues Startdatum eingeben (TT.MM.JJJJ): 17.06.2026
```