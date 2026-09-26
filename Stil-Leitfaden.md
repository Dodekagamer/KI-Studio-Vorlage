# Stil-Leitfaden (Vorlage)

**Status:** noch nicht eingerichtet. Bis der Abschnitt „Stil festlegen“ mit dem Nutzer durchlaufen ist, gilt der **Grundstil** unten. Danach hier Marke, Regeln und Werte eintragen, `stil.json` im selben Zug anpassen und diesen Status ersetzen.

**Vorrang:** das neueste Feedback des Nutzers vor diesem Leitfaden, dieser Leitfaden vor Stil-Matrix und Effekt-Rezepten in `Reel-Studio_Projektanweisungen.md`. Ändert sich hier etwas, `stil.json` und bei Bedarf `Kurzanleitung.md` im selben Zug anpassen.

## Kurzfassung: die Regeln (vor jedem Reel lesen)

1. **Der Song ist der Chef.** Er läuft unverändert, ohne Soundeffekte, ohne Absenken.
2. **Nur volle Phrasen.** Ab der Eins der Hook (ein Auftakt davor ist erlaubt) bis zur Eins danach. Nie mitten im Takt enden, nie einen Bass-Schlag abschneiden.
3. **Story in 4 Kapiteln** (Namen in `stil.json`, Standard: Einstieg, Aufbau, Höhepunkt, Finale), je 4 Takte, jedes Kapitel startet auf einer Phrase des Songs. Reihenfolge nach Story, nicht nach Uhrzeit.
4. **Grundraster 2 Beats.** Harte Schnitte auf Schlag 1 und 3 jedes Takts.
5. **Jeder Akzent im Beat bekommt seinen Bild-Akzent:** 808/Kick = Zoom-Punch mit Blur, Nachschlag = zweiter Punch, Clap/Snare = Schnitt mit Mini-Punch, sonst harter Schnitt.
6. **Keine neue Szene kürzer als 2 Beats.** Schnelle Schlagfolgen als Punches im selben Shot, nicht als 1-Beat-Szenen.
7. **Ganze, gelungene Bewegungen.** Langsame Bewegungen bekommen 4 Beats oder eine Speed-Ramp, der Schnitt kommt nach der Endposition. Keine misslungenen Versuche.
8. **Eine Speed-Ramp pro Kapitel 1–3** auf dem Showpiece. Der Hit liegt auf der Eins des 3. Takts der Phrase.
9. **Effekte sparsam:** höchstens 2 Flashes (Kapitelstart Finale, Schlussbild), Shake nur auf Treffern, höchstens 2 Shots.
10. **Kein Glitch, Split-Screen, Freeze, Whip, Echo, keine SFX, kein Text**, außer der Nutzer will es (oder `stil.json` erlaubt es).
11. **Wiedererkennung sofort:** das stärkste Bild auf dem ersten Hit, Marke oder Logo in den ersten 3 Sekunden.
12. **Finale:** Schlussbild mindestens 4 Beats, Zeitlupe 0,5× plus Push-in ~12 %, bis zum Ende des Tons. Ende und Anfang passen zusammen, so loopt es sauber.

---

## Stil festlegen (einmalig, vor dem ersten Reel)

Ziel: aus dem Grundstil den Stil des Nutzers machen, mit möglichst wenig Fragen. So ist auch das Original-Studio entstanden: Ein Referenz-Reel, das dem Nutzer gefiel, wurde vermessen, seine Kritik daran wurde zu Regeln.

1. **Fragen, eine Nachricht, alles optional** (was fehlt, entscheidest du und nennst es):
   - Account bzw. Marke, dein Name für den Nutzer, worum es in den Reels geht, für wen.
   - 1–3 Reels, die ihm gefallen (eigene oder fremde), **als Videodatei im Drive-Ordner**: Instagram-Links kann der Server nicht öffnen. Was genau gefällt daran?
   - Musik: welche Genres, gern ein typischer Song.
   - Look: natürlich, kräftig, dunkel/moody, Film, Schwarzweiß? Gibt es schon einen Filter/Preset (.cube aus Lightroom, DaVinci, CapCut)?
   - Text im Video, Untertitel, Soundeffekte: nie, manchmal, immer?
   - Logo (PNG/SVG), Schrift, Farben, Wiedererkennung (Ort, Shirt, Banner, Maskottchen).
   - No-Gos.
