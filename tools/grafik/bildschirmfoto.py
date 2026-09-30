#!/usr/bin/env python3
"""Hexraster und geplante Einrichtung auf ein Bildschirmfoto aus dem Spiel legen.

Ohne die Grafiken des Originalspiels (Boden, Waende, Vanilla-Moebel) laesst sich
eine Karte hier nur schematisch zeichnen. Ein Bildschirmfoto zeigt den echten
Raum. Dieses Werkzeug eicht das Foto an einem eigenen Objekt, dessen Hexfeld
bekannt ist (Massstab und Lage per Mustervergleich), und kann dann
  raster    jedes Hexfeld mit Reihe.Spalte beschriften (zum Planen von Plaetzen)
  vorschau  die Einrichtung aus katalog.py an ihren Plaetzen einsetzen (nachgestellt:
            ohne Verdeckung durch Waende davor, alte Objekte im Foto bleiben sichtbar)

Aufruf (Python mit numpy und Pillow):
  bildschirmfoto.py raster   foto.png ziel.png --palette color.pal --anker rlschild:17065 \\
                   --suche 960,330,1090,480 [--ausschnitt x0,y0,x1,y1] [--reihen 80-98] [--spalten 58-81]
  bildschirmfoto.py vorschau foto.png ziel.png --palette color.pal --anker rlschild:17065 --suche ...

Das Anker-Objekt muss im Foto gut sichtbar sein (die Preistafel ist ideal: hell,
kantig, nicht verdeckt). Beim Foto zur ersten Einrichtung der Gosse (1280 x 685
Spielpixel auf 2000 x 1070 skaliert) ergab sich Massstab 1,55.
"""
import argparse
import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path[:0] = [str(HIER), str(HIER.parent)]

import numpy as np  # noqa: E402
from PIL import Image, ImageDraw, ImageEnhance  # noqa: E402

import frm  # noqa: E402
import geometrie as g  # noqa: E402
import katalog  # noqa: E402

ROOT = HIER.parent.parent


def frm_datei(name):
    return frm.Frm.lesen((ROOT / "grafik" / "frm" / f"{name}.frm").read_bytes())


def eichen(foto, pal, datei, tile, suche, massstaebe=np.arange(1.0, 2.51, 0.02)):
    """Mustervergleich des Anker-FRMs im Suchfenster -> (Massstab, Versatz x, Versatz y, Guete)."""
    bild = np.asarray(foto.convert("RGB"), dtype=float)
    f = frm_datei(datei)
    b = f.richtungen[0][0]
    rgba = frm.als_rgba(b, pal)
    x0, y0, x1, y1 = suche
    beste = None
    for s in massstaebe:
        w, h = round(b.breite * s), round(b.hoehe * s)
        if w >= x1 - x0 or h >= y1 - y0:
            continue
        muster = np.asarray(rgba.resize((w, h), Image.BILINEAR), dtype=float)
        maske = muster[:, :, 3] > 200
        q = muster[:, :, :3][maske]
        q = q - q.mean(0)
        qq = (q * q).sum()
        for y in range(y0, y1 - h):
            for x in range(x0, x1 - w):
                p = bild[y:y + h, x:x + w][maske]
                p = p - p.mean(0)
                guete = (p * q).sum() / np.sqrt((p * p).sum() * qq + 1e-9)
                if beste is None or guete > beste[0]:
                    beste = (guete, s, x, y)
    guete, s, x, y = beste
    # Hexmitte des Ankers im Foto (Engine: links = Mitte + dx - Breite/2, unten = Mitte + dy)
    cx = x + s * (b.breite / 2 - f.dx[0])
    cy = y + s * (b.hoehe - 1 - f.dy[0])
    hx, hy = g.hex_bild(tile)
    return s, cx - s * (hx + 16), cy - s * (hy + 8), guete


def hexmitte(tile, eichung):
    s, ox, oy = eichung
    x, y = g.hex_bild(tile)
    return ox + s * (x + 16), oy + s * (y + 8)


