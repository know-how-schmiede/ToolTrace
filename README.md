# ToolTrace

ToolTrace ist eine webbasierte Flask-Anwendung zur Erfassung, Verwaltung und automatischen Verarbeitung von Werkzeugkonturen.

Ein Benutzer legt ein Werkzeug an, laedt ein Foto eines einzelnen Werkzeugs auf einem vollstaendig sichtbaren DIN-A4-Blatt hoch und verwaltet den Datensatz in seiner persoenlichen Werkzeugbibliothek. ToolTrace erkennt das DIN-A4-Blatt, korrigiert die Perspektive, segmentiert das Werkzeug, erzeugt eine Aussenkontur und speichert diese masshaltig in Millimeter-Koordinaten.

Aktuelle Version: `0.5.0`

## Aktueller Stand

Implementiert ist aktuell:

* Flask Application Factory
* getrennte Blueprints fuer Auth, Dashboard, Werkzeuge, API, Layouts, Exporte und Administration
* SQLAlchemy-Modelle fuer Benutzer, Kategorien, Werkzeuge, Bilder, Jobs, Konturen, Layouts, Exporte und Audit-Logs
* Flask-Migrate/Alembic-Migrationsgeruest mit Initialschema
* Flask-Login mit Registrierung, Anmeldung und Abmeldung
* Werkzeugbibliothek mit Suche und Statusfilter
* Formular zum Anlegen eines Werkzeugs
* Loeschen von Werkzeugen inklusive zugehoeriger Datenbankeintraege und Dateien
* sicherer Bild-Upload fuer JPEG/PNG mit Pillow-Validierung
* Speicherung von Upload-Metadaten und Dateien unter `storage/users/<user_id>/tools/<tool_id>/source/`
* OpenCV-basierte DIN-A4-Erkennung mit markierter Vorschau unter `processed/`
* Perspektivkorrektur erkannter DIN-A4-Blaetter mit konfigurierbarer Pixel-pro-Millimeter-Skalierung
* OpenCV-Werkzeugsegmentierung fuer dunkle bzw. kontrastreiche Werkzeuge auf weissem DIN-A4-Blatt
* robustere Hintergrundschaetzung, Beleuchtungskorrektur, Schattenreduktion und Kantenunterstuetzung fuer schmale Werkzeugbereiche
* Maskenbereinigung mit Entfernung kleiner Stoerungen und Randartefakte am DIN-A4-Blatt
* Konturerkennung fuer die aeussere Werkzeugkontur
* rote Kontur-Overlay-Vorschau mit 30 Prozent Transparenz
* Ausrichtung der erkannten Aussenkontur ueber die minimale rotierte Bounding Box
* Werkzeug-Koordinatensystem mit Ursprung links unten, X nach rechts und Y nach oben
* Speicherung der Konturpunkte, Bounding Box, Flaeche und Umfang in Millimeterwerten
* Quellreferenz der originalen Pixelkontur in den Geometriedaten
* einfache Layout-Helfer fuer freies Rechteck und Gridfinity-Groessen
* SVG-Grundausgabe fuer leere Layout-Rahmen mit Millimeter-Massen
* automatisierte Basistests

Noch nicht implementiert:

* interaktiver Kontureditor
* echter SVG-Export aus Werkzeugkonturen
* Benutzeroberflaeche fuer Konturversatz, Konturvereinfachung und Layoutauswahl

## Voraussetzungen

* Python 3.11 oder neuer
* Git
* pip

## Installation

Repository klonen und in das Projekt wechseln:

```powershell
git clone https://github.com/<username>/ToolTrace.git
cd ToolTrace
```

Virtuelle Umgebung erstellen und aktivieren:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Abhaengigkeiten installieren:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Konfiguration anlegen:

```powershell
Copy-Item .env.example .env
```

Die wichtigsten Standardwerte:

```env
SECRET_KEY=change-me
DATABASE_URL=sqlite:///instance/tooltrace.sqlite3
STORAGE_PATH=storage
MAX_UPLOAD_SIZE_MB=20
MIN_IMAGE_WIDTH=1200
MIN_IMAGE_HEIGHT=1200
GRIDFINITY_UNIT_MM=42
SEGMENTATION_BACKEND=opencv
```

