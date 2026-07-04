# ToolTrace

**ToolTrace** ist eine webbasierte Anwendung zur automatischen Erkennung, Bearbeitung und Verwaltung von Werkzeugkonturen.

Ein Benutzer fotografiert ein einzelnes Werkzeug auf einem vollständig sichtbaren DIN-A4-Blatt und lädt das Bild in ToolTrace hoch. Die Anwendung erkennt das Blatt, korrigiert die Perspektive, segmentiert das Werkzeug und erzeugt daraus eine maßhaltige Vektorkontur.

Die Kontur kann anschließend als SVG-Datei exportiert und beispielsweise für Schaumstoffeinlagen, Shadowboards, Werkzeugschubladen, Lasercutter, CNC-Fräsen oder Schneidplotter verwendet werden.

> **ToolTrace – Werkzeugkonturen erkennen, bearbeiten und exportieren**

---

## Projektstatus

ToolTrace befindet sich derzeit in der Konzeptions- und frühen Entwicklungsphase.

Die erste Version konzentriert sich auf einen kontrollierten Ablauf mit genau einem Werkzeug pro Bild und einem vollständig sichtbaren DIN-A4-Blatt als Größen- und Perspektivreferenz.

Das Projekt ist noch nicht für den produktiven Einsatz vorgesehen.

---

## Geplanter Ablauf

1. Benutzer registriert sich oder meldet sich an.
2. Benutzer legt einen neuen Werkzeugdatensatz an.
3. Ein Bild mit einem Werkzeug auf einem DIN-A4-Blatt wird hochgeladen.
4. ToolTrace prüft die Bildqualität.
5. Das DIN-A4-Blatt wird erkannt.
6. Die Perspektive wird automatisch korrigiert.
7. Das Werkzeug wird vom Hintergrund getrennt.
8. Außen- und Innenkonturen werden erkannt.
9. Die Kontur wird in reale Millimeter umgerechnet.
10. Das Werkzeug wird automatisch ausgerichtet.
11. Ein Konturversatz kann eingestellt werden.
12. Die Kontur wird in einem Rechteck- oder Gridfinity-Raster platziert.
13. Der Benutzer kontrolliert das Ergebnis in einer Vorschau.
14. Das Werkzeugprojekt wird in der persönlichen Bibliothek gespeichert.
15. Die fertige Kontur kann als SVG-Datei heruntergeladen werden.

---

## Einsatzbereiche

ToolTrace ist für unterschiedliche Anwendungen im Werkstatt- und Makerspace-Umfeld vorgesehen:

* Schaumstoffeinlagen für Werkzeugschubladen
* Shadowboards
* Werkzeugtafeln
* Gridfinity-kompatible Werkzeugeinsätze
* Fräsvorlagen
* Lasercutter-Vorlagen
* Schneidplotter
* Werkzeugdokumentation
* Inventarisierung
* Erstellung maßhaltiger Werkzeugumrisse

---

## Ziele des Projekts

ToolTrace soll folgende Hauptfunktionen bereitstellen:

* Benutzerregistrierung und Anmeldung
* persönliche Werkzeugbibliothek
* Upload von Werkzeugfotos
* automatische DIN-A4-Erkennung
* Perspektivkorrektur
* Werkzeugsegmentierung
* Erkennung von Außen- und Innenkonturen
* Konturglättung und Konturvereinfachung
* automatische Ausrichtung
* einstellbarer Konturversatz
* Platzierung in einem Rechteck-Raster
* Gridfinity-Unterstützung
* maßhaltige SVG-Vorschau
* SVG-Export
* Speicherung von Bildern, Konturen, Layouts und Exporten
* Werkzeugmetadaten und Tags
* Kontur- und Layoutversionen

---

## Umfang des MVP

Die erste funktionsfähige Version wird bewusst begrenzt.

### Unterstützt

* genau ein Werkzeug pro Bild
* vollständig sichtbares DIN-A4-Blatt
* Werkzeug vollständig innerhalb des Blattes
* JPEG- und PNG-Dateien
* Erkennung der Außenkontur
* Erkennung geschlossener Innenkonturen
* automatische horizontale oder vertikale Ausrichtung
* freies Rechteck als Layout
* Gridfinity-Raster
* einstellbarer Sicherheitsabstand
* maßhaltiger SVG-Export
* persönliche Werkzeugbibliothek
* grundlegende Werkzeugmetadaten

### Noch nicht Bestandteil des MVP

