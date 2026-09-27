#!/usr/bin/env python3
"""Baut die Rotlicht-Karten und haelt alle Kartenpositionen an einer Stelle.

Die Positionen stehen unten in GOSSE und RLDEN01 (eine Quelle der Wahrheit).
Daraus entstehen:

  scripts_src/headers/rl_karten.h   Hexfelder und PIDs fuer die Skripte (Befehl "header")
  <out>/rlden01.map                 die Innenkarte der Gosse (Befehl "bauen")
  docs/bilder/*.png                 Draufsichten fuer die Pruefliste (Befehl "bilder")

Die Innenkarte wird nicht von Hand gezeichnet, sondern aus einer Vorlage des
Restoration Project abgeleitet: Beckys Keller (denbus1, Ebene 1). Uebernommen
werden Boden, Waende und Einrichtung. Die Destille (Vanilla-Quest) faellt weg,
die Treppe fuehrt zur Ruine auf Den Business 2 zurueck, dazu kommen Essie und
Kolbe mit ihren Skripten. Die Vorlage wird beim Bauen aus dem RPU gelesen und
nicht im Repository mitgeliefert.

Aufruf:
  python3 tools/bau_karten.py header
  python3 tools/bau_karten.py bauen  --karten RPU/data/maps --out build/maps
                                     [--skript-basis 1559] [--karten-index 173]
                                     [--protos RPU/data/proto]
  python3 tools/bau_karten.py bilder --karten RPU/data/maps --karte build/maps/rlden01.map
                                     [--skripte RPU/data/scripts/scripts.lst] [--protos ...]
"""
import argparse
import copy
import re
import sys
from pathlib import Path

import fomap

ROOT = Path(__file__).resolve().parent.parent

# ------------------------------------------------------------------ Positionen
# Den Business 2 (Vanilla, maps.txt [Map 007], in den Headern MAP_DEN_BUSINESS).
# Der Eingang wird zur Laufzeit vom globalen Skript gesetzt, die Vanilla-Karte
# bleibt unveraendert.
DEN_BUSINESS_2 = 7
GOSSE = dict(
    treppe_pid=0x2000164,    # "Treppe" (stway.frm), dieselbe Kellertreppe wie bei Becky (denbus1)
    treppe_hex=18458,        # im ueberdachten Rest der Ruine oestlich der Sklavengilde
    treppe_ebene=0,
    ankunft_hex=18658,       # hier steht man, wenn man aus der Gosse heraufkommt
    ankunft_rot=3,           # Blick nach Suedwesten, wie bei Beckys Treppe
)

RLDEN01 = dict(
    datei="rlden01.map",
    name=b"RLDEN01.MAP",
    vorlage="denbus1",       # Beckys Keller
    vorlage_ebene=1,
    entfernen=[0x20003E8],   # Destille (diStill.int, Vanilla-Quest um Beckys Schnaps)
    treppe_pid=0x200015C,    # "Treppe" (stair00.frm) nach oben
    treppe_hex=16666,
    eingang_hex=17066,       # Startpunkt der Karte (unten an der Treppe)
    eingang_rot=3,
    figuren=[
        # Werte fuer fid und Kampfdaten wie bei den Vanilla-Figuren mit derselben PID
        # (Frau: dcStory1 in denbus1, Schlaeger: ncCorBro in newr2).
        dict(name="Essie", skript="SCRIPT_RLESSIE", pid=0x1000042, fid=0x1000021,
             hex=17866, rot=5, daten=[0, 0, 0, 7, 0, 14, 1, -1, 28, 0, 0]),
        dict(name="Kolbe", skript="SCRIPT_RLKOLBE", pid=0x100001E, fid=0x100000D,
             hex=17270, rot=1, daten=[0, 0, 0, 7, 0, 13, 1, -1, 68, 0, 0]),
    ],
    kartenskript="SCRIPT_RLDEN01",
)


def built_tile(tile, ebene, rot):
    """Ziel von Treppen und Leitern: Hex | Ebene << 29 | Blickrichtung << 26."""
    return tile | (ebene << 29) | (rot << 26)


