# KI-Reel-Studio: Projektordner

Instagram-Reels mit Claude: aus einem Google-Drive-Ordner mit Clips und Song wird ein beatgenau geschnittenes 9:16-Reel, jedes Mal mit drei Varianten zur Auswahl. Einrichtung: `EINRICHTUNG.md`.

**Für dich:** Ein neues Reel startest du mit einer Nachricht wie „Neues Reel, Ordner: <Drive-Link>“. Song, Part, Länge und Fokus sind optional (Vorlage in `EINRICHTUNG.md`). Der Drive-Ordner braucht die Freigabe „Jeder mit dem Link – Betrachter“. Du bekommst zuerst drei deutlich verschiedene Varianten (Standard: A Story, B Power mit anderer Songstelle und anderen Clips, C Clean kürzer und ruhiger). Jede kommt als Vorschau-Video (das echte Reel klein mit Song, Shot-Nummern und einer Wiederholung des Anfangs) mit Storyboard und einem Satz, was sie anders macht. Du wählst eine, gern mit Änderungswünschen, danach kommen die fertigen Videos. Alles zu einem Reel liegt danach in `reels/<datum>_<name>/`.

## Vor jedem Reel lesen (Claude)

1. `Kurzanleitung.md`: Ablauf mit Befehlen, Handwerk, das kein Werkzeug prüft, und Regeln zum sparsamen Arbeiten (spart das Nutzungslimit). Im Standardfall reicht das.
2. Die Kurzfassung des Stils oben in `Stil-Leitfaden.md` (`sed -n '1,/^---$/p' Stil-Leitfaden.md`). Ist der Stil noch nicht eingerichtet (`python3 tools/stil.py`), zuerst dort „Stil festlegen“.
3. Nur bei Bedarf und gezielt: `Reel-Studio_Projektanweisungen.md` (Arbeitsablauf im Detail, Stil-Matrix, Effekt-Rezepte, Looks, Stolperfallen, Anfrage-Vorlage Teil C). Vorrang: neuestes Feedback des Nutzers, dann Stil-Leitfaden, dann Anweisungen.

## Was wo liegt

| Ordner / Datei | Inhalt |
|---|---|
| `stil.json` | maschinenlesbarer Stil: Marke, Look, Vignette, Kapitel, Effekt-Budget, Finale, erlaubte Extras, Varianten A/B/C. Werkzeuge lesen ihn, `tools/stil.py` zeigt ihn |
| `Stil-Leitfaden.md` | der Stil für Menschen: Regeln, Begründungen, Referenzen, Änderungsprotokoll; Abschnitt „Stil festlegen“ für den Start |
| `reels/JJJJ-MM-TT_name/` | ein Ordner pro Reel: oben die aktuelle Fassung (vor der Wahl die drei Varianten), `schnitt/` (Raster, Schnittlisten A, B, C, Tonspur-Specs), `archiv/` (Varianten und ältere Fassungen), `README.md` (Steckbrief) |
| `reels/_vorlage/` | Vorlage dafür, anlegen mit `tools/neues_reel.py` |
| `referenz/` | Marke (Logo, Schrift, eigener Look), Referenz-Reels und ihre Messwerte, Sichtungen von Drive-Ordnern |
| `tools/` | Werkzeuge, Übersicht in `tools/README.md`: Setup, Selbsttest, Stil, Tonspur (`reel_audio.py`), Ansichten |
| `tools/pipeline/` | Schnitt-Pipeline: Sichtung, Frames, Render, Storyboard, Vorschau-Video, drei Varianten (`varianten.py`), Export, Prüfung |
| `tools/analyse/`, `tools/vfx/` | Analyse-Werkzeuge (Song, Clips, Shotliste, Reel-Prüfung) und Effekt-Bibliothek (61 Effekte, 7 Looks) |
| `sfx/` | SFX-Grundkit (28 synthetische Sounds), Liste in `sfx/README.md` |
| `uploads/`, `.notes/` | im Claude-Projekt vom System verwaltet (Anhänge aus Nachrichten), nicht anfassen |
| `CLAUDE.md`, `EINRICHTUNG.md` | Startdatei für Claude, Einrichtung für dich |

## Ein neues Reel

Ausführlich; kompakt mit Sparregeln in `Kurzanleitung.md`. Arbeitsordner für Downloads und Frames ist `/home/user/reel` im Container (`$REEL_WORK`), nicht der Projektordner.

