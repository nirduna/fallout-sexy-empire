#!/usr/bin/env python3
"""Lesen und Schreiben von Fallout-2-Karten (.MAP, Version 20).

Das Format ist aus dem Quellcode von fallout2-ce abgeleitet
(map.cc: mapHeaderRead/_square_load, scripts.cc: scriptRead/scriptLoadAll,
object.cc: objectRead/objectLoadAllInternal, proto.cc: objectDataRead).
Alle Zahlen sind 32-Bit big-endian.

Aufbau einer Karte:
  Kopf (236 Byte) · globale Kartenvariablen · lokale Kartenvariablen ·
  Bodenkacheln je vorhandener Ebene (10000 x int32) ·
  5 Skriptlisten (System, Spatial, Timed, Item, Critter) in Bloecken zu 16 ·
  Objekte je Ebene, jeweils mit Inventar (rekursiv).

Die Laenge der Objektdaten haengt bei Gegenstaenden und Szenerie vom Untertyp
im Proto ab. Protos, die nicht vorliegen, werden durch Ausprobieren mit
Plausibilitaetspruefung und Rueckverfolgung bestimmt; das Ergebnis muss die
Datei exakt bis zum Ende erklaeren und byte-gleich zurueckschreiben.

Aufruf:
  python3 tools/fomap.py pruefen <karten...> [--protos DIR]   Round-Trip-Test
  python3 tools/fomap.py info <karte> [--protos DIR]          Kurzuebersicht
"""
import json
import struct
import sys
from pathlib import Path

# Objekttypen (PID_TYPE)
T_ITEM, T_CRITTER, T_SCENERY, T_WALL, T_TILE, T_MISC = range(6)
# Zusatzdaten je Untertyp (Anzahl int32), siehe proto.cc objectDataRead
ITEM_EXTRA = {0: 0, 1: 0, 2: 0, 3: 2, 4: 1, 5: 1, 6: 1}       # Ruestung, Behaelter, Droge, Waffe, Munition, Sonstiges, Schluessel
SCENERY_EXTRA = {0: 1, 1: 2, 2: 2, 3: 2, 4: 2, 5: 0}          # Tuer, Treppe, Aufzug, Leiter hoch, Leiter runter, generisch
EXIT_GRID_PIDS = range(0x5000010, 0x5000018)
PID_SCROLL_BLOCKER = 0x500000C
ELEV_FLAGS = (2, 4, 8)
SCRIPT_TYPES = 5
KOPF_FELDER = ["version", "name", "entering_tile", "entering_elevation", "entering_rotation",
               "local_vars", "script_index", "flags", "darkness", "global_vars", "index", "last_visit"]
OBJ_FELDER = ["id", "tile", "x", "y", "sx", "sy", "frame", "rotation", "fid", "flags",
              "elevation", "pid", "cid", "light_distance", "light_intensity", "outline", "sid", "script_index"]
CACHE = Path(__file__).resolve().parent / "data" / "proto_extra.json"


class Ungueltig(Exception):
    """Daten passen nicht: falsche Annahme ueber einen Untertyp."""


class Unbekannt(Exception):
    def __init__(self, pid):
        super().__init__(f"unbekannter Untertyp fuer PID {pid:#x}")
        self.pid = pid


def pid_typ(pid):
    return (pid >> 24) & 0xFF


class Leser:
    def __init__(self, daten, pos=0):
        self.d = daten
        self.pos = pos

    def i32(self):
        if self.pos + 4 > len(self.d):
            raise Ungueltig("Dateiende")
        (v,) = struct.unpack_from(">i", self.d, self.pos)
        self.pos += 4
        return v

    def i32s(self, n):
        if self.pos + 4 * n > len(self.d):
            raise Ungueltig("Dateiende")
        v = list(struct.unpack_from(f">{n}i", self.d, self.pos))
        self.pos += 4 * n
        return v

    def roh(self, n):
        if self.pos + n > len(self.d):
            raise Ungueltig("Dateiende")
        v = self.d[self.pos:self.pos + n]
        self.pos += n
        return v