# ------------------------------------------------------------------ Skriptnummern
def skript_offsets():
    """SCRIPT_RL* = RL_SCRIPT_BASE + n aus rotlicht.h."""
    text = (ROOT / "scripts_src/headers/rotlicht.h").read_text(encoding="utf-8")
    return {m.group(1): int(m.group(2))
            for m in re.finditer(r"#define\s+(SCRIPT_RL\w+)\s+\(RL_SCRIPT_BASE \+ (\d+)\)", text)}


# ------------------------------------------------------------------ Header
def header():
    zeilen = [
        "/*",
        "   rl_karten.h - Kartenpositionen, ERZEUGT von tools/bau_karten.py.",
        "   Nicht von Hand aendern: Die Werte stehen dort in GOSSE und RLDEN01.",
        "*/",
        "#ifndef RL_KARTEN_H",
        "#define RL_KARTEN_H",
        "",
        "// Eingang der Gosse auf Den Business 2 (zur Laufzeit gesetzt, siehe gl_rotlicht.ssl)",
        f"#define RL_GOSSE_TREPPE_PID         ({GOSSE['treppe_pid']})   // Treppe (stway.frm)",
        f"#define RL_GOSSE_TREPPE_HEX         ({GOSSE['treppe_hex']})",
        f"#define RL_GOSSE_TREPPE_EBENE       ({GOSSE['treppe_ebene']})",
        f"#define RL_GOSSE_ANKUNFT_HEX        ({GOSSE['ankunft_hex']})   // nach dem Rueckweg",
        "",
        "// Innenkarte der Gosse",
        f"#define RL_KARTE_GOSSE              \"{RLDEN01['datei']}\"",
        f"#define RL_GOSSE_EINGANG_HEX        ({RLDEN01['eingang_hex']})",
        "",
        "#endif",
        "",
    ]
    ziel = ROOT / "scripts_src/headers/rl_karten.h"
    ziel.write_text("\n".join(zeilen), encoding="utf-8")
    print(f"{ziel.relative_to(ROOT)} geschrieben.")


# ------------------------------------------------------------------ Karte bauen
def neuer_skriptsatz(typ, nummer, index, besitzer):
    """Skriptsatz wie in Vanilla-Karten: keine lokalen Variablen, die Engine legt sie an."""
    return [(typ << 24) | nummer, -1, 0, index, 0, besitzer, -1, 0, 0, 0, 0, -1, 0, 0, 0, 0]


def skriptlisten(saetze_je_typ):
    """5 Listen in Bloecken zu 16 Saetzen (wie scriptListExtentRead)."""
    leer = [0] * 16
    listen = []
    for typ in range(fomap.SCRIPT_TYPES):
        saetze = saetze_je_typ.get(typ, [])
        bloecke = []
        for i in range(0, len(saetze), 16):
            teil = saetze[i:i + 16]
            bloecke.append({"saetze": teil + [leer[:] for _ in range(16 - len(teil))],
                            "laenge": len(teil), "next": 0})
        listen.append({"anzahl": len(saetze), "bloecke": bloecke})
    return listen


