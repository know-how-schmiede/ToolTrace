# ToolTrace: Vom Bild zur SVG

Diese Anleitung beschreibt, wie ein Werkzeugfoto in ToolTrace aufbereitet wird und welche automatischen Bearbeitungsschritte daraus eine masshaltige Kontur vorbereiten. Sie ist fuer Einsteiger gedacht und erklaert deshalb auch, warum die einzelnen Schritte notwendig sind.

Wichtig: Der aktuelle Stand erzeugt bereits eine erkannte Aussenkontur in Millimeter-Koordinaten. Ein echter SVG-Export dieser Werkzeugkontur ist noch nicht fertig umgesetzt. Vorhanden ist bisher ein SVG-Grundrahmen fuer Layouts. Die Konturdaten sind aber so gespeichert, dass sie im naechsten Ausbauschritt in eine SVG-Kontur geschrieben werden koennen.

## Ziel des Workflows

Aus einem Foto soll eine verwertbare 2D-Kontur entstehen:

1. Werkzeug fotografieren.
2. Hintergrundgroesse auswaehlen und Bild hochladen.
3. Hintergrund erkennen.
4. Perspektive korrigieren.
5. Werkzeug vom Hintergrund trennen.
6. Maske bereinigen.
7. Aussenkontur finden.
8. Kontur in Millimeter umrechnen.
9. Kontur ausrichten.
10. Kontur bei Bedarf manuell an einer Kante ausrichten.
11. Kontur bei Bedarf glaetten oder vereinfachen.
12. Spaeter: Kontur als SVG exportieren.

Der sichtbare Hintergrund dient dabei als Massreferenz. Das kann ein DIN-A4-Blatt sein oder ein Leuchttisch-Hintergrund, dessen Groesse der User in den Einstellungen pflegt und beim Upload auswaehlt. Aus dieser bekannten physischen Groesse kann ToolTrace echte Millimeter berechnen.

## 1. Foto vorbereiten

Lege ein einzelnes Werkzeug auf einen hellen, vollstaendig sichtbaren Hintergrund. Das kann ein weisses DIN-A4-Blatt oder ein Leuchttisch sein.

Das Foto sollte so aufgenommen werden:

* Der komplette Hintergrund ist sichtbar.
* Alle vier Hintergrundkanten und Ecken sind im Bild.
* Das Werkzeug liegt vollstaendig auf dem Hintergrund.
* Es liegt nur ein Werkzeug auf dem Hintergrund.
* Der Hintergrund ausserhalb der Massreferenz stoert moeglichst wenig.
* Das Bild ist scharf und gut beleuchtet.
* Harte Schatten, Spiegelungen und sehr dunkle Raender werden moeglichst vermieden.
* Das Werkzeug beruehrt den Hintergrundrand nicht.

Warum das wichtig ist:

ToolTrace sucht zuerst die Flaeche der Massreferenz. Wenn diese Flaeche abgeschnitten, stark verdeckt oder kaum vom Umfeld unterscheidbar ist, kann die automatische Verarbeitung nicht sicher starten. Danach sucht ToolTrace das Werkzeug innerhalb des entzerrten Hintergrunds. Werkzeuge am Rand koennen deshalb als Randartefakt entfernt werden.

Bei Leuchttisch-Fotos ist das Umfeld oft stark unterbelichtet. ToolTrace sucht deshalb zuerst grosse helle Flaechen im dunklen Umfeld und nutzt die Kantenkontur-Erkennung als Fallback fuer normale Fotos.

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

## 4. Hintergrund erkennen

Zuerst sucht ToolTrace den ausgewaehlten Hintergrund im Foto.

Bearbeitungsschritte:

1. Bild mit OpenCV laden.
2. Fuer die Analyse auf maximal `1600 px` an der laengsten Seite verkleinern.
3. In Graustufen umwandeln.
4. Mit Gaussian Blur glaetten.
5. Kanten mit Canny erkennen.
6. Aeussere Konturen suchen.
7. Grosse helle Leuchttisch-Flaechen im dunklen Umfeld bewerten.
8. Vierseitige, konvexe Flaechen bewerten.
9. Die beste Flaeche als Hintergrund verwenden.

Wichtige Parameter:

| Parameter | Wert | Bedeutung |
| --- | ---: | --- |
| Maximale Analyseseite | `1600 px` | Grosse Fotos werden fuer die Suche verkleinert. |
| Gaussian Blur | `5 x 5` | Reduziert Bildrauschen vor der Kantensuche. |
| Canny-Untergrenze | `50` | Unterer Schwellwert fuer Kanten. |
| Canny-Obergrenze | `150` | Oberer Schwellwert fuer Kanten. |
| Mindestflaeche | `8 %` des Analysebildes | Sehr kleine Rechtecke werden ignoriert. |
| Konturvereinfachung | `0.02 * Umfang` | Sucht eine vereinfachte Kontur mit vier Ecken. |
| Erwartetes Seitenverhaeltnis | ausgewaehlte Hintergrundgroesse | Entspricht dem beim Upload gewaehlten Hintergrund. |
| Mindestscore | `0.55` | Darunter gilt der Hintergrund als nicht sicher erkannt. |

