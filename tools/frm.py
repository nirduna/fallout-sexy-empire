#!/usr/bin/env python3
"""FRM-Grafiken, Paletten und Szenerie-Prototypen fuer Fallout 2.

Das Format ist aus dem Quellcode von fallout2-ce abgeleitet (art.h, art.cc,
proto.cc, cycle.cc) und an Dateien des Restoration Project geprueft: Lesen und
Schreiben sind byte-gleich.

FRM (alle Zahlen big-endian):
  Kopf 62 Byte: Version (4) · Bilder je Sekunde (2) · Aktionsbild (2) ·
  Bilder je Richtung (2) · x-Verschiebung je Richtung (6 x 2) ·
  y-Verschiebung je Richtung (6 x 2) · Datenbeginn je Richtung (6 x 4) · Datengroesse (4)
  je Bild: Breite (2) · Hoehe (2) · Groesse (4) · x (2) · y (2) · Pixel (1 Byte je Punkt)
  Gibt es nur eine Richtung, zeigen alle sechs Datenbeginne auf dieselbe Stelle.

Die Engine setzt ein Bild mit seiner unteren Mitte auf die Mitte seines Hexfelds,
verschoben um die x-/y-Verschiebung der Richtung (object.cc, objectGetRect):
  links = Hexmitte_x + dx - Breite / 2,  unten = Hexmitte_y + dy.

Palette (color.pal, 33.536 Byte): 256 x RGB mit 6 Bit (0-63), danach eine
Farbtabelle der Engine. Index 0 ist durchsichtig. Die Farben 229-254 setzt die
Engine laufend neu (cycle.cc): Schleim 229-232, Monitore 233-237, Feuer langsam
238-242, Feuer schnell 243-247, Ufer 248-253 und 254, ein pulsierendes Rot.
Feste Farben fuer eigene Grafiken sind daher 1-228.

Die Palette gehoert zum Originalspiel und liegt nicht im Repository. Man gibt
sie als Datei an (--palette) oder liest sie aus der eigenen master.dat (DAT2).

Aufruf:
  python3 tools/frm.py png <grafik.frm> <bild.png> --palette color.pal
  python3 tools/frm.py frm <bild.png> <grafik.frm> --palette color.pal [--leucht maske.png]
  python3 tools/frm.py palette <master.dat> <color.pal>
  python3 tools/frm.py info <grafik.frm>
"""
import argparse
import struct
import sys
import zlib
from pathlib import Path

FEST = range(1, 229)                 # feste Farben fuer eigene Grafiken
ROT_PULS = 254                       # die Engine laesst diese Farbe rot pulsieren (0-60)
FEUER_LANGSAM = range(238, 243)
FEUER_SCHNELL = range(243, 248)
MONITORE = range(233, 238)


# ------------------------------------------------------------------ Palette
class Palette:
    def __init__(self, daten):
        if len(daten) < 768:
            raise ValueError("keine Fallout-Palette: zu kurz")
        self.roh = daten
        self.rgb = []
        for i in range(256):
            r, g, b = daten[3 * i:3 * i + 3]
            # Werte ueber 63 markieren Eintraege, die die Engine selbst fuellt
            self.rgb.append((r * 4, g * 4, b * 4) if max(r, g, b) < 64 else (255, 0, 255))
        self._cache = {}
        self._lab = {i: lab(*self.rgb[i]) for i in FEST}

    @classmethod
    def lesen(cls, pfad):
        return cls(Path(pfad).read_bytes())

    def naechste(self, r, g, b):
        """Naechste feste Farbe (1-228) im Lab-Farbraum; der Farbton zaehlt so mehr als
        bei RGB-Abstaenden (ein leicht graues Rot bleibt rot statt braun zu werden)."""
        schluessel = (r >> 2, g >> 2, b >> 2)
        treffer = self._cache.get(schluessel)
        if treffer is not None:
            return treffer
        l0, a0, b0 = lab(r, g, b)
        beste = min(FEST, key=lambda i: (self._lab[i][0] - l0) ** 2 + (self._lab[i][1] - a0) ** 2
                    + (self._lab[i][2] - b0) ** 2)
        self._cache[schluessel] = beste
        return beste