def baue_rlden01(karten_dir, db, skript_basis, karten_index):
    offs = skript_offsets()
    idx0 = lambda name: skript_basis + offs[name] - 1          # 0-basiert (scripts.lst-Zeile - 1)
    v = fomap.Karte.lesen((Path(karten_dir) / f"{RLDEN01['vorlage']}.map").read_bytes(), db)
    alt_saetze = {s[0]: s for _, s in v.skript_saetze()}

    k = fomap.Karte()
    k.kopf = dict(version=20, name=RLDEN01["name"].ljust(16, b"\0"),
                  entering_tile=RLDEN01["eingang_hex"], entering_elevation=0,
                  entering_rotation=RLDEN01["eingang_rot"], local_vars=0,
                  script_index=skript_basis + offs[RLDEN01["kartenskript"]],   # 1-basiert
                  flags=fomap.ELEV_FLAGS[1] | fomap.ELEV_FLAGS[2],             # nur Ebene 0
                  darkness=v.kopf["darkness"], global_vars=0, index=karten_index, last_visit=0)
    k.kopf_rest = [0] * 44
    k.kacheln = {0: v.kacheln[RLDEN01["vorlage_ebene"]]}

    saetze = {}
    naechste = {}

    def skript_fuer(obj, index):
        typ = 4 if fomap.pid_typ(obj["kopf"]["pid"]) == fomap.T_CRITTER else 3
        n = naechste.get(typ, 0)
        naechste[typ] = n + 1
        satz = neuer_skriptsatz(typ, n, index, obj["kopf"]["id"])
        saetze.setdefault(typ, []).append(satz)
        obj["kopf"]["sid"] = satz[0]
        obj["kopf"]["script_index"] = index

    def uebernehmen(obj):
        obj["kopf"]["elevation"] = 0
        if obj["kopf"]["sid"] != -1:
            alt = alt_saetze[obj["kopf"]["sid"]]
            skript_fuer(obj, fomap.skript_index(alt))
        for _, inhalt in obj["inventar"]:
            uebernehmen(inhalt)

    objekte = []
    treppe = None
    for o in v.objekte[RLDEN01["vorlage_ebene"]]:
        if o["kopf"]["pid"] in RLDEN01["entfernen"]:
            continue
        o = copy.deepcopy(o)
        uebernehmen(o)
        if o["kopf"]["pid"] == RLDEN01["treppe_pid"] and o["kopf"]["tile"] == RLDEN01["treppe_hex"]:
            treppe = o
        objekte.append(o)
    if treppe is None:
        raise SystemExit("Treppe in der Vorlage nicht gefunden")
    # Treppe: [Flags, Ziel (built tile), Zielkarte]
    treppe["daten"] = [treppe["daten"][0],
                       built_tile(GOSSE["ankunft_hex"], GOSSE["treppe_ebene"], GOSSE["ankunft_rot"]),
                       DEN_BUSINESS_2]

    naechste_id = max(o["kopf"]["id"] for _, o in v.alle_objekte()) + 1
    for f in RLDEN01["figuren"]:
        kopf = dict(id=naechste_id, tile=f["hex"], x=0, y=0, sx=0, sy=0, frame=0, rotation=f["rot"],
                    fid=f["fid"], flags=0x20000000, elevation=0, pid=f["pid"],
                    cid=-1, light_distance=0, light_intensity=0, outline=0, sid=-1, script_index=-1)
        naechste_id += 1
        o = {"kopf": kopf, "inv": [0, 0, 0], "daten": list(f["daten"]), "inventar": []}
        skript_fuer(o, idx0(f["skript"]))
        objekte.append(o)

    k.skripte = skriptlisten(saetze)
    k.objekte = [objekte, [], []]
    k.objekte_gesamt = len(objekte)
    pruefe(k, db)
    return k


def pruefe(k, db):
    """Selbstkontrolle: Round-Trip, jede SID hat einen Satz mit passendem Besitzer,
    die neuen Figuren haben eigene IDs. (Vanilla-Karten haben viele doppelte
    Objekt-IDs, auch bei Objekten mit Skript; die Engine verbindet ueber die SID.)"""
    daten = k.schreiben()
    k2 = fomap.Karte.lesen(daten, db)
    assert k2.schreiben() == daten, "Round-Trip nicht byte-gleich"
    saetze = {s[0]: s for _, s in k.skript_saetze()}
    ids = [o["kopf"]["id"] for _, o in k.alle_objekte()]
    for f in RLDEN01["figuren"]:
        fig = [o for _, o in k.alle_objekte() if o["kopf"]["tile"] == f["hex"] and o["kopf"]["pid"] == f["pid"]]
        assert len(fig) == 1 and ids.count(fig[0]["kopf"]["id"]) == 1, f"{f['name']}: ID nicht eindeutig"
    sids = [s[0] for _, s in k.skript_saetze()]
    assert len(sids) == len(set(sids)), "doppelte SIDs"
    for _, o in k.alle_objekte():
        sid = o["kopf"]["sid"]
        if sid != -1:
            assert sid in saetze, f"SID {sid:#x} ohne Skriptsatz"
            assert fomap.skript_besitzer(saetze[sid]) == o["kopf"]["id"], "Besitzer passt nicht"
    for liste in k.skripte:
        assert liste["anzahl"] == sum(b["laenge"] for b in liste["bloecke"])
    hexe = [o["kopf"]["tile"] for _, o in k.alle_objekte() if fomap.pid_typ(o["kopf"]["pid"]) == fomap.T_CRITTER]
    assert len(hexe) == len(set(hexe)), "zwei Figuren auf einem Feld"


