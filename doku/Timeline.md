# ToolTrace Timeline

## 0.5.3 - 2026-07-05

### Geaendert

* Werkzeugkonturen koennen auf der Detailseite manuell ueber eine vom User gewaehlte Kante ausgerichtet werden.
* Die manuelle Ausrichtung erzeugt eine neue aktive Kontur-Version und berechnet die Bounding Box danach neu.
* Optionales Rastermass wird als gerundete Raster-Bounding-Box in den Konturdaten gespeichert.

## 0.5.2 - 2026-07-05

### Geaendert

* Hintergrunderkennung erkennt Leuchttisch-Fotos robuster ueber die grosse helle Flaeche im unterbelichteten Umfeld.
* Bestehende Kantenkontur-Erkennung bleibt als Fallback fuer normale Hintergrundfotos erhalten.
* Regressionstest fuer unterbelichtete Leuchttischaufnahme mit heller Hintergrundflaeche ergaenzt.

## 0.5.1 - 2026-07-05

### Geaendert

* User koennen in den Einstellungen die Masse fuer Leuchttisch-Hintergruende A3, A4 und A5 pflegen.
* Foto-Uploads enthalten eine Auswahlbox fuer die Hintergrundgroesse.
* Blatterkennung, Perspektivkorrektur und Millimeterskalierung verwenden die beim Upload gewaehlten Hintergrundmasse.
* Bildlisten zeigen den beim Upload verwendeten Hintergrund mit Groesse an.

## 0.5.0 - 2026-07-04

### Geaendert

* Erkannte Aussenkontur wird in ein eigenes Werkzeug-Koordinatensystem ueberfuehrt.
* Kontur wird ueber die minimale rotierte Bounding Box ausgerichtet, die lange Achse liegt parallel zur X-Achse.
* Ursprung der Konturgeometrie liegt links unten; alle gespeicherten Koordinaten sind positive Millimeterwerte.
* Originale Pixelkontur bleibt als Quellreferenz in den Geometriedaten erhalten.

## 0.4.0 - 2026-07-04

### Geaendert

* Konturerkennung fuer die aeussere Werkzeugkontur umgesetzt.
* Erkannte Aussenkontur wird als rot gefuellte Flaeche mit 30% Transparenz im Werkzeugbild angezeigt.
* Innere Artefakte innerhalb der Aussenkontur werden bei der Konturvorschau ignoriert.
* Verarbeitungspipeline speichert das Kontur-Overlay und einen aktiven Konturdatensatz.

## 0.3.3 - 2026-07-04

### Geaendert

* Randartefakte am DIN-A4-Blatt werden vor der Konturermittlung aus der Werkzeugmaske entfernt.
* Regressionstest fuer schmale Artefakte am Blattrand ergaenzt.

## 0.3.2 - 2026-07-04

### Geaendert

* OpenCV-Segmentierung reduziert den Einfluss weicher Schatten um Werkzeuge.
* Dunkle Werkzeugbereiche werden nach Beleuchtungskorrektur ueber lokale Kantenunterstuetzung wieder aufgenommen.
* Regressionstest fuer Schraubendreher mit seitlichem Schatten ergaenzt.

## 0.3.1 - 2026-07-04

### Geaendert

* OpenCV-Segmentierung fuer realistische Schraubendreherfotos nachjustiert.
* Hintergrund wird robuster aus dem A4-Blatt geschaetzt, statt mit einem festen Helligkeitswert zu arbeiten.
* Maskenbereinigung erhaelt duenne Werkzeugbereiche besser und filtert Randartefakte staerker aus.

## 0.3.0 - 2026-07-04

### Geaendert

* Erste OpenCV-basierte Werkzeugsegmentierung auf dem perspektivisch entzerrten DIN-A4-Bild umgesetzt.
* Bereinigte Werkzeugmaske wird im Werkzeugordner unter `masks/` gespeichert.
* Pipeline aktualisiert Job-Status, Segmentierungs-Score und erzeugt eine Maskenvorschau.
* Werkzeugdetailseite zeigt die bereinigte Werkzeugmaske an.

## 0.2.3 - 2026-07-04

### Geaendert

* Perspektivkorrektur fuer erkannte DIN-A4-Blaetter umgesetzt.
* Entzerrtes DIN-A4-Bild wird in konfigurierter Pixel-pro-Millimeter-Skalierung gespeichert.
* Werkzeugdetailseite zeigt die perspektivisch korrigierte Vorschau an.

## 0.2.2 - 2026-07-04

### Geaendert

* Erkannte DIN-A4-Fläche in der Verarbeitungsvorschau mit transparenter gruener Flaechenmarkierung hervorgehoben; Deckkraft auf 30 Prozent gesetzt.

## 0.2.1 - 2026-07-04

### Geaendert

* Loeschbutton fuer Werkzeuge in Bibliothek und Detailseite ergaenzt.
* Werkzeugloeschung entfernt neben dem Datensatz auch Uploads, verarbeitete Bilder und weitere Dateien aus dem Werkzeugordner.
* Loeschaktion prueft weiterhin den angemeldeten Besitzer des Werkzeugs.

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