def lab(r, g, b):
    """sRGB (0-255) -> CIE L*a*b* (D65)."""
    def lin(c):
        c /= 255
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4
    rl, gl, bl = lin(r), lin(g), lin(b)
    x = (0.4124 * rl + 0.3576 * gl + 0.1805 * bl) / 0.95047
    y = 0.2126 * rl + 0.7152 * gl + 0.0722 * bl
    z = (0.0193 * rl + 0.1192 * gl + 0.9505 * bl) / 1.08883

    def f(t):
        return t ** (1 / 3) if t > 0.008856 else 7.787 * t + 16 / 116
    fx, fy, fz = f(x), f(y), f(z)
    return 116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz)


# ------------------------------------------------------------------ DAT2 (master.dat)
def dat2_datei(pfad_dat, name):
    """Eine Datei aus einem Fallout-2-Archiv (DAT2, little-endian, zlib)."""
    d = Path(pfad_dat).read_bytes()
    baum_groesse, dat_groesse = struct.unpack_from("<II", d, len(d) - 8)
    if dat_groesse != len(d):
        raise ValueError("kein DAT2-Archiv")
    pos = len(d) - 8 - baum_groesse
    anzahl = struct.unpack_from("<I", d, pos)[0]
    pos += 4
    gesucht = name.replace("/", "\\").lower()
    for _ in range(anzahl):
        laenge = struct.unpack_from("<I", d, pos)[0]
        pfad = d[pos + 4:pos + 4 + laenge].decode("cp1252").lower()
        pos += 4 + laenge
        gepackt, echt, groesse, versatz = struct.unpack_from("<BIII", d, pos)
        pos += 13
        if pfad == gesucht:
            roh = d[versatz:versatz + groesse]
            return zlib.decompress(roh) if gepackt else roh[:echt]
    raise KeyError(f"{name} nicht im Archiv")


def dat2_schreiben(dateien):
    """Kleines DAT2-Archiv (fuer Tests): {pfad: bytes}."""
    daten, baum = bytearray(), bytearray(struct.pack("<I", len(dateien)))
    for pfad, inhalt in dateien.items():
        gepackt = zlib.compress(inhalt)
        name = pfad.replace("/", "\\").encode("cp1252")
        baum += struct.pack("<I", len(name)) + name + struct.pack("<BIII", 1, len(inhalt), len(gepackt), len(daten))
        daten += gepackt
    gesamt = len(daten) + len(baum) + 8
    return bytes(daten + baum + struct.pack("<II", len(baum), gesamt))


# ------------------------------------------------------------------ FRM
class Bild:
    def __init__(self, breite, hoehe, pixel, x=0, y=0):
        if len(pixel) != breite * hoehe:
            raise ValueError("Pixelzahl passt nicht zur Groesse")
        self.breite, self.hoehe, self.pixel, self.x, self.y = breite, hoehe, bytes(pixel), x, y


