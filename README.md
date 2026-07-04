# ToolTrace

ToolTrace ist eine webbasierte Flask-Anwendung zur Erfassung, Verwaltung und spaeteren Verarbeitung von Werkzeugkonturen.

Ein Benutzer legt ein Werkzeug an, laedt ein Foto eines einzelnen Werkzeugs auf einem vollstaendig sichtbaren DIN-A4-Blatt hoch und verwaltet den Datensatz in seiner persoenlichen Werkzeugbibliothek. Die eigentliche OpenCV-Konturerkennung ist noch nicht Teil dieses ersten Entwicklungsschritts.

## Aktueller Stand

Implementiert ist die technische Grundstruktur:

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
* einfache OpenCV-Werkzeugsegmentierung fuer dunkle bzw. kontrastreiche Werkzeuge auf weissem DIN-A4-Blatt
* Platzhalter fuer Konturerkennung, Layout- und SVG-Exportservices
* automatisierte Basistests

Noch nicht implementiert:

* Konturerkennung
* interaktiver Kontureditor
* echter SVG-Export aus Werkzeugkonturen

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

Die Tests decken aktuell App-Erzeugung, Registrierung/Login, Werkzeuganlage, Upload-Metadaten, Gridfinity-Berechnung, Pixel-zu-Millimeter-Umrechnung und SVG-Grundausgabe ab.

## Projektstruktur

```text
app/
  auth/          Registrierung, Anmeldung, Abmeldung
  dashboard/     Benutzer-Dashboard
  tools/         Werkzeugbibliothek, Werkzeugformular, Upload, API
  processing/    Pipeline- und Bildverarbeitungsplatzhalter
  layouts/       Layoutservices und Gridfinity-Helfer
  exports/       SVG-Exportservice-Platzhalter
  models/        SQLAlchemy-Modelle
  admin/         Administrationsplatzhalter
  templates/     globale Templates
  static/        CSS und spaetere Frontend-Dateien
migrations/      Alembic-Migrationen
storage/         lokale Uploads und generierte Dateien
tests/           Unit- und Integrationstests
```

## MVP-Zielbild

Das spaetere MVP soll folgenden Ablauf ermoeglichen:

1. Benutzer registriert sich und meldet sich an.
2. Benutzer legt ein Werkzeug an.
3. Benutzer laedt ein Foto eines Werkzeugs auf einem DIN-A4-Blatt hoch.
4. ToolTrace erkennt das Blatt und korrigiert die Perspektive.
5. ToolTrace segmentiert das Werkzeug und erzeugt eine Kontur.
6. ToolTrace rechnet die Kontur in Millimeter um.
7. Benutzer waehlt Konturversatz und Layout.
8. ToolTrace erzeugt eine masshaltige Vorschau.
9. Benutzer exportiert eine SVG-Datei.

Der aktuelle Stand bildet die Grundlage bis einschliesslich Upload und Pipeline-Platzhalter ab.