2. **Referenzen vermessen:** je Referenz-Reel `python3 $T/analyse/reel_qc.py <reel.mp4> -o $W/ref_1` (Schnittlängen, Szenen pro 16 Takte, Punches, Flashes, Standbilder, Lautheit, Ende auf Taktgrenze), dazu `python3 $T/ansicht.py reel <reel.mp4>` einmal ansehen (Look, Motive, Text, Übergänge). Befunde als Tabelle in Abschnitt 1 unten.
3. **Werte ableiten:** Szenenlänge (`budget.min_beats`), Schnittdichte (`budget.segmente_16`), Effekt-Budget, erlaubte Extras, Kapitel-Namen passend zum Inhalt (Beispiele in Abschnitt 4), Varianten A/B/C (Namen und Ideen dürfen zum Inhalt passen).
4. **Look wählen:** ein typisches Standbild aus dem Material des Nutzers (Keyframe aus `$W/kf/…` nach `ingest.py`) in allen Looks zeigen: `python3 $T/vfx/looks.py vergleich <bild.jpg>` (ein Bild, beschriftet; Looks in `tools/vfx/README.md`). Der Nutzer wählt. Eigene `.cube` nach `referenz/marke/` und in `stil.json` eintragen.
5. **Eintragen:** `stil.json` (`eingerichtet: true`, `marke`, `nutzer`, `inhalt`, `look`, `kapitel`, `budget`, `erlaubt`, `varianten`), diesen Leitfaden (Status oben, Kurzfassung, Abschnitte 1–8), Logo und Schriften nach `referenz/marke/` bzw. `tools/fonts/`. `python3 tools/stil.py` muss „Stil eingerichtet“ melden.
6. **Erstes Reel als Test:** Feedback wörtlich mit Datum ins Änderungsprotokoll, was dauerhaft gilt, als Regel hier und in `stil.json`.

## 1. Marke und Inhalt (ausfüllen)

| | |
|---|---|
| Marke / Account | … |
| Nutzer (so nennst du ihn) | … |
| Inhalt, Zielgruppe | … |
| Wiedererkennung | Logo, Farben, Schrift, Ort, Kleidung, Banner … |
| Referenz-Reels | Datei, was gefällt, gemessene Werte (Szenen pro 16 Takte, kürzeste Szene, Punches, Flashes, Look) |
| Musik | Genres, typische BPM |
| No-Gos | … |

## 2. Rhythmus und Schnitt (Grundstil)

- **Raster:** 2 Beats (halber Takt) als Grundschnitt, Dramaturgie in Phrasen zu 4 Takten (= Kapitel).
- **Länge:** Standard die Hook, 16 Takte (≈ 24–30 s) bei genug starkem Material (mindestens 25 gute Momente), sonst 8 Takte (≈ 12–16 s).
- **Hook-Start:** die Eins der Hook ist der Taktanfang der Phrase, nicht der erste laute Bass-Schlag. Ende = Eins + 16 (8) Takte, dort 30–40 ms Fade, in den letzten 150 ms kein 808. Ein Auftakt verlängert das Reel und gehört zu Kapitel 1, er kürzt nie das Ende.
- **Szenenlänge:** neue Szene mindestens 2 Beats (`budget.min_beats`). Schnelle Folgen von Bass-Schlägen: 2 Szenen à 2 Beats mit je 2 Punches statt 4 Szenen à 1 Beat. Schnelle Bewegungen (Springen, Werfen, Tanzen) dürfen 2 Beats, langsame bekommen 4 Beats oder eine Ramp.
- **Schnittdichte:** Richtwert 24–30 Segmente pro 16 Takte (`budget.segmente_16`; Ramps zählen doppelt). Zu viele wirkt hektisch („zu früh zur nächsten Szene“), zu wenige zäh.
- **Andere Genres:** Stil-Matrix in `Reel-Studio_Projektanweisungen.md` Abschnitt 3 (z. B. House: 8-Takt-Phrasen, Drop = Highlight; Cinematic: 1–2 Takte pro Shot, kaum Punches). Wird ein Genre zum Standard, hier eintragen.

