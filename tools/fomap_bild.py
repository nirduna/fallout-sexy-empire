#!/usr/bin/env python3
"""Schematische Draufsicht einer Fallout-2-Karte als PNG.

Zeichnet die Karte in der Spielperspektive (isometrisch wie im Mapper), aber
ohne Spielgrafiken, die in den Spieldaten stecken:
  Boden (hell), Daecher (blaugrau), Waende (braun), Tueren (gelb),
  Szenerie (grau), Figuren (rot, mit Skriptname), Ausgaenge (gruen),
  Spatial-Skripte (violett), Scroll-Blocker (magenta, Rand des sichtbaren Bereichs),
  markierte Hexfelder (cyan, mit Nummer oder Beschriftung).

Aufruf:
  python3 tools/fomap_bild.py KARTE.map ausgabe.png [--ebene 0] [--protos DIR]
          [--skripte scripts.lst] [--mitte HEX --radius N] [--markiere HEX,HEX,...]
          [--raster N]   (jedes N-te Hexfeld mit Nummer beschriften)
"""
import argparse
import struct
from pathlib import Path

from PIL import Image, ImageDraw

import fomap


def hex_xy(tile):
    """Bildschirmposition (Mitte) eines Hexfelds, wie tileToScreenXY in fallout2-ce."""
    v3 = 199 - tile % 200
    v4 = tile // 200
    sx = 48 * (v3 // 2) + (32 if v3 & 1 else 0) + 16 * v4
    sy = -12 * (v3 // 2) + 12 * v4
    return sx + 16, sy + 8


def quadrat_ecken(sq):
    """Die vier Ecken einer Bodenkachel (80x36-Parallelogramm), wie squareTileToScreenXY."""
    v5 = 99 - sq % 100
    v6 = sq // 100
    x = 48 * v5 + 32 * v6 - 16
    y = -12 * v5 + 24 * v6 - 2
    return [(x, y + 12), (x + 48, y), (x + 80, y + 24), (x + 32, y + 36)]


def hex_von_xy(x, y):
    """Naechstes Hexfeld zu einem Bildpunkt (fuer Beschriftungen)."""
    best, bd = None, None
    for t in range(40000):
        hx, hy = hex_xy(t)
        d = (hx - x) ** 2 + (hy - y) ** 2
        if bd is None or d < bd:
            best, bd = t, d
    return best


def skriptnamen(scripts_lst):
    """Namen aus scripts.lst (Index 0-basiert, ohne Endung)."""
    return [l.split(";")[0].strip().split(".")[0]
            for l in Path(scripts_lst).read_text(errors="replace").splitlines()]


def zeichne(k, db, ausgabe, ebene=0, namen=(), mitte=None, radius=30, massstab=1.0,
            markiere=(), raster=0, extra_namen=None):
    """Zeichnet Karte k nach ausgabe (PNG).

    markiere:    Hexnummern oder (hex, text)-Paare
    extra_namen: {skriptindex: name} fuer Skripte, die nicht in namen stehen
    """
    namen = list(namen)
    extra_namen = extra_namen or {}
    sid2name = {}
    for _, s in k.skript_saetze():
        i = fomap.skript_index(s)
        sid2name[s[0]] = extra_namen.get(i) or (namen[i] if 0 <= i < len(namen) else f"#{i}")

    # Ausschnitt bestimmen
    if mitte is not None:
        cx, cy = hex_xy(mitte)
        r = radius * 32
        box = (cx - r, cy - r * 0.6, cx + r, cy + r * 0.6)
    else:
        box = (-200, -1300, 8200, 2500)
    s = massstab
    w, h = int((box[2] - box[0]) * s), int((box[3] - box[1]) * s)
    img = Image.new("RGB", (w, h), (24, 24, 24))
    d = ImageDraw.Draw(img)
    P = lambda x, y: ((x - box[0]) * s, (y - box[1]) * s)

    kacheln = k.kacheln.get(ebene)
    if kacheln:
        werte = struct.unpack(">10000i", kacheln)
        for sq, v in enumerate(werte):
            boden = v & 0xFFFF
            ecken = [P(*e) for e in quadrat_ecken(sq)]
            if not all(-100 <= px <= w + 100 and -100 <= py <= h + 100 for px, py in ecken):
                continue
            if boden > 1:
                d.polygon(ecken, fill=(70, 66, 58))
        for sq, v in enumerate(werte):
            dach = (v >> 16) & 0xFFFF
            if dach > 1:
                ecken = [P(x, y - 96) for x, y in quadrat_ecken(sq)]
                d.polygon(ecken, outline=(90, 110, 150))

    def punkt(tile, farbe, groesse):
        x, y = P(*hex_xy(tile))
        d.ellipse([x - groesse, y - groesse, x + groesse, y + groesse], fill=farbe)
        return x, y

    beschriftungen = []
    for e, o in k.alle_objekte():
        if e != ebene:
            continue
        kopf = o["kopf"]
        t, typ = kopf["tile"], fomap.pid_typ(kopf["pid"])
        if t < 0:
            continue
        if typ == fomap.T_WALL:
            punkt(t, (150, 95, 50), 3 * s + 1)
        elif typ == fomap.T_SCENERY:
            tuer = db.extra.get(kopf["pid"]) == 1
            punkt(t, (230, 200, 40) if tuer else (120, 120, 120), (4 if tuer else 2) * s + 1)
        elif typ == fomap.T_MISC and kopf["pid"] in fomap.EXIT_GRID_PIDS:
            punkt(t, (40, 200, 80), 3 * s + 1)
        elif typ == fomap.T_MISC and kopf["pid"] == fomap.PID_SCROLL_BLOCKER:
            punkt(t, (210, 60, 210), 2 * s + 1)
        elif typ == fomap.T_CRITTER:
            x, y = punkt(t, (220, 50, 50), 4 * s + 1)
            if kopf["sid"] != -1:
                beschriftungen.append((x + 5, y - 5, sid2name.get(kopf["sid"], "?"), (255, 140, 140)))
        elif typ == fomap.T_ITEM:
            punkt(t, (90, 140, 200), 1 * s + 1)
    for typ, satz in k.skript_saetze():
        if typ == 1:
            gebaut = satz[2]
            if (gebaut >> 29) & 7 == ebene:
                x, y = punkt(gebaut & 0xFFFF, (170, 80, 220), 5 * s + 1)
                beschriftungen.append((x + 5, y + 3, sid2name.get(satz[0], "spatial"), (200, 150, 255)))
    if raster:
        for t in range(40000):
            if (t % 200) % raster or (t // 200) % raster:
                continue
            x, y = P(*hex_xy(t))
            if 0 <= x < w and 0 <= y < h:
                d.point((x, y), fill=(200, 200, 200))
                beschriftungen.append((x + 2, y + 1, str(t), (150, 150, 150)))
    for m in markiere:
        tile, text = m if isinstance(m, tuple) else (m, str(m))
        x, y = punkt(int(tile), (40, 220, 220), 5 * s + 2)
        beschriftungen.append((x + 6, y - 6, text, (120, 255, 255)))
    for x, y, text, farbe in beschriftungen:
        d.text((x, y), text, fill=farbe)
    img.save(ausgabe)
    return w, h


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("karte")
    ap.add_argument("ausgabe")
    ap.add_argument("--ebene", type=int, default=0)
    ap.add_argument("--protos", default=None)
    ap.add_argument("--skripte", default=None)
    ap.add_argument("--mitte", type=int, default=None)
    ap.add_argument("--radius", type=int, default=30)
    ap.add_argument("--markiere", default="")
    ap.add_argument("--massstab", type=float, default=1.0)
    ap.add_argument("--raster", type=int, default=0)
    a = ap.parse_args()

    db = fomap.ProtoDB([a.protos] if a.protos else [])
    k = fomap.Karte.lesen(Path(a.karte).read_bytes(), db)
    namen = skriptnamen(a.skripte) if a.skripte else []
    markiere = [int(m) for m in a.markiere.split(",") if m]
    w, h = zeichne(k, db, a.ausgabe, a.ebene, namen, a.mitte, a.radius, a.massstab, markiere, a.raster)
    print(f"{a.ausgabe}: {w}x{h}")


if __name__ == "__main__":
    main()
