#!/usr/bin/env python3
"""Tonspur für Reels: mehrere Songs + Soundeffekte sample-genau mischen.

    python3 reel_audio.py mix   spec.json  mix.wav     # mischen, Bericht ausgeben
    python3 reel_audio.py mux   video.mp4  mix.wav  out.mp4   # AAC 320k/48 kHz, Video per Stream-Copy
    python3 reel_audio.py check datei.(wav|mp4) [referenz]    # Pegel in 100-ms-Blöcken, Stille, LUFS, True Peak

spec.json (Zeiten in Sekunden; relative Pfade gelten ab dem Ordner der spec,
"sfx/…" fällt auf sfx/ im Projektordner zurück):

{
  "duration": 24.0,                       # = Videodauer
  "music": [
    {"file": "songA.mp3", "src": 61.224, "at": 0.0,   "dur": 12.25,
     "fade_in": 0.004, "fade_out": 0.25},
    {"file": "songB.mp3", "src": 30.487, "at": 11.75, "dur": 12.25,
     "fade_in": 0.25,  "fade_out": 0.038, "gain_db": 0, "tempo": 1.0, "semitones": 0}
  ],
  "sfx": [
    {"file": "sfx/whoosh.wav", "at": 12.0, "align": "peak",  "gain_db": -8},
    {"file": "sfx/impact.wav", "at": 0.0,  "align": "start", "gain_db": -4, "duck_db": 4}
  ],
  "match_loudness": true,   # Songs vorher auf gleiche Lautheit (LUFS des leisesten Songs)
  "target_lufs": null,      # null = Songpegel behalten; z. B. -14 = Gesamtmix normalisieren
  "ceiling_db": -1.0        # True-Peak-Grenze (Look-ahead-Limiter greift nur darüber)
}

- src ist die Position im ffmpeg-Decode des Songs (dieselbe Zeitachse wie die
  librosa-Analyse); den Decoder-Versatz (Anweisungen Abschnitt 2, Punkt 8) dort einrechnen.
- Überlappende Songs mit fade_out/fade_in = Crossfade (Equal-Power). Harter Wechsel auf
  einer Taktgrenze: at_B = at_A + dur_A, Fades 4 ms bzw. 38 ms.
- tempo/semitones: Rubber Band (rubberband-cli); tempo 1.05 = 5 % schneller, z. B. um die
  BPM zweier Songs anzugleichen. src/dur beziehen sich auf die Reel-Zeit, verbraucht
  werden dur*tempo Sekunden Quelle.
- align: "start" (Datei-Anfang auf at), "peak" (lautester Punkt auf at), "end" (Ende auf at).
- duck_db: Musik für die Dauer des Effekts um so viele dB absenken (20 ms Attack, 150 ms Release).
"""
import json
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
import pyloudnorm as pyln
import soundfile as sf
from scipy.ndimage import minimum_filter1d, uniform_filter1d
from scipy.signal import resample_poly

SR = 48000
PROJECT_SFX = Path(__file__).resolve().parent.parent  # Projektordner oder Repository-Kopie


@lru_cache(maxsize=16)
def decode(path):
    """Ganze Datei per ffmpeg als float32 Stereo 48 kHz (erste Audiospur, Cover-Bild ignoriert)."""
    raw = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", str(path), "-vn", "-map", "0:a:0",
         "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
        check=True, capture_output=True).stdout
    return np.frombuffer(raw, dtype=np.float32).reshape(-1, 2).astype(np.float64)


def resolve(p, base):
    p = Path(p)
    if p.is_absolute():
        return p
    if (base / p).exists():
        return base / p
    if (PROJECT_SFX / p).exists():
        return PROJECT_SFX / p
    raise FileNotFoundError(p)


def fade_curve(n, kind_in):
    x = (np.arange(n) + 0.5) / max(n, 1)
    return np.sin(np.pi / 2 * x) if kind_in else np.cos(np.pi / 2 * x)


def lufs(x):
    if len(x) < int(0.4 * SR):
        return float("nan")
    return pyln.Meter(SR).integrated_loudness(x)


def true_peak_db(x):
    up = resample_poly(x, 4, 1, axis=0)
    return 20 * np.log10(np.max(np.abs(up)) + 1e-12)


