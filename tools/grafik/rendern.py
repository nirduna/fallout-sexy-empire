"""Rendert die eigene Szenerie mit Blender (laeuft mit dem Python-Modul bpy).

Je Objekt aus katalog.py: bild.png, leucht.png und meta.json in <ausgabe>/<name>/.
Danach wandelt tools/grafik/umwandeln.py die Bilder in FRM-Dateien um.

Aufruf: <python mit bpy> tools/grafik/rendern.py <ausgabe> [name ...]
"""
import json
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path[:0] = [str(HIER), str(HIER.parent)]

import geometrie as g  # noqa: E402
import katalog  # noqa: E402
import modelle  # noqa: E402
import szene  # noqa: E402


def main():
    aus = Path(sys.argv[1])
    namen = sys.argv[2:] or list(katalog.OBJEKTE)
    for name in namen:
        obj = katalog.OBJEKTE[name]
        ref = katalog.bezug(name)
        felder = [g.hex_welt(g.versatz(ref, dx, dy), ref) for dx, dy in obj["felder"]]
        breite, hoehe, ox, oy = modelle.LEINWAND[name]
        ziel = aus / name
        ziel.mkdir(parents=True, exist_ok=True)
        sc = szene.leeren()
        szene.kamera(sc, breite, hoehe, ox, oy)
        szene.licht()
        modelle.MODELLE[name](modelle.materialien(), felder)
        szene.rendern(sc, ziel / "bild.png", ziel / "leucht.png")
        (ziel / "meta.json").write_text(json.dumps(dict(name=name, ursprung=[ox, oy], bezug=ref,
                                                        felder=obj["felder"]), indent=1))
        print(f"OK    {name}")


if __name__ == "__main__":
    main()