Weitere relevante Standardwerte:

```env
PROCESSING_PIXELS_PER_MM=10
DEFAULT_CONTOUR_OFFSET_MM=1.5
DEFAULT_CONTOUR_SIMPLIFICATION_MM=0.2
DEFAULT_LAYOUT_TYPE=gridfinity
DEFAULT_LAYOUT_MARGIN_MM=5
```

## Datenbank initialisieren

```powershell
$env:FLASK_APP = "run.py"
flask db upgrade
```

## Anwendung starten

```powershell
$env:FLASK_APP = "run.py"
flask run
```

Alternativ:

```powershell
python run.py
```

Die Anwendung ist danach unter `http://127.0.0.1:5000` erreichbar.

## Tests

```powershell
pytest
```

Die Tests decken aktuell App-Erzeugung, Registrierung/Login, Werkzeuganlage, Upload-Metadaten, DIN-A4-Vorschau, Perspektivkorrektur, OpenCV-Segmentierung, Randartefakt-Filterung, Konturextraktion, Konturausrichtung, Gridfinity-Berechnung, Pixel-zu-Millimeter-Umrechnung und SVG-Grundausgabe ab.

## Dokumentation

Die Einsteigerbeschreibung [Vom Bild zur SVG](doku/Bild_zu_SVG_Workflow.md) erklaert den Workflow vom Werkzeugfoto bis zur vorbereiteten SVG-Kontur. Sie beschreibt die Bildanforderungen, die automatische Verarbeitung, die wichtigsten OpenCV-Schritte und die verwendeten Parameter.

## Projektstruktur

```text
app/
  auth/          Registrierung, Anmeldung, Abmeldung
  dashboard/     Benutzer-Dashboard
  tools/         Werkzeugbibliothek, Werkzeugformular, Upload, API
  processing/    Bildverarbeitungspipeline, Blatterkennung, Segmentierung, Konturen
  layouts/       Layoutservices und Gridfinity-Helfer
  exports/       SVG-Exportservice fuer Layout-Grundausgabe
  models/        SQLAlchemy-Modelle
  admin/         Administrationsplatzhalter
  templates/     globale Templates
  static/        CSS und spaetere Frontend-Dateien
migrations/      Alembic-Migrationen
storage/         lokale Uploads, Masken, Vorschauen, Konturen und Exporte
tests/           Unit- und Integrationstests
```

## Aktueller Bildverarbeitungsablauf

Der aktuelle Ablauf nach einem Upload:

1. Benutzer registriert sich und meldet sich an.
2. Benutzer legt ein Werkzeug an.
3. Benutzer laedt ein Foto eines Werkzeugs auf einem DIN-A4-Blatt hoch.
4. ToolTrace erkennt das Blatt und korrigiert die Perspektive.
5. ToolTrace segmentiert das Werkzeug auf dem entzerrten Blatt.
6. ToolTrace bereinigt die Maske und entfernt Stoerungen am Blattrand.
7. ToolTrace erzeugt die aeussere Werkzeugkontur.
8. ToolTrace rechnet die Kontur in Millimeter um.
9. ToolTrace richtet die Kontur in einem Werkzeug-Koordinatensystem aus.
10. ToolTrace speichert Vorschaubilder, Messwerte und Geometriedaten am Werkzeug.

## MVP-Zielbild

Das naechste MVP-Ziel ist der vollstaendige Exportfluss:

1. Benutzer prueft die automatisch erkannte Kontur.
2. Benutzer waehlt Konturversatz, Konturvereinfachung und Layout.
3. ToolTrace erzeugt eine masshaltige Vorschau.
4. ToolTrace exportiert eine SVG-Datei mit der Werkzeugkontur.

Der aktuelle Stand bildet die Grundlage bis einschliesslich automatischer Konturerkennung, Millimeter-Umrechnung und Konturausrichtung ab.
