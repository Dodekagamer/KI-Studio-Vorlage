# Einrichtung (einmalig, ca. 20 Minuten)

Diese Vorlage ist ein komplettes KI-Reel-Studio für Claude: Claude sichtet deine Clips aus Google Drive, analysiert den Song, schneidet beatgenau drei Varianten zur Auswahl und liefert das fertige Reel in Instagram-Qualität. Deinen eigenen Stil legt ihr beim ersten Mal gemeinsam fest.

Es gibt zwei Wege. **Weg A** (Claude-Projekt) ist der bequemste und läuft komplett in der Claude-App. **Weg B** (Claude Code mit GitHub) ist für dich, wenn du GitHub nutzt und jede Änderung versioniert haben willst. Die Namen der Menüpunkte können sich je nach App-Version leicht unterscheiden.

## Was du brauchst

- Ein Claude-Abo mit Codeausführung (Code execution) und Netzwerkzugriff.
- Google Drive mit deinen Clips und dem Song (je Reel ein Ordner).
- Diese Vorlage als ZIP (`KI-Studio-Vorlage.zip`) oder als GitHub-Repository.

## Weg A: Claude-Projekt

1. **Projekt anlegen:** in Claude unter „Projekte“ ein neues Projekt, z. B. „Reel-Studio“.
2. **Funktionen prüfen** (Einstellungen → Funktionen bzw. Settings → Capabilities):
   - „Codeausführung und Dateierstellung“: an
   - „Netzwerkzugriff erlauben“: an; in der Domain-Liste mindestens `drive.google.com` und `drive.usercontent.google.com`, für das Setup zusätzlich die Paketquellen (apt, `pypi.org`, `files.pythonhosted.org`).
3. **Umgebung:** Falls dein Projekt ein Setup-Skript für die Umgebung erlaubt, den Inhalt von `tools/setup.sh` dort eintragen (installiert ffmpeg und die Python-Pakete, ca. 70 s pro neuem Chat). Sonst macht Claude das zu Beginn selbst (`bash tools/setup.sh`).
4. **Google-Drive-Connector** verbinden (Einstellungen → Connectors).
5. **Projektanweisungen** („Projektanweisungen festlegen“ bzw. Set project instructions) mit diesem Text:
   > Du bist mein Reel-Studio. Projektordner ist /mnt/project-files. Liegen dort noch keine tools/, entpacke die KI-Studio-Vorlage*.zip aus dem Chat bzw. aus /mnt/project-files/uploads/ so, dass README.md, CLAUDE.md und tools/ direkt in /mnt/project-files liegen. Lies danach immer zuerst /mnt/project-files/CLAUDE.md und arbeite danach.
6. **Erster Chat im Projekt:** die ZIP anhängen und schreiben: „Richte das Studio ein und lass uns meinen Stil festlegen.“ Claude entpackt die Vorlage, prüft die Werkzeuge (Selbsttest) und stellt dir ein paar Fragen zu deinem Stil (siehe unten).

## Weg B: Claude Code mit GitHub

1. Ein **privates** GitHub-Repository anlegen und den Inhalt der Vorlage hochladen (alles aus dem Ordner `KI-Studio-Vorlage`, also `README.md`, `CLAUDE.md`, `tools/` … direkt im Hauptverzeichnis).
2. Auf claude.ai/code eine **Umgebung** anlegen: Netzwerkzugriff wie in Weg A Punkt 2, als Setup-Skript den Inhalt von `tools/setup.sh`.
3. Google-Drive-Connector verbinden.
4. Neue Session mit dem Repository und der Umgebung starten und schreiben: „Lass uns meinen Stil festlegen.“ `CLAUDE.md` erklärt Claude den Rest.
5. Videos kommen nicht ins Repository (`.gitignore`) und liegen nur im Container der Session: Fertige Reels also gleich herunterladen.

## Stil festlegen (erster Chat)

Claude fragt in einer Nachricht nach (alles optional):

- Account/Marke, wie Claude dich nennen soll, worum es in deinen Reels geht und für wen.
- 1–3 Reels, die dir gefallen (eigene oder fremde), **als Videodatei in einem Drive-Ordner** (Instagram-Links kann Claude nicht öffnen). Claude vermisst sie (Schnitttempo, Effekte, Lautheit) und leitet daraus deine Werte ab.
- Musik, Look (natürlich, kräftig, dunkel, Film, Schwarzweiß oder dein eigenes Preset als `.cube`), Text im Video ja/nein, Logo, Schrift, No-Gos.

Das Ergebnis landet in `Stil-Leitfaden.md` (für Menschen lesbar) und `stil.json` (für die Werkzeuge). Nach jedem Reel kannst du Feedback geben, Claude übernimmt es in den Leitfaden. Ohne Einrichtung schneidet Claude im neutralen Grundstil.

## Pro Reel

1. In Google Drive einen Ordner mit Clips und Song anlegen. Freigabe: **„Jeder mit dem Link – Betrachter“** (nicht „Bearbeiter“), sonst kann Claude nicht laden.
2. Im Projekt schreiben (nur der Ordner ist Pflicht):
   ```
   Neues Reel
   Ordner: <Drive-Link>
   Song: <Dateiname – oder leer lassen, wenn nur einer im Ordner liegt>
   Part: <Hook / Drop / Strophe – oder leer = Claude entscheidet>
   Länge: <z. B. 15 s oder 25–30 s – oder leer>
   Anlass/Fokus: <optional>
   Text im Video: <nein / ja: „…“>
   Muss rein / muss raus: <optional>
   ```
3. Du bekommst drei Varianten (Vorschau-Video mit Song, Shot-Nummern und Loop, dazu Storyboard). Du wählst eine, gern mit Änderungen per Shot-Nummer („#7 raus, #12 länger“).
4. Danach kommen die fertigen Dateien: `…_mit_song.mp4`, `…_ohne_ton.mp4` (für die Instagram-Musikbibliothek) und ein Titelbild.
5. Freigabe des Drive-Ordners danach wieder auf „Eingeschränkt“.

## Instagram-App (einmalig)

Einstellungen und Privatsphäre → „Datennutzung und Medienqualität“ → **„In höchster Qualität hochladen“ an** (ist standardmäßig aus), „Weniger mobile Daten verwenden“ aus. Dateien unverändert aufs Handy bringen (Download, Drive oder AirDrop, **nicht WhatsApp**), in Instagram keine Filter und kein Zuschneiden.

## Wenn etwas hakt

- „Kein Zugriff“ beim Download: Ordnerfreigabe prüfen (Punkt 1 bei „Pro Reel“) und ob die Drive-Domains erlaubt sind.
- Werkzeuge fehlen oder Selbsttest rot: Claude soll `bash tools/setup.sh` ausführen; dafür braucht es Netzwerkzugriff auf die Paketquellen.
- Das Nutzungslimit ist schnell erreicht: Claude arbeitet nach `Kurzanleitung.md` sparsam. Lange Chats lieber pro Reel neu beginnen.
