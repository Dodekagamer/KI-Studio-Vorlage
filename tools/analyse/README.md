# Analyse-Werkzeuge

Alles läuft ohne Zusatzpakete (ffmpeg, OpenCV, librosa, pyloudnorm aus `../setup.sh`).
Ausgaben (klein: JSON, Markdown, Bilder) in den Reel-Ordner, z. B. `reels/<datum>_<name>/schnitt/analyse/`; Downloads und Song bleiben in `/home/user/reel/` (siehe `../../README.md`).

| Werkzeug | Wofür | Phase laut Projektanweisungen |
|---|---|---|
| `analyse.py` | Gesamtablauf: `vorbereiten` (Song + Clips + Shotliste) und `pruefen` (fertiges Reel) | 2–4, 17 |
| `song_analyse.py` | Beat-Raster, Takte, Songteile, Hook, 808/Clap-Akzent-Karte, empfohlene Reel-Fenster | 3 |
| `clip_analyse.py` | Clip-Metadaten, Bewegung (Action ohne Kameraschwenk), Schärfe, Belichtung, Highlights, Duplikate, Kontaktbögen | 2 |
| `shotliste.py` | Shotlisten-Vorschlag nach Stil (4 Kapitel aus `stil.json`, 2-Beat-Raster, Bild-Akzente, Ramps, Finale) | 4 |
| `storyboard_vorschau.py` | Vorschau-Storyboard aus der Shotliste: ein Bild pro Shot am Hit-Moment direkt aus den Clips, Kapitel-Abschnitte, Zeitleiste mit 808 | 4 |
| `reel_qc.py` | Prüfung des fertigen Reels: Format, Schnitte auf Beat, 808 gegen Schnitte, Lautheit, Ende auf Taktgrenze, Standbilder, Safe-Zones | 17 |
| `selftest_analyse.py` | Kurztest aller Werkzeuge mit synthetischem Beat und Testclips (~20 s), läuft in `../selftest.py` mit | |
| `tags_beispiel.json` | Format der Tags-Datei (Kapitel, Tags, bester Moment je Clip) mit allen Standard-Tags; die echte Sichtung eines Drive-Ordners kommt als `tags.json` in den Reel-Ordner bzw. nach `referenz/rohmaterial/` | 2 |

Aufruf am besten aus `/home/user` mit absoluten Pfaden: Liegt das Arbeitsverzeichnis im Projektordner, kann librosa/numba sporadisch mit `FileNotFoundError` (getcwd) abbrechen, wenn andere Threads dort gerade schreiben. `analyse.py` und `../selftest.py` fangen das selbst ab.

## Schnellstart

```bash
cd /home/user; A=$P/tools/analyse; R=$P/reels/<datum>_<name>      # P = Projektordner (Kurzanleitung)
# 1. Vor dem Storyboard (Clips lokal oder direkt vom Drive über das Manifest)
python3 $A/analyse.py vorbereiten --song /home/user/reel/song.mp3 --clips /home/user/reel/clips \
    --tags $R/schnitt/tags.json --vorschau -o $R/schnitt/analyse      # --schnell für ganze Ordner
python3 $A/analyse.py vorbereiten --song /home/user/reel/song.mp3 --manifest /home/user/reel/manifest.tsv \
    --only IMG_6166,IMG_3419 --tags $R/schnitt/tags.json -o $R/schnitt/analyse
# 2. Vor der Abgabe
python3 $A/analyse.py pruefen $R/<name>_mit_song.mp4 --song /home/user/reel/song.mp3 -o $R/schnitt/analyse
```

## song_analyse.py

`python3 song_analyse.py song.mp3 -o OUT [--bpm 140] [--eins 13.718]`, ~20 s für einen 2-Minuten-Song.

- **Raster:** librosa `beat_track`, Regression über die Beat-Nummern, dann Tempo (±0,15 %) und Phase (±30 ms) an einer 1-ms-Einsatzkurve feinjustiert. Die Zeiten liegen damit auf den echten Einsätzen im ffmpeg-Decode; der frühere Abzug von 13 ms beim `atrim` entfällt.
- **Taktlage:** Clap auf Schlag 3 (Drill/Trap) oder Snare auf 2+4 mit Kick auf 1. Bei falscher Erkennung `--eins <Zeit einer Eins>` angeben.
- **Songteile:** taktweise Chroma, MFCC und Pegel, Self-Similarity, Grenzen auf 4-Takt-Phrasen. Hook = wiederholter Teil (Ähnlichkeit ≥ 0,9) mit der meisten Energie; Hook-Start zusätzlich beatgenau gegen die zweite Hook geprüft.
- **Akzente:** 808 = Einsatz unter 120 Hz (Stärke ≥ 1,2), 808-Nachschlag = schwächerer Einsatz genau 1 Beat nach einem frischen 808, Clap = 1,5–3 kHz deutlich über den Nachbar-Beats. Geeicht an einem Drill-Song (140 BPM, alle 12 frischen 808 und 5 Nachschläge getroffen). Bei anderen Genres (House, Pop) heißen die Einsätze trotzdem „808“ (Kick/Bass) und „Clap“ (Snare).
- **Tonart** (Krumhansl-Schätzung) mit Camelot-Code: bei zwei Songs im Mix passen gleiche oder benachbarte Codes.
- **Reel-Fenster:** ab der Eins der Hook 16 bzw. 8 Takte bis zur nächsten Eins, auf Wunsch mit 2-Beat-Auftakt; Prüfung „kein 808 in den letzten 150 ms“. Pro Fenster fertige `atrim`-Zeile und `reel_audio.py`-Eintrag.
- **Ausgabe:** `song.json`, `grid.json` (Format der Pipeline: per, ph, bpm, dur + erste_eins, hook_eins), `song.md` (Songteile, Fenster, Akzent-Karte als Text, 1 Zeile pro Takt: `8` 808, `n` Nachschlag, `c` Clap), `song.png` (Wellenform mit Teilen, Takten, Einsätzen), `akzentkarte.png`.