Wenn ein Hintergrund erkannt wird, erzeugt ToolTrace eine Vorschau:

```text
storage/users/<user_id>/tools/<tool_id>/processed/page_detected_job_<job_id>.png
```

In dieser Vorschau wird der erkannte Hintergrund gruen markiert. Die gruene Flaeche hat `30 %` Deckkraft, die Kontur wird gruen gezeichnet und die vier Ecken werden nummeriert.

## 5. Perspektive korrigieren

Ein Foto wird fast nie exakt von oben aufgenommen. Deshalb sieht der Hintergrund im Foto oft trapezfoermig aus. ToolTrace entzerrt den erkannten Hintergrund so, dass daraus wieder ein rechteckiges Bild mit bekannter Millimetergroesse wird.

Bearbeitungsschritte:

1. Die vier erkannten Hintergrund-Ecken werden als Ausgangspunkte verwendet.
2. ToolTrace prueft, ob der Hintergrund im Foto eher hoch oder quer liegt.
3. Die Zielgroesse wird aus der beim Upload gewaehlten Hintergrundgroesse gesetzt.
4. Mit `cv2.getPerspectiveTransform` wird die Transformationsmatrix berechnet.
5. Mit `cv2.warpPerspective` wird das Bild entzerrt.

Wichtige Parameter:

| Parameter | Wert | Bedeutung |
| --- | ---: | --- |
| Hintergrundbreite | User-Auswahl, z.B. `313.0 mm` | Physische Breite der Massreferenz. |
| Hintergrundhoehe | User-Auswahl, z.B. `215.0 mm` | Physische Hoehe der Massreferenz. |
| Pixel pro Millimeter | standardmaessig `10` | Bestimmt die Aufloesung des entzerrten Bildes. |

Bei `10 px/mm` entsteht fuer einen Leuchttisch A4 mit `313 x 215 mm` je nach Orientierung ein Bild mit ungefaehr:

```text
3130 x 2150 px
```

Das perspektivisch korrigierte Bild wird gespeichert unter:

```text
storage/users/<user_id>/tools/<tool_id>/processed/perspective_corrected_job_<job_id>.png
```

## 6. Werkzeug segmentieren

Nach der Perspektivkorrektur sucht ToolTrace das Werkzeug auf dem hellen Hintergrund. Dafuer wird aktuell der OpenCV-Backend verwendet.

Ziel dieses Schritts:

Aus dem farbigen Bild soll eine Schwarz-Weiss-Maske entstehen. Weiss bedeutet: hier ist wahrscheinlich Werkzeug. Schwarz bedeutet: hier ist Hintergrund.

Bearbeitungsschritte:

1. Bild in Graustufen, HSV und LAB umwandeln.
2. Beleuchtung im Graustufenbild normalisieren.
3. Hintergrundfarbe aus den Bereichen am Rand schaetzen.
4. Dunkle Bereiche erkennen.
5. Farblich auffaellige Bereiche erkennen.
6. Gesaettigte Bereiche erkennen.
7. Kantenunterstuetzte dunkle Bereiche ergaenzen.
8. Randbereiche des Hintergrunds entfernen.
9. Kanten-Artefakte am Hintergrundrand entfernen.
10. Maske bereinigen.

Wichtige Parameter:

| Parameter | Wert | Bedeutung |
| --- | ---: | --- |
| Beleuchtungskorrektur-Kernel | max. aus `51` und `9 %` der kurzen Bildseite | Gleicht weiche Helligkeitsunterschiede aus. |
| Hintergrundrand fuer LAB-Samples | max. aus `10 px` und `8 %` der kurzen Bildseite | Dort wird die Hintergrundfarbe geschaetzt. |
| Dunkelgrenze | zwischen `152` und `198` | Wird aus der normalisierten Hintergrundhelligkeit abgeleitet. |
| Sehr-dunkel-Grenze | `158` | Nimmt sehr dunkle Werkzeugteile sicher auf. |
| LAB-Farbabstand | `> 38` | Erkennt Bereiche, die farblich vom Hintergrund abweichen. |
| LAB-Chroma-Abstand | `> 16` | Erkennt farbige Werkzeugteile. |
| HSV-Saettigung | `> 60` | Erkennt gesaettigte Farben. |
| Canny fuer Kantenhilfe | `18` bis `60` | Hilft bei dunklen Kanten und Schattenbereichen. |
| Kanten-Dilatation | Ellipse `11 x 11`, `1` Iteration | Erweitert Kantenbereiche leicht. |
| Aeusserer Maskenrand | max. aus `8 px` und `4 %` der kurzen Bildseite | Wird vor der Bereinigung auf Hintergrund gesetzt. |
| Randartefakt-Marge | max. aus `12 px` und `7 %` der kurzen Bildseite | Entfernt Stoerungen an Hintergrundkanten. |

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

