# ToolTrace: Vom Bild zur SVG

Diese Anleitung beschreibt, wie ein Werkzeugfoto in ToolTrace aufbereitet wird und welche automatischen Bearbeitungsschritte daraus eine masshaltige Kontur vorbereiten. Sie ist fuer Einsteiger gedacht und erklaert deshalb auch, warum die einzelnen Schritte notwendig sind.

Wichtig: Der aktuelle Stand erzeugt bereits eine erkannte Aussenkontur in Millimeter-Koordinaten. Ein echter SVG-Export dieser Werkzeugkontur ist noch nicht fertig umgesetzt. Vorhanden ist bisher ein SVG-Grundrahmen fuer Layouts. Die Konturdaten sind aber so gespeichert, dass sie im naechsten Ausbauschritt in eine SVG-Kontur geschrieben werden koennen.

## Ziel des Workflows

Aus einem Foto soll eine verwertbare 2D-Kontur entstehen:

1. Werkzeug fotografieren.
2. Bild hochladen.
3. DIN-A4-Blatt erkennen.
4. Perspektive korrigieren.
5. Werkzeug vom Blatt trennen.
6. Maske bereinigen.
7. Aussenkontur finden.
8. Kontur in Millimeter umrechnen.
9. Kontur ausrichten.
10. Spaeter: Kontur als SVG exportieren.

Das DIN-A4-Blatt dient dabei als Massreferenz. Da ein DIN-A4-Blatt immer 210 mm x 297 mm gross ist, kann ToolTrace aus den Bildpixeln echte Millimeter berechnen.

## 1. Foto vorbereiten

Lege ein einzelnes Werkzeug auf ein weisses DIN-A4-Blatt.

Das Foto sollte so aufgenommen werden:

* Das komplette DIN-A4-Blatt ist sichtbar.
* Alle vier Blattkanten und Ecken sind im Bild.
* Das Werkzeug liegt vollstaendig auf dem Blatt.
* Es liegt nur ein Werkzeug auf dem Blatt.
* Der Hintergrund ausserhalb des Blatts stoert moeglichst wenig.
* Das Bild ist scharf und gut beleuchtet.
* Harte Schatten, Spiegelungen und sehr dunkle Raender werden moeglichst vermieden.
* Das Werkzeug beruehrt den Blattrand nicht.

Warum das wichtig ist:

ToolTrace sucht zuerst das DIN-A4-Blatt. Wenn das Blatt abgeschnitten, stark verdeckt oder kaum vom Hintergrund unterscheidbar ist, kann die automatische Verarbeitung nicht sicher starten. Danach sucht ToolTrace das Werkzeug innerhalb des entzerrten Blatts. Werkzeuge am Blattrand koennen deshalb als Randartefakt entfernt werden.

## 2. Erlaubte Bilddateien

Beim Upload werden aktuell JPEG- und PNG-Dateien akzeptiert.

Die wichtigsten Upload-Regeln:

* Erlaubte Dateitypen: `jpg`, `jpeg`, `png`
* Maximale Uploadgroesse: standardmaessig `20 MB`
* Empfohlene Mindestaufloesung: `1200 x 1200 px`

Kleinere Bilder werden nicht automatisch abgelehnt. ToolTrace speichert sie, zeigt aber eine Warnung an. Fuer eine saubere Kontur sind groessere, scharfe Bilder besser.

Beim Speichern wird das Bild mit Pillow geprueft. Ausserdem wird die EXIF-Orientierung angewendet. Das ist wichtig bei Smartphone-Fotos, weil diese oft gedreht gespeichert sind und die Drehung nur in Metadaten steht.

Die Originaldatei wird im Werkzeugordner abgelegt:

```text
storage/users/<user_id>/tools/<tool_id>/source/
```

## 3. Automatische Verarbeitung nach dem Upload

Nach dem Upload legt ToolTrace einen Verarbeitungsauftrag an und fuehrt die Pipeline aus. Die Pipeline arbeitet synchron, also direkt waehrend des Upload-Ablaufs.

Die technischen Pipeline-Schritte heissen:

```text
validate_image
detect_page
correct_perspective
segment_tool
clean_mask
extract_contours
convert_to_mm
align_contour
generate_preview
completed
```

Einige dieser Namen sind Statusnamen. Die konkrete Verarbeitung ist aktuell in folgenden Codepfaden umgesetzt:

* `app/processing/page_detection.py`
* `app/processing/perspective.py`
* `app/processing/segmentation/opencv_backend.py`
* `app/processing/mask_cleanup.py`
* `app/processing/contour_extraction.py`

