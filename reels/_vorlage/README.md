# Reel {NAME} ({DATUM})

| | |
|---|---|
| Auftrag | Anfrage vom {DATUM}: … |
| Drive-Ordner | Link bzw. Ordner-ID |
| Song | Interpret – Titel, BPM (Abschnitt je Variante unten) |
| Stil | Stil-Leitfaden, Abweichungen laut Auftrag: … |
| Status | Sichtung / 3 Varianten zur Auswahl / Variante … gewählt / geliefert |
| Fertig | `{NAME}_mit_song.mp4`, `{NAME}_ohne_ton.mp4`, `{NAME}_titelbild.jpg` |

## Varianten (Pflicht-Stopp: der Nutzer wählt eine)

| | Idee | Songabschnitt | Länge, Shots | Unterschied in einem Satz |
|---|---|---|---|---|
| A | … | Takt a.1 bis b.1 (von–bis s) | … s, … Shots | … |
| B | … | … | … | … |
| C | … | … | … | … |

- Unterschied-Check (`tools/pipeline/varianten.py <reel> --check`): …
- Gewählt: Variante … am … („wörtlich“), Änderungswünsche: …

## Ordner

- oben vor der Wahl: je Variante `{NAME}_A_vorschau.mp4` und `{NAME}_A_storyboard.jpg` (B und C genauso); nach der Wahl nur die aktuelle Fassung (Videos, Titelbild, Storyboard)
- `schnitt/`: `grid.json` (Beat-Raster, gilt für alle Varianten), `A/`, `B/`, `C/` je mit `edl.py` → `edl.json`, `fx.json`, `audio_spec.json`
- `archiv/varianten/`: Vorschau-Videos und Storyboards aller Varianten (verschiebt `varianten.py --wahl`)
- `archiv/v1/`, `archiv/v2/` …: ältere Fassungen samt ihrer Schnittliste, nie löschen

## Versionen

- v1 (Datum): Variante …, Shots, Länge, was drin ist

## Feedback

- (wörtlich, mit Datum; was davon dauerhaft gilt, kommt in Stil-Leitfaden.md und stil.json)

## Prüfwerte (tools/pipeline/verify.py)

- Schnitte: … / 808-Versatz: … Frames / Lautheit: … LUFS / True Peak: … dBTP