## clip_analyse.py

`python3 clip_analyse.py CLIPS_ODER_ORDNER... -o OUT [--fps 10] [--jobs 2] [--schnell] [--fenster 0.86]`
oder direkt vom Drive: `--manifest manifest.tsv [--only IMG_6166,IMG_3419]` (lädt per curl, prüft die Größe, analysiert, löscht; höchstens 2 Originale gleichzeitig).

- **Metadaten:** Auflösung (Rotation beachtet), fps, HDR (HLG/PQ, wird für Messung und Bilder getonemappt), Aufnahmezeit, GPS, Kamera-Modell.
- **Zeitreihen** bei 10 Bildern/s, alle in px/s bei 1080 px Breite: `motion` = Bewegung im Bild minus Kamerabewegung (Farneback-Fluss, globale Bewegung per RANSAC abgezogen), `motion_top` (stärkste 5 %), `camera` (Schwenk), `shake` (Wackeln), `zoom`; dazu `sharp` (Laplace-Varianz, unter 150 = unscharf), `luma` und Clipping.
- **Highlights:** bis zu 5 Fenster à 2 Beats mit `peak` (dort gehört der Hit hin) und Score 0–100. **Clip-Score** 0–100 (40 % Action, je 20 % Schärfe, Belichtung, Ruhe) und Hinweise: verwackelt, unscharf, zu dunkel, überbelichtet, kaum Bewegung, sehr kurz (<2 s), Querformat, schon geschnitten?, ohne Ton.
- **Duplikate** über Bild-Hashes. **Kontaktbögen** 1600 px breit, 6 Clips pro Bogen, 8 Bilder mit Zeitstempel, Sparkline (Action weiß, Kamera blau, Highlights orange, Schnitte rot).
- **Laufzeit:** 1080p-HLG ~0,8 s pro Clip-Sekunde, 4K-HEVC ~2,5 s pro Clip-Sekunde (Dekodieren ist der Engpass). `--schnell` nur Keyframes (~8× schneller, grobe Werte) für ganze Ordner.
- **Grenzen:** Personen-/Gesichtserkennung geht in dieser OpenCV-Version nicht (keine Modelle), `people_max` bleibt leer. Kleine Gesten in Totalen (Arme hoch) ranken schwach, Leute direkt vor der Linse und schnelle Kameraschwenks zählen als Action. Gesichtete Momente in den Tags haben deshalb in `shotliste.py` Vorrang.

## shotliste.py

`python3 shotliste.py --song OUT/song/song.json [--clips OUT/clips/clips.json] [--tags tags.json] [--fenster 1 | --start-takt 48 --takte 8] -o OUT`

- 4 Kapitel (Namen aus `stil.json`, Standard Einstieg, Aufbau, Höhepunkt, Finale) auf den Song-Phrasen, 2-Beat-Grundraster, langsame Bewegungen 4 Beats, 1 Speed-Ramp pro Kapitel 1–3 (Anlauf ab Schlag 3 im 2. Takt, Hit auf der Eins im 3. Takt), Finale 6 Beats (Zeitlupe und Push-in laut `stil.json`).
- Slots je Kapitel: Einstieg `opener, branding, action, ramp, action, langsam`; Aufbau `action, action, nah, ramp, action, langsam`; Höhepunkt `power, power, nah, ramp, action, action`; Finale `payoff, payoff, emotion, emotion, gruppe, finale`. Welche Tags ein Slot sucht, steht in `SLOT_TAGS` (Tags: `tags_beispiel.json`). Eigene Vorlagen und Tags gehen in `stil.json` unter `"shotliste"` (Kopf von `shotliste.py`).
- Bild-Akzent je Schnitt aus der Akzent-Karte (808 → Punch 0,14, Nachschlag → 0,12, Clap → Mini-Punch 0,06, sonst harter Schnitt), 808 innerhalb eines Shots → Punch im selben Shot. Flash nur im letzten Kapitel (Start und Finale) auf 808, Shake nur auf Clips mit Tag `schlag`, beides im Budget aus `stil.json`.
- Clips nach Kapitel und Tags, jeder Clip höchstens einmal, Showpieces für die Ramps reserviert, In-Punkt so, dass der beste Moment auf dem Hit liegt (zuerst `moment` aus den Tags, dann die Highlights der Clip-Analyse, der erste, der ganz in den Clip passt).
- `shotliste.json` hat die Felder der Render-EDL (`n, beat, t, beats, clip, src, mode, fx, fxp, desc`); `shotliste.md` mit Tabelle und Checkliste (Segmente, Ramps, Flashes, Shakes, Ramp-Hit ohne 808, fehlende Clips). Es bleibt ein Entwurf: In-Punkte an dichten Frames prüfen.
- `--meiden <reel>/schnitt/A/edl.json` (oder eine Clip-Liste `6132,6140`): Clips, die eine andere Variante schon nutzt, kommen nur dran, wenn für den Slot nichts anderes passt. So bekommt Variante B andere Clips als A.