def raster(foto, eichung, reihen, spalten):
    s = eichung[0]
    im = ImageEnhance.Brightness(foto.convert("RGBA")).enhance(1.8)
    ebene = Image.new("RGBA", im.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ebene)
    for r in reihen:
        for c in spalten:
            x, y = hexmitte(r * 200 + c, eichung)
            d.polygon([(x - 16 * s, y), (x - 8 * s, y - 6 * s), (x + 8 * s, y - 6 * s), (x + 16 * s, y),
                       (x + 8 * s, y + 6 * s), (x - 8 * s, y + 6 * s)], outline=(0, 255, 0, 110))
            d.text((x - 9, y - 5), f"{r}.{c}", fill=(255, 255, 0, 230))
    im.alpha_composite(ebene)
    return im


def vorschau(foto, eichung, pal):
    s = eichung[0]
    im = foto.convert("RGBA")
    stuecke = json.loads((ROOT / "grafik" / "stuecke.json").read_text())
    teile = []
    for name, obj in katalog.OBJEKTE.items():
        for platz in obj["platz"]:
            for e in stuecke[name]["stuecke"]:
                t = g.versatz(platz, *e["feld"])
                teile.append((not obj.get("flach"), g.hex_bild(t)[1], -g.hex_bild(t)[0], t, e["datei"]))
    for _, _, _, t, datei in sorted(teile):          # flach zuerst, dann von hinten nach vorn
        f = frm_datei(datei)
        b = f.richtungen[0][0]
        cx, cy = hexmitte(t, eichung)
        bild = frm.als_rgba(b, pal).resize((round(b.breite * s), round(b.hoehe * s)), Image.NEAREST)
        rot, gruen, blau, alpha = bild.split()
        dunkler = ImageEnhance.Brightness(Image.merge("RGB", (rot, gruen, blau))).enhance(0.7)   # Kellerlicht
        bild = Image.merge("RGBA", (*dunkler.split(), alpha))
        im.alpha_composite(bild, (round(cx + s * (f.dx[0] - b.breite // 2)),
                                  round(cy + s * (f.dy[0] - b.hoehe + 1))))
    return ImageEnhance.Brightness(im).enhance(1.6)


def zahlen(text):
    return [int(v) for v in text.split(",")]


def bereich(text):
    a, b = text.split("-")
    return range(int(a), int(b) + 1)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("befehl", choices=["raster", "vorschau"])
    ap.add_argument("foto")
    ap.add_argument("ziel")
    ap.add_argument("--palette", required=True)
    ap.add_argument("--anker", required=True, help="FRM:Hexfeld, z. B. rlschild:17065")
    ap.add_argument("--suche", required=True, type=zahlen, help="Suchfenster x0,y0,x1,y1 im Foto")
    ap.add_argument("--ausschnitt", type=zahlen)
    ap.add_argument("--reihen", type=bereich, default=range(80, 99))
    ap.add_argument("--spalten", type=bereich, default=range(58, 82))
    a = ap.parse_args()
    pal = frm.Palette.lesen(a.palette)
    foto = Image.open(a.foto)
    datei, tile = a.anker.split(":")
    s, ox, oy, guete = eichen(foto, pal, datei, int(tile), a.suche)
    print(f"Eichung: Massstab {s:.2f}, Guete {guete:.3f}" + ("  (unsicher, Suchfenster pruefen)" if guete < 0.8 else ""))
    im = raster(foto, (s, ox, oy), a.reihen, a.spalten) if a.befehl == "raster" else vorschau(foto, (s, ox, oy), pal)
    if a.ausschnitt:
        im = im.crop(tuple(a.ausschnitt))
    im.resize((im.width * 2, im.height * 2), Image.LANCZOS).save(a.ziel)
    print(f"OK    {a.ziel}")


if __name__ == "__main__":
    main()
