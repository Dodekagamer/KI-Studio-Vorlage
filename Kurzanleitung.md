# Reel-Kurzanleitung (Standardfall)

Für Claude: Diese Datei ersetzt im Standardfall das Lesen von `README.md`, `Reel-Studio_Projektanweisungen.md` und den Tool-READMEs. Dazu vor jedem Reel die Kurzfassung des Stils: `sed -n '1,/^---$/p' $P/Stil-Leitfaden.md`. Vorrang: neuestes Feedback des Nutzers > Stil-Leitfaden > Projektanweisungen. Deutsch, kurz, handyfreundlich. Fehlende Angaben selbst entscheiden und nennen, nicht nachfragen. Einziger Pflicht-Stopp: der Nutzer wählt eine von 3 Varianten.

## Erster Start

- `python3 $P/tools/stil.py` meldet „NOCH NICHT EINGERICHTET“? Dann vor dem ersten Reel mit dem Nutzer den Abschnitt „Stil festlegen“ im Stil-Leitfaden abarbeiten (eine Nachricht mit Fragen, alles optional). Will er sofort ein Reel, mit dem Grundstil schneiden und das sagen.
- Name und Marke des Nutzers stehen in `stil.json` (`nutzer`, `marke`).

## Sparsam arbeiten (Nutzungslimit)

Jeder Tool-Aufruf schickt den ganzen bisherigen Thread noch einmal mit. Was früh im Kontext landet, zahlt man bei jedem weiteren Schritt erneut.

1. Nur diese Datei und die Stil-Kurzfassung lesen. Lange Dokumente nur gezielt nachschlagen (`grep -n`, dann `sed -n` für den Abschnitt), siehe Tabelle am Ende.
2. Nicht pollen: lange Läufe (ingest, Clip-Analyse, `varianten.py`) im Hintergrund starten (Bash `run_in_background` bzw. `setsid nohup … &`), auf die Fertig-Meldung warten. Kein `sleep`, kein wiederholtes `tail` aufs Log.
3. Schritte bündeln: mehrere Befehle in einem Bash-Aufruf (`&&`), Ausgabe kappen (`2>&1 | tail -n 15`).
4. Keine großen Dateien ausgeben: `song.json`, `clips.json`, `shotliste.json`, `qc.json` und Logs nie mit `cat`. Die `.md`-Berichte reichen, einzelne Werte per `python3 -c`.
5. Bilder nur über `tools/ansicht.py` (ein kleines Raster statt vieler Einzelbilder): je Variante einmal `ansicht.py reel`, dichte Frames nur für Ramps, langsame Bewegungen und unsichere Peaks. Storyboards (1080×5500) nie ganz öffnen, sonst `ansicht.py bild … --teil 1/4`. Jedes Bild einmal ansehen, Befund sofort notieren.
6. Schon Gesichtetes nicht neu ansehen: Sichtungen stehen als Tags-Datei im Reel-Ordner bzw. in `referenz/rohmaterial/`. Neue Sichtung einmal als `tags.json` festhalten.
7. Dateien per Edit ändern statt neu schreiben, in `edl.py` nur den Block „pro Reel anpassen“.
8. Antworten kurz, Zwischenstände nur in einer Status-Checkliste.

## Ablauf

`P=` Projektordner: `/mnt/project-files`, wenn es dort `tools/` gibt, sonst die Repository-Kopie (`P=$(git rev-parse --show-toplevel)`). Dazu `T=$P/tools; W=/home/user/reel` (Arbeitsordner im Container; Downloads, Frames, Master und Mix bleiben dort). Werkzeuge aus `/home/user` oder `/tmp` starten, nie im Projektordner als Arbeitsverzeichnis.

