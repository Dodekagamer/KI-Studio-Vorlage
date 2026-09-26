# Reel-Studio Werkzeuge

| Datei | Zweck |
|---|---|
| `setup.sh` | Setup-Skript der Umgebung: ffmpeg, sox, rubberband-cli, Schriften, Python-Pakete (versionsgenau). Läuft bei jedem neuen Thread bzw. jeder Session, ca. 70 s. |
| `selftest.py` | Prüft in ~30 s die ganze Kette: Look aus `stil.json` als LUT, OpenCV→ffmpeg-Master, Instagram-2-Pass, HLG-Tonemapping, Beat-Analyse, Mix + Mux, Analyse-Werkzeuge, VFX, SFX-Kit. Meldet am Ende, ob der Stil schon eingerichtet ist. |
| `stil.py` | Liest `../stil.json` (maschinenlesbarer Teil des Stil-Leitfadens: Marke, Look, Vignette, Kapitel, Effekt-Budget, Finale, erlaubte Extras, Varianten). `python3 stil.py` zeigt den Stil und ob er eingerichtet ist. Fehlende Werte = Grundstil. |
| `reel_audio.py` | Tonspur aus mehreren Songs + Soundeffekten, sample-genau; Crossfades, Tempo-Angleichung (Rubber Band, ±1 ms im Raster), Ducking, Lautheitsangleich, True-Peak-Limiter, Pegelprüfung in 100-ms-Blöcken. Beispiel-spec im Kopf der Datei. |
| `make_sfx_kit.py` | Erzeugt das synthetische SFX-Grundkit in `../sfx/` neu. |
| `neues_reel.py` | Legt `reels/<datum>_<name>/` aus `reels/_vorlage/` an (Steckbrief, je Variante aus `stil.json` eine Schnittliste mit Stil-Prüfung). |
| `ordnung.py` | Prüft die Ordnung im Projektordner (Root, Reel-Ordner, Fassungen, Varianten-Dateien, Zwischendaten) und zeigt alle Reels mit Status; `--fix` löscht nur `__pycache__`. |
| `repo_sync.py` | Nur für Claude-Projekte mit GitHub-Sicherung: zieht den Stand von `/mnt/project-files` in eine Repository-Kopie (ohne Videos, Regeln in `../.gitignore`). |
| `ansicht.py` | Kleine Ansichten für Claude (spart Nutzungslimit): `reel <video> --edl edl.json` ein Frame pro Shot als Raster mit #Nr, `clip <clip> <von> <bis>` dichte Frames (Peak, Wiederholung), `bild <bild> --teil 2/4` Ausschnitt eines Storyboards. Höchstens ~1,1 MP, Ausgabe in `$REEL_WORK/ansicht/`. |
| `pipeline/` | Schnitt-Pipeline: `ingest.py` Sichtung, `extract.py` Frames, `timing.py` Tempo/Ramps, `render.py` Effekte + Look + Master, `storyboard.py`, `vorschau.py` Vorschau-Video, `varianten.py` drei Varianten zur Auswahl bauen, vergleichen und die gewählte exportieren, `export.py` Instagram-2-Pass + Ton + Titelbild, `verify.py` Schnitte/808/Ende/Pegel, `test_pipeline.py` Ende-zu-Ende-Test ohne Drive (~3 min). Ablauf pro Reel: `../README.md`. |
| `analyse/` | Song-, Clip- und Reel-Analyse, Shotlisten-Vorschlag (Doku in `analyse/README.md`). |
| `vfx/` | 61 Effekte, 7 Looks mit Vergleichsbild (`looks.py vergleich <bild>`), Galerie (Doku in `vfx/README.md`). |
| `fonts/` | Schriften für Titel und Text-Effekte (Doku in `fonts/README.md`). |

- **Arbeitsordner** im Container: `$REEL_WORK`, Standard `/home/user/reel` (Downloads, Frames, Master, Mix). Große Zwischendaten gehören nie in den Projektordner.
- **Look:** `render.py` backt den Look aus `stil.json` als 33³-LUT und legt ihn am Ende der ffmpeg-Kette an (`lut3d … tetrahedral`); Storyboard und Vorschaubilder nutzen denselben Look. Für einen einzelnen Lauf überschreibt `REEL_LOOK=moody` (oder ein `.cube`-Pfad, `none`) den Look.
- **Soundeffekte:** `../sfx/` (Liste und Anker in `sfx/README.md`, Hörprobe `sfx_vorschau.mp3`). Eigene SFX aus dem Drive-Ordner gehen genauso.
- **Schriften:** Montserrat und Inter kommen aus dem Setup-Skript (`/usr/share/fonts/truetype/`), dazu Bebas Neue, League Spartan und Oswald in `fonts/` (kein Setup nötig); in der `fx.json` als `"weight": "BebasNeue-Bold"`. Eigene Markenschrift dort ablegen.
- **Neuer Drive-Ordner ohne Tags:** `analyse.py vorbereiten --manifest … --vorschau` behält die Downloads in `$REEL_WORK/dl` und zeichnet das Vorschau-Storyboard; `shotliste.py` füllt Slots ohne passenden Tag mit dem besten freien Clip (`passt: frei`).
- **Drei Varianten zur Auswahl:** `pipeline/varianten.py <reel>` baut aus `schnitt/A/`, `B/`, `C/` je Vorschau-Video und Storyboard (`<name>_A_vorschau.mp4`, `<name>_A_storyboard.jpg` …) und prüft, dass sich jedes Paar in mindestens 2 von 3 Punkten unterscheidet (Songabschnitt, Clip-Auswahl, Tempo/Effekt-Dichte; `--check` ohne Rendern). `--wahl X` exportiert die gewählte Variante, prüft sie und räumt die Varianten nach `archiv/varianten/`; `--fassung v2` für Feedback-Runden.
- **Vorschau-Video** (`varianten.py` ruft es je Variante auf): `pipeline/vorschau.py master.mp4 <out>.mp4 mix.wav` macht aus dem Master ein Handy-Video 720×1520 (~40 s Rechenzeit, ~12 MB für 28 s): oben das Reel unverändert, darunter eine Leiste mit Zeitleiste (Shots, 808-Hits, Abspielkopf), Shot-Nummer wie im Storyboard, Kapitel, Clip, Zeit, Takt und Effekt-Tags, die im Moment des Effekts aufleuchten. Danach läuft der Anfang 2 Takte lang noch einmal (`--loop 8`, Beats) wie auf Instagram.
- **Fotos** (nur auf Wunsch): `ingest.py`/`extract.py` nehmen HEIC vom iPhone, JPG und PNG aus dem Manifest als Standbild-Clip (EXIF gedreht, Display P3 → sRGB, Aufnahmezeit aus EXIF); in der EDL wie ein Clip mit `src` 0, Bewegung per `push` in der fx.json. HEIC braucht `pillow-heif`, das `reelcfg.py` beim ersten Foto selbst nachinstalliert (braucht pypi im Netzwerk).
- **Tempo-Änderung** nie mit `pedalboard.time_stretch` (driftet bis 30 ms) oder ffmpeg `atempo` (~17 ms Versatz); `reel_audio.py` nutzt rubberband-cli.
