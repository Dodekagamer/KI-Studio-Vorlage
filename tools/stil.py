#!/usr/bin/env python3
"""Stil des Studios laden: stil.json im Projektordner (maschinenlesbarer Teil von Stil-Leitfaden.md).

    python3 tools/stil.py            # aktuellen Stil zeigen und prüfen, ob er eingerichtet ist

Im Code:  from stil import STIL      (tools/ muss im sys.path liegen; reelcfg.py und reelvfx.py machen das)
Fehlt ein Wert in stil.json, gilt der Grundstil unten. So laufen alle Werkzeuge auch vor der Einrichtung.
"""
import copy
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
DATEI = PROJECT / "stil.json"

GRUNDSTIL = {
    "eingerichtet": False,
    "marke": "",             # Name der Marke bzw. des Accounts, z. B. "@meinaccount" (Wortmarke, Kopfzeilen)
    "nutzer": "",            # wie Claude die Person nennt, für die geschnitten wird
    "inhalt": "",            # worum es in den Reels geht, ein Satz
    "look": "clean",         # Look aus tools/vfx/looks.py, Pfad zu einer .cube, Parameter-Objekt oder null
    "vignette": 0.12,        # Randabdunklung 0–0,25 (0 = aus)
    "kapitel": ["Einstieg", "Aufbau", "Höhepunkt", "Finale"],
    "budget": {"ramps": 3, "flashes": 2, "shakes": 2, "uebergaenge": 2, "min_beats": 2, "segmente_16": [24, 30]},
    "punch": {"808": 0.14, "nachschlag": 0.12, "clap": 0.06},
    "finale": {"beats": 4, "zeitlupe": True, "push": True},
    "erlaubt": [],           # Extras ohne Einzelwunsch: "text", "sfx", "split", "glitch", "freeze", "whip", "echo" …
    "varianten": [
        {"x": "A", "name": "Story", "idee": "Stil-Leitfaden 1:1", "kurz": "Hook, 16 Takte, Story in 4 Kapiteln"},
        {"x": "B", "name": "Power", "idee": "andere Songstelle, andere Clips", "kurz": "andere Songstelle, andere Clips"},
        {"x": "C", "name": "Clean", "idee": "kürzer und ruhiger", "kurz": "kürzer und ruhiger"},
    ],
}


def _merge(basis, neu):
    out = copy.deepcopy(basis)
    for k, v in neu.items():
        if k.startswith("_"):
            continue
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def laden(pfad=None):
    p = Path(pfad or DATEI)
    return _merge(GRUNDSTIL, json.loads(p.read_text())) if p.is_file() else copy.deepcopy(GRUNDSTIL)


def erlaubt(name, extra=()):
    """True, wenn ein Extra (z. B. "text", "split") laut stil.json oder für dieses Reel ausdrücklich gewollt ist."""
    return name in set(STIL["erlaubt"]) | set(extra)


def look_name(look=None):
    look = STIL["look"] if look is None else look
    if not look:
        return "ohne Look"
    if isinstance(look, dict):
        return "eigener Look (" + str(look.get("basis", "Parameter")) + ")"
    return Path(str(look)).stem if str(look).endswith(".cube") else str(look)


STIL = laden()


def main():
    s = STIL
    print(f"stil.json: {'vorhanden' if DATEI.is_file() else 'fehlt, Grundstil'} ({DATEI})")
    print(f"  Marke: {s['marke'] or '–'} · Nutzer: {s['nutzer'] or '–'} · Inhalt: {s['inhalt'] or '–'}")
    print(f"  Look: {look_name()} · Vignette {s['vignette']:.0%} · Kapitel: {', '.join(s['kapitel'])}")
    b = s["budget"]
    print(f"  Budget: {b['ramps']} Ramps, {b['flashes']} Flashes, {b['shakes']} Shakes, {b['uebergaenge']} Übergänge, "
          f"Szenen ab {b['min_beats']} Beats, {b['segmente_16'][0]}–{b['segmente_16'][1]} Segmente pro 16 Takte")
    print(f"  Extras ohne Einzelwunsch: {', '.join(s['erlaubt']) or 'keine'} · "
          f"Varianten: {', '.join(v['x'] + ' ' + v['name'] for v in s['varianten'])}")
    fehlt = [k for k in ("marke", "nutzer", "inhalt") if not s[k]]
    if not s["eingerichtet"] or fehlt:
        print("NOCH NICHT EINGERICHTET: vor dem ersten Reel Stil-Leitfaden.md, Abschnitt „Stil festlegen“ abarbeiten"
              + (f" (leer: {', '.join(fehlt)})" if fehlt else ""))
        return 1
    print("Stil eingerichtet.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
