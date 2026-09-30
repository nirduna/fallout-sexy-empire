"""Eichung der Blender-Kamera gegen die Spielgrafik (laeuft mit bpy).

1. Eine flache Kachel der Groesse L1 x L2 muss genau die Form einer echten
   Bodenkachel des RPU haben (Parallelogramm (0,12) (48,0) (80,24) (32,36)).
2. Eine Saeule von 1,75 m muss so hoch sein wie ein Mensch im Spiel (~68 Pixel).

Aufruf: <python mit bpy> tools/grafik/eichung.py <ausgabeordner> [kachel.frm]
Ohne kachel.frm wird mit dem Parallelogramm aus geometrie.py verglichen.
"""
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path[:0] = [str(HIER), str(HIER.parent)]

from PIL import Image  # noqa: E402

import geometrie as g  # noqa: E402
import szene  # noqa: E402


def maske_render(pfad):
    im = Image.open(pfad).convert("RGBA")
    return {(x, y) for y in range(im.height) for x in range(im.width) if im.getpixel((x, y))[3] >= 128}


def main():
    aus = Path(sys.argv[1])
    aus.mkdir(parents=True, exist_ok=True)
    ox, oy = 20, 40

    # 1. Kachel
    sc = szene.leeren()
    szene.kamera(sc, 120, 80, ox, oy)
    grau = szene.material("grau", (0.5, 0.5, 0.5))
    szene.quader((g.L1 / 2, -g.L2 / 2, -0.005), (g.L1, g.L2, 0.01), grau, fase=0)
    szene.licht()
    szene.rendern(sc, aus / "kachel.png", aus / "kachel_leucht.png")
    ist = maske_render(aus / "kachel.png")
    if len(sys.argv) > 2:
        import frm
        b = frm.Frm.lesen(Path(sys.argv[2]).read_bytes()).richtungen[0][0]
        soll = {(ox + x, oy - 12 + y) for y in range(b.hoehe) for x in range(b.breite) if b.pixel[y * b.breite + x]}
    else:
        soll = set()
        for y in range(36):
            for x in range(80):
                # Punkt in Kachelkoordinaten (alpha, beta) zwischen 0 und 1?
                wx, wy = g.boden_aus_bild(x + 0.5, y - 12 + 0.5)
                if 0 <= wx <= g.L1 and -g.L2 <= wy <= 0:
                    soll.add((ox + x, oy - 12 + y))
    schnitt = len(ist & soll) / len(ist | soll)

    # 2. Mensch
    sc = szene.leeren()
    szene.kamera(sc, 60, 120, 30, 100)
    grau = szene.material("grau", (0.5, 0.5, 0.5))
    szene.quader((0, 0, 0.875), (0.3, 0.3, 1.75), grau, fase=0)
    szene.licht()
    szene.rendern(sc, aus / "saeule.png", aus / "saeule_leucht.png")
    m = maske_render(aus / "saeule.png")
    oben = min(y for x, y in m if abs(x - 30) <= 1)
    print(f"Kachel: Ueberdeckung {schnitt:.3f} ({len(ist)} / {len(soll)} Pixel)")
    print(f"Saeule 1,75 m: {100 - oben} Pixel ueber dem Ursprung")
    ok = schnitt >= 0.9 and 64 <= 100 - oben <= 72
    print("EICHUNG OK" if ok else "EICHUNG FEHLER")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
