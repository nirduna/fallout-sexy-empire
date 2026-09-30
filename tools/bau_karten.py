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
    # Figuren, die das Kartenskript zur Laufzeit setzt (Umsetzung 5, "Ketten" Akt 2-5)
    laufzeit={
        "MARA": 18466,        # hinter dem alten Kessel, weg von der Treppe
        "DEKE": 17466,        # Deke oder Jess, mitten im Raum
        "ANGREIFER1": 16866,  # kommen die Treppe herunter
        "ANGREIFER2": 17264,
    },
    # Felder, die die eigene Einrichtung vom Raum trennen darf (keine)
    nischen=set(),
)


# Szenerie, die nicht im Weg steht (unsichtbare Lichtquelle)
NICHT_BLOCKIEREND = {0x200008D}
BLOCKER_PID = 0x2000043          # "Secret Blocking Hex", auf den freien Feldern grosser Moebel

# ------------------------------------------------------------------ weitere Haeuser (Umsetzung 6)
# Jedes Haus: ein Eingang auf der Vanilla-Stadtkarte (zur Laufzeit gesetzt, dieselbe
# Steintreppe wie bei der Gosse) und eine Innenkarte aus einer Vorlage des RPU.
# Aus der Vorlage bleiben Boden, Waende und Einrichtung; Figuren, lose Gegenstaende,
# Kartenausgaenge und alle Vanilla-Skripte fallen weg. Eine vorhandene Treppe oder
# Leiter der Vorlage wird zum Rueckweg auf die Stadtkarte.
# Figuren setzt das Kartenskript zur Laufzeit an die Plaetze in "plaetze", gefunden
# mit einer Breitensuche vom Startpunkt: erreichbar und frei in RPU 2.3.34, 2.4.34
# und dem aktuellen Stand; die Madame 4-10 Schritte vom Eingang, die Angreifer 2-8,
# die Gaeste verteilt bis 16 Schritte.
HAEUSER = [
    dict(kuerzel="STRUMPF", haus="RL_NEW_RENO", titel="Das Silberne Strumpfband",
         stadtkarte="newr1", stadtkarte_index=54, stadtkarte_konst="MAP_NEW_RENO_1",
         treppe_hex=23296, ankunft_hex=23496, ankunft_rot=3,          # Virgin Street, am Cat's Paw
         datei="rlren01.map", name=b"RLREN01.MAP", vorlage="newr3", vorlage_ebene=1,
         ausgang_hex=22692, eingang_hex=23093, eingang_rot=3, kartenskript="SCRIPT_RLREN01",
         plaetze=dict(MADAME=23699, GAST1=25699, GAST2=24703, GAST3=24900, GAST4=23106,
                      ANGREIFER1=23300, ANGREIFER2=24098)),
    dict(kuerzel="SCHLACKE", haus="RL_REDDING", titel="Die Schlacke",
         stadtkarte="redment", stadtkarte_index=65, stadtkarte_konst="MAP_REDDING_MINE_ENT",
         treppe_hex=16483, ankunft_hex=16683, ankunft_rot=3,          # Mining Camp, zwischen den Schuppen
         datei="rlred01.map", name=b"RLRED01.MAP", vorlage="redmtun", vorlage_ebene=0,
         ausgang_hex=11475, eingang_hex=11075, eingang_rot=3, kartenskript="SCRIPT_RLRED01",
         plaetze=dict(MADAME=9674, GAST1=9459, GAST2=12459, GAST3=13679, GAST4=9088,
                      ANGREIFER1=10674, ANGREIFER2=10676)),
    dict(kuerzel="KLOAKE", haus="RL_VAULT_CITY", titel="Die Kloake",
         stadtkarte="vctyctyd", stadtkarte_index=15, stadtkarte_konst="MAP_VAULTCITY_COURTYARD",
         treppe_hex=15671, ankunft_hex=15871, ankunft_rot=3,          # Courtyard, hinter Cassidy's
         datei="rlvct01.map", name=b"RLVCT01.MAP", vorlage="abbasem", vorlage_ebene=0,
         ausgang_hex=12282, eingang_hex=12683, eingang_rot=3, kartenskript="SCRIPT_RLVCT01",
         plaetze=dict(MADAME=13884, GAST1=12679, GAST2=14683, GAST3=14680, GAST4=13678,
                      ANGREIFER1=12284, ANGREIFER2=13483)),
    dict(kuerzel="TRAENKE", haus="RL_NCR", titel="Die Traenke",
         stadtkarte="ncrent", stadtkarte_index=46, stadtkarte_konst="MAP_NCR_BAZAAR",
         treppe_hex=24947, ankunft_hex=25147, ankunft_rot=3,          # Bazaar, am Rawhide Saloon
         datei="rlncr01.map", name=b"RLNCR01.MAP", vorlage="ncrent", vorlage_ebene=1,
         ausgang_hex=20358, eingang_hex=20756, eingang_rot=3, kartenskript="SCRIPT_RLNCR01",
         plaetze=dict(MADAME=21958, GAST1=21344, GAST2=23758, GAST3=20748, GAST4=22758,
                      ANGREIFER1=21157, ANGREIFER2=20754)),
    dict(kuerzel="BILGE", haus="RL_SAN_FRAN", titel="Die Bilge",
         stadtkarte="sfdock", stadtkarte_index=136, stadtkarte_konst="MAP_SAN_FRAN_DOCK",
         treppe_hex=25075, ankunft_hex=25076, ankunft_rot=3,          # Docks
         datei="rlsfr01.map", name=b"RLSFR01.MAP", vorlage="sftanker", vorlage_ebene=2,
         ausgang_hex=22483, eingang_hex=22682, eingang_rot=3, kartenskript="SCRIPT_RLSFR01",
         plaetze=dict(MADAME=22290, GAST1=22098, GAST2=21091, GAST3=21894, GAST4=21690,
                      ANGREIFER1=22885, ANGREIFER2=22488)),
]
TREPPE_PID = 0x2000164          # Steintreppe (stway.frm), wie bei der Gosse
EXIT_GRIDS = set(range(0x5000010, 0x5000018))


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
        "   Nicht von Hand aendern: Die Werte stehen dort in GOSSE, RLDEN01 und HAEUSER.",
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
        f"#define RL_GOSSE_ESSIE_HEX          ({RLDEN01['figuren'][0]['hex']})",
        f"#define RL_GOSSE_KOLBE_HEX          ({RLDEN01['figuren'][1]['hex']})",
    ] + [f"#define RL_GOSSE_{name}_HEX{' ' * (15 - len(name))}({hexfeld})"
         for name, hexfeld in RLDEN01["laufzeit"].items()]
    for h in HAEUSER:
        k = h["kuerzel"]
        def d(name, wert):
            return f"#define RL_{k}_{name}".ljust(36) + f"({wert})"
        zeilen += [
            "",
            f"// {h['titel']}: Eingang auf {h['stadtkarte']} ({h['stadtkarte_konst']}), Innenkarte {h['datei']}",
            d("TREPPE_PID", TREPPE_PID),
            d("TREPPE_HEX", h["treppe_hex"]),
            d("TREPPE_EBENE", 0),
            d("ANKUNFT_HEX", h["ankunft_hex"]),
            d("STADTKARTE", h["stadtkarte_konst"]),
            f"#define RL_KARTE_{k}".ljust(36) + f"\"{h['datei']}\"",
            d("EINGANG_HEX", h["eingang_hex"]),
        ] + [d(f"{n}_HEX", v) for n, v in h["plaetze"].items()]
    zeilen += ["", "#endif", ""]
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


