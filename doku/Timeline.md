# ToolTrace Timeline

## 0.2.0 - 2026-07-04

### Geaendert

* Erste OpenCV-basierte DIN-A4-Erkennung fuer hochgeladene Werkzeugbilder umgesetzt.
* Verarbeitungspipeline fuehrt die Blatterkennung nach dem Upload synchron aus.
* Vorschau mit markierter Blattkontur und Eckpunkten wird unter `processed/` gespeichert.
* Werkzeugdetailseite zeigt den aktuellen Status und Score der DIN-A4-Erkennung an.
* Geschuetzte Route fuer verarbeitete Vorschaubilder ergaenzt.
* OpenCV und NumPy als Bildverarbeitungsabhaengigkeiten aufgenommen.

## 0.1.1 - 2026-07-04

### Geaendert

* Thumbnails fuer hochgeladene Werkzeugbilder in Werkzeugbibliothek und Werkzeugdetailseite ergaenzt.
* Geschuetzte Bildroute fuer eigene Werkzeugbilder angelegt.

## 0.1.0 - 2026-07-04

Erste technische Grundversion von ToolTrace.

### Geaendert

* Flask-Anwendung mit Application Factory angelegt.
* Blueprints fuer Authentifizierung, Dashboard, Werkzeuge, API, Layouts, Exporte und Administration angelegt.
* SQLAlchemy-Modelle und Alembic-Initialmigration erstellt.
* Registrierung, Anmeldung und Abmeldung umgesetzt.
* Werkzeugbibliothek und Werkzeuganlage umgesetzt.
* Bild-Upload mit Metadatenspeicherung vorbereitet.
* Platzhalter fuer Processing-Pipeline, Kontur-, Layout- und Exportservices erstellt.
* Footer mit ToolTrace-Version, Impressum und Datenschutz ergaenzt.
* Version zentral in `version.py` gespeichert.
* Automatisierte Basistests eingerichtet.
* Upload-Validierung angepasst: kleine Bilder werden gespeichert und als Warnung markiert, statt den Upload hart abzubrechen.
* Werkzeuganlage vereinfacht: nur das Foto ist Pflichtfeld, alle anderen Metadaten sind optional und koennen spaeter ergaenzt werden.