def bauen(a):
    db = fomap.ProtoDB([a.protos] if a.protos else [])
    k = baue_rlden01(a.karten, db, a.skript_basis, a.karten_index)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ziel = out / RLDEN01["datei"]
    ziel.write_bytes(k.schreiben())
    anz = [l["anzahl"] for l in k.skripte]
    print(f"OK    {ziel.name}: {len(k.objekte[0])} Objekte, Skripte je Typ {anz}, "
          f"Kartenskript {k.kopf['script_index']}, Index {k.kopf['index']}")


# ------------------------------------------------------------------ Bilder
def bilder(a):
    import fomap_bild as fb
    db = fomap.ProtoDB([a.protos] if a.protos else [])
    namen = fb.skriptnamen(a.skripte) if a.skripte else []
    offs = skript_offsets()
    extra = {a.skript_basis + n - 1: name.replace("SCRIPT_", "").lower() for name, n in offs.items()}
    ziel = ROOT / "docs/bilder"
    ziel.mkdir(parents=True, exist_ok=True)

    den = fomap.Karte.lesen((Path(a.karten) / "denbus2.map").read_bytes(), db)
    marken = [(GOSSE["treppe_hex"], f"Treppe {GOSSE['treppe_hex']}"),
              (GOSSE["ankunft_hex"], f"Ankunft {GOSSE['ankunft_hex']}")]
    fb.zeichne(den, db, ziel / "gosse_eingang_uebersicht.png", 0, namen, mitte=19098, radius=40,
               massstab=0.6, markiere=marken)
    fb.zeichne(den, db, ziel / "gosse_eingang.png", 0, namen, mitte=GOSSE["treppe_hex"], radius=14,
               massstab=1.6, markiere=marken, raster=4)
    k = fomap.Karte.lesen(Path(a.karte).read_bytes(), db)
    marken = [(RLDEN01["treppe_hex"], f"Treppe {RLDEN01['treppe_hex']}"),
              (RLDEN01["eingang_hex"], f"Start {RLDEN01['eingang_hex']}")]
    fb.zeichne(k, db, ziel / "rlden01.png", 0, namen, mitte=17670, radius=12, massstab=1.8,
               markiere=marken, raster=2, extra_namen=extra)
    for p in sorted(ziel.glob("*.png")):
        print(f"OK    {p.relative_to(ROOT)}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("befehl", choices=["header", "bauen", "bilder"])
    ap.add_argument("--karten", help="Kartenordner des RPU (data/maps)")
    ap.add_argument("--karte", help="gebaute rlden01.map (fuer 'bilder')")
    ap.add_argument("--out", default=str(ROOT / "build/maps"))
    ap.add_argument("--protos", default=None)
    ap.add_argument("--skripte", default=None)
    ap.add_argument("--skript-basis", type=int, default=1559)
    ap.add_argument("--karten-index", type=int, default=173)
    a = ap.parse_args()
    if a.befehl == "header":
        header()
    elif a.befehl == "bauen":
        if not a.karten:
            ap.error("--karten fehlt")
        bauen(a)
    else:
        if not (a.karten and a.karte):
            ap.error("--karten und --karte fehlen")
        bilder(a)


if __name__ == "__main__":
    sys.exit(main())