def baue_rlden01(karten_dir, db, skript_basis, karten_index, dekor=None):
    """dekor: {Stueck: (fid, pid)} aus szenerie.einfuegen; dann kommt die eigene
    Einrichtung (tools/grafik/katalog.py) dazu. Ohne dekor die Karte wie bisher."""
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

    neu = []
    if dekor:
        import szenerie
        k.objekte = [objekte, [], []]
        weg_vorher = erreichbar_von(k, RLDEN01["eingang_hex"])
        # Vanilla-Objekte, an deren Stelle die eigene Einrichtung kommt (das graue Bett im Zimmer)
        gefunden = set()
        for pid, t in szenerie.ersetzt():
            for o in [o for o in objekte if o["kopf"]["pid"] == pid and o["kopf"]["tile"] == t]:
                objekte.remove(o)
                gefunden.add(pid)
        fehlt = {pid for pid, _ in szenerie.ersetzt()} - gefunden - {BLOCKER_PID}
        if fehlt:
            raise SystemExit(f"Vorlage: {', '.join(map(hex, fehlt))} nicht gefunden, die Einrichtung passt nicht mehr")
        zu = {o["kopf"]["tile"] for o in objekte if blockiert(o)}
        # Kamerasperren und unsichtbare Lichtquellen duerfen mit auf dem Feld liegen
        vorher = {o["kopf"]["tile"]: hex(o["kopf"]["pid"]) for o in objekte
                  if fomap.pid_typ(o["kopf"]["pid"]) != fomap.T_MISC and o["kopf"]["pid"] not in NICHT_BLOCKIEREND}
        # Blocker nur, wo nicht schon eine Wand oder ein Blocker der Vorlage steht
        neu = [o for o in szenerie.kartenobjekte(dekor, naechste_id)
               if not (o["kopf"]["pid"] == BLOCKER_PID and o["kopf"]["tile"] in zu)]
        for o in neu:
            t = o["kopf"]["tile"]
            if t in vorher:
                raise SystemExit(f"Einrichtung {o['kopf']['pid']:#x} auf Hex {t}, dort ist schon {vorher[t]}")
            vorher[t] = hex(o["kopf"]["pid"])
            db.extra.setdefault(o["kopf"]["pid"], 0)        # generische Szenerie: keine Zusatzdaten
        objekte += neu
        # Die Einrichtung nimmt nur ihre eigenen Felder weg und schneidet keinen Teil des Raums ab
        weg = erreichbar_von(k, RLDEN01["eingang_hex"])
        zu = {o["kopf"]["tile"] for o in neu if blockiert(o)}
        abgeschnitten = sorted(weg_vorher - zu - weg - RLDEN01["nischen"])
        if abgeschnitten:
            raise SystemExit(f"Einrichtung schneidet Felder vom Raum ab: {abgeschnitten[:10]}")

    k.skripte = skriptlisten(saetze)
    k.objekte = [objekte, [], []]
    k.objekte_gesamt = len(objekte)
    pruefe(k, db, neu)
    return k


