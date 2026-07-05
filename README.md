# ToolTrace

ToolTrace ist eine webbasierte Flask-Anwendung zur Erfassung, Verwaltung und automatischen Verarbeitung von Werkzeugkonturen.

Ein Benutzer legt ein Werkzeug an, laedt ein Foto eines einzelnen Werkzeugs auf einem vollstaendig sichtbaren Hintergrund hoch und verwaltet den Datensatz in seiner persoenlichen Werkzeugbibliothek. ToolTrace erkennt den Hintergrund, korrigiert die Perspektive, segmentiert das Werkzeug, erzeugt eine Aussenkontur und speichert diese masshaltig in Millimeter-Koordinaten.

Aktuelle Version: `0.5.5`

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
* User-Einstellungen fuer Leuchttisch-Hintergrundgroessen A3, A4 und A5
* Upload-Auswahl fuer die Hintergrundgroesse, die als Massreferenz verwendet wird
* OpenCV-basierte Hintergrunderkennung mit markierter Vorschau unter `processed/`
* robustere Leuchttisch-Erkennung ueber grosse helle Flaechen in unterbelichteten Fotos
* Perspektivkorrektur erkannter Hintergruende mit konfigurierbarer Pixel-pro-Millimeter-Skalierung
* OpenCV-Werkzeugsegmentierung fuer dunkle bzw. kontrastreiche Werkzeuge auf hellem Hintergrund
* robustere Hintergrundschaetzung, Beleuchtungskorrektur, Schattenreduktion und Kantenunterstuetzung fuer schmale Werkzeugbereiche
* Maskenbereinigung mit Entfernung kleiner Stoerungen und Randartefakte am Hintergrundrand
* Konturerkennung fuer die aeussere Werkzeugkontur
* rote Kontur-Overlay-Vorschau mit 30 Prozent Transparenz
* Ausrichtung der erkannten Aussenkontur ueber die minimale rotierte Bounding Box
* manuelle Konturausrichtung ueber zwei vom User gewaehlte Punkte auf einer Werkzeugkante
* automatische Projektion der gewaehlten Punkte auf die naechste Konturkante
* optionale Raster-Bounding-Box, zum Beispiel fuer Gridfinity-Rastermasse
* Konturglaettung und Konturvereinfachung als nicht-destruktive neue Konturversionen
* Reset fuer Glaettung/Vereinfachung bis zur urspruenglichen nicht geglaetteten Konturversion
* Bibliotheks-Thumbnails verwenden bevorzugt die aktive ausgerichtete oder bearbeitete Konturvorschau
* Werkzeug-Koordinatensystem mit Ursprung links unten, X nach rechts und Y nach oben
* Speicherung der Konturpunkte, Bounding Box, Flaeche und Umfang in Millimeterwerten
* Quellreferenz der originalen Pixelkontur in den Geometriedaten
* einfache Layout-Helfer fuer freies Rechteck und Gridfinity-Groessen
* SVG-Grundausgabe fuer leere Layout-Rahmen mit Millimeter-Massen
* automatisierte Basistests

Noch nicht implementiert:

* echter SVG-Export aus Werkzeugkonturen
* Benutzeroberflaeche fuer Konturversatz und Layoutauswahl

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

Die Tests decken aktuell App-Erzeugung, Registrierung/Login, Werkzeuganlage, Upload-Metadaten, Hintergrunderkennung, Leuchttisch-Erkennung, Perspektivkorrektur, OpenCV-Segmentierung, Randartefakt-Filterung, Konturextraktion, automatische und manuelle Konturausrichtung, Konturglaettung, Konturvereinfachung, Reset der Konturbearbeitung, Bibliotheksvorschauen, Gridfinity-Berechnung, Pixel-zu-Millimeter-Umrechnung und SVG-Grundausgabe ab.

## Dokumentation

Die Einsteigerbeschreibung [Vom Bild zur SVG](doku/Bild_zu_SVG_Workflow.md) erklaert den Workflow vom Werkzeugfoto bis zur vorbereiteten SVG-Kontur. Sie beschreibt die Bildanforderungen, die automatische Verarbeitung, die wichtigsten OpenCV-Schritte und die verwendeten Parameter.

Die Anleitung [Fotos fuer die Konturerkennung aufnehmen](doku/Fotoaufnahme_fuer_Konturerkennung.md) beschreibt zwei Aufnahmewege: schnelle Fotos mit minimalem Aufwand und ein genaueres Setup mit Stativ, diffuser Beleuchtung und optionalem Leuchttisch fuer bestmoegliche Konturqualitaet.

## Lizenz

ToolTrace verwendet dieselbe Lizenzstruktur wie NeoFab. Die nicht-kommerzielle Nutzung steht unter der Creative-Commons-Lizenz [Attribution-NonCommercial-ShareAlike 4.0 International](LICENCE.txt). Kommerzielle Nutzung ist nur nach vorheriger schriftlicher Genehmigung erlaubt; Details stehen in [LICENSE-COMMERCIAL.md](LICENSE-COMMERCIAL.md).

## Projektstruktur

```text
app/
  auth/          Registrierung, Anmeldung, Abmeldung
  dashboard/     Benutzer-Dashboard
  tools/         Werkzeugbibliothek, Werkzeugformular, Upload, API
  processing/    Bildverarbeitungspipeline, Hintergrunderkennung, Segmentierung, Konturen
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
3. Benutzer waehlt die Hintergrundgroesse und laedt ein Foto eines Werkzeugs hoch.
4. ToolTrace erkennt den Hintergrund und korrigiert die Perspektive.
5. ToolTrace segmentiert das Werkzeug auf dem entzerrten Hintergrund.
6. ToolTrace bereinigt die Maske und entfernt Stoerungen am Hintergrundrand.
7. ToolTrace erzeugt die aeussere Werkzeugkontur.
8. ToolTrace rechnet die Kontur in Millimeter um.
9. ToolTrace richtet die Kontur in einem Werkzeug-Koordinatensystem aus.
10. Benutzer kann die Kontur manuell an einer gewaehlten Kante ausrichten.
11. Benutzer kann die Kontur glaetten, vereinfachen oder diese Bearbeitung per Reset zuruecknehmen.
12. ToolTrace speichert Vorschaubilder, Messwerte und Geometriedaten am Werkzeug.

## MVP-Zielbild

Das naechste MVP-Ziel ist der vollstaendige Exportfluss:

1. Benutzer prueft die automatisch erkannte Kontur.
2. Benutzer richtet die Kontur bei Bedarf manuell aus und glaettet oder vereinfacht sie.
3. Benutzer waehlt Konturversatz und Layout.
4. ToolTrace erzeugt eine masshaltige Vorschau.
5. ToolTrace exportiert eine SVG-Datei mit der Werkzeugkontur.

Der aktuelle Stand bildet die Grundlage bis einschliesslich automatischer Konturerkennung, Millimeter-Umrechnung, Konturausrichtung und nicht-destruktiver Konturbearbeitung ab.