0. **Start:** `cd /tmp && python3 $T/selftest.py 2>&1 | tail -n 4` muss grün sein. Fehlt ffmpeg: `bash $T/setup.sh`.
1. **Ordner:** `python3 $T/neues_reel.py <name>` legt `R=$P/reels/<heute>_<name>` mit `schnitt/A|B|C/edl.py` an.
2. **Material:** Drive-Connector `search_files`, Query `parentId = '<Ordner-ID>'`, pageSize 100, alle Seiten, nach ID deduplizieren (gleicher Name und Größe: per MD5 nur eine Kopie). `get_file_permissions` am Ordner: ohne `type: anyone` stoppen und um „Jeder mit dem Link – Betrachter“ bitten (bei `writer`: Betrachter reicht). Videos als `<id>\t<name>\t<bytes>` in `$W/manifest.tsv`. Song: `curl -L -o $W/song.mp3 "https://drive.usercontent.google.com/download?id=<ID>&export=download&confirm=t"`, Größe prüfen (HTML oder winzig = Fehlerseite, bis 5 Versuche). Fotos nur auf Wunsch. Fehlt der Drive-Connector: den Nutzer bitten, ihn zu verbinden (EINRICHTUNG.md).
3. **Sichtung** (Hintergrund): `python3 $T/pipeline/ingest.py`. Neues Material zusätzlich `python3 $T/analyse/clip_analyse.py --manifest $W/manifest.tsv --schnell -o $R/schnitt/analyse` (Kandidaten genauer mit `--only IMG_…`), `clips.md` und Kontaktbögen einmal ansehen, Kapitel, Tags, besten Moment und Ausschuss als `$R/schnitt/tags.json` im Format von `$T/analyse/tags_beispiel.json`. Ausschuss: Stil-Leitfaden Abschnitt 5.
4. **Song:** `python3 $T/analyse/song_analyse.py $W/song.mp3 -o $R/schnitt` schreibt `grid.json` und `song.md` (nur die lesen: Songteile, Eins der Hook, Fenster, Akzent-Karte je Takt). Länge: Standard die Hook, 16 Takte bei genug starkem Material (mindestens 25 gute Momente), sonst 8.
5. **Entwurf je Variante:** `python3 $T/analyse/shotliste.py --song $R/schnitt/song.json --tags $R/schnitt/tags.json [--clips …/clips.json] [--fenster 1 | --start-takt N --takte 16|8] [--auftakt 2] [--meiden $R/schnitt/A/edl.json] -o $R/schnitt/X`, dann `shotliste.md` lesen. Es bleibt ein Entwurf.
6. **Schnittliste:** in `schnitt/X/edl.py` den Block „pro Reel anpassen“ füllen (SONG, HOOK_EINS, AUFTAKT, TAKTE, HITS, UNTERSCHIED, ERLAUBT, `s(…)`-Zeilen), `cd $R/schnitt/X && python3 edl.py`. Jede WARNUNG ist ein Stil-Verstoß: beheben oder begründen. Danach `python3 $T/pipeline/varianten.py $R --check` (jedes Paar in 2 von 3 Punkten verschieden).
7. **Bauen** (Hintergrund, etwa 7 min je Variante): `cd /home/user && python3 $T/pipeline/varianten.py $R 2>&1 | tail -n 25`. Eine Variante neu: `--nur X`.
8. **Sichtprüfung:** je Variante `python3 $T/ansicht.py reel $W/master_X.mp4 --edl $R/schnitt/X/edl.json` (ein Bild, #Nr wie im Storyboard). Ramps, langsame Bewegungen, unsichere Peaks: `python3 $T/ansicht.py clip <clip> <von> <bis>` (Quellzeit). Abweichungen vom Entwurf später nennen. Dateien aus früheren Läufen nie blind übernehmen.
9. **Pflicht-Stopp:** die 3 Vorschau-Videos und 3 Storyboards (`$R/<name>_X_vorschau.mp4`, `$R/<name>_X_storyboard.jpg`) an den Nutzer (im Claude-Projekt als Anhang; in einer eigenen Session: Pfade nennen, er öffnet sie in der App), je Variante eine Zeile: Songpart (Takte, Zeit), Länge, was sie anders macht. Dazu eine Zeile, was nicht verwendet wird und warum. Dann stoppen.
10. **Nach der Wahl:** Änderungswünsche (Shot-Nummern) in `schnitt/X/edl.py`, `varianten.py $R --nur X` (neue Vorschau nur bei großen Umbauten schicken), dann `varianten.py $R --wahl X [--titel <frame>]`: Export, `verify.py` muss „alles OK“ melden. Container neu gestartet (Arbeitsordner leer)? Vorher Schritt 2, 3 und `--nur X`. Steckbrief `$R/README.md` ausfüllen.
11. **Liefern:** `<name>_mit_song.mp4`, `_ohne_ton.mp4`, `_titelbild.jpg` an den Nutzer, dazu kurz:
    - Datei unverändert aufs Handy (Download aus Claude, Drive oder AirDrop, nicht WhatsApp). In Instagram „In höchster Qualität hochladen“ an, Upload über WLAN, keine Filter, kein Zuschneiden, keine Effekte. Eigenes Titelbild, Motiv im mittleren 1080×1440-Bereich.
    - Stumme Version: Song in der Instagram-Musikbibliothek am Hook-Start ansetzen (Zeitstempel nennen).
    - Ordnerfreigabe wieder auf „Eingeschränkt“.
12. **Feedback-Runde:** alte Fassung samt Schnittliste nach `archiv/v1/`, `edl.py` ändern, `--nur X`, `--wahl X --fassung v2`. Was dauerhaft gelten soll, wörtlich mit Datum ins Änderungsprotokoll des Stil-Leitfadens, als Regel dort und in `stil.json`. Zum Schluss `python3 $T/ordnung.py`.

## Handwerk, das kein Werkzeug prüft

- Eins der Hook = Taktanfang der Phrase, nicht der erste laute 808. Ende = Eins + 16 (8) Takte, 30–40 ms Fade, in den letzten 150 ms kein 808. Ein Auftakt verlängert das Reel und gehört zu Kapitel 1, er kürzt nie das Ende.
- Schnelle Folgen von Bass-Schlägen: 2 Szenen à 2 Beats mit je 2 Punches statt 4 Szenen à 1 Beat.
- Pro Shot notieren, welcher Teil der Bewegung zu sehen ist, nie nur die Ausholphase. Nur gelungene Versuche.
- Peak der Bewegung genau auf dem Hit, an dichten Frames prüfen (Keyframes im Abstand von 1 s täuschen). Zeitlupe nur aus 60-fps-Material.
- Jeder Clip höchstens einmal. Wechsel total und nah, Einzelne und Gruppe. Wiedererkennung immer wieder im Hintergrund.
- Push-in nur auf ruhigen Shots. Schlussbild: niemanden am Rand anschneiden.
- Ton: Songpegel unverändert, Limiter nur wenn nötig (Decke −0,3 dBTP). SFX nur auf Wunsch.

## Drei Varianten

Namen und Ideen stehen in `stil.json` (Standard: A Story = Stil-Leitfaden 1:1, Hook ab der Eins, 16 Takte; B Power = andere Songstelle, andere Clips per `--meiden`, stärkste Action, Effekt-Budget voll; C Clean = 8 Takte oder ruhigerer Teil, 4-Beat-Shots, Punches nur auf die stärksten Akzente, Zeitlupe und Push-ins). Jedes Paar unterscheidet sich in mindestens 2 von 3 Punkten: Songabschnitt, Auswahl/Story, Tempo/Effekt-Dichte. Alle bleiben im Stil-Leitfaden. Vorgaben des Nutzers (Part, Länge, Muss rein) gelten für alle drei. Namen und Idee dürfen zum Material passen.

## Nachschlagen nur bei Bedarf

| Wenn | Dann |
|---|---|
| Stil noch nicht eingerichtet | `Stil-Leitfaden.md`, Abschnitt „Stil festlegen“ |
| Song-Genre ohne Regel im Leitfaden | `Reel-Studio_Projektanweisungen.md` Abschnitt 3 (Stil-Matrix) und 5 (Looks) |
| Sonderwunsch (Text, Split, SFX, anderer Look) | `tools/vfx/README.md`, `sfx/README.md` |
| mehrere Songs, SFX-Mix | Kopf von `tools/reel_audio.py` |
| Werkzeug-Fehler | Kopf des Skripts, `tools/README.md`, `tools/analyse/README.md` |
| Ordnerregeln, Einrichtung | `README.md`, `EINRICHTUNG.md` |

Ändert sich der Stil-Leitfaden oder kommt neues Feedback, `stil.json` und bei Bedarf diese Datei im selben Zug anpassen.