1. **Ordner:** `python3 tools/neues_reel.py <name>` legt `reels/<heute>_<name>/` an, mit je einer Schnittliste für die Varianten aus `stil.json`.
2. **Material:** Drive-Ordner per Drive-Connector listen (`search_files`, `parentId`), Videos als `<id>\t<name>\t<bytes>` in `/home/user/reel/manifest.tsv`, Song nach `/home/user/reel/song.mp3` laden (Projektanweisungen Abschnitt 2). Fotos nur, wenn der Nutzer sie will: dann ebenfalls ins Manifest (HEIC vom iPhone geht, JPG, PNG); sie werden Standbild-Shots, Bewegung per Push-in in der `fx.json`.
3. **Sichtung:** `python3 tools/pipeline/ingest.py` (Keyframes, Metadaten, Aufnahmezeit je Clip), bei neuem Material `tools/analyse/clip_analyse.py` und eine Tags-Datei `schnitt/tags.json` (Format `tools/analyse/tags_beispiel.json`).
4. **Song:** `python3 tools/analyse/song_analyse.py /home/user/reel/song.mp3 -o <reel>/schnitt` schreibt Beat-Raster `grid.json`, Akzent-Karte und Hook-Vorschlag. Eins der Hook prüfen.
5. **Drei Schnittlisten:** `schnitt/A/edl.py`, `B/edl.py` und `C/edl.py` ausfüllen (Vorschlag mit `tools/analyse/shotliste.py`), je `python3 edl.py` (schreibt `edl.json`, `fx.json`, `audio_spec.json` und warnt bei Verstößen gegen den Stil). Jedes Paar muss sich in mindestens 2 von 3 Punkten unterscheiden: Songabschnitt, Auswahl/Story, Tempo/Effekt-Dichte. `python3 tools/pipeline/varianten.py <reel> --check` prüft das ohne Rendern.
6. **Varianten bauen:** `python3 tools/pipeline/varianten.py <reel>` zieht je Variante die Frames, rendert den Master, mischt den Ton und legt `<name>_A_vorschau.mp4` und `<name>_A_storyboard.jpg` (B und C genauso) in den Reel-Ordner. Rechenzeit je Variante etwa 7 min (24 Clips, 28 s). Eine Variante neu: `--nur B`.
7. **Pflicht-Stopp, Wahl:** die drei Vorschau-Videos und Storyboards an den Nutzer, je Variante ein Satz, was sie anders macht. Er wählt eine. Änderungswünsche in `schnitt/X/edl.py` einbauen und `varianten.py <reel> --nur X` laufen lassen.
8. **Export:** `python3 tools/pipeline/varianten.py <reel> --wahl X [--titel <frame>]` exportiert die gewählte Variante (`<name>_mit_song.mp4`, `_ohne_ton.mp4`, `_titelbild.jpg`), prüft sie mit `verify.py`, legt ihr Storyboard als `<name>_storyboard.jpg` nach oben und verschiebt alle Varianten-Dateien nach `archiv/varianten/`. Ist der Container seit den Varianten neu gestartet (Arbeitsordner leer), vorher Schritt 2 und 3 und `--nur X` wiederholen.
9. **Liefern:** Die Prüfung muss „alles OK“ melden. Steckbrief im Reel-README ausfüllen, Videos und Titelbild an den Nutzer. Feedback-Runde danach: alte Fassung samt Schnittliste nach `archiv/v1/`, `schnitt/X/edl.py` ändern, `--nur X`, dann `--wahl X --fassung v2`.

## Ordnung halten

- Pro Reel liegt oben nur die aktuelle Fassung, vor der Wahl die drei Varianten. Nach der Wahl kommen die Varianten nach `archiv/varianten/`, ältere Fassungen samt Schnittliste nach `archiv/v1/`, `archiv/v2/` …, nie löschen.
- Namen: `<name>_mit_song.mp4`, `<name>_ohne_ton.mp4`, `<name>_titelbild.jpg`, `<name>_storyboard.jpg`, Varianten `<name>_A_vorschau.mp4` und `<name>_A_storyboard.jpg` (B, C), Folgefassungen mit `_v2` usw.
- Große Zwischendaten (Downloads, Frames, Master ohne Ton, Mix) bleiben im Container und kommen nicht in den Projektordner.
- Wiederverwendbarer Code gehört nach `tools/`, einmalige Skripte in den `schnitt/`-Ordner des Reels.
- Prüfen: `python3 tools/ordnung.py` zeigt alle Reels mit Status und meldet, was nicht an seinem Platz liegt.

## Sicherung (optional)

- **Claude-Projekt:** Der Projektordner `/mnt/project-files` ist die Arbeitskopie. Wer zusätzlich eine Sicherung mit Versionsverlauf will, legt ein privates GitHub-Repository an; `python3 /mnt/project-files/tools/repo_sync.py <Repository-Kopie>` zieht den Stand hinein (ohne Videos, Songs und Storyboards, Regeln in `.gitignore`), danach committen und pushen.
- **Claude Code mit Repository:** Das Repository ist der Projektordner. Schnittlisten, Skripte und Steckbriefe committen; Videos bleiben draußen und sind weg, wenn der Container gelöscht wird.