* mehrere Werkzeuge pro Bild
* automatische Anordnung mehrerer Werkzeuge
* vollständiger Vektoreditor
* automatische Hersteller- und Modellerkennung
* DXF-Export
* STL-Erzeugung
* vollständige Gridfinity-Box-Erzeugung
* CAM- oder G-Code-Ausgabe
* gemeinsame Team-Bibliotheken
* mobile Kamera-Liveansicht

---

## Anforderungen an das Aufnahmebild

Für eine zuverlässige Erkennung sollte das Bild folgende Voraussetzungen erfüllen:

* genau ein Werkzeug befindet sich auf dem Blatt
* das vollständige DIN-A4-Blatt ist sichtbar
* alle vier Blattecken sind erkennbar
* das Werkzeug liegt vollständig innerhalb des Blattes
* das Werkzeug berührt den Blattrand nicht
* die Kamera befindet sich möglichst senkrecht über dem Blatt
* das Bild ist ausreichend scharf
* das Blatt ist gleichmäßig ausgeleuchtet
* starke Schatten werden vermieden
* Reflexionen auf glänzenden Werkzeugen werden reduziert
* Werkzeug und Hintergrund besitzen ausreichend Kontrast

Das DIN-A4-Blatt dient als:

* Größenreferenz
* Perspektivreferenz
* Hintergrund
* Begrenzung des Aufnahmebereichs

---

## Bildverarbeitung

Die geplante Verarbeitungspipeline besteht aus mehreren Schritten:

```text
Bild-Upload
    ↓
Datei- und Qualitätsprüfung
    ↓
DIN-A4-Blatt erkennen
    ↓
Perspektive korrigieren
    ↓
Bild auf 210 × 297 mm normieren
    ↓
Werkzeug segmentieren
    ↓
Maske bereinigen
    ↓
Außen- und Innenkonturen erkennen
    ↓
Konturen glätten und vereinfachen
    ↓
Pixel in Millimeter umrechnen
    ↓
Werkzeug automatisch ausrichten
    ↓
Konturversatz erzeugen
    ↓
Layout berechnen
    ↓
SVG-Vorschau und Export
```

---

## Segmentierung

ToolTrace soll verschiedene Verfahren zur Werkzeugsegmentierung unterstützen.

### Klassische Bildverarbeitung

Die erste Version soll zunächst mit OpenCV umgesetzt werden.

Mögliche Verfahren:

* Graustufenkonvertierung
* adaptive Schwellenwertbildung
* Otsu-Schwellenwert
* Farbabstand zum weißen Hintergrund
* Canny-Kantenerkennung
* morphologische Operationen
* Konturerkennung
* Filterung kleiner Störflächen

### KI-gestützte Segmentierung

Die Architektur soll spätere KI-Backends ermöglichen.

Geplante Optionen:

* YOLO-Segmentation
* Segment Anything
* eigene trainierte Segmentierungsmodelle

Alle Segmentierungsverfahren sollen über eine gemeinsame interne Schnittstelle angesprochen werden.

---

## Automatische Ausrichtung

Nach der Konturerkennung soll die Werkzeugkontur automatisch ausgerichtet werden.

Geplanter Ablauf:

1. Hauptachse des Werkzeugs bestimmen
2. kleinstes umschließendes Rechteck berechnen
3. Werkzeug entlang der längsten Achse ausrichten
4. Werkzeug standardmäßig horizontal platzieren
5. Kontur in den positiven Koordinatenbereich verschieben

Der Benutzer soll später zwischen verschiedenen Ausrichtungen wählen können:

* automatisch
* horizontal
* vertikal
* ursprüngliche Ausrichtung
* benutzerdefinierter Winkel

---

## Konturversatz

Für Schaumstoffeinlagen ist häufig ein Abstand zwischen Werkzeug und Schnittkontur erforderlich.

Beispiele:

* `0,0 mm` für die erkannte Originalkontur
* `0,5 mm` für eine enge Passung
* `1,0 bis 2,0 mm` für eine normale Schaumstoffeinlage
* `3,0 mm` für eine großzügige Aufnahme

Die erkannte Originalkontur bleibt erhalten. Der Konturversatz erzeugt eine separate Produktionskontur.

---

## Gridfinity-Unterstützung

ToolTrace soll Werkzeugkonturen automatisch in einem Gridfinity-kompatiblen Rechteck platzieren können.

Das Standardraster beträgt:

```text
42 × 42 mm
```

Die erforderliche Rastergröße wird aus Werkzeugkontur, Konturversatz und Randabständen berechnet.