## storyboard_vorschau.py

`python3 storyboard_vorschau.py OUT/shotliste/shotliste.json --clips /home/user/reel/clips --song OUT/song/song.json -o vorschau.jpg`

1080 px breit, 4 Spalten, ein Abschnitt pro Kapitel, pro Kachel das Bild am Hit (`peak`) mit Nummer, Zeit, Takt, Beats, Modus, Clip, In-Punkt, Effekten und Inhalt. HLG wird getonemappt. Das ist eine Arbeitsvorschau ohne Grading; das Freigabe-Storyboard kommt weiter aus `tools/pipeline/storyboard.py`.

## reel_qc.py

`python3 reel_qc.py REEL.mp4 [--song song.mp3] [--song-json song.json] [--src 12.861] [--edl edl.json] -o OUT [--streng]`, ~20 s pro Reel. Immer `-o` angeben.

- Jede Prüfung meldet OK, WARNUNG, FEHLER oder INFO (reine Messwerte). Exit-Code 1 bei FEHLER, mit `--streng` auch bei WARNUNG.
- **Format:** 1080×1920, 30 fps konstant (auch Paket-Zeitstempel), H.264 High, yuv420p, bt709-Tags, Video 8–25 Mbit/s, AAC 48 kHz, Ton und Bild gleich lang (< 1 Frame), faststart, Dateigröße.
- **Bild:** harte Schnitte (Punches, Schwenks, Flashes und animierte Übergänge werden herausgefiltert), Zoom-Punches, Flashes, Schwarzbilder, Standbilder (außer geplante Freezes laut EDL), Szenen unter der Mindestlänge und Szenen pro 16 Takte (beides aus `stil.json`).
- **Beat-Sync:** Songposition per Korrelation (samplegenau, mit Takt und Songteil), Schnitte und Punches gegen Beat/Halbbeat (≤ 1 Frame OK), 808 gegen Schnitt/Punch, mit `--edl` geplant gegen erkannt (±2 Frames). Ohne Song: Raster aus der eigenen Tonspur.
- **Ton:** Lautheit, True Peak (≤ −0,3 dBTP OK, über 0 FEHLER), 100-ms-Blöcke ohne Aussetzer, Pegel gegen den Song-Ausschnitt (< 1 dB), Fade-in ≤ ~12 ms, Fade-out 25–45 ms, Ende auf der Taktgrenze (±20 ms), kein 808 in den letzten 150 ms.
- **Bilder:** `qc_timeline.png` (Wellenform, Raster, Schnitte, Punches, Flashes, 808, Problemstellen) und `qc_shots.jpg` (Mittel-Frame jeder Szene mit Instagram-UI-Zonen oben 10 %, unten 20 %, rechts 10 % und dem 3:4-Ausschnitt fürs Profilraster).
- **Grenzen:** Fades nur mit Song-Referenz messbar; ohne song.json wird die Taktlage geschätzt; Standbilder mit Push-in oder Korn gelten nicht als eingefroren; Punches erst ab ~3 % Zoomsprung; ohne EDL gilt ein Effekt neben dem Beat (z. B. Split-Aufklappen) als FEHLER.
- **True Peak:** Der AAC-Encode kann die −0,3-dBTP-Decke leicht überschwingen (gemessen −0,16 dBTP). Wer sicher darunter bleiben will, setzt in der `reel_audio.py`-Spec `"ceiling_db": -1.0`.

Gegenprobe an einem Referenz-Reel: `reel_qc.py` an einem Reel laufen lassen, das der Nutzer mag (eigenes oder fremdes, als Datei), liefert Schnittlängen, Szenen pro 16 Takte, Punches, Flashes, Lautheit und ob der Ton auf der Taktgrenze endet. Daraus lassen sich Werte für `stil.json` ableiten (Stil-Leitfaden, „Stil festlegen“).