def blockiert(o):
    """Steht das Objekt im Weg? Waende und Szenerie, ausser NoBlock-Objekten und Tueren
    (Szenerie mit genau einem Zusatzwert; Tueren oeffnen sich beim Durchgehen)."""
    p = o["kopf"]["pid"]
    typ = fomap.pid_typ(p)
    if typ == fomap.T_SCENERY and len(o["daten"]) == 2:
        return False
    return (typ in (fomap.T_WALL, fomap.T_SCENERY) and p not in NICHT_BLOCKIEREND
            and not o["kopf"]["flags"] & 0x10)


def erreichbar_von(k, start):
    """Alle Hexfelder, die man vom Start aus auf Ebene 0 erreicht (Breitensuche)."""
    zu = {o["kopf"]["tile"] for _, o in k.alle_objekte() if blockiert(o)}
    gesehen, offen = {start}, [start]
    while offen:
        t = offen.pop()
        for n in hex_nachbarn(t):
            if n not in gesehen and n not in zu:
                gesehen.add(n)
                offen.append(n)
    return gesehen


def pruefe(k, db, dekor=()):
    """Selbstkontrolle: Round-Trip, jede SID hat einen Satz mit passendem Besitzer,
    die neuen Figuren haben eigene IDs. (Vanilla-Karten haben viele doppelte
    Objekt-IDs, auch bei Objekten mit Skript; die Engine verbindet ueber die SID.)
    Danach: Startpunkt, Figuren, Laufzeitplaetze und die Treppe sind vom Start aus
    erreichbar, auch mit der eigenen Einrichtung (dekor), und jedes Stueck der
    Einrichtung steht auf Boden und im Raum (ein Nachbarfeld ist erreichbar)."""
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
    # Figuren und Startpunkt nicht auf Waenden oder Einrichtung (Vorlagen aendern sich je RPU-Version)
    belegt = {}
    for _, o in k.alle_objekte():
        if blockiert(o):
            belegt.setdefault(o["kopf"]["tile"], hex(o["kopf"]["pid"]))
    pruef = ([("Startpunkt", RLDEN01["eingang_hex"])] + [(f["name"], f["hex"]) for f in RLDEN01["figuren"]]
             + list(RLDEN01["laufzeit"].items()))
    for name, t in pruef:
        assert t not in belegt, f"{name} steht auf Hex {t}, dort ist schon {belegt[t]}"
    felder = [t for _, t in pruef]
    assert len(felder) == len(set(felder)), "zwei Positionen auf einem Feld"
    # Wege: alles Wichtige vom Startpunkt aus erreichbar
    weg = erreichbar_von(k, RLDEN01["eingang_hex"])
    for name, t in pruef:
        assert t in weg, f"{name} (Hex {t}) ist vom Startpunkt aus nicht erreichbar"
    assert any(n in weg for n in hex_nachbarn(RLDEN01["treppe_hex"])), "Treppe nicht erreichbar"
    kacheln = k.kacheln[0]
    for o in dekor:
        t = o["kopf"]["tile"]
        sq = (t // 200 // 2) * 100 + (t % 200) // 2
        boden = int.from_bytes(kacheln[sq * 4:sq * 4 + 4], "big") & 0xFFF
        assert boden != 1, f"Einrichtung {o['kopf']['pid']:#x} auf Hex {t}: dort ist kein Boden"
    # Im Raum: jedes Stueck grenzt an begehbaren Boden, oder ueber andere Stuecke desselben
    # Moebels (das Kopfende eines Betts an der Wand hat keinen freien Nachbarn)
    felder = {o["kopf"]["tile"] for o in dekor}
    im_raum = {t for t in felder if t in weg or any(n in weg for n in hex_nachbarn(t))}
    offen = list(im_raum)
    while offen:
        for n in hex_nachbarn(offen.pop()):
            if n in felder and n not in im_raum:
                im_raum.add(n)
                offen.append(n)
    for o in dekor:
        assert o["kopf"]["tile"] in im_raum, \
            f"Einrichtung {o['kopf']['pid']:#x} auf Hex {o['kopf']['tile']} steht ausserhalb des Raums"


def hex_nachbarn(t):
    """Die sechs Nachbarn eines Hexfelds (fallout2-ce tile.cc, _dir_tile)."""
    x, y = t % 200, t // 200
    d = ([(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (0, -1)] if x % 2 == 0
         else [(-1, -1), (-1, 0), (0, 1), (1, 0), (1, -1), (0, -1)])
    for dx, dy in d:
        nx, ny = x + dx, y + dy
        if 0 <= nx < 200 and 0 <= ny < 200:
            yield ny * 200 + nx


def ist_leiter(obj, db):
    """Leitern speichern [Flags, Zielkarte, Ziel]; Treppen [Flags, Ziel, Zielkarte]."""
    sub = db.subtyp(obj["kopf"]["pid"]) if hasattr(db, "subtyp") else None
    if sub is not None:
        return sub in (3, 4)
    return obj["kopf"]["pid"] in (0x200008B, 0x20008C9, 0x20008CA, 0x2000891, 0x2000840)


def baue_haus(h, karten_dir, db, skript_basis, karten_index):
    """Innenkarte eines weiteren Hauses aus seiner Vorlage (siehe HAEUSER)."""
    offs = skript_offsets()
    v = fomap.Karte.lesen((Path(karten_dir) / f"{h['vorlage']}.map").read_bytes(), db)
    e = h["vorlage_ebene"]
    k = fomap.Karte()
    k.kopf = dict(version=20, name=h["name"].ljust(16, b"\0"),
                  entering_tile=h["eingang_hex"], entering_elevation=0,
                  entering_rotation=h["eingang_rot"], local_vars=0,
                  script_index=skript_basis + offs[h["kartenskript"]],   # 1-basiert
                  flags=fomap.ELEV_FLAGS[1] | fomap.ELEV_FLAGS[2],         # nur Ebene 0
                  darkness=v.kopf["darkness"], global_vars=0, index=karten_index, last_visit=0)
    k.kopf_rest = [0] * 44
    k.kacheln = {0: v.kacheln[e]}

    def saeubern(obj):
        obj["kopf"]["elevation"] = 0
        obj["kopf"]["sid"] = -1                 # keine Vanilla-Skripte
        obj["kopf"]["script_index"] = -1
        if obj["inventar"]:                    # keine Beute aus der Vorlage
            obj["inventar"] = []
            obj["inv"][0] = 0

    objekte = []
    ausgang = None
    for o in v.objekte[e]:
        pid = o["kopf"]["pid"]
        typ = fomap.pid_typ(pid)
        if typ in (fomap.T_CRITTER, fomap.T_ITEM) or pid in EXIT_GRIDS:
            continue
        o = copy.deepcopy(o)
        saeubern(o)
        if o["kopf"]["tile"] == h["ausgang_hex"] and typ == fomap.T_SCENERY and len(o["daten"]) >= 3:
            ausgang = o
        objekte.append(o)
    if ausgang is None:
        raise SystemExit(f"{h['datei']}: Treppe/Leiter auf Hex {h['ausgang_hex']} nicht in der Vorlage")
    ziel = built_tile(h["ankunft_hex"], 0, h["ankunft_rot"])
    if ist_leiter(ausgang, db):
        ausgang["daten"] = [ausgang["daten"][0], h["stadtkarte_index"], ziel]
    else:
        ausgang["daten"] = [ausgang["daten"][0], ziel, h["stadtkarte_index"]]

    k.skripte = skriptlisten({})
    k.objekte = [objekte, [], []]
    k.objekte_gesamt = len(objekte)
    pruefe_haus(k, db, h)
    return k


def pruefe_haus(k, db, h):
    """Round-Trip; keine Skripte ausser dem Kartenskript; Start und alle Figurenplaetze
    frei und vom Startpunkt aus erreichbar; Ausgang fuehrt zur Stadtkarte."""
    daten = k.schreiben()
    assert fomap.Karte.lesen(daten, db).schreiben() == daten, f"{h['datei']}: Round-Trip"
    assert not list(k.skript_saetze()), f"{h['datei']}: Skriptsaetze uebrig"
    blockiert, belegt = set(), {}
    for _, o in k.alle_objekte():
        p, t = o["kopf"]["pid"], o["kopf"]["tile"]
        if fomap.pid_typ(p) in (fomap.T_WALL, fomap.T_SCENERY) and p not in NICHT_BLOCKIEREND:
            blockiert.add(t)
        if p not in NICHT_BLOCKIEREND:
            belegt.setdefault(t, hex(p))
    start = h["eingang_hex"]
    assert start not in belegt, f"{h['datei']}: Startpunkt {start} belegt ({belegt.get(start)})"
    erreichbar, offen = {start}, [start]
    while offen:
        t = offen.pop()
        for n in hex_nachbarn(t):
            if n not in erreichbar and n not in blockiert:
                erreichbar.add(n)
                offen.append(n)
    plaetze = list(h["plaetze"].items())
    felder = [t for _, t in plaetze] + [start]
    assert len(felder) == len(set(felder)), f"{h['datei']}: zwei Plaetze auf einem Feld"
    for name, t in plaetze:
        assert t not in belegt, f"{h['datei']}: {name} auf Hex {t}, dort ist schon {belegt[t]}"
        assert t in erreichbar, f"{h['datei']}: {name} (Hex {t}) ist vom Start aus nicht erreichbar"
    aus = [o for _, o in k.alle_objekte() if o["kopf"]["tile"] == h["ausgang_hex"] and len(o["daten"]) >= 3]
    assert aus and h["stadtkarte_index"] in aus[0]["daten"][1:], f"{h['datei']}: Ausgang zeigt nicht zur Stadt"


def pruefe_eingang(stadt, db, h):
    """Eingang und Ankunft auf der Vanilla-Stadtkarte: frei, nicht unter einem Dach."""
    import struct
    kach = stadt.kacheln[0]

    def dach(t):
        sq = (t // 200 // 2) * 100 + (t % 200) // 2
        return ((struct.unpack(">I", kach[sq * 4:sq * 4 + 4])[0] >> 16) & 0xFFF) != 1
    belegt = {}
    for o in stadt.objekte[0]:
        if o["kopf"]["pid"] not in NICHT_BLOCKIEREND:
            belegt.setdefault(o["kopf"]["tile"], hex(o["kopf"]["pid"]))
    for name, t in (("Treppe", h["treppe_hex"]), ("Ankunft", h["ankunft_hex"])):
        assert t not in belegt, f"{h['stadtkarte']}: {name} {t} belegt ({belegt[t]})"
        assert not dach(t), f"{h['stadtkarte']}: {name} {t} liegt unter einem Dach"


def bauen(a):
    db = fomap.ProtoDB([a.protos] if a.protos else [])
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    karten = [(RLDEN01["datei"], baue_rlden01(a.karten, db, a.skript_basis, a.karten_index))]
    for i, h in enumerate(HAEUSER, 1):
        stadt = fomap.Karte.lesen((Path(a.karten) / f"{h['stadtkarte']}.map").read_bytes(), db)
        pruefe_eingang(stadt, db, h)
        karten.append((h["datei"], baue_haus(h, a.karten, db, a.skript_basis, a.karten_index + i)))
    for datei, k in karten:
        (out / datei).write_bytes(k.schreiben())
        anz = [l["anzahl"] for l in k.skripte]
        print(f"OK    {datei}: {len(k.objekte[0])} Objekte, Skripte je Typ {anz}, "
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
    # weitere Haeuser: Eingang auf der Stadtkarte und Innenkarte mit allen Plaetzen
    for h in HAEUSER:
        stadt = fomap.Karte.lesen((Path(a.karten) / f"{h['stadtkarte']}.map").read_bytes(), db)
        marken = [(h["treppe_hex"], f"Treppe {h['treppe_hex']}"), (h["ankunft_hex"], "Ankunft")]
        fb.zeichne(stadt, db, ziel / f"{h['kuerzel'].lower()}_eingang.png", 0, namen, mitte=h["treppe_hex"],
                   radius=16, massstab=1.2, markiere=marken)
        innen_pfad = Path(a.karte).parent / h["datei"]
        if innen_pfad.exists():
            innen = fomap.Karte.lesen(innen_pfad.read_bytes(), db)
            marken = [(h["ausgang_hex"], "Ausgang"), (h["eingang_hex"], "Start")] + \
                     [(t, n.title()) for n, t in h["plaetze"].items()]
            fb.zeichne(innen, db, ziel / f"{h['datei'][:-4]}.png", 0, namen, mitte=h["eingang_hex"],
                       radius=18, massstab=1.2, markiere=marken)
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