Beispiel:

```text
Benötigte Fläche: 108 × 67 mm

Rasterbreite:
ceil(108 / 42) = 3

Rasterhöhe:
ceil(67 / 42) = 2

Ergebnis:
3 × 2 Gridfinity-Einheiten
126 × 84 mm
```

Die Rastereinheit wird zentral konfiguriert und nicht fest in mehreren Programmteilen hinterlegt.

---

## Werkzeugbibliothek

Jeder Benutzer erhält eine persönliche Werkzeugbibliothek.

Ein Werkzeugprojekt kann folgende Daten enthalten:

* Originalbild
* perspektivisch korrigiertes Bild
* Segmentierungsmaske
* erkannte Originalkontur
* bereinigte Kontur
* Produktionskontur
* Layout
* Vorschaugrafik
* SVG-Export
* Werkzeugmetadaten
* Verarbeitungsparameter
* Verarbeitungshistorie
* Konturversionen
* Layoutversionen

Mögliche Aktionen:

* Werkzeug öffnen
* Werkzeug bearbeiten
* Metadaten ändern
* Kontur neu berechnen
* Layout anpassen
* SVG erneut erzeugen
* Werkzeug duplizieren
* Werkzeug archivieren
* Werkzeug löschen

---

## Werkzeugmetadaten

ToolTrace soll zu jedem Werkzeug zusätzliche Informationen speichern können.

### Allgemeine Angaben

* Werkzeugname
* Kategorie
* Unterkategorie
* Hersteller
* Modell
* Artikelnummer
* Seriennummer
* Inventarnummer
* Beschreibung
* Bemerkungen
* Tags

### Organisatorische Angaben

* Besitzer
* Werkstatt
* Arbeitsbereich
* Schrank
* Schublade
* Shadowboard
* Lagerort
* verantwortliche Person

### Technische Angaben

* erkannte Breite
* erkannte Höhe
* Konturfläche
* Konturlänge
* Konturversatz
* Rastertyp
* Rastergröße
* Ausrichtung
* Exportmaßstab

### Fertigungsangaben

* Einsatzzweck
* Material
* Materialstärke
* gewünschte Schnitttiefe
* Fräserdurchmesser
* Kerf-Korrektur
* Fertigungshinweise

Für das MVP sollen nur wenige Felder verpflichtend sein:

* Werkzeugname
* Kategorie
* Einsatzzweck

---

## Vorgesehener Technologie-Stack

### Backend

* Python
* Flask
* SQLAlchemy
* Alembic
* Flask-Login
* Flask-WTF

### Bildverarbeitung

* OpenCV
* NumPy
* Pillow
* Shapely
* scikit-image

### Export

* svgwrite
* XML/SVG
* Shapely für Geometrieoperationen

### Frontend

* HTML
* Jinja2
* Bootstrap
* JavaScript
* SVG

### Datenbank

Entwicklung:

* SQLite

Produktiver Betrieb:

* PostgreSQL

### Optionale KI-Komponenten

* PyTorch
* Ultralytics YOLO
* Segment Anything

---

## Vorgesehene Projektstruktur

```text
tooltrace/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── extensions.py
│   │
│   ├── auth/
│   │   ├── routes.py
│   │   ├── forms.py
│   │   ├── services.py
│   │   └── templates/
│   │
│   ├── dashboard/
│   │   ├── routes.py
│   │   └── templates/
│   │
│   ├── tools/
│   │   ├── routes.py
│   │   ├── api.py
│   │   ├── forms.py
│   │   ├── services.py
│   │   └── templates/
│   │
│   ├── processing/
│   │   ├── pipeline.py
│   │   ├── jobs.py
│   │   ├── exceptions.py
│   │   ├── page_detection.py
│   │   ├── perspective.py
│   │   ├── quality.py
│   │   ├── mask_cleanup.py
│   │   ├── contour_extraction.py
│   │   ├── geometry.py
│   │   └── segmentation/
│   │       ├── base.py
│   │       ├── opencv_backend.py
│   │       ├── yolo_backend.py
│   │       └── sam_backend.py
│   │
│   ├── layouts/
│   │   ├── routes.py
│   │   ├── services.py
│   │   ├── gridfinity.py
│   │   └── free_rectangle.py
│   │
│   ├── exports/
│   │   ├── routes.py
│   │   ├── services.py
│   │   └── svg_export.py
│   │
│   ├── models/
│   │   ├── user.py
│   │   ├── tool.py
│   │   ├── category.py
│   │   ├── source_image.py
│   │   ├── processing_job.py
│   │   ├── processed_image.py
│   │   ├── contour.py
│   │   ├── layout.py
│   │   ├── export.py
│   │   └── audit_log.py
│   │
│   ├── admin/
│   │   ├── routes.py
│   │   └── templates/
│   │
│   ├── templates/
│   │   ├── base.html
│   │   ├── components/
│   │   └── errors/
│   │
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
│
├── migrations/
├── storage/
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── processing/
│   └── fixtures/
│
├── scripts/
├── instance/
├── docs/
├── .env.example
├── .gitignore
├── pyproject.toml
├── requirements.txt
├── run.py
└── README.md
```

