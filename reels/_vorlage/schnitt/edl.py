#!/usr/bin/env python3
"""Schnittliste einer Variante -> edl.json, fx.json, audio_spec.json im selben Ordner.

    cd <reel>/schnitt/A && python3 edl.py        # genauso B und C (neues_reel.py legt alle drei an)

Der Nutzer bekommt 3 deutlich verschiedene Varianten zur Auswahl (Songabschnitt, Auswahl/Story, Tempo/Effekt-Dichte;
jedes Paar in mindestens 2 Punkten anders, alle im Stil-Leitfaden). Bauen und vergleichen:
tools/pipeline/varianten.py <reel> (--check nur Unterschied-Check).
Vorher grid.json anlegen (Beat-Raster des Songs, gemeinsam in schnitt/ oder hier): {"per": …, "ph": …, "bpm": …}.
Regeln: Stil-Leitfaden.md und stil.json im Projektordner (Kapitel, Effekt-Budget, Finale, erlaubte Extras).
Die Prüfungen unten melden Verstöße gegen den Stil, brechen aber nur bei harten Fehlern ab.

Shot-Zeile: s(beats, kapitel, clip, src, mode, tags, beschreibung, fx=dict(...), prev=Vorschauzeit, **extra)
  clip  Kürzel aus dem Dateinamen, z. B. "6132" für IMG_6132.MOV
  src   Sekunde im Clip, an der der Shot beginnt (Echtzeit-Shot: Endposition der Bewegung vor dem Schnitt!)
  mode  normal | ramp | ramp_hold | speed (+ speed=0.5) | freeze (+ freeze_at=Beats) | fast | split (+ strips=[…])
  tags  Effekt-Tags fürs Storyboard; fx = Parameter für tools/pipeline/render.py (Liste dort im Kopf)
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJEKT = next(p for p in HERE.parents if (p / "tools" / "stil.py").exists())
sys.dont_write_bytecode = True  # kein __pycache__ im geteilten Projektordner
sys.path.insert(0, str(PROJEKT / "tools"))
from stil import STIL  # noqa: E402

g = json.load(open(HERE / "grid.json" if (HERE / "grid.json").exists() else HERE.parent / "grid.json"))
per, ph = g["per"], g["ph"]

# ---- pro Reel anpassen -------------------------------------------------------------------------------
TITEL = "{NAME}"
VARIANTE, VARIANTE_NAME = "{VARIANTE}", "{VARIANTE_NAME}"    # Name darf zum Reel passen
# Idee: {VARIANTE_IDEE}
UNTERSCHIED = "{VARIANTE_KURZ}"   # 1 Zeile fürs Storyboard und den Nutzer: was diese Variante anders macht
UNTERTITEL = "Variante " + VARIANTE + " · " + VARIANTE_NAME
SONG = "Interpret – Titel"
SONG_DATEI = "/home/user/reel/song.mp3"   # Song im Arbeitsordner (Download aus dem Drive-Ordner)
HOOK_EINS = 32                             # Beat-Nummer der Eins der Hook im Song (Takt × 4)
AUFTAKT = 0                                # Beats vor der Hook (0 oder 2); verlängert das Reel, kürzt nie das Ende
TAKTE = 16                                 # 16 oder 8, immer volle Takte bis zur nächsten Eins
DECODER_VERSATZ = 0.0                      # s, Projektanweisungen Abschnitt 2 (song_analyse.py eicht schon selbst)
HITS = [0, 4, 8, 12, 16, 20, 24, 28, 32, 36, 40, 44, 48, 52, 56, 60]   # 808-Hits in Beats ab Reel-Start (Akzent-Karte)
ERLAUBT = []                               # Extras, die der Nutzer für dieses Reel will, z. B. ["Split-Screen", "SFX"]
P808, P808_NACH, MINI = STIL["punch"]["808"], STIL["punch"]["nachschlag"], STIL["punch"]["clap"]   # Punch-Stärken

S = []


def s(beats, sec, clip, src, mode, tags, desc, fx=None, prev=None, **kw):
    S.append(dict(beats=beats, sec=sec, clip=clip, src=src, mode=mode, fx=tags, fxp=fx or {}, desc=desc,
                  prev=prev if prev is not None else src, **kw))


K1, K2, K3, K4 = STIL["kapitel"][:4]
# Beispiel mit Platzhalter-Clips A1…D6 (ersetzen). Je Kapitel 16 Beats; Ramp startet auf Schlag 3 im 2. Takt,
# ihr Hit (Beat 2 im Shot) liegt auf der Eins des 3. Takts.
s(2, K1, "A1", 0.0, "normal", ["Punch-in", "Flash"], "Opener: stärkstes Bild auf dem ersten Hit", dict(punch=[[0, P808]], flash=[[0, .55]]))
s(2, K1, "A2", 0.0, "normal", ["Push-in"], "Marke/Logo/Wiedererkennung", dict(push=[1.0, 1.06]))
s(2, K1, "A3", 0.0, "normal", ["Mini-Punch"], "Action mit Marke im Hintergrund", dict(punch=[[0, MINI, 0]]))
s(4, K1, "A5", 0.0, "ramp", ["Speed-Ramp"], "Showpiece 1: Höhepunkt der Bewegung auf dem Hit", dict(punch=[[0, MINI, 0], [2, 0.126]]))
s(2, K1, "A4", 0.0, "normal", ["Punch-in"], "Action nah, 808-Roll", dict(punch=[[0, P808], [1, P808_NACH]]))
s(4, K1, "A6", 0.0, "normal", ["Push-in"], "langsame Bewegung, ganz zu sehen", dict(push=[1.0, 1.06]))
s(2, K2, "B1", 0.0, "normal", ["Punch-in"], "Action", dict(punch=[[0, P808]]))
s(4, K2, "B3", 0.0, "normal", [], "Ablauf bis zur Endposition", {})
s(4, K2, "B4", 0.0, "ramp", ["Speed-Ramp"], "Showpiece 2", dict(punch=[[0, MINI, 0], [2, 0.126]]))
s(2, K2, "B2", 0.0, "normal", ["Mini-Punch"], "Detail/Nahaufnahme", dict(punch=[[0, MINI, 0]]))
s(4, K2, "B5", 0.0, "normal", ["Punch-in"], "Action total", dict(punch=[[0, P808]]))
s(2, K3, "C1", 0.0, "normal", ["Shake"], "Treffer/Schlag (Shake nur auf Aufprall)", dict(shake=[[0, 18, .6]]))
s(2, K3, "C2", 0.0, "normal", ["Punch-in"], "Power-Moment", dict(punch=[[0, P808]]))
s(2, K3, "C5", 0.0, "normal", ["Mini-Punch"], "Zusammenspiel, Gruppe", dict(punch=[[0, MINI, 0]]))
s(4, K3, "C3", 0.0, "ramp_hold", ["Speed-Ramp"], "Showpiece 3: Landung auf dem 808", dict(punch=[[0, MINI, 0], [2, 0.126]]))
s(2, K3, "C4", 0.0, "normal", ["Shake"], "zweiter Treffer", dict(shake=[[0, 18, .6]]))
s(4, K3, "C6", 0.0, "normal", ["Push-in"], "ruhiger Shot vor dem Finale", dict(push=[1.0, 1.10]))
s(2, K4, "D1", 0.0, "normal", ["Flash", "Punch-in"], "Payoff: Ergebnis, Ziel, Auftritt", dict(flash=[[0, .55]], punch=[[0, P808]]))
s(2, K4, "D2", 0.0, "normal", ["Punch-in"], "Payoff 2", dict(punch=[[0, P808]]))
s(2, K4, "D3", 0.0, "normal", ["Push-in"], "Emotion: Freude, Erschöpfung", dict(push=[1.0, 1.06]))
s(2, K4, "D4", 0.0, "normal", [], "Emotion 2", {})
s(2, K4, "D5", 0.0, "normal", ["Mini-Punch"], "Gruppe/Team", dict(punch=[[0, MINI, 0]]))
s(6, K4, "D6", 0.0, "speed", ["Zeitlupe", "Push-in"], "Finale: Schlussbild, loopt in den Opener", dict(push=[1.0, 1.12]), speed=0.5)
# -------------------------------------------------------------------------------------------------------

BEATS = AUFTAKT + TAKTE * 4
b = 0
for i, x in enumerate(S):
    x["n"], x["beat"], x["t"] = i + 1, b, b * per
    b += x["beats"]
assert b == BEATS, f"Summe {b} Beats, erwartet {BEATS} (Auftakt {AUFTAKT} + {TAKTE} Takte)"
used = [x["clip"] for x in S if x["clip"] != "split" and not x.get("cont")] + \
       [st["clip"] for x in S if x["clip"] == "split" for st in x["strips"]]
dup = sorted({c for c in used if used.count(c) > 1})
assert not dup, f"Clip doppelt: {dup}"

# Stil-Prüfung (Warnungen, Werte aus stil.json)
B = STIL["budget"]
warn = []
starts = {x["sec"]: x["beat"] for x in reversed(S)}
phrase = 16 if TAKTE == 16 else 8
for k, (sec, st) in enumerate(sorted(starts.items(), key=lambda kv: kv[1])):
    if k and (st - AUFTAKT) % phrase:
        warn.append(f"Kapitel {sec} startet auf Beat {st}, nicht auf einer Phrase ({phrase} Beats ab der Eins)")
for x in S:
    if x["mode"] in ("ramp", "ramp_hold") and (x["beat"] + 2 - AUFTAKT) % phrase != phrase // 2:
        warn.append(f"Ramp Shot {x['n']}: Hit auf Beat {x['beat'] + 2}, nicht auf der Eins des 3. Takts der Phrase")
short = [x["n"] for x in S if x["beats"] < B["min_beats"] and not x.get("cont")]
if short:
    warn.append(f"Szenen unter {B['min_beats']} Beats: Shot {short}")
count = lambda tag: sum(tag in x["fx"] for x in S)
if count("Speed-Ramp") > B["ramps"]:
    warn.append(f"{count('Speed-Ramp')} Ramps (Budget {B['ramps']})")
if count("Flash") > B["flashes"]:
    warn.append(f"{count('Flash')} Flashes (Budget {B['flashes']})")
if count("Shake") > B["shakes"]:
    warn.append(f"{count('Shake')} Shakes (Budget {B['shakes']})")
EXTRA = {"Split-Screen": "split", "Freeze-Frame": "freeze", "Whip-Zoom": "whip", "Echo-Trail": "echo",
         "Glitch": "glitch", "Text": "text", "Whoosh": "sfx", "SFX": "sfx"}
extra = [t for t, key in EXTRA.items() if count(t) and key not in STIL["erlaubt"] and t not in ERLAUBT]
if extra:
    warn.append(f"nur auf ausdrücklichen Wunsch (dann in ERLAUBT eintragen): {extra}")
fin, F = S[-1], STIL["finale"]
if fin["beats"] < F["beats"] or (F["zeitlupe"] and fin["mode"] not in ("slow", "speed")) \
        or (F["push"] and "push" not in fin["fxp"]):
    warn.append(f"Finale laut stil.json: mindestens {F['beats']} Beats"
                + (", Zeitlupe" if F["zeitlupe"] else "") + (", Push-in" if F["push"] else ""))

hook = ph + (HOOK_EINS - AUFTAKT) * per
E = dict(titel=TITEL, untertitel=UNTERTITEL, song=SONG, per=per, hook=hook, beats=BEATS, hits=HITS, shots=S,
         variante=VARIANTE, variante_name=VARIANTE_NAME, hinweis=UNTERSCHIED)
json.dump(E, open(HERE / "edl.json", "w"), indent=1, ensure_ascii=False)
json.dump({str(x["n"]): x["fxp"] for x in S}, open(HERE / "fx.json", "w"), indent=1)
dur = BEATS * per
json.dump(dict(duration=dur, music=[dict(file=SONG_DATEI, src=round(hook - DECODER_VERSATZ, 4), at=0.0, dur=dur,
                                         fade_in=0.004, fade_out=0.038)], sfx=[],
               match_loudness=False, target_lufs=None, ceiling_db=-0.3),
          open(HERE / "audio_spec.json", "w"), indent=1)
print(f"{len(S)} Shots, {len(used)} Clips, {BEATS} Beats = {dur:.3f} s, Song ab {hook:.3f} s")
print("\n".join("WARNUNG " + w for w in warn) or "Stil: keine Verstöße gefunden")
