#!/usr/bin/env python3
"""Shotlisten-Vorschlag nach Stil-Leitfaden: 4 Kapitel auf den Song-Phrasen, 2-Beat-Raster,
Bild-Akzent aus der Akzent-Karte, Clips nach Kapitel-Tags und Clip-Analyse.

    python3 shotliste.py --song OUT/song.json --tags tags.json -o OUTDIR
    python3 shotliste.py --song OUT/song.json --clips OUT/clips.json --tags tags.json --fenster 2 -o OUTDIR
    python3 shotliste.py --song OUT/song.json --tags tags.json --start-takt 8 --takte 8 --auftakt 0 -o OUTDIR
    python3 shotliste.py --song OUT/song.json --tags tags.json --fenster 2 --meiden <reel>/schnitt/A/edl.json -o B
      (Variante B: andere Songstelle, Clips von A nur, wenn sonst nichts passt)

Eingaben:
- song.json von song_analyse.py (Fenster 1 = Empfehlung; --fenster N oder --start-takt/--takte).
- clips.json von clip_analyse.py (optional): Dauer, Highlights (peak), Score je Clip.
- tags.json (optional, sonst nur grober Vorschlag): {"6166": {"kapitel": [3], "tags": ["showpiece"],
  "desc": "Sprung auf die Box", "moment": 6.4}, ...}; Schlüssel = Clipname ohne "IMG_" und Endung.
  Format und Tag-Liste: tags_beispiel.json daneben.

Ausgabe: shotliste.json (Felder der Render-EDL: n, beat, t, beats, clip, src, mode, fx, fxp, desc) und
shotliste.md mit Tabelle und Checkliste. Das ist ein Entwurf fürs Storyboard: In-Punkte danach an dichten
Frames prüfen (Projektanweisungen Punkt 14).

Kapitel-Namen, Punch-Stärken und Budget kommen aus stil.json. Eigene Kapitel-Vorlagen gehen dort unter
"shotliste": {"vorlage16": {"1": [[0, 2, "opener"], …], …}, "vorlage8": {…}, "slot_tags": {"slot": [["tag"], …]}}.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from stil import STIL  # noqa: E402

KAPITEL = STIL["kapitel"][:4]
# Vorlage pro Kapitel mit 16 Beats: (Offset, Beats, Slot). Ramp: Anlauf ab Schlag 3 im 2. Takt,
# Hit auf der Eins im 3. Takt. Kapitel 4 ist der Payoff, der letzte Slot das Finale.
VORLAGE16 = {
    1: [(0, 2, "opener"), (2, 2, "branding"), (4, 2, "action"), (6, 4, "ramp"), (10, 2, "action"), (12, 4, "langsam")],
    2: [(0, 2, "action"), (2, 2, "action"), (4, 2, "nah"), (6, 4, "ramp"), (10, 2, "action"), (12, 4, "langsam")],
    3: [(0, 2, "power"), (2, 2, "power"), (4, 2, "nah"), (6, 4, "ramp"), (10, 2, "action"), (12, 4, "action")],
    4: [(0, 2, "payoff"), (2, 2, "payoff"), (4, 2, "emotion"), (6, 2, "emotion"), (8, 2, "gruppe"), (10, 6, "finale")],
}
VORLAGE8 = {
    1: [(0, 2, "opener"), (2, 2, "branding"), (4, 2, "action"), (6, 2, "action")],
    2: [(0, 2, "action"), (2, 2, "nah"), (4, 4, "ramp")],
    3: [(0, 2, "power"), (2, 2, "action"), (4, 4, "ramp")],
    4: [(0, 2, "payoff"), (2, 2, "emotion"), (4, 4, "finale")],
}
# Welche Tags ein Slot sucht (erste passende Gruppe gewinnt)
SLOT_TAGS = {
    "opener": [["opener"], ["gruppe", "branding"], ["branding"], ["gruppe"]],
    "branding": [["branding"], ["gruppe"]],
    "action": [["action"], ["power"], ["langsam"]],
    "nah": [["action", "nah"], ["nah"], ["action"]],
    "langsam": [["langsam"], ["action"]],
    "ramp": [["showpiece"], ["action", "nah"], ["action"]],
    "power": [["power"], ["schlag"], ["action"]],
    "payoff": [["payoff"], ["emotion"], ["action"]],
    "emotion": [["emotion"], ["payoff"], ["gruppe"]],
    "gruppe": [["gruppe"], ["emotion"]],
    "finale": [["finale"], ["gruppe", "branding"], ["gruppe"]],
}
_eigen = STIL.get("shotliste", {})
if _eigen.get("vorlage16"):
    VORLAGE16 = {int(k): [tuple(x) for x in v] for k, v in _eigen["vorlage16"].items()}
if _eigen.get("vorlage8"):
    VORLAGE8 = {int(k): [tuple(x) for x in v] for k, v in _eigen["vorlage8"].items()}
SLOT_TAGS.update(_eigen.get("slot_tags", {}))
PUNCH = {"808": STIL["punch"]["808"], "808_nachschlag": STIL["punch"]["nachschlag"], "clap": STIL["punch"]["clap"]}
BUDGET = STIL["budget"]
MEIDEN = set()   # Clips anderer Varianten (--meiden): nur nehmen, wenn sonst nichts passt


def stem(name):
    s = Path(str(name)).stem
    return s[4:] if s.upper().startswith("IMG_") else s


def load_pool(clips_json, tags_json):
    pool = {}
    tags = json.loads(Path(tags_json).read_text()) if tags_json else {}
    for k, v in tags.items():
        if k.startswith("_") or "ausschuss" in v.get("tags", []):
            continue
        pool[k] = dict(clip=k, kapitel=v.get("kapitel", [1, 2, 3, 4]), tags=set(v.get("tags", [])),
                       desc=v.get("desc", ""), moment=v.get("moment"), dur=None, fps=None, score=50.0,
                       highlights=[], analysiert=False)
    if clips_json:
        for c in json.loads(Path(clips_json).read_text()).get("clips", []):
            k = stem(c["name"])
            if tags and k not in pool:
                continue                       # mit Tags: nur getaggte, nicht als Ausschuss markierte Clips
            p = pool.setdefault(k, dict(clip=k, kapitel=[1, 2, 3, 4], tags={"action"}, desc=c["name"], moment=None))
            m = c.get("stats", {}).get("motion_mean", 0)
            p.update(dur=c.get("dur"), fps=c.get("fps"), score=float(c.get("score", 50)),
                     highlights=c.get("highlights", []), analysiert=True, motion=m, flags=c.get("flags", []))
            if not tags:                        # ohne Tags: grob nach Bewegung einteilen
                p["tags"] = {"action", "nah"} if m > 0 else {"gruppe"}
    return pool


def pick(pool, used, kap, slot, need_s):
    for group in SLOT_TAGS[slot]:
        cands = [p for p in pool.values() if p["clip"] not in used and kap in p["kapitel"]
                 and set(group) <= p["tags"] and (p["dur"] is None or p["dur"] >= need_s)
                 and (slot == "ramp" or "showpiece" not in p["tags"])]     # Showpieces für die Ramps aufheben
        if not cands:
            cands = [p for p in pool.values() if p["clip"] not in used and set(group) <= p["tags"]
                     and (p["dur"] is None or p["dur"] >= need_s) and not ({"payoff"} & p["tags"] and kap < 4)
                     and (slot == "finale" or "finale" not in p["tags"])]            # Schlussbild aufheben
        if cands:
            # analysierte zuerst, dann Score, dann bekannter Moment
            cands.sort(key=lambda p: (p["clip"] in MEIDEN, -p["analysiert"], -p["score"], p["moment"] is None))
            return cands[0], group
    # kein Tag passt (z. B. neuer Ordner ohne Tags): bester freier Clip statt Lücke
    rest = [p for p in pool.values() if p["clip"] not in used and (p["dur"] is None or p["dur"] >= need_s)
            and (slot == "ramp" or "showpiece" not in p["tags"]) and not ({"payoff"} & p["tags"] and kap < 4)
            and (slot == "finale" or "finale" not in p["tags"])]
    if rest:
        rest.sort(key=lambda p: (p["clip"] in MEIDEN, -p["analysiert"], -p["score"]))
        return rest[0], ["frei"]
    return None, None


def src_in(p, beats, per, hit_off_beats, speed_before=1.0, speed=1.0):
    """In-Punkt so wählen, dass der beste Moment auf dem Hit liegt. Vorrang: gesichteter Moment
    aus den Tags, dann Highlights der Clip-Analyse (nach Score), der erste, der ganz in den Clip passt."""
    need = beats * per * speed
    peaks = ([p["moment"]] if p["moment"] is not None else []) + \
            [h["peak"] for h in sorted(p["highlights"], key=lambda h: -h.get("score", 0)) if h.get("peak") is not None]
    if not peaks:
        return (round(max(0.0, p["dur"] / 2 - need / 2), 3) if p["dur"] else None), None
    for peak in peaks:
        s = peak - hit_off_beats * per * speed_before
        if s >= 0 and (not p["dur"] or s + need <= p["dur"] - 0.05):
            return round(s, 3), round(peak, 3)
    peak = peaks[0]
    s = peak - hit_off_beats * per * speed_before
    if p["dur"]:
        s = min(s, p["dur"] - need - 0.05)
    return round(max(0.0, s), 3), round(peak, 3)


def build(song, pool, fenster=1, start_takt=None, takte=None, auftakt=None):
    per = song["beat_period"]
    bars = [b["t"] for b in song["bars"]]
    if start_takt is not None:
        b0, n_takte, auf = start_takt, takte or 16, auftakt or 0
    else:
        w = song["windows"][fenster - 1]
        n_takte, auf = w["takte"], w["auftakt_beats"]
        b0 = int(round((w["start"] + auf * per - bars[0]) / (4 * per)))
    t0 = bars[b0] - auf * per
    beats_total = n_takte * 4 + auf
    amap = {a["hb"]: a for a in song["accent_map"]}
    k808 = song["onsets"]["kick808"]
    vorlage = VORLAGE16 if n_takte >= 16 else VORLAGE8
    kap_len = 16 if n_takte >= 16 else 8
    slots = []
    if auf:
        slots.append((1, -auf, auf, "opener"))
    for k in range(1, 5):
        for off, bt, slot in vorlage[k]:
            if k == 1 and off == 0 and not auf:
                slot = "opener"
            slots.append((k, (k - 1) * kap_len + off, bt, slot))
    used, shots = set(), []
    n_flash = n_shake = n_ramp = 0
    ramp_ohne_808 = []
    for n, (k, bo, bt, slot) in enumerate(slots, 1):
        mode = {"ramp": "ramp", "finale": "slow" if STIL["finale"]["zeitlupe"] else "normal"}.get(slot, "normal")
        if mode == "ramp" and k == 3:
            mode = "ramp_hold"
        speed = 0.5 if mode == "slow" else 1.0
        need = bt * per * (1.4 if mode.startswith("ramp") else speed) + 0.2
        p, group = pick(pool, used, k, slot, need)
        beat_abs = b0 * 4 + bo                              # Beat-Nummer ab Takt 0
        hb = beat_abs * 2
        acc = amap.get(hb, {}).get("kind", "none")
        fx, fxp = [], {}
        if acc in PUNCH:
            fx.append({"808": "Punch-in", "808_nachschlag": "Punch-in 0,12", "clap": "Mini-Punch"}[acc])
            fxp["punch"] = [[0, PUNCH[acc]]]
        else:
            fx.append("harter Schnitt")
        # 808 im Shot (nicht auf dem Schnitt) -> Punch im selben Shot (höchstens 2)
        inner = [o for o in k808 if beat_abs + 0.25 <= o["beat"] < beat_abs + bt - 0.01]
        inner.sort(key=lambda o: -o["strength"])
        for o in inner[:2]:
            a = 0.05 if mode == "slow" else PUNCH["808_nachschlag"]
            if mode.startswith("ramp") and abs(o["beat"] - (beat_abs + 2)) < 0.01:
                continue
            fxp.setdefault("punch", []).append([round(o["beat"] - beat_abs, 2), a])
            fx.append(f"Punch@{o['beat'] - beat_abs:g}")
        hit_off = 1.0
        if mode.startswith("ramp"):
            n_ramp += 1
            if amap.get(hb + 4, {}).get("kind") not in ("808", "808_nachschlag"):
                ramp_ohne_808.append(n)
            fx.append("Speed-Ramp" + (" (hold)" if mode == "ramp_hold" else "") + ", Hit@2 Punch 0,126")
            fxp.setdefault("punch", []).append([2, 0.126])
            hit_off = 2.8                                   # ~2,8 Beats Quelle bis zum Hit (1,0× -> 2,2×)
        if slot == "finale":
            fx += (["Zeitlupe 0,5×"] if mode == "slow" else []) + (["Push-in +12 %"] if STIL["finale"]["push"] else [])
            if STIL["finale"]["push"]:
                fxp["push"] = [1.0, 1.12]
            hit_off = 1.0
        if slot == "branding" and "push" not in fxp:
            fx.append("Push-in +6 %")
            fxp["push"] = [1.0, 1.06]
        if p and "nah" in p["tags"] and slot in ("nah", "action") and "push" not in fxp:
            fx.append("Push-in +10 %")
            fxp["push"] = [1.0, 1.10]
        if acc in ("808", "808_nachschlag") and n_flash < BUDGET["flashes"] and k == 4 and \
                (slot == "finale" or bo == 3 * kap_len):
            fx.append("Flash")
            fxp["flash"] = [[0, 0.55]]
            n_flash += 1
        if p and "schlag" in p["tags"] and acc in ("808", "808_nachschlag") and n_shake < BUDGET["shakes"]:
            fx.append("Shake")
            fxp["shake"] = [[0, 20]]
            n_shake += 1
        shot = dict(n=n, kapitel=k, kapitel_name=KAPITEL[k - 1], slot=slot, beat=bo + auf, beats=bt,
                    t=round(bo * per + auf * per, 4), song_t=round(t0 + (bo + auf) * per, 4),
                    takt=f"T{beat_abs // 4}.{beat_abs % 4 + 1}", akzent=acc, mode=mode, fx=fx, fxp=fxp)
        if p:
            used.add(p["clip"])
            s, peak = src_in(p, bt, per, hit_off, speed=speed)
            shot.update(clip=p["clip"], src=s, peak=peak, desc=p["desc"], passt=" + ".join(group),
                        analysiert=p["analysiert"])
        else:
            shot.update(clip=None, src=None, peak=None, desc=f"FEHLT: Clip für '{slot}'", passt="", analysiert=False)
        shots.append(shot)
    # Checkliste (Budget aus stil.json)
    short = [s["n"] for s in shots if s["beats"] < BUDGET["min_beats"]]
    checks = {
        "segmente": len(shots) + sum(1 for s in shots if s["mode"].startswith("ramp")),
        "ramps": n_ramp, "flashes": n_flash, "shakes": n_shake, "ramp_hit_ohne_808": ramp_ohne_808,
        "szenen_unter_2_beats": short,
        "clips_doppelt": len(used) != len([s for s in shots if s["clip"]]),
        "fehlende_clips": [s["n"] for s in shots if not s["clip"]],
        "finale_beats": shots[-1]["beats"],
        "ohne_analyse": [s["clip"] for s in shots if s["clip"] and not s["analysiert"]],
    }
    return dict(song=song["file"], per=per, bpm=song["bpm"], song_start=round(t0, 4), takte=n_takte, auftakt=auf,
                beats=beats_total, dauer=round(beats_total * per, 4), start_takt=b0,
                kapitel=[dict(n=k, name=KAPITEL[k - 1], start_s=round(((k - 1) * kap_len + auf) * per, 3) if k > 1 else 0.0)
                         for k in range(1, 5)],
                checks=checks, shots=shots)


def write_md(E, out):
    L = [f"# Shotlisten-Vorschlag ({E['takte']} Takte{' + Auftakt' if E['auftakt'] else ''}, {E['dauer']:.2f} s)", "",
         f"Song ab {E['song_start']:.3f} s (T{E['start_takt']}.1{' minus 2 Beats Auftakt' if E['auftakt'] else ''}), "
         f"{E['bpm']:.2f} BPM, {E['beats']} Beats. Entwurf: In-Punkte an dichten Frames prüfen.", "",
         "| # | Zeit | Takt | Beats | Kapitel | Clip | In (s) | Modus | Akzent | Effekte | Inhalt |",
         "|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in E["shots"]:
        L.append(f"| {s['n']} | {s['t']:.2f} | {s['takt']} | {s['beats']} | {s['kapitel']} | {s['clip'] or '–'} | "
                 f"{'offen' if s['src'] is None else s['src']} | {s['mode']} | {s['akzent']} | {', '.join(s['fx'])} | {s['desc']} |")
    c = E["checks"]
    L += ["", "## Checkliste", "",
          f"- Segmente (Ramps zählen doppelt): {c['segmente']} (Richtwert {BUDGET['segmente_16'][0]}–"
          f"{BUDGET['segmente_16'][1]} pro 16 Takte)",
          f"- Ramp-Hit ohne 808 (Shot verschieben): {c['ramp_hit_ohne_808'] or 'keiner'}",
          f"- Ramps {c['ramps']} (max. {BUDGET['ramps']}), Flashes {c['flashes']} (max. {BUDGET['flashes']}), "
          f"Shakes {c['shakes']} (max. {BUDGET['shakes']}, nur auf Schlägen)",
          f"- Szenen unter {BUDGET['min_beats']} Beats: {c['szenen_unter_2_beats'] or 'keine'}; "
          f"Finale {c['finale_beats']} Beats",
          f"- Fehlende Clips: {c['fehlende_clips'] or 'keine'}; ohne Clip-Analyse (In-Punkt geschätzt): "
          f"{', '.join(c['ohne_analyse']) or 'keine'}"]
    Path(out).write_text("\n".join(L) + "\n")


def main():
    ap = argparse.ArgumentParser(description="Shotlisten-Vorschlag nach Stil-Leitfaden")
    ap.add_argument("--song", required=True, help="song.json von song_analyse.py")
    ap.add_argument("--clips", help="clips.json von clip_analyse.py")
    ap.add_argument("--tags", help="Tags je Clip (Format: tags_beispiel.json)")
    ap.add_argument("--fenster", type=int, default=1, help="Reel-Fenster aus song.json (1 = Empfehlung)")
    ap.add_argument("--start-takt", type=int)
    ap.add_argument("--takte", type=int)
    ap.add_argument("--auftakt", type=int, default=0, help="Beats Auftakt vor der Eins (0 oder 2)")
    ap.add_argument("--meiden", help="Clips einer anderen Variante meiden: edl.json/shotliste.json oder Kürzel "
                                     "mit Komma (z. B. für Variante B: --meiden reel/schnitt/A/edl.json)")
    ap.add_argument("-o", "--out", default=".")
    a = ap.parse_args()
    for m in (a.meiden or "").split(","):
        if m.strip().endswith(".json"):
            for sh_ in json.loads(Path(m.strip()).read_text())["shots"]:
                MEIDEN.update([st["clip"] for st in sh_.get("strips", [])] if sh_["clip"] == "split" else [sh_["clip"]])
        elif m.strip():
            MEIDEN.add(stem(m.strip()))
    song = json.loads(Path(a.song).read_text())
    pool = load_pool(a.clips, a.tags)
    E = build(song, pool, a.fenster, a.start_takt, a.takte, a.auftakt if a.start_takt is not None else None)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "shotliste.json").write_text(json.dumps(E, ensure_ascii=False, indent=1))
    write_md(E, out / "shotliste.md")
    for s in E["shots"]:
        print(f"#{s['n']:<2} {s['t']:6.2f}s {s['takt']:>6} {s['beats']}B K{s['kapitel']} {str(s['clip']):>5} "
              f"in {s['src']}  {s['mode']:9s} {', '.join(s['fx'])}")
    print("Checkliste:", json.dumps(E["checks"], ensure_ascii=False))
    print(f"-> {out / 'shotliste.json'}, shotliste.md")


if __name__ == "__main__":
    main()