## 4. DIN-A4-Blatt erkennen

Zuerst sucht ToolTrace das DIN-A4-Blatt im Foto.

Bearbeitungsschritte:

1. Bild mit OpenCV laden.
2. Fuer die Analyse auf maximal `1600 px` an der laengsten Seite verkleinern.
3. In Graustufen umwandeln.
4. Mit Gaussian Blur glaetten.
5. Kanten mit Canny erkennen.
6. Aeussere Konturen suchen.
7. Vierseitige, konvexe Flaechen bewerten.
8. Die beste Flaeche als DIN-A4-Blatt verwenden.

Wichtige Parameter:

| Parameter | Wert | Bedeutung |
| --- | ---: | --- |
| Maximale Analyseseite | `1600 px` | Grosse Fotos werden fuer die Suche verkleinert. |
| Gaussian Blur | `5 x 5` | Reduziert Bildrauschen vor der Kantensuche. |
| Canny-Untergrenze | `50` | Unterer Schwellwert fuer Kanten. |
| Canny-Obergrenze | `150` | Oberer Schwellwert fuer Kanten. |
| Mindestflaeche | `8 %` des Analysebildes | Sehr kleine Rechtecke werden ignoriert. |
| Konturvereinfachung | `0.02 * Umfang` | Sucht eine vereinfachte Kontur mit vier Ecken. |
| Erwartetes Seitenverhaeltnis | `210 / 297` | Entspricht DIN A4 im Hochformat. |
| Mindestscore | `0.55` | Darunter gilt das Blatt als nicht sicher erkannt. |

Wenn ein Blatt erkannt wird, erzeugt ToolTrace eine Vorschau:

```text
storage/users/<user_id>/tools/<tool_id>/processed/page_detected_job_<job_id>.png
```

In dieser Vorschau wird das erkannte Blatt gruen markiert. Die gruene Flaeche hat `30 %` Deckkraft, die Blattkontur wird gruen gezeichnet und die vier Ecken werden nummeriert.

## 5. Perspektive korrigieren

Ein Foto wird fast nie exakt von oben aufgenommen. Deshalb sieht das DIN-A4-Blatt im Foto oft trapezfoermig aus. ToolTrace entzerrt das erkannte Blatt so, dass daraus wieder ein rechteckiges DIN-A4-Bild wird.

Bearbeitungsschritte:

1. Die vier erkannten Blattecken werden als Ausgangspunkte verwendet.
2. ToolTrace prueft, ob das Blatt im Foto eher hoch oder quer liegt.
3. Die Zielgroesse wird auf DIN A4 gesetzt.
4. Mit `cv2.getPerspectiveTransform` wird die Transformationsmatrix berechnet.
5. Mit `cv2.warpPerspective` wird das Bild entzerrt.

Wichtige Parameter:

| Parameter | Wert | Bedeutung |
| --- | ---: | --- |
| DIN-A4-Breite Hochformat | `210.0 mm` | Physische Blattbreite. |
| DIN-A4-Hoehe Hochformat | `297.0 mm` | Physische Blatthoehe. |
| Pixel pro Millimeter | standardmaessig `10` | Bestimmt die Aufloesung des entzerrten Bildes. |

Bei `10 px/mm` entsteht fuer ein hochformatiges DIN-A4-Blatt ein Bild mit ungefaehr:

```text
2100 x 2970 px
```

Das perspektivisch korrigierte Bild wird gespeichert unter:

```text
storage/users/<user_id>/tools/<tool_id>/processed/perspective_corrected_job_<job_id>.png
```

## 6. Werkzeug segmentieren

Nach der Perspektivkorrektur sucht ToolTrace das Werkzeug auf dem weissen Blatt. Dafuer wird aktuell der OpenCV-Backend verwendet.

Ziel dieses Schritts:

Aus dem farbigen Bild soll eine Schwarz-Weiss-Maske entstehen. Weiss bedeutet: hier ist wahrscheinlich Werkzeug. Schwarz bedeutet: hier ist Hintergrund.

Bearbeitungsschritte:

1. Bild in Graustufen, HSV und LAB umwandeln.
2. Beleuchtung im Graustufenbild normalisieren.
3. Hintergrundfarbe aus den Blattbereichen am Rand schaetzen.
4. Dunkle Bereiche erkennen.
5. Farblich auffaellige Bereiche erkennen.
6. Gesaettigte Bereiche erkennen.
7. Kantenunterstuetzte dunkle Bereiche ergaenzen.
8. Randbereiche des Blatts entfernen.
9. Blattkanten-Artefakte entfernen.
10. Maske bereinigen.

