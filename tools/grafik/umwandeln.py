#!/usr/bin/env python3
"""Gerenderte Szenerie -> FRM-Dateien der Mod (Pillow, ohne Blender).

Liest <render>/<name>/bild.png, leucht.png und meta.json (tools/grafik/rendern.py),
rechnet auf die festen Farben der Palette um (Leuchtflaechen: Farbe 254,
pulsierendes Rot) und schneidet mehrfeldrige Moebel in senkrechte Streifen:
Die Engine zeichnet Objekte in der Reihenfolge ihrer Felder von hinten nach
vorn, ein breites Bild wuerde Figuren daneben falsch ueberdecken. Jeder Streifen
steht auf dem vordersten seiner Felder.

Ergebnis (im Repository):
  grafik/frm/<stueck>.frm       die Grafiken
  grafik/stuecke.json           je Objekt: Stuecke mit Feld relativ zum Bezugsfeld,
                                Blocker-Felder
  grafik/vorschau/<name>.png    zusammengesetzt wie im Spiel, mit Hexmitten

Aufruf: python3 tools/grafik/umwandeln.py <render> --palette color.pal
"""
import argparse
import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path[:0] = [str(HIER), str(HIER.parent)]

from PIL import Image, ImageDraw  # noqa: E402

import frm  # noqa: E402
import geometrie as g  # noqa: E402
import katalog  # noqa: E402

ROOT = HIER.parent.parent
KURZ = dict(rllatern="rllatern", rlbett="rlbett", rlparavnt="rlparav", rlwasch="rlwasch",
            rlteppich="rltepp", rlschild="rlschild")


def felder_pixel(meta):
    """Pixelmitte jedes belegten Felds im gerenderten Bild."""
    ox, oy = meta["ursprung"]
    ref = meta["bezug"]
    rx, ry = g.hex_bild(ref)
    aus = []
    for dx, dy in meta["felder"]:
        t = g.versatz(ref, dx, dy)
        tx, ty = g.hex_bild(t)
        aus.append(((dx, dy), ox + tx - rx, oy + ty - ry))
    return aus


def zerlegen(bild, felder):
    """-> [(Frm, (dx, dy))]: Streifen mit ihrem Ankerfeld."""
    spalten = sorted({px for _, px, _ in felder})
    grenzen = [(a + b) // 2 for a, b in zip(spalten, spalten[1:])]
    stuecke = []
    for streifen, x0 in frm.streifen(bild, grenzen):
        drin = [(f, px - x0, py) for f, px, py in felder if x0 <= px < x0 + streifen.breite]
        feld, ax, ay = max(drin, key=lambda e: (e[2], -e[1]))
        try:
            teil, lx, ly = frm.zuschneiden(streifen)
        except ValueError:
            continue
        stuecke.append((frm.einzelbild(teil, ax - lx, ay - ly), feld))
    return stuecke


def zusammensetzen(stuecke, felder, meta, pal, rand=20):
    """Die Stuecke so zusammensetzen, wie die Engine sie zeichnet (objectGetRect)."""
    ox, oy = meta["ursprung"]
    breite, hoehe = 2 * ox + 2 * rand + 200, 2 * oy + 2 * rand
    im = Image.new("RGBA", (breite, hoehe), (0, 0, 0, 0))
    pos = {f: (px + rand, py + rand) for f, px, py in felder}
    for f_obj, feld in stuecke:
        b = f_obj.richtungen[0][0]
        cx, cy = pos[tuple(feld)]
        links = cx + f_obj.dx[0] - b.breite // 2
        oben = cy + f_obj.dy[0] - b.hoehe + 1
        im.alpha_composite(frm.als_rgba(b, pal), (links, oben))
    return im, pos


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("render")
    ap.add_argument("--palette", required=True)
    ap.add_argument("--ziel", default=str(ROOT / "grafik"))
    a = ap.parse_args()
    pal = frm.Palette.lesen(a.palette)
    ziel = Path(a.ziel)
    (ziel / "frm").mkdir(parents=True, exist_ok=True)
    (ziel / "vorschau").mkdir(parents=True, exist_ok=True)
    liste = {}
    for name in katalog.OBJEKTE:
        quelle = Path(a.render) / name
        meta = json.loads((quelle / "meta.json").read_text())
        bild = frm.aus_rgba(Image.open(quelle / "bild.png"), pal,
                            Image.open(quelle / "leucht.png") if katalog.OBJEKTE[name].get("leucht") else None)
        felder = felder_pixel(meta)
        stuecke = zerlegen(bild, felder)
        # Pruefung: zusammengesetzt ergibt sich genau das umgerechnete Bild
        im, pos = zusammensetzen(stuecke, felder, meta, pal)
        ox, oy = meta["ursprung"]
        (f0, fx, fy) = felder[0]
        versatz_x, versatz_y = pos[f0][0] - fx, pos[f0][1] - fy
        vergleich = Image.new("RGBA", im.size, (0, 0, 0, 0))
        vergleich.alpha_composite(frm.als_rgba(bild, pal), (versatz_x, versatz_y))
        if vergleich.tobytes() != im.tobytes():
            raise SystemExit(f"{name}: Stuecke ergeben nicht das Bild")
        eintraege = []
        for i, (f_obj, feld) in enumerate(stuecke):
            datei = KURZ[name] + (str(i) if len(stuecke) > 1 else "")
            if len(datei) > 8:
                raise SystemExit(f"{datei}: Dateiname laenger als 8 Zeichen")
            (ziel / "frm" / f"{datei}.frm").write_bytes(f_obj.schreiben())
            eintraege.append(dict(datei=datei, feld=list(feld)))
        anker = {tuple(e["feld"]) for e in eintraege}
        liste[name] = dict(stuecke=eintraege,
                           blocker=[list(f) for f in map(tuple, katalog.OBJEKTE[name]["felder"]) if f not in anker])
        # Vorschau: doppelt gross, Hexmitten der Felder als Punkte
        hinter = Image.new("RGBA", im.size, (58, 52, 46, 255))
        d = ImageDraw.Draw(hinter)
        for f, (x, y) in pos.items():
            d.ellipse([x - 2, y - 1, x + 2, y + 1], fill=(120, 110, 95, 255))
        hinter.alpha_composite(im)
        box = im.getbbox()
        hinter = hinter.crop((max(0, box[0] - 12), max(0, box[1] - 12), min(im.width, box[2] + 12),
                              min(im.height, box[3] + 12)))
        hinter.resize((hinter.width * 2, hinter.height * 2), Image.NEAREST).save(ziel / "vorschau" / f"{name}.png")
        print(f"OK    {name}: {len(stuecke)} Stueck(e), {len(liste[name]['blocker'])} Blocker")
    (ziel / "stuecke.json").write_text("{\n" + ",\n".join(f" {json.dumps(n)}: {json.dumps(e)}" for n, e in liste.items())
                                       + "\n}\n")


if __name__ == "__main__":
    main()