class ProtoDB:
    """Untertypen von Gegenstaenden und Szenerie: aus .pro-Dateien und gelernt."""

    def __init__(self, verzeichnisse=()):
        self.extra = {}                      # pid -> Anzahl int32 Zusatzdaten
        self.quelle = {}                     # pid -> "proto" | "gelernt"
        if CACHE.exists():
            for k, v in json.loads(CACHE.read_text()).items():
                self.extra[int(k, 16)] = v
                self.quelle[int(k, 16)] = "gelernt"
        for vz in verzeichnisse:
            self._lade(Path(vz))

    def _lade(self, vz):
        for art, typ, tabelle in (("items", T_ITEM, ITEM_EXTRA), ("scenery", T_SCENERY, SCENERY_EXTRA)):
            for pro in (vz / art).glob("*.pro"):
                d = pro.read_bytes()
                if len(d) < 36:
                    continue
                pid, untertyp = struct.unpack_from(">i", d, 0)[0], struct.unpack_from(">i", d, 32)[0]
                if pid_typ(pid) == typ and untertyp in tabelle:
                    self.extra[pid] = tabelle[untertyp]
                    self.quelle[pid] = "proto"

    def speichere_gelerntes(self):
        CACHE.parent.mkdir(parents=True, exist_ok=True)
        gelernt = {f"{p:#x}": v for p, v in sorted(self.extra.items()) if self.quelle.get(p) == "gelernt"}
        CACHE.write_text(json.dumps(gelernt, indent=1, sort_keys=True) + "\n")