Wichtige Parameter:

| Parameter | Wert | Bedeutung |
| --- | ---: | --- |
| Beleuchtungskorrektur-Kernel | max. aus `51` und `9 %` der kurzen Bildseite | Gleicht weiche Helligkeitsunterschiede aus. |
| Hintergrundrand fuer LAB-Samples | max. aus `10 px` und `8 %` der kurzen Bildseite | Dort wird die Blattfarbe geschaetzt. |
| Dunkelgrenze | zwischen `152` und `198` | Wird aus der normalisierten Hintergrundhelligkeit abgeleitet. |
| Sehr-dunkel-Grenze | `158` | Nimmt sehr dunkle Werkzeugteile sicher auf. |
| LAB-Farbabstand | `> 38` | Erkennt Bereiche, die farblich vom Blatt abweichen. |
| LAB-Chroma-Abstand | `> 16` | Erkennt farbige Werkzeugteile. |
| HSV-Saettigung | `> 60` | Erkennt gesaettigte Farben. |
| Canny fuer Kantenhilfe | `18` bis `60` | Hilft bei dunklen Kanten und Schattenbereichen. |
| Kanten-Dilatation | Ellipse `11 x 11`, `1` Iteration | Erweitert Kantenbereiche leicht. |
| Aeusserer Maskenrand | max. aus `8 px` und `4 %` der kurzen Bildseite | Wird vor der Bereinigung auf Hintergrund gesetzt. |
| Randartefakt-Marge | max. aus `12 px` und `7 %` der kurzen Bildseite | Entfernt Stoerungen an Blattkanten. |

Die Segmentierung erzeugt noch keine Kontur, sondern zuerst eine Maske. Diese Maske wird im naechsten Schritt bereinigt.

## 7. Maske bereinigen

Die Rohmaske kann kleine Stoerungen enthalten, zum Beispiel Schattenreste, Staubpunkte oder Kantenreste. Die Maskenbereinigung versucht, daraus eine stabilere Werkzeugmaske zu machen.

Bearbeitungsschritte:

1. Alle Maskenwerte werden auf Schwarz oder Weiss gesetzt.
2. Kleine Loecher werden mit einer morphologischen Schliessung reduziert.
3. Kleine Stoerpunkte werden mit einer morphologischen Oeffnung reduziert.
4. Zusammenhaengende Bildbereiche werden gesucht.
5. Zu kleine, zu grosse und randberuehrende Bereiche werden verworfen.
6. Die groessten plausiblen Bereiche bleiben erhalten.

Wichtige Parameter:

| Parameter | Wert | Bedeutung |
| --- | ---: | --- |
| Schliessen-Kernel | `5 x 5` | Fuellt kleine Luecken in der Werkzeugmaske. |
| Schliessen-Iterationen | `1` | Ein Durchlauf. |
| Oeffnen-Kernel | `3 x 3` | Entfernt kleine Einzelstoerungen. |
| Oeffnen-Iterationen | `1` | Ein Durchlauf. |
| Komponentenverbindung | `8` | Pixel gelten auch diagonal als verbunden. |
| Randabstand | max. aus `8 px` und `2.5 %` der kurzen Bildseite | Bereiche am Rand werden verworfen. |
| Mindestflaeche | max. aus `250 px` und `0.035 %` der Bildflaeche | Sehr kleine Bereiche werden ignoriert. |
| Maximalflaeche | `45 %` der Bildflaeche | Sehr grosse Bereiche werden ignoriert. |
| Behaltene Nebenbereiche | mindestens `4 %` der groessten Flaeche | Erlaubt mehrere plausible Werkzeugteile. |

Die bereinigte Maske wird gespeichert unter:

```text
storage/users/<user_id>/tools/<tool_id>/masks/cleaned_mask_job_<job_id>.png
```

## 8. Aussenkontur extrahieren

Aus der bereinigten Maske wird die Aussenkontur des Werkzeugs berechnet.

Bearbeitungsschritte:

1. Maske laden.
2. Maske erneut binaer machen.
3. Aeussere Konturen mit OpenCV suchen.
4. Die groesste Kontur als Werkzeug-Aussenkontur verwenden.
5. Flaeche und Umfang in Pixeln berechnen.
6. Die Kontur als rote Flaeche ueber das Werkzeugbild legen.
7. Die Kontur in Millimeter umrechnen.