---

## Dateispeicher

Bilder und Exportdateien sollen nicht direkt als Binärdaten in der Datenbank gespeichert werden.

Vorgesehene Verzeichnisstruktur:

```text
storage/
└── users/
    └── <user_id>/
        └── tools/
            └── <tool_id>/
                ├── source/
                ├── processed/
                ├── masks/
                ├── previews/
                ├── contours/
                └── exports/
```

Beispiel:

```text
storage/users/12/tools/48/source/original.jpg
storage/users/12/tools/48/processed/perspective_corrected.png
storage/users/12/tools/48/masks/tool_mask.png
storage/users/12/tools/48/previews/layout_preview.svg
storage/users/12/tools/48/exports/kombizange_gridfinity.svg
```

---

## Installation

Die folgenden Schritte beschreiben die geplante lokale Entwicklungsinstallation.

### Voraussetzungen

* Python 3.11 oder neuer
* Git
* pip
* optional PostgreSQL
* optional Redis für spätere Hintergrundjobs

### Repository klonen

```bash
git clone https://github.com/<username>/ToolTrace.git
cd ToolTrace
```

### Virtuelle Umgebung erstellen

Linux und macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Abhängigkeiten installieren

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### Konfiguration anlegen

```bash
cp .env.example .env
```

Unter Windows:

```powershell
Copy-Item .env.example .env
```

Anschließend die Werte in `.env` anpassen.

Beispiel:

```env
FLASK_ENV=development
SECRET_KEY=change-me
DATABASE_URL=sqlite:///tooltrace.sqlite3

STORAGE_PATH=storage
MAX_UPLOAD_SIZE_MB=20

ALLOWED_IMAGE_TYPES=jpg,jpeg,png
MIN_IMAGE_WIDTH=1200
MIN_IMAGE_HEIGHT=1200

PROCESSING_PIXELS_PER_MM=10
DEFAULT_CONTOUR_OFFSET_MM=1.5
DEFAULT_CONTOUR_SIMPLIFICATION_MM=0.2

DEFAULT_LAYOUT_TYPE=gridfinity
GRIDFINITY_UNIT_MM=42
DEFAULT_LAYOUT_MARGIN_MM=5

SEGMENTATION_BACKEND=opencv
```

### Datenbank initialisieren

```bash
flask db upgrade
```

### Anwendung starten

```bash
flask run
```

Alternativ:

```bash
python run.py
```

Die Anwendung ist anschließend standardmäßig unter folgender Adresse erreichbar:

```text
http://127.0.0.1:5000
```

---

## Beispiel für die SVG-Ausgabe

ToolTrace soll SVG-Dateien mit realen Millimeterabmessungen erzeugen.

```xml
<svg
    xmlns="http://www.w3.org/2000/svg"
    width="126mm"
    height="84mm"
    viewBox="0 0 126 84">

    <g id="layout-border">
        <rect
            x="0"
            y="0"
            width="126"
            height="84"
            fill="none"
            stroke="black" />
    </g>

    <g id="production-contour">
        <path
            d="M 12.4 18.2 L 13.0 18.0 L 14.1 17.8 Z"
            fill="none"
            stroke="black" />
    </g>
</svg>
```

Geplante SVG-Gruppen:

```text
metadata
layout-border
grid
original-contour
production-contour
inner-contours
labels
dimensions
```

---

## Geplante API-Endpunkte

### Werkzeuge

```text
GET    /api/tools
POST   /api/tools
GET    /api/tools/<id>
PATCH  /api/tools/<id>
DELETE /api/tools/<id>
```

### Bilder

```text
POST /api/tools/<id>/images
GET  /api/tools/<id>/images
```

### Verarbeitung

```text
POST /api/tools/<id>/process
GET  /api/processing-jobs/<id>
POST /api/processing-jobs/<id>/retry
```