class Frm:
    def __init__(self, richtungen, fps=0, aktion=0, dx=None, dy=None, version=4):
        self.richtungen = richtungen          # Liste (1 oder 6) von Listen von Bild
        self.fps, self.aktion, self.version = fps, aktion, version
        self.dx = list(dx or [0] * 6)
        self.dy = list(dy or [0] * 6)

    @classmethod
    def lesen(cls, daten):
        version, fps, aktion, n = struct.unpack_from(">IHHH", daten, 0)
        dx = list(struct.unpack_from(">6h", daten, 10))
        dy = list(struct.unpack_from(">6h", daten, 22))
        beginn = struct.unpack_from(">6I", daten, 34)
        richtungen = []
        for r in range(6):
            if r and beginn[r] == beginn[0]:
                break
            pos, bilder = 62 + beginn[r], []
            for _ in range(n):
                b, h, groesse, x, y = struct.unpack_from(">HHIhh", daten, pos)
                bilder.append(Bild(b, h, daten[pos + 12:pos + 12 + groesse], x, y))
                pos += 12 + groesse
            richtungen.append(bilder)
        return cls(richtungen, fps, aktion, dx, dy, version)

    def schreiben(self):
        n = len(self.richtungen[0])
        if any(len(r) != n for r in self.richtungen) or len(self.richtungen) not in (1, 6):
            raise ValueError("1 oder 6 Richtungen mit gleich vielen Bildern")
        daten, beginn = bytearray(), []
        for r in self.richtungen:
            beginn.append(len(daten))
            for b in r:
                daten += struct.pack(">HHIhh", b.breite, b.hoehe, len(b.pixel), b.x, b.y) + b.pixel
        beginn += [beginn[0]] * (6 - len(beginn))
        kopf = struct.pack(">IHHH", self.version, self.fps, self.aktion, n)
        kopf += struct.pack(">6h", *self.dx) + struct.pack(">6h", *self.dy)
        kopf += struct.pack(">6I", *beginn) + struct.pack(">I", len(daten))
        return kopf + bytes(daten)


def einzelbild(bild, anker_x, anker_y):
    """Ein FRM mit einem Bild, dessen Punkt (anker_x, anker_y) auf der Hexmitte liegt."""
    dx = bild.breite // 2 - anker_x
    dy = bild.hoehe - 1 - anker_y
    return Frm([[bild]], dx=[dx] * 6, dy=[dy] * 6)


# ------------------------------------------------------------------ Umwandlung (Pillow)
def aus_rgba(bild_rgba, palette, leucht=None, leucht_index=ROT_PULS):
    """RGBA-Bild (Pillow) -> Bild mit Palettenindizes. Durchsichtig unter Alpha 128.
    leucht: Graustufenmaske gleicher Groesse; helle Punkte (> 127) bekommen leucht_index."""
    b, h = bild_rgba.size
    punkte = bild_rgba.convert("RGBA").get_flattened_data() if hasattr(bild_rgba, "get_flattened_data") \
        else bild_rgba.convert("RGBA").getdata()
    maske = None
    if leucht is not None:
        lm = leucht.convert("L")
        maske = lm.get_flattened_data() if hasattr(lm, "get_flattened_data") else lm.getdata()
    px = bytearray(b * h)
    for i, (r, g, bl, a) in enumerate(punkte):
        if a < 128:
            continue
        if maske is not None and maske[i] > 127:
            px[i] = leucht_index
        else:
            px[i] = palette.naechste(r, g, bl)
    return Bild(b, h, px)


def als_rgba(bild, palette, puls=60):
    """Bild -> RGBA-Vorschau. Das pulsierende Rot wird mit Staerke puls (0-60) gezeigt."""
    from PIL import Image
    im = Image.new("RGBA", (bild.breite, bild.hoehe))
    farben = list(palette.rgb)
    farben[ROT_PULS] = (puls * 4, 0, 0)
    im.putdata([(0, 0, 0, 0) if i == 0 else farben[i] + (255,) for i in bild.pixel])
    return im


def zuschneiden(bild):
    """Leere Raender entfernen. Rueckgabe: (Bild, links, oben)."""
    b, h, px = bild.breite, bild.hoehe, bild.pixel
    zeilen = [y for y in range(h) if any(px[y * b:(y + 1) * b])]
    spalten = [x for x in range(b) if any(px[y * b + x] for y in range(h))]
    if not zeilen:
        raise ValueError("leeres Bild")
    x0, x1, y0, y1 = spalten[0], spalten[-1] + 1, zeilen[0], zeilen[-1] + 1
    neu = bytearray()
    for y in range(y0, y1):
        neu += px[y * b + x0:y * b + x1]
    return Bild(x1 - x0, y1 - y0, neu), x0, y0