class Karte:
    def __init__(self):
        self.kopf = {}
        self.kopf_rest = []                  # field_3C[44]
        self.gvars = []
        self.lvars = []
        self.kacheln = {}                    # Ebene -> bytes (40000)
        self.skripte = []                    # 5 Listen: {"anzahl", "bloecke": [{"saetze": [[int]], "laenge", "next"}]}
        self.objekte_gesamt = 0
        self.objekte = [[], [], []]          # je Ebene: Liste von Objekten

    # ------------------------------------------------------------ Lesen
    @classmethod
    def lesen(cls, daten, protos):
        k = cls()
        r = Leser(daten)
        v = r.i32s(1)[0]
        name = r.roh(16)
        rest = r.i32s(10)
        k.kopf = dict(zip(KOPF_FELDER, [v, name] + rest))
        k.kopf_rest = r.i32s(44)
        if v != 20:
            raise ValueError(f"Kartenversion {v} wird nicht unterstuetzt")
        k.gvars = r.i32s(max(0, k.kopf["global_vars"]))
        k.lvars = r.i32s(max(0, k.kopf["local_vars"]))
        for e in range(3):
            if (k.kopf["flags"] & ELEV_FLAGS[e]) == 0:
                k.kacheln[e] = r.roh(40000)
        for _ in range(SCRIPT_TYPES):
            anzahl = r.i32()
            liste = {"anzahl": anzahl, "bloecke": []}
            for _ in range((anzahl + 15) // 16 if anzahl else 0):
                saetze = []
                for _ in range(16):
                    sid, f4 = r.i32(), r.i32()
                    typ = (sid >> 24) & 0xFF
                    extra = 2 if typ == 1 else 1 if typ == 2 else 0
                    saetze.append([sid, f4] + r.i32s(extra + 14))
                liste["bloecke"].append({"saetze": saetze, "laenge": r.i32(), "next": r.i32()})
            k.skripte.append(liste)
        start = r.pos
        k._objekte_lesen(daten, start, protos)
        return k

    def _objekte_lesen(self, daten, start, protos):
        annahmen = {}
        entscheidungen = []                  # [(pid, verbleibende Kandidaten)]
        while True:
            try:
                r = Leser(daten, start)
                gesamt = r.i32()
                ebenen = []
                for _ in range(3):
                    n = r.i32()
                    if not 0 <= n <= 20000:
                        raise Ungueltig("Objektanzahl")
                    ebenen.append([self._objekt(r, protos, annahmen, True) for _ in range(n)])
                if r.pos != len(daten):
                    raise Ungueltig(f"{len(daten) - r.pos} Byte uebrig")
                self.objekte_gesamt, self.objekte = gesamt, ebenen
                for pid, v in annahmen.items():
                    if pid not in protos.extra:
                        protos.extra[pid] = v
                        protos.quelle[pid] = "gelernt"
                return
            except Unbekannt as u:
                kandidaten = [0, 1, 2]
                annahmen[u.pid] = kandidaten.pop(0)
                entscheidungen.append((u.pid, kandidaten))
            except Ungueltig:
                while entscheidungen and not entscheidungen[-1][1]:
                    pid, _ = entscheidungen.pop()
                    del annahmen[pid]
                if not entscheidungen:
                    raise
                pid, rest = entscheidungen[-1]
                annahmen[pid] = rest.pop(0)

    def _objekt(self, r, protos, annahmen, oben):
        kopf = dict(zip(OBJ_FELDER, r.i32s(18)))
        pid, typ = kopf["pid"], pid_typ(kopf["pid"])
        if typ > T_MISC or not -1 <= kopf["tile"] < 40000 or not 0 <= kopf["rotation"] <= 5:
            raise Ungueltig("Objektkopf")
        if oben and not 0 <= kopf["elevation"] <= 2:
            raise Ungueltig("Ebene")
        inv_len, inv_kap, inv_ptr = r.i32s(3)
        if not 0 <= inv_len <= 5000 or inv_kap < inv_len:
            raise Ungueltig("Inventar")
        if typ == T_CRITTER:
            daten = r.i32s(11)
        else:
            if typ in (T_ITEM, T_SCENERY):
                extra = protos.extra.get(pid, annahmen.get(pid))
                if extra is None:
                    raise Unbekannt(pid)
            elif typ == T_MISC and pid in EXIT_GRID_PIDS:
                extra = 4
            else:
                extra = 0
            daten = r.i32s(1 + extra)
        inventar = []
        for _ in range(inv_len):
            menge = r.i32()
            if menge < 0:
                raise Ungueltig("Menge")
            inventar.append((menge, self._objekt(r, protos, annahmen, False)))
        return {"kopf": kopf, "inv": [inv_len, inv_kap, inv_ptr], "daten": daten, "inventar": inventar}

    # ------------------------------------------------------------ Schreiben
    def schreiben(self):
        out = bytearray()
        w = lambda *vs: out.extend(struct.pack(f">{len(vs)}i", *vs))
        kk = self.kopf
        w(kk["version"])
        out.extend(kk["name"])
        w(*[kk[f] for f in KOPF_FELDER[2:]])
        w(*self.kopf_rest)
        if self.gvars:
            w(*self.gvars)
        if self.lvars:
            w(*self.lvars)
        for e in range(3):
            if e in self.kacheln:
                out.extend(self.kacheln[e])
        for liste in self.skripte:
            w(liste["anzahl"])
            for b in liste["bloecke"]:
                for s in b["saetze"]:
                    w(*s)
                w(b["laenge"], b["next"])
        w(self.objekte_gesamt)
        for ebene in self.objekte:
            w(len(ebene))
            for o in ebene:
                self._objekt_schreiben(o, w)
        return bytes(out)

    def _objekt_schreiben(self, o, w):
        w(*[o["kopf"][f] for f in OBJ_FELDER])
        w(*o["inv"])
        w(*o["daten"])
        for menge, item in o["inventar"]:
            w(menge)
            self._objekt_schreiben(item, w)

    # ------------------------------------------------------------ Hilfen
    def alle_objekte(self):
        for e, ebene in enumerate(self.objekte):
            for o in ebene:
                yield e, o

    def skript_saetze(self):
        """Alle belegten Skriptsaetze: (typ, satz)."""
        for typ, liste in enumerate(self.skripte):
            n = liste["anzahl"]
            for b in liste["bloecke"]:
                for s in b["saetze"][:min(16, n)]:
                    yield typ, s
                n -= 16


def skript_index(satz):
    """Skriptindex eines Satzes (Position von 'index' haengt vom Typ ab)."""
    typ = (satz[0] >> 24) & 0xFF
    extra = 2 if typ == 1 else 1 if typ == 2 else 0
    return satz[2 + extra + 1]


def skript_besitzer(satz):
    """Objekt-ID, der der Skriptsatz gehoert (ownerId)."""
    typ = (satz[0] >> 24) & 0xFF
    extra = 2 if typ == 1 else 1 if typ == 2 else 0
    return satz[2 + extra + 3]


def main():
    args = sys.argv[1:]
    protos_dirs = []
    if "--protos" in args:
        i = args.index("--protos")
        protos_dirs = [args[i + 1]]
        del args[i:i + 2]
    if not args:
        print(__doc__)
        return 1
    befehl, dateien = args[0], args[1:]
    db = ProtoDB(protos_dirs)
    if befehl == "pruefen":
        fehler = 0
        for f in dateien:
            daten = Path(f).read_bytes()
            try:
                k = Karte.lesen(daten, db)
                ok = k.schreiben() == daten
            except Exception as e:  # noqa: BLE001 - Pruefwerkzeug, alles melden
                ok, k = False, None
                print(f"FEHLER {Path(f).name}: {e}")
            if k is not None and not ok:
                print(f"FEHLER {Path(f).name}: Round-Trip nicht byte-gleich")
            fehler += not ok
        db.speichere_gelerntes()
        gelernt = sum(1 for q in db.quelle.values() if q == "gelernt")
        print(f"{len(dateien) - fehler}/{len(dateien)} Karten byte-gleich; {gelernt} Untertypen gelernt")
        return 1 if fehler else 0
    if befehl == "info":
        k = Karte.lesen(Path(dateien[0]).read_bytes(), db)
        print({f: k.kopf[f] for f in KOPF_FELDER if f != "name"}, k.kopf["name"].split(b"\0")[0])
        print("Ebenen mit Kacheln:", sorted(k.kacheln), "Objekte je Ebene:", [len(e) for e in k.objekte])
        print("Skripte je Typ:", [l["anzahl"] for l in k.skripte])
        return 0
    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main())