Die Kontur entsteht zuerst in Pixelkoordinaten. Da die Perspektivkorrektur den Hintergrund auf eine bekannte Groesse skaliert hat, kann ToolTrace Pixel in Millimeter umrechnen.

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

## 11. Kontur manuell an einer Kante ausrichten

Die automatische Ausrichtung nutzt die laengste Kante der minimalen Bounding Box. Bei Werkzeugen mit schraegem Griff, Rundungen oder unklarer Hauptachse kann der User die fachlich richtige Kante selbst auswaehlen.

Bearbeitungsschritte:

1. Die Detailseite zeigt eine SVG-Vorschau der aktiven Kontur.
2. Der User klickt zwei Punkte in der Naehe einer relevanten Werkzeugkante.
3. ToolTrace projiziert die Klickpunkte automatisch auf das naechste Kontursegment.
4. Aus den zwei korrigierten Punkten wird der Winkel der Kante berechnet.
5. Die Kontur wird so gedreht, dass diese Kante parallel zur X-Achse liegt.
6. Die Bounding Box wird danach neu berechnet.
7. Optional wird eine Raster-Bounding-Box berechnet, zum Beispiel fuer `42 mm` Gridfinity.
8. Die manuelle Ausrichtung wird als neue aktive Konturversion gespeichert.

Das gespeicherte Geometrieformat enthaelt dann unter anderem:

```text
alignment method: user_selected_edge
edge_start_mm: erster korrigierter Punkt
edge_end_mm: zweiter korrigierter Punkt
rotation_deg: angewendete Rotation
raster_bounding_box_mm: optionale auf Rastermass gerundete Bounding Box
```

Die manuell ausgerichtete Vorschau wird gespeichert unter:

```text
storage/users/<user_id>/tools/<tool_id>/contours/manual_aligned_contour_<contour_id>.png
```

Diese Vorschau wird in der Werkzeugbibliothek bevorzugt als Thumbnail angezeigt, solange die manuell ausgerichtete Kontur aktiv ist.

## 12. Kontur glaetten und vereinfachen

Die erkannte Kontur kann kleine Zacken oder viele nahe beieinanderliegende Punkte enthalten. ToolTrace kann die aktive Kontur deshalb nicht-destruktiv glaetten und vereinfachen.

Bearbeitungsschritte:

1. Der User waehlt auf der Detailseite eine Glaettungsstaerke.
2. Optional gibt der User eine Vereinfachungstoleranz in Millimeter an.
3. ToolTrace glaettet die Kontur mit einem Chaikin-Verfahren.
4. ToolTrace vereinfacht die Punkte mit Douglas-Peucker (`cv2.approxPolyDP`).
5. Die Kontur wird wieder auf positive Millimeterkoordinaten normalisiert.
6. Die Bounding Box wird neu berechnet.
7. Die bearbeitete Kontur wird als neue aktive Konturversion gespeichert.

Die Bearbeitung ueberschreibt die vorherige Kontur nicht. Dadurch kann der User verschiedene Staerken ausprobieren.

### Was macht das Chaikin-Verfahren?

Das Chaikin-Verfahren ist ein einfaches Verfahren zum Abrunden einer Polygonlinie. Die Kontur besteht in ToolTrace aus vielen geraden Strecken zwischen einzelnen Punkten. Kleine Messfehler oder Segmentierungszacken erzeugen dabei harte Ecken. Chaikin ersetzt jede Strecke durch zwei neue Punkte, die etwas innerhalb der alten Strecke liegen.

Fuer eine Strecke von Punkt `A` nach Punkt `B` entstehen zwei neue Punkte:

```text
Q = 75 % A + 25 % B
R = 25 % A + 75 % B
```

Die urspruenglichen Eckpunkte werden dadurch nicht direkt beibehalten. Die neue Kontur laeuft etwas weicher um die alte Kontur herum. Bei einer geschlossenen Werkzeugkontur wird dieser Schritt fuer jede Kante ausgefuehrt, auch fuer die letzte Kante zurueck zum ersten Punkt.

Wirkung:

* kleine Zacken werden abgerundet
* harte Ecken werden weicher
* die Anzahl der Punkte steigt pro Glaettungsdurchlauf
* sehr starke Glaettung kann echte scharfe Werkzeugkanten abrunden

Deshalb kombiniert ToolTrace die Glaettung optional mit einer Vereinfachung. Nach dem Glaetten kann Douglas-Peucker (`cv2.approxPolyDP`) ueberfluessige Punkte entfernen. Die Glaettung macht die Form ruhiger, die Vereinfachung reduziert danach die Punktanzahl.

Wichtige Bedienlogik:

* `Keine`, `Leicht`, `Mittel`, `Stark` und `Sehr stark` steuern die Anzahl der Glaettungsdurchlaeufe.
* Die Vereinfachungstoleranz in mm steuert, wie stark Punkte reduziert werden.
* Reset nimmt auch mehrfach angewendete Glaettung/Vereinfachung bis zur urspruenglichen nicht geglaetteten Konturversion zurueck.
* Die Bibliothek zeigt nur die Vorschau der aktuell aktiven Konturversion bevorzugt an.

Die bearbeitete Konturvorschau wird gespeichert unter:

```text
storage/users/<user_id>/tools/<tool_id>/contours/edited_contour_<contour_id>.png
```

## 13. Aktueller Stand des SVG-Exports

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

## 14. Vorgesehener SVG-Schritt

Die Kontur liegt bereits als Liste von Millimeterpunkten vor. Fuer einen echten SVG-Export muss daraus ein SVG-Pfad oder Polygon erzeugt werden.

Grundidee:

1. `points_mm` aus der aktiven Kontur lesen.
2. Aktuelle aktive Konturversion verwenden.
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

## 15. Layoutberechnung

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

## 16. Woran erkennt man ein gutes Ergebnis?

Ein gutes Ergebnis sieht in ToolTrace so aus:

* Die Hintergrundvorschau markiert genau die Massreferenz.
* Die Perspektivkorrektur zeigt einen gerade entzerrten Hintergrund.
* Die Werkzeugmaske zeigt nur das Werkzeug, nicht den Hintergrundrand.
* Die rote Aussenkontur deckt die Werkzeugform plausibel ab.
* Die ausgerichtete Vorschau zeigt die Kontur vollstaendig in einer Bounding Box.
* Manuelle Ausrichtung und Glaettung erzeugen nachvollziehbare neue Konturversionen.
* Breite und Hoehe in Millimeter wirken realistisch.

Wenn das Ergebnis schlecht ist, sollte zuerst das Foto verbessert werden. Besonders wichtig sind ein voll sichtbarer Hintergrund, gute Beleuchtung und Abstand des Werkzeugs zum Hintergrundrand.

## 17. Typische Probleme und Ursachen

### Hintergrund wird nicht erkannt

Moegliche Ursachen:

* Eine oder mehrere Hintergrundecken fehlen.
* Der Hintergrund hebt sich zu wenig vom Umfeld ab.
* Das Foto ist unscharf.
* Andere rechteckige Objekte im Bild stoeren.
* Der Hintergrund ist zu klein im Foto.

### Werkzeugmaske ist leer

Moegliche Ursachen:

* Das Werkzeug hat zu wenig Kontrast zum Hintergrund.
* Das Werkzeug ist sehr hell oder weiss.
* Das Bild ist ueberbelichtet.
* Schatten wurden staerker erkannt als das Werkzeug.

### Zu viel wird als Werkzeug erkannt

Moegliche Ursachen:

* Harte Schatten liegen direkt am Werkzeug.
* Der Hintergrundrand ist unruhig.
* Das Werkzeug beruehrt den Hintergrundrand.
* Der Hintergrund ist verschmutzt oder stark strukturiert.

### Kontur ist ungenau

Moegliche Ursachen:

* Das Foto ist zu niedrig aufgeloest.
* Die Werkzeugkante ist unscharf.
* Es gibt Spiegelungen.
* Die Maske enthaelt Loecher oder Stoerflaechen.

## 18. Kurzzusammenfassung fuer Einsteiger

ToolTrace nutzt den ausgewaehlten Hintergrund als Lineal. Zuerst wird die Massreferenz erkannt und geradegezogen. Danach trennt ToolTrace das Werkzeug vom Hintergrund, bereinigt die Maske und sucht die aeussere Werkzeugkontur. Diese Kontur wird in Millimeter umgerechnet, ausgerichtet und kann bei Bedarf manuell korrigiert, geglaettet oder vereinfacht werden. Die aktive Konturversion ist die Grundlage fuer Layout und spaeteren SVG-Export.

Der wichtigste Praxistipp lautet: Ein gutes Foto ist der groesste Hebel fuer eine gute Kontur.