def streifen(bild, grenzen):
    """Ein breites Bild in senkrechte Streifen schneiden (Fallout sortiert Objekte
    nach Hexfeld; grosse Moebel bestehen deshalb aus mehreren Stuecken).
    grenzen: aufsteigende x-Werte der Schnitte. Rueckgabe: [(Bild, x0)]."""
    teile, xs = [], [0] + list(grenzen) + [bild.breite]
    for x0, x1 in zip(xs, xs[1:]):
        px = bytearray()
        for y in range(bild.hoehe):
            px += bild.pixel[y * bild.breite + x0:y * bild.breite + x1]
        teile.append((Bild(x1 - x0, bild.hoehe, px), x0))
    return teile


# ------------------------------------------------------------------ Szenerie-Prototyp
# Aufbau wie proto.cc protoRead/protoSceneryDataRead, Werte wie die generische
# Szenerie des RPU (00000007.pro): 45 Byte.
MATERIAL = dict(glas=0, metall=1, plastik=2, holz=3, erde=4, stein=5, zement=6, leder=7)
FLAG_KEIN_BLOCK = 0x00000010
FLAG_FLACH = 0x00000008
FLAG_LICHT_DURCH = 0x20000000
FLAG_SCHUSS_DURCH = 0x80000000


def szenerie_pro(pid, fid, material="holz", licht_weite=0, licht_staerke=0, flags=FLAG_LICHT_DURCH,
                 ext=0x80000000, geraeusch=ord("0")):
    """Generische Szenerie (Untertyp 5). Die Textnummer ist Index * 100 (pro_scen.msg)."""
    index = pid & 0xFFFFFF
    kopf = struct.pack(">iiiiiIIiii", pid, index * 100, fid, licht_weite, licht_staerke,
                       flags & 0xFFFFFFFF, ext & 0xFFFFFFFF, -1, 5, MATERIAL[material])
    return kopf + bytes([geraeusch]) + b"\xcc\xcc\xcc\xcc"


# ------------------------------------------------------------------ Befehle
def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("befehl", choices=["png", "frm", "palette", "info"])
    ap.add_argument("quelle")
    ap.add_argument("ziel", nargs="?")
    ap.add_argument("--palette")
    ap.add_argument("--leucht")
    a = ap.parse_args()
    if a.befehl == "info":
        f = Frm.lesen(Path(a.quelle).read_bytes())
        print(f"Version {f.version}, {f.fps} fps, {len(f.richtungen)} Richtung(en) x {len(f.richtungen[0])} Bild(er)")
        for r, bilder in enumerate(f.richtungen):
            print(f"  Richtung {r}: Verschiebung {f.dx[r]}/{f.dy[r]}, Groessen "
                  + ", ".join(f"{b.breite}x{b.hoehe}" for b in bilder[:6]))
        return
    if a.befehl == "palette":
        Path(a.ziel).write_bytes(dat2_datei(a.quelle, "color.pal"))
        print(f"{a.ziel}: Palette aus {a.quelle}")
        return
    if not a.palette:
        sys.exit("--palette fehlt")
    pal = Palette.lesen(a.palette)
    from PIL import Image
    if a.befehl == "png":
        f = Frm.lesen(Path(a.quelle).read_bytes())
        als_rgba(f.richtungen[0][0], pal).save(a.ziel)
    else:
        leucht = Image.open(a.leucht) if a.leucht else None
        bild = aus_rgba(Image.open(a.quelle), pal, leucht)
        b, x0, y0 = zuschneiden(bild)
        Path(a.ziel).write_bytes(einzelbild(b, b.breite // 2, b.hoehe - 1).schreiben())
    print(f"{a.ziel}: geschrieben")


if __name__ == "__main__":
    main()