def music_clip(m, base):
    src = decode(resolve(m["file"], base))
    tempo = float(m.get("tempo", 1.0))
    semis = float(m.get("semitones", 0.0))
    n_out = int(round(m["dur"] * SR))
    a = int(round(m["src"] * SR))
    if a < 0:
        raise ValueError(f"src < 0 bei {m['file']}")
    if tempo != 1.0 or semis != 0.0:
        # rubberband-cli (Offline-Modus): Beats bleiben auf ±1 ms im Raster.
        # pedalboard.time_stretch driftet dagegen bis 30 ms, ffmpeg atempo ~17 ms.
        pad = int(0.25 * SR)  # Rand gegen Einschwingen des Stretchers
        a0 = max(a - pad, 0)
        seg = src[a0: a + int(n_out * tempo) + pad]
        with tempfile.TemporaryDirectory() as d:
            i, o = Path(d, "i.wav"), Path(d, "o.wav")
            sf.write(i, seg.astype(np.float32), SR, subtype="FLOAT")
            subprocess.run(["rubberband", "-q", "-T", str(tempo), "-p", str(semis), str(i), str(o)],
                           check=True, capture_output=True)
            y, _ = sf.read(o, always_2d=True)
        s = int(round((a - a0) / tempo))
        seg = y[s:s + n_out]
    else:
        seg = src[a:a + n_out]
    if len(seg) < n_out:
        print(f"WARNUNG: {m['file']} endet {(n_out - len(seg)) / SR:.3f} s zu früh", file=sys.stderr)
        seg = np.pad(seg, ((0, n_out - len(seg)), (0, 0)))
    seg = seg.copy()
    fi, fo = int(round(m.get("fade_in", 0.004) * SR)), int(round(m.get("fade_out", 0.004) * SR))
    if fi:
        seg[:fi] *= fade_curve(fi, True)[:, None]
    if fo:
        seg[-fo:] *= fade_curve(fo, False)[:, None]
    return seg


def sfx_clip(s, base):
    y = decode(resolve(s["file"], base)).copy()
    env = np.max(np.abs(y), axis=1)
    align = s.get("align", "start")
    anchor = {"start": 0, "peak": int(np.argmax(env)), "end": len(y)}[align]
    start = int(round(s["at"] * SR)) - anchor
    y *= 10 ** (s.get("gain_db", 0.0) / 20)
    # hörbares Ende (−30 dB unter Peak) für das Ducking
    loud = np.nonzero(env > env.max() * 10 ** (-30 / 20))[0]
    return y, start, start + (loud[-1] if len(loud) else len(y))


def limit(x, ceiling_db):
    """Look-ahead-Limiter auf 4x-Oversampling-Peaks; garantiert True Peak <= ceiling (Schätzung)."""
    c = 10 ** (ceiling_db / 20)
    up = np.max(np.abs(resample_poly(x, 4, 1, axis=0)), axis=1)
    n = len(x)
    peak = up[: n * 4].reshape(n, 4).max(axis=1) if len(up) >= n * 4 else np.max(np.abs(x), axis=1)
    g = np.minimum(1.0, c / (peak + 1e-12))
    if g.min() >= 1.0:
        return x, 0.0, 0.0
    hold = int(0.010 * SR)
    g = minimum_filter1d(g, size=2 * hold + 1)
    g = uniform_filter1d(g, size=hold + 1)
    return x * g[:, None], float(-20 * np.log10(g.min())), int(np.argmin(g)) / SR