Wichtige Parameter:

| Parameter | Wert | Bedeutung |
| --- | ---: | --- |
| Konturmodus | `cv2.RETR_EXTERNAL` | Es werden nur aeussere Konturen gesucht. |
| Konturapproximation | `cv2.CHAIN_APPROX_SIMPLE` | Speichert Konturpunkte kompakter. |
| Auswahl | groesste Flaeche | Die groesste gefundene Kontur gilt als Werkzeug. |
| Overlay-Farbe | Rot | Markiert die erkannte Aussenkontur. |
| Overlay-Deckkraft | `30 %` | Das Originalbild bleibt sichtbar. |

Die Overlay-Vorschau wird gespeichert unter:

```text
storage/users/<user_id>/tools/<tool_id>/contours/outer_contour_overlay_job_<job_id>.png
```

## 9. Kontur in Millimeter umrechnen

Die Kontur entsteht zuerst in Pixelkoordinaten. Da die Perspektivkorrektur das DIN-A4-Blatt auf eine bekannte Groesse skaliert hat, kann ToolTrace Pixel in Millimeter umrechnen.

Standardwert:

```text
PROCESSING_PIXELS_PER_MM = 10
```

Damit gilt:

```text
1 mm = 10 px
1 px = 0.1 mm
```

ToolTrace berechnet daraus:

* Breite in mm
* Hoehe in mm
* Flaeche in mm2
* Umfang in mm
* Konturpunkte in mm

Beispiele fuer die Umrechnung:

```text
width_mm = width_px / pixels_per_mm
height_mm = height_px / pixels_per_mm
area_mm2 = area_px / (pixels_per_mm * pixels_per_mm)
perimeter_mm = perimeter_px / pixels_per_mm
```

## 10. Kontur ausrichten

Damit die Kontur spaeter sinnvoll in ein Layout oder eine SVG-Datei geschrieben werden kann, wird sie in ein eigenes Werkzeug-Koordinatensystem ueberfuehrt.

Bearbeitungsschritte:

1. Aus der Kontur wird die kleinste rotierte Bounding Box berechnet.
2. Die laengste Kante dieser Box bestimmt die Ausrichtung.
3. Die Kontur wird so gedreht, dass die lange Achse parallel zur X-Achse liegt.
4. Die Kontur wird auf positive Koordinaten verschoben.
5. Der Ursprung liegt danach links unten.
6. X zeigt nach rechts, Y zeigt nach oben.

Das gespeicherte Geometrieformat enthaelt unter anderem:

```text
type: outer_contour
coordinate_space: tool_mm
origin: bottom_left
axis: x right, y up
alignment method: min_area_rect_long_axis
points_mm: Konturpunkte in Millimeter
bounding_box_mm: Breite und Hoehe der ausgerichteten Kontur
source_contour_px: originale Pixelkontur als Referenz
```

Die Ausrichtungsvorschau wird gespeichert unter:

```text
storage/users/<user_id>/tools/<tool_id>/contours/aligned_outer_contour_job_<job_id>.png
```

In dieser Vorschau sieht man:

* die ausgerichtete rote Kontur
* die Bounding Box
* den Nullpunkt
* X- und Y-Achse

## 11. Aktueller Stand des SVG-Exports

Der echte Export der erkannten Werkzeugkontur als SVG ist noch nicht fertig.

Aktuell vorhanden ist ein SVG-Grundrahmen:

```text
app/exports/svg_export.py
```

Dieser Service erzeugt ein leeres SVG mit Millimeter-Massen:

```xml
<svg width="126mm" height="84mm" viewBox="0 0 126 84">
  <title>Kombizange</title>
  <g id="layout-border">
    <rect x="0" y="0" width="126" height="84" fill="none" stroke="black"/>
  </g>
</svg>
```

Das bedeutet:

* Die SVG-Datei verwendet Millimeter als reale Einheit.
* Die `viewBox` entspricht denselben Zahlenwerten in mm.
* Ein Layout-Rahmen kann bereits ausgegeben werden.
* Die erkannte Werkzeugkontur wird noch nicht als SVG-Pfad geschrieben.

## 12. Vorgesehener SVG-Schritt

Die Kontur liegt bereits als Liste von Millimeterpunkten vor. Fuer einen echten SVG-Export muss daraus ein SVG-Pfad oder Polygon erzeugt werden.

Grundidee:

1. `points_mm` aus der aktiven Kontur lesen.
2. Optional Kontur vereinfachen.
3. Optional Konturversatz anwenden.
4. Layoutgroesse berechnen.
5. Punkte in SVG-Koordinaten umsetzen.
6. Pfad oder Polygon in die SVG-Datei schreiben.

Wichtige vorbereitete Standardwerte:

| Parameter | Standardwert | Zweck |
| --- | ---: | --- |
| `DEFAULT_CONTOUR_OFFSET_MM` | `1.5` | Vorgesehener Abstand um die Werkzeugkontur. |
| `DEFAULT_CONTOUR_SIMPLIFICATION_MM` | `0.2` | Vorgesehene Vereinfachung der Konturpunkte. |
| `DEFAULT_LAYOUT_TYPE` | `gridfinity` | Standardlayouttyp. |
| `GRIDFINITY_UNIT_MM` | `42` | Gridfinity-Rastermass. |
| `DEFAULT_LAYOUT_MARGIN_MM` | `5` | Standardrand um die Kontur. |

Diese Werte sind konfiguriert, aber der vollstaendige SVG-Exportpfad fuer Werkzeugkonturen ist noch nicht angebunden.

## 13. Layoutberechnung

ToolTrace enthaelt bereits einfache Layout-Helfer.

Freies Rechteck:

```text
layout_width = contour_width + margin_left + margin_right
layout_height = contour_height + margin_top + margin_bottom
```

Gridfinity:

```text
grid_x = ceil(contour_width_mm / grid_unit_mm)
grid_y = ceil(contour_height_mm / grid_unit_mm)
layout_width = grid_x * grid_unit_mm
layout_height = grid_y * grid_unit_mm
```

Mit dem Standardwert `42 mm` entsteht also immer eine Layoutgroesse, die auf volle Gridfinity-Zellen aufgerundet ist.

## 14. Woran erkennt man ein gutes Ergebnis?

Ein gutes Ergebnis sieht in ToolTrace so aus:

* Die DIN-A4-Vorschau markiert genau das Blatt.
* Die Perspektivkorrektur zeigt ein gerade entzerrtes Blatt.
* Die Werkzeugmaske zeigt nur das Werkzeug, nicht den Blattrand.
* Die rote Aussenkontur deckt die Werkzeugform plausibel ab.
* Die ausgerichtete Vorschau zeigt die Kontur vollstaendig in einer Bounding Box.
* Breite und Hoehe in Millimeter wirken realistisch.

Wenn das Ergebnis schlecht ist, sollte zuerst das Foto verbessert werden. Besonders wichtig sind ein voll sichtbares DIN-A4-Blatt, gute Beleuchtung und Abstand des Werkzeugs zum Blattrand.

## 15. Typische Probleme und Ursachen

### DIN-A4-Blatt wird nicht erkannt

Moegliche Ursachen:

* Eine oder mehrere Blattecken fehlen.
* Das Blatt hebt sich zu wenig vom Hintergrund ab.
* Das Foto ist unscharf.
* Andere rechteckige Objekte im Bild stoeren.
* Das Blatt ist zu klein im Foto.

### Werkzeugmaske ist leer

Moegliche Ursachen:

* Das Werkzeug hat zu wenig Kontrast zum Blatt.
* Das Werkzeug ist sehr hell oder weiss.
* Das Bild ist ueberbelichtet.
* Schatten wurden staerker erkannt als das Werkzeug.

### Zu viel wird als Werkzeug erkannt

Moegliche Ursachen:

* Harte Schatten liegen direkt am Werkzeug.
* Der Hintergrund oder Blattrand ist unruhig.
* Das Werkzeug beruehrt den Blattrand.
* Das Blatt ist verschmutzt oder stark strukturiert.

### Kontur ist ungenau

Moegliche Ursachen:

* Das Foto ist zu niedrig aufgeloest.
* Die Werkzeugkante ist unscharf.
* Es gibt Spiegelungen.
* Die Maske enthaelt Loecher oder Stoerflaechen.

## 16. Kurzzusammenfassung fuer Einsteiger

ToolTrace nutzt das DIN-A4-Blatt als Lineal. Zuerst wird das Blatt erkannt und geradegezogen. Danach trennt ToolTrace das Werkzeug vom weissen Blatt, bereinigt die Maske und sucht die aeussere Werkzeugkontur. Diese Kontur wird in Millimeter umgerechnet und so ausgerichtet, dass sie spaeter in ein Layout und eine SVG-Datei exportiert werden kann.

Der wichtigste Praxistipp lautet: Ein gutes Foto ist der groesste Hebel fuer eine gute Kontur.
