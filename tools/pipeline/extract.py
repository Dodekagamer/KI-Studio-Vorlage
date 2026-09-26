#!/usr/bin/env python3
"""Frames für die Schnittliste ziehen: je Clip das Quellfenster aller Shots ±1,5 s als JPG.

    REEL_WORK=/home/user/reel REEL_EDL=<reel>/schnitt/edl.json python3 extract.py [--jobs 3]

Braucht die EDL, WORK/manifest.tsv und WORK/meta/ (ingest.py). Schreibt WORK/frames/<clip>/f_%05d.jpg
und times.json (Quellzeit je Frame). HDR wird getonemappt. Quellen bis 1300 px Breite -> 1080×1920,
4K -> 1440×2560 (Reserve für Zooms); das Seitenverhältnis bleibt, Überstand schneidet render.py ab.
Prüft die Frame-Zahl gegen die Fensterlänge und zieht bei Ausfall einmal neu
(Lernpunkt: ein Clip hatte beim ersten Lauf nur 93 Frames). Fotos (meta "photo") werden ein einziges
Bild in derselben Größe (times [0.0]); render.py zeigt es als Standbild mit den Effekten der fx.json.
"""
import json
import re
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor

from PIL import Image

sys.dont_write_bytecode = True  # kein __pycache__ im geteilten Projektordner
from reelcfg import WORK, download, load_edl, load_photo, log, manifest, run, stem_of, tonemap_for
from timing import windows

JOBS = int(sys.argv[sys.argv.index("--jobs") + 1]) if "--jobs" in sys.argv else 3


def job(c, win, man):
    stem = stem_of(c, set(man))
    fid, name, size = man[stem]
    m = json.load(open(WORK / "meta" / f"{stem}.json"))
    a, b = win[c]
    a0, b0 = max(0.0, a - 1.5), min(m["dur"], b + 1.5)
    od = WORK / "frames" / c
    tj = od / "times.json"
    if m.get("photo"):
        return photo(c, fid, name, size, m, od, tj)
    if tj.exists():
        t = json.load(open(tj))["times"]
        if t and t[0] <= max(0.0, a - 0.3) + 0.02 and t[-1] >= min(m["dur"] - 0.05, b + 0.3):
            return f"{c}: schon da"
    path = WORK / "dl" / name
    if not download(fid, path, size, "extract"):
        log("extract", "FAIL download", c)
        return f"{c}: Download fehlgeschlagen"
    tw, th = (1440, 2560) if min(m["w"], m["h"]) > 1300 else (1080, 1920)
    vf = (tonemap_for(m["trc"]) + f"scale=w={tw}:h={th}:force_original_aspect_ratio=increase"
          ":force_divisible_by=2:flags=lanczos,showinfo")
    want = (b0 - a0) * m["fps"]
    for attempt in range(2):
        if od.exists():
            shutil.rmtree(od)
        od.mkdir(parents=True)
        r = run(["ffmpeg", "-v", "info", "-hide_banner", "-ss", f"{a0:.3f}", "-t", f"{b0 - a0:.3f}", "-i", path,
                 "-vf", vf, "-fps_mode", "passthrough", "-q:v", "3", f"{od}/f_%05d.jpg"])
        t = [a0 + float(x) for x in re.findall(r"pts_time:\s*([-0-9.]+)", r.stderr)]
        n = len(list(od.glob("f_*.jpg")))
        if n >= 0.97 * want - 2:
            break
        log("extract", "zu wenig Frames", c, n, "statt", round(want), "Versuch", attempt + 1)
    json.dump(dict(times=t[:n], fps=m["fps"], w=tw), open(tj, "w"))
    path.unlink()
    log("extract", "ok", c, f"{a0:.2f}-{b0:.2f}", n, "frames", m["trc"] or "SDR")
    return f"{c}: {n} Frames" + ("" if n >= 0.97 * want - 2 else f"  WARNUNG: erwartet ~{round(want)}")


def photo(c, fid, name, size, m, od, tj):
    if tj.exists():
        return f"{c}: schon da (Foto)"
    path = WORK / "dl" / name
    if not download(fid, path, size, "extract"):
        log("extract", "FAIL download", c)
        return f"{c}: Download fehlgeschlagen"
    im = load_photo(path)
    tw, th = (1440, 2560) if min(im.size) > 1300 else (1080, 1920)
    k = max(tw / im.width, th / im.height)          # wie force_original_aspect_ratio=increase
    im = im.resize((round(im.width * k / 2) * 2, round(im.height * k / 2) * 2), Image.Resampling.LANCZOS)
    od.mkdir(parents=True, exist_ok=True)
    im.save(od / "f_00001.jpg", quality=92)
    json.dump(dict(times=[0.0], fps=30.0, w=tw, photo=True), open(tj, "w"))
    path.unlink()
    log("extract", "ok", c, "Foto", im.size)
    return f"{c}: Foto {im.width}×{im.height}"


if __name__ == "__main__":
    E, man = load_edl(), manifest()
    win = windows(E)
    with ThreadPoolExecutor(JOBS) as ex:
        for line in ex.map(lambda c: job(c, win, man), sorted(win)):
            print(line, flush=True)
    log("extract", "DONE")