### Konturen

```text
GET   /api/tools/<id>/contours
GET   /api/contours/<id>
PATCH /api/contours/<id>
POST  /api/contours/<id>/offset
POST  /api/contours/<id>/smooth
POST  /api/contours/<id>/align
```

### Layouts

```text
POST  /api/tools/<id>/layouts
GET   /api/layouts/<id>
PATCH /api/layouts/<id>
```

### Export

```text
POST /api/layouts/<id>/exports/svg
GET  /api/exports/<id>/download
```

---

## Entwicklungsphasen

### Phase 1: Projektgrundlage

* Flask Application Factory
* Blueprints
* Konfiguration
* SQLAlchemy
* Alembic
* Benutzerregistrierung
* Anmeldung und Abmeldung
* Basistemplates

### Phase 2: Werkzeugbibliothek

* Werkzeugmodell
* Werkzeugkategorien
* Metadaten
* Bibliotheksansicht
* Werkzeugdetailseite

### Phase 3: Bild-Upload

* sicherer Upload
* Dateivalidierung
* Dateispeicher
* Vorschaubilder
* Upload-Metadaten

### Phase 4: DIN-A4-Erkennung

* Blatterkennung
* Eckpunkterkennung
* Perspektivkorrektur
* Millimeterskalierung

### Phase 5: Werkzeugsegmentierung

* OpenCV-Segmentierung
* Maskenbereinigung
* Außenkontur
* Innenkonturen

### Phase 6: Konturbearbeitung

* Konturglättung
* Vereinfachung
* Ausrichtung
* Konturversatz
* Konturversionen

### Phase 7: Layout

* freies Rechteck
* Gridfinity-Raster
* automatische Rasterberechnung
* Positionierung

### Phase 8: Vorschau und Export

* SVG-Vorschau
* SVG-Export
* Download
* Speicherung der Exporte

### Phase 9: Qualität und Tests

* Bildqualitätsprüfung
* Fehlermeldungen
* Testbilder
* automatisierte Tests
* Dokumentation

---

## Tests

Geplante Testbereiche:

### Unit-Tests

* Pixel-zu-Millimeter-Umrechnung
* Gridfinity-Rasterberechnung
* Konturversatz
* automatische Ausrichtung
* Dateivalidierung
* Benutzerrechte

### Bildverarbeitungstests

Testbilder für:

* Hammer
* Zange
* Schraubenschlüssel
* Schraubendreher
* Säge
* Werkzeug mit Innenkontur
* dunkles Werkzeug
* glänzendes Werkzeug
* unscharfes Bild
* unvollständiges DIN-A4-Blatt
* starke Perspektive
* starke Schatten

### Integrationstests

* Benutzer registrieren
* Benutzer anmelden
* Werkzeug anlegen
* Bild hochladen
* Verarbeitung starten
* Kontur speichern
* Layout erzeugen
* SVG exportieren
* Benutzer voneinander trennen

Tests ausführen:

```bash
pytest
```

---

## Sicherheitsanforderungen

ToolTrace verarbeitet vom Benutzer hochgeladene Dateien. Daher sind unter anderem folgende Maßnahmen erforderlich:

* Dateiformate serverseitig prüfen
* MIME-Type und tatsächlichen Dateiinhalt prüfen
* Dateigröße begrenzen
* Bildabmessungen begrenzen
* sichere interne Dateinamen verwenden
* Upload-Dateien außerhalb ausführbarer Verzeichnisse speichern
* Benutzerzugriff auf alle Datensätze prüfen
* CSRF-Schutz verwenden
* Passwörter sicher hashen
* keine ungeprüften SVG-Dateien direkt darstellen
* serverseitig erzeugte SVG-Dateien verwenden
* Verarbeitungsdauer begrenzen
* Speicherverbrauch überwachen
* Fehlermeldungen ohne interne Serverpfade ausgeben

---

## Akzeptanzkriterien für das MVP

Das MVP gilt als funktionsfähig, wenn folgender Ablauf vollständig möglich ist:

1. Ein Benutzer registriert sich.
2. Der Benutzer meldet sich an.
3. Der Benutzer legt ein neues Werkzeug an.
4. Der Benutzer lädt ein Bild mit einem Werkzeug auf einem DIN-A4-Blatt hoch.
5. ToolTrace erkennt das Blatt.
6. ToolTrace korrigiert die Perspektive.
7. ToolTrace segmentiert das Werkzeug.
8. ToolTrace erzeugt eine geschlossene Kontur.
9. ToolTrace berechnet die reale Größe in Millimetern.
10. ToolTrace richtet die Kontur automatisch aus.
11. Der Benutzer stellt einen Konturversatz ein.
12. ToolTrace berechnet ein passendes Gridfinity-Raster.
13. Der Benutzer sieht eine maßhaltige Vorschau.
14. Der Benutzer speichert das Werkzeug in seiner Bibliothek.
15. Der Benutzer lädt die Kontur als SVG-Datei herunter.
16. Der Benutzer kann das Werkzeug später erneut öffnen und exportieren.

---

## Geplante Erweiterungen

* mehrere Werkzeuge auf einem Bild
* KI-basierte Werkzeugklassifikation
* automatische Hersteller- oder Modellerkennung
* gemeinsame Shadowboard-Layouts
* Nesting und automatische Platzoptimierung
* Fingeraussparungen
* Griffmulden
* Werkzeugbeschriftungen
* QR-Codes
* Data-Matrix-Codes
* DXF-Export
* PDF-Export
* OpenSCAD-Export
* STL-Erzeugung
* Gridfinity-Bin-Erzeugung
* direkte CAM-Ausgabe
* gemeinsame Werkstattbibliotheken
* Team- und Rollenverwaltung
* öffentliche Werkzeugvorlagen
* Freigabelinks
* REST-API
* React- oder Vue-Frontend
* mobile Aufnahmehilfe

---

## Mitwirken

Beiträge zum Projekt sind willkommen.

Mögliche Beitragsbereiche:

* Python- und Flask-Entwicklung
* OpenCV-Bildverarbeitung
* KI-Segmentierung
* SVG- und Geometrieverarbeitung
* Frontend und Benutzerführung
* Testbilder und Testszenarien
* Dokumentation
* Übersetzungen
* Gridfinity- und Shadowboard-Funktionen

Für größere Änderungen sollte zunächst ein Issue erstellt werden, in dem die geplante Änderung beschrieben wird.

Typischer Ablauf:

```bash
git checkout -b feature/meine-funktion
git commit -m "Add meine Funktion"
git push origin feature/meine-funktion
```

Anschließend kann ein Pull Request erstellt werden.

---

## Hinweise für Entwicklung mit CodeX

Die Entwicklung sollte schrittweise erfolgen.

Im ersten Schritt soll CodeX nur folgende Grundlage erstellen:

* Flask Application Factory
* Blueprint-Struktur
* SQLAlchemy-Modelle
* Alembic-Migrationen
* Flask-Login
* Registrierung
* Anmeldung
* Abmeldung
* Werkzeugmodell
* Kategorien
* Werkzeugbibliothek
* Werkzeugformular
* sicherer Bild-Upload
* Speicherung der Upload-Metadaten
* Platzhalter für die Verarbeitungspipeline
* Platzhalter für Kontur-, Layout- und Exportservices
* automatisierte Basistests
* lokale Installationsanleitung

Die eigentliche OpenCV-Konturerkennung soll erst implementiert werden, wenn die Projektgrundlage getestet und stabil ist.

---

## Lizenz

Die Lizenz des Projekts ist noch festzulegen.

Für ein Open-Source-Projekt kommen beispielsweise folgende Lizenzen infrage:

* MIT License
* Apache License 2.0
* GNU General Public License v3.0

Vor der Veröffentlichung sollte eine passende `LICENSE`-Datei ergänzt werden.

---

## Haftungsausschluss

ToolTrace befindet sich in Entwicklung.

Erzeugte Konturen und Maße müssen vor der Fertigung geprüft werden. Bildfehler, Perspektivfehler, Schatten, Reflexionen oder eine ungenaue Segmentierung können zu abweichenden Konturen führen.

Die Software übernimmt keine Gewähr für:

* Maßhaltigkeit
* Fertigungstauglichkeit
* Materialeignung
* Maschinenkompatibilität
* sichere Verwendung erzeugter Dateien

Vor dem Fräsen, Schneiden oder Lasern sollte jede exportierte Datei in der verwendeten CAD-, CAM- oder Fertigungssoftware kontrolliert werden.

---

## Name und Bedeutung

Der Name **ToolTrace** setzt sich aus folgenden Begriffen zusammen:

* **Tool** – Werkzeug
* **Trace** – Kontur erfassen oder nachzeichnen

Der Name beschreibt damit die zentrale Aufgabe der Anwendung:

> Aus einem Werkzeugfoto wird eine bearbeitbare und maßhaltige Werkzeugkontur.
