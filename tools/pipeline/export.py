#!/usr/bin/env python3
"""Lieferdateien aus dem Master: Instagram-Export in 2 Pässen (Projektanweisungen Punkt 15), Ton dazu, Titelbild.

    python3 export.py <master.mp4> <reel-ordner>/<name> [mix.wav] [--titel <frame>]

Schreibt <name>_ohne_ton.mp4 (x264 high 4.1, 18/25 Mbit/s, unsharp leicht, bt709, faststart),
mit mix.wav zusätzlich <name>_mit_song.mp4 (Video per Stream-Copy, AAC 320k/48 kHz über reel_audio.mux)
und mit --titel <frame> <name>_titelbild.jpg (Frame aus dem Master, 1080×1920).
"""
import subprocess
import sys
import tempfile
from pathlib import Path

sys.dont_write_bytecode = True  # kein __pycache__ im geteilten Projektordner
from reelcfg import run

VF = ("unsharp=5:5:0.4:5:5:0,scale=flags=lanczos+accurate_rnd+full_chroma_int:"
      "out_color_matrix=bt709:out_range=tv,format=yuv420p")
X264 = ["-c:v", "libx264", "-preset", "slow", "-tune", "film", "-profile:v", "high", "-level", "4.1",
        "-b:v", "18M", "-maxrate", "25M", "-bufsize", "50M", "-g", "60", "-bf", "3",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709"]


def instagram(master, out):
    with tempfile.TemporaryDirectory() as d:
        common = ["-vf", VF, *X264, "-passlogfile", f"{d}/x264"]
        for p, tail in (("1", ["-an", "-f", "null", "-"]), ("2", ["-an", "-movflags", "+faststart", str(out)])):
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(master), *common, "-pass", p, *tail], check=True)


def main(args):
    master, base = Path(args[0]), Path(args[1])
    mix = next((Path(a) for a in args[2:] if a.endswith(".wav")), None)
    base.parent.mkdir(parents=True, exist_ok=True)
    stumm = base.parent / f"{base.name}_ohne_ton.mp4"
    instagram(master, stumm)
    print(stumm)
    if mix:
        import reel_audio as ra
        mit = base.parent / f"{base.name}_mit_song.mp4"
        ra.mux(str(stumm), str(mix), str(mit))
        ra.check(str(mit))
        print(mit)
    if "--titel" in args:
        i = int(args[args.index("--titel") + 1])
        jpg = base.parent / f"{base.name}_titelbild.jpg"
        r = run(["ffmpeg", "-v", "error", "-y", "-i", master, "-vf", f"select=eq(n\\,{i}),"
                 "scale=out_color_matrix=bt709:out_range=pc", "-frames:v", "1", "-q:v", "2", jpg])
        assert r.returncode == 0, r.stderr
        print(jpg)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    main(sys.argv[1:])