## 3. Akzente: Ton → Bild

Vor der Schnittliste pro Halbbeat bestimmen, was im Song passiert (`song_analyse.py` schreibt die Akzent-Karte). Dann gilt:

| Im Song | Im Bild | Rezept (Stärke in `stil.json` → `punch`) |
|---|---|---|
| frischer 808 / Kick | Schnitt oder Punch mit Zoom-Blur | Zoom 1 + 0,14·e^(−t/0,09 s), Blur auf den ersten 3 Frames; am Ramp-Hit 0,126 |
| Nachschlag 1 Beat später | zweiter Punch im selben Shot | 0,12 mit Blur; in einer Zeitlupe 0,05 ohne Blur |
| Clap/Snare auf Schlag 3, kein 808 | Schnitt mit Mini-Punch | 1 + 0,06·e^(−t/0,09 s), ohne Blur, aus der Bildmitte |
| Schlag 1 ohne 808 und Clap | harter Schnitt | kein Effekt |
| Break (kein 808, kein Clap) | kein Akzent | Zeitlupe oder ruhiger Push-in |

Der Mini-Punch fällt auf den Schnitt: Man sieht kein Hineinzoomen, nur wie das neue Bild in ~0,27 s um 6 % zurückzoomt. Das macht den Schnitt weich. Wer keine Punches will: `punch` in `stil.json` auf 0 setzen und hier streichen.

**Speed-Ramp (4 Beats):** Schnitt auf dem Clap mit Mini-Punch (~1,0×), Tempo steigt auf ~2×, auf dem Hit (Beat 2, Punch 0,126) in ~3 Frames auf 0,5×, 0,5× etwa 1 Beat halten, dann bis zum Schnitt auf ~1,5×. `ramp_hold` bleibt nach dem Hit bei 0,5× (Landung, Abschluss). Der Höhepunkt der Bewegung liegt genau auf dem Hit, an dichten Frames prüfen. Zeitlupe nur aus 60-fps-Material.

## 4. Story und Kapitel

- 4 Kapitel à 4 Takte (bei 8 Takten: 4 à 2 Takte oder 3 Kapitel 2 + 4 + 2, höchstens 2 Ramps). Kapitel beginnen auf den Phrasen des Songs.
- Muster: **Einstieg** (wer/was, Wiedererkennung) → **Aufbau** (Arbeit, Prozess, Vielfalt) → **Höhepunkt** (stärkste Action, Showpieces) → **Finale** (Payoff, Emotion, Gruppe, Schlussbild).
- Namen passend zum Inhalt in `stil.json` → `kapitel`, zum Beispiel:
  - Sport/Fitness: Einstieg, Grind, Power, Team
  - Food: Zutaten, Zubereitung, Anrichten, Genuss
  - Event/Konzert: Anreise, Aufbau, Show, Crowd
  - Handwerk/Produkt: Material, Arbeit, Detail, Ergebnis
- Shot-Auswahl nach Thema des Kapitels, nicht nach Uhrzeit. Payoff-Clips (Ergebnis, Ziel, Auftritt) nur im letzten Kapitel.

## 5. Shot-Auswahl

