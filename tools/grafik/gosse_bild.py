#!/usr/bin/env python3
"""Vorschau der Gosse mit der eigenen Einrichtung, so gesetzt wie die Engine zeichnet.

Boden, Waende und Vanilla-Einrichtung liegen nur als Grafiken des Originalspiels
vor und werden hier schematisch gezeichnet (Boden hell, Waende dunkel, Vanilla-
Einrichtung grau, Figuren und Plaetze als Punkte). Die eigenen Grafiken stehen
pixelgenau an ihrer Spielposition (Hexmitte + Verschiebung, Reihenfolge von
hinten nach vorn, flache Objekte zuerst).

Aufruf: python3 tools/grafik/gosse_bild.py <mods/rotlicht aus dem Paket> <bild.png> --palette color.pal
"""
import argparse
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path[:0] = [str(HIER), str(HIER.parent)]

from PIL import Image, ImageDraw  # noqa: E402

import bau_karten  # noqa: E402
import fomap  # noqa: E402
import frm  # noqa: E402
import geometrie as g  # noqa: E402

REIHEN, SPALTEN = range(80, 99), range(59, 74)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mod")
    ap.add_argument("ziel")
    ap.add_argument("--palette", required=True)
    a = ap.parse_args()
    mod = Path(a.mod)
    pal = frm.Palette.lesen(a.palette)
    art = [z.strip().lower() for z in (mod / "art/scenery/scenery.lst").read_bytes().decode("cp1252").splitlines()]
    db = fomap.ProtoDB()
    k = fomap.Karte.lesen((mod / "maps" / bau_karten.RLDEN01["datei"]).read_bytes(), db)
    eigene = {}
    for _, o in k.alle_objekte():
        fid = o["kopf"]["fid"]
        if fid >> 24 == 2 and art[fid & 0xFFF].startswith("rl") and (mod / "art/scenery" / art[fid & 0xFFF]).exists():
            eigene.setdefault(o["kopf"]["tile"], []).append(o)

    hexe = [r * 200 + c for r in REIHEN for c in SPALTEN]
    pos = {t: g.hex_bild(t) for t in hexe}
    x0 = min(x for x, _ in pos.values()) - 60
    y0 = min(y for _, y in pos.values()) - 140
    b = max(x for x, _ in pos.values()) - x0 + 60
    h = max(y for _, y in pos.values()) - y0 + 40
    im = Image.new("RGBA", (b, h), (22, 20, 18, 255))
    d = ImageDraw.Draw(im)
    art_typ = {}
    for _, o in k.alle_objekte():
        t = o["kopf"]["tile"]
        typ = fomap.pid_typ(o["kopf"]["pid"])
        if typ == fomap.T_WALL:
            art_typ[t] = "wand"
        elif typ == fomap.T_SCENERY and bau_karten.blockiert(o) and t not in eigene and art_typ.get(t) != "wand":
            art_typ[t] = "szenerie"
    weg = bau_karten.erreichbar_von(k, bau_karten.RLDEN01["eingang_hex"])
    for t in hexe:
        cx, cy = pos[t][0] - x0 + 16, pos[t][1] - y0 + 8
        form = [(cx - 16, cy), (cx - 8, cy - 6), (cx + 8, cy - 6), (cx + 16, cy), (cx + 8, cy + 6), (cx - 8, cy + 6)]
        farbe = {"wand": (140, 90, 50, 255), "szenerie": (120, 120, 120, 255)}.get(
            art_typ.get(t), (58, 52, 46, 255) if t in weg else None)
        if farbe:
            d.polygon(form, fill=farbe, outline=(40, 36, 32, 255))
    marken = [(bau_karten.RLDEN01["eingang_hex"], (80, 200, 220)), (bau_karten.RLDEN01["treppe_hex"], (80, 200, 220))]
    marken += [(f["hex"], (220, 70, 70)) for f in bau_karten.RLDEN01["figuren"]]
    marken += [(t, (220, 180, 60)) for t in bau_karten.RLDEN01["laufzeit"].values()]
    for t, farbe in marken:
        cx, cy = pos[t][0] - x0 + 16, pos[t][1] - y0 + 8
        d.ellipse([cx - 4, cy - 3, cx + 4, cy + 3], fill=farbe + (255,))
    # eigene Grafiken: flache zuerst, dann von hinten nach vorn
    liste = [o for os_ in eigene.values() for o in os_]
    liste.sort(key=lambda o: (not o["kopf"]["flags"] & 0x08, pos[o["kopf"]["tile"]][1], -pos[o["kopf"]["tile"]][0]))
    for o in liste:
        f = frm.Frm.lesen((mod / "art/scenery" / art[o["kopf"]["fid"] & 0xFFF]).read_bytes())
        bild = f.richtungen[0][0]
        cx, cy = pos[o["kopf"]["tile"]][0] - x0 + 16, pos[o["kopf"]["tile"]][1] - y0 + 8
        links = cx + f.dx[0] - bild.breite // 2
        oben = cy + f.dy[0] - bild.hoehe + 1
        im.alpha_composite(frm.als_rgba(bild, pal), (links, oben))
    # Legende
    for i, (text, farbe) in enumerate((("Wand", (140, 90, 50)), ("Vanilla-Einrichtung (Tisch, Kisten, Blocker)", (120, 120, 120)),
                                       ("begehbarer Boden", (58, 52, 46)), ("Treppe und Startpunkt", (80, 200, 220)),
                                       ("Essie, Kolbe", (220, 70, 70)), ("Plaetze fuer Mara, Deke, Angreifer", (220, 180, 60)))):
        d.rectangle([8, 8 + 12 * i, 16, 16 + 12 * i], fill=farbe + (255,))
        d.text((22, 6 + 12 * i), text, fill=(200, 200, 200, 255))
    im = im.resize((im.width * 2, im.height * 2), Image.NEAREST)
    im.save(a.ziel)
    print(f"OK    {a.ziel}: {len(liste)} eigene Objekte")


if __name__ == "__main__":
    main()