def mix(spec, base):
    n = int(round(spec["duration"] * SR))
    report = []
    clips = []
    for m in spec.get("music", []):
        seg = music_clip(m, base) * 10 ** (m.get("gain_db", 0.0) / 20)
        clips.append((m, seg))
    if spec.get("match_loudness", True) and len(clips) > 1:
        # auf den leisesten Song absenken: nie anheben, damit der Limiter nicht arbeiten muss
        levels = [lufs(seg[int(0.3 * SR): -int(0.3 * SR) or None]) for _, seg in clips]
        ref = np.nanmin(levels)
        for (m, seg), L in zip(clips, levels):
            gain = 0.0 if np.isnan(L) else ref - L
            seg *= 10 ** (gain / 20)
            report.append(f"Song {m['file']}: {L:.1f} LUFS, Angleichung {gain:+.1f} dB")
    music = np.zeros((n, 2))
    for m, seg in clips:
        a = int(round(m["at"] * SR))
        b = min(a + len(seg), n)
        music[a:b] += seg[: b - a]

    duck_db = np.zeros(n)
    sfx = np.zeros((n, 2))
    for s in spec.get("sfx", []):
        y, start, loud_end = sfx_clip(s, base)
        a, b = max(start, 0), min(start + len(y), n)
        if b > a:
            sfx[a:b] += y[a - start: b - start]
        if s.get("duck_db"):
            att, rel = int(0.02 * SR), int(0.15 * SR)
            env = np.zeros(n)
            lo, hi = max(start, 0), min(loud_end, n)
            env[lo:hi] = 1
            if lo > 0:
                env[max(lo - att, 0):lo] = np.linspace(0, 1, lo - max(lo - att, 0), endpoint=False)
            if hi < n:
                env[hi:min(hi + rel, n)] = np.linspace(1, 0, min(hi + rel, n) - hi)
            duck_db = np.minimum(duck_db, -s["duck_db"] * env)
        report.append(f"SFX {s['file']} @ {s['at']:.3f}s ({s.get('align', 'start')}), {s.get('gain_db', 0):+.1f} dB")
    out = music * 10 ** (duck_db / 20)[:, None] + sfx

    if spec.get("target_lufs") is not None:
        L = lufs(out)
        out *= 10 ** ((spec["target_lufs"] - L) / 20)
        report.append(f"Normalisiert {L:.1f} -> {spec['target_lufs']} LUFS")
    out, gr, at = limit(out, spec.get("ceiling_db", -1.0))
    report.append(f"Limiter max. {gr:.1f} dB bei {at:.2f} s"
                  + ("  (WARNUNG: dort SFX bzw. Song leiser machen)" if gr > 3 else ""))
    return out, report


def blocks_db(x, ms=100):
    b = int(SR * ms / 1000)
    k = len(x) // b
    rms = np.sqrt(np.mean(x[: k * b].reshape(k, b, -1) ** 2, axis=(1, 2)))
    return 20 * np.log10(rms + 1e-12)


def load_any(path):
    p = Path(path)
    if p.suffix.lower() == ".wav":
        x, sr = sf.read(p, always_2d=True)
        if sr == SR:
            return x.astype(np.float64)
    return decode(p)


def check(path, ref=None):
    x = load_any(path)
    db = blocks_db(x)
    silent = np.nonzero(db < -50)[0]
    print(f"{path}: {len(x) / SR:.3f} s, {lufs(x):.1f} LUFS, True Peak {true_peak_db(x):.2f} dBTP")
    print(f"  stumme 100-ms-Blöcke (< -50 dBFS): {len(silent)}"
          + (f" ab {silent[0] * 0.1:.1f} s" if len(silent) else ""))
    if ref:
        r = blocks_db(load_any(ref))
        k = min(len(r), len(db))
        d = db[:k] - r[:k]
        d -= np.median(d)  # konstanter Pegelversatz (Normalisierung) zählt nicht
        print(f"  Abweichung zur Referenz: max {np.max(np.abs(d)):.2f} dB (Block {np.argmax(np.abs(d)) * 0.1:.1f} s)")
    return db


def mux(video, wav, out):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", video, "-i", wav,
                    "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy",
                    "-c:a", "aac", "-b:a", "320k", "-ar", str(SR),
                    "-movflags", "+faststart", out], check=True)


def main():
    cmd, *args = sys.argv[1:] or ["-h"]
    if cmd == "mix":
        spec_path = Path(args[0])
        out, report = mix(json.loads(spec_path.read_text()), spec_path.parent.resolve())
        sf.write(args[1], out.astype(np.float32), SR, subtype="FLOAT")
        print("\n".join(report))
        check(args[1])
    elif cmd == "mux":
        mux(*args[:3])
        check(args[2])
    elif cmd == "check":
        check(*args[:2])
    else:
        print(__doc__)


if __name__ == "__main__":
    main()