- **Erster Hit:** das stärkste, klarste Bild, mit Marke oder Menschen. Kein Intro.
- **Wiedererkennung** in den ersten 3 Sekunden (Logo, Ort, Kleidung, Banner), danach immer wieder im Hintergrund.
- **Vielfalt:** jeder Clip höchstens einmal. Wechsel zwischen total und nah, Einzelnen und Gruppe. Ein wiederkehrendes Motiv ist erlaubt (immer andere Perspektive).
- **In jedem Shot passiert etwas.** Ausnahmen: Branding am Anfang, Emotion nach der Leistung, Finale.
- **Ganze Bewegungen:** pro Shot notieren, welcher Teil zu sehen ist, nie nur die Ausholbewegung. Nur gelungene Versuche.
- **Showpieces** (Sprünge, Tricks, Höhepunkte) für die Ramps aufheben.
- **Ausschuss:** versehentliche Clips, Person winzig oder weit weg, Selfie- und Talking-Head-Monologe, schon geschnittene Videos (`copy_…`, CapCut-Exporte), Duplikate, Fotos ohne Wunsch.

## 6. Effekte und Budget

- „Smooth und klein“: Obergrenze ist das Budget in `stil.json` (Standard: 3 Ramps, 2 Flashes, 2 Shakes, 2 Übergänge). `edl.py`, `shotliste.py` und `vfx/reelvfx.py check` warnen darüber.
- Push-in +6–12 % nur auf ruhigen Shots (Marke, Nahaufnahme, Schlussbild). Alles andere in Echtzeit.
- Split-Screen nur auf Wunsch, dann mindestens 4 Beats und nicht direkt in einen kurzen Shot.
- Kein Korn, keine extreme Schärfe (Instagram macht daraus Blockrauschen bzw. Halos).

## 7. Look

- Look aus `stil.json` (Grundstil `clean`: nur leichte Kontrastkurve, keine Farbverschiebung), dazu Belichtungsangleich pro Shot und Vignette (`vignette`, Standard 12 %).
- Grading zurückhaltend: erst korrigieren (Belichtung, Weißabgleich), dann stylen; Hauttöne schützen, kein schweres Teal-Orange.
- HDR-Clips (HLG vom iPhone) werden automatisch getonemappt.

## 8. Ton, Text und Extras

- Songpegel unverändert, Limiter nur wenn nötig (Decke −0,3 dBTP). Start mit 4 ms Fade-in auf einem Beat, Ende mit 30–40 ms Fade-out auf einer Taktgrenze.
- Standard ohne SFX; auf Wunsch höchstens 1–2 leise (−14 bis −18 dB).
- Text nur auf Wunsch: höchstens 5 Wörter, kinetisch, in den Safe Zones (oben 10 %, unten 20 %, rechts 10 % frei). Schrift aus `tools/fonts/` oder die eigene Markenschrift dort.
- Keine Reichweite-Extras (Text-Hooks, Captions, Hashtags), außer der Nutzer fragt danach.

## 9. Checkliste

**Vor dem Storyboard**
- [ ] Eins der Hook bestimmt, Ende = nächste Eins, Länge in vollen Takten (plus Auftakt, falls genutzt).
- [ ] Akzent-Karte pro Halbbeat: 808, Nachschlag, Clap, Break.
- [ ] 4 Kapitel mit Thema, jedes startet auf einer Phrase.
- [ ] Jeder Schnitt und Punch hat den Akzent aus Abschnitt 3.
- [ ] Keine neue Szene unter der Mindestlänge, schnelle Folgen als Punches.
- [ ] Langsame Bewegungen: 4 Beats oder Ramp, ganze Bewegung notiert.
- [ ] Effekt-Budget aus `stil.json` eingehalten, keine Extras ohne Wunsch.
- [ ] Finale laut `stil.json` (Länge, Zeitlupe, Push-in).

**Vor der Abgabe**
- [ ] `verify.py` meldet „alles OK“.
- [ ] Letztes Sample auf der Taktgrenze, kein 808-Einsatz in den letzten 150 ms.
- [ ] Jede Bewegung an dichten Frames komplett (Endposition im Bild).
- [ ] Loop Ende zu Anfang angesehen.

---

## Änderungsprotokoll

- (Datum): Vorlage übernommen, Grundstil gilt.
