#!/usr/bin/env python3
"""Eigene Szenerie im Paket: Grafiklisten, Prototypen, Texte und Kartenobjekte.

Quelle sind die fertigen Grafiken im Repository (grafik/frm/*.frm und
grafik/stuecke.json, erzeugt von tools/grafik/umwandeln.py) und der Katalog
tools/grafik/katalog.py (Namen, Texte, Material, Licht, Plaetze in der Gosse).

Jedes Stueck (ein FRM) bekommt
  - eine Zeile in art/scenery/scenery.lst:     FID = 0x02000000 | Zeile (ab 0)
  - einen Prototyp in proto/scenery/scenery.lst: PID = 0x02000000 | Zeile (ab 1),
    Datei proto/scenery/<stueck>.pro (der Name in der Liste ist frei waehlbar)
  - Titel und Beschreibung in pro_scen.msg unter Index * 100 und Index * 100 + 1.
Die Nummern haengen von der Laenge der Listen im installierten RPU ab (2.3.34 und
2.4.34 unterscheiden sich) und werden erst beim Packen vergeben.

Aufruf (Pruefung ohne Paket): python3 tools/szenerie.py
"""
import json
import re
import sys
from pathlib import Path

HIER = Path(__file__).resolve().parent
sys.path.insert(0, str(HIER / "grafik"))

import frm  # noqa: E402
import geometrie  # noqa: E402
import katalog  # noqa: E402

ROOT = HIER.parent
GRAFIK = ROOT / "grafik"
CRLF = b"\r\n"
TYP_SZENERIE = 0x02000000


class Fehler(Exception):
    pass


def lst_zeilen(daten):
    """Eintraege einer .lst-Datei, gezaehlt wie die Engine (eine Zeile je Eintrag)."""
    return daten.decode("cp1252").splitlines()


def anhaengen(basis, neu):
    if basis and not basis.endswith(b"\n"):
        basis += CRLF
    return basis + CRLF.join(z.encode("cp1252") for z in neu) + CRLF


def stuecke(grafik=GRAFIK):
    """Alle Stuecke in fester Reihenfolge (Katalog, dann Stuecknummer):
    [dict(name, datei, feld, frm)]. Liest jedes FRM und prueft es."""
    liste = json.loads((Path(grafik) / "stuecke.json").read_text())
    if set(liste) != set(katalog.OBJEKTE):
        raise Fehler(f"stuecke.json passt nicht zum Katalog: {sorted(set(liste) ^ set(katalog.OBJEKTE))}")
    aus, dateien = [], set()
    for name, obj in katalog.OBJEKTE.items():
        felder = {tuple(f) for f in obj["felder"]}
        belegt = set()
        for e in liste[name]["stuecke"]:
            datei, feld = e["datei"], tuple(e["feld"])
            if not re.fullmatch(r"[a-z0-9_]{1,8}", datei) or datei in dateien:
                raise Fehler(f"{name}: Dateiname {datei!r} ungueltig oder doppelt")
            if feld not in felder or feld in belegt:
                raise Fehler(f"{name}: Stueck {datei} auf Feld {feld} (nicht im Katalog oder doppelt)")
            dateien.add(datei)
            belegt.add(feld)
            daten = (Path(grafik) / "frm" / f"{datei}.frm").read_bytes()
            f = frm.Frm.lesen(daten)
            if f.schreiben() != daten:
                raise Fehler(f"{datei}.frm: Lesen und Schreiben nicht byte-gleich")
            if len(f.richtungen) != 1 or len(f.richtungen[0]) != 1:
                raise Fehler(f"{datei}.frm: erwartet eine Richtung mit einem Bild")
            b = f.richtungen[0][0]
            if b.breite * b.hoehe == 0 or not any(b.pixel):
                raise Fehler(f"{datei}.frm: leeres Bild")
            erlaubt = set(frm.FEST) | {0} | ({frm.ROT_PULS} if obj.get("leucht") else set())
            fremd = set(b.pixel) - erlaubt
            if fremd:
                raise Fehler(f"{datei}.frm: Farben ausserhalb der festen Palette: {sorted(fremd)[:8]}")
            aus.append(dict(name=name, datei=datei, feld=feld, frm=daten))
        blocker = {tuple(f) for f in liste[name]["blocker"]}
        if blocker != felder - belegt:
            raise Fehler(f"{name}: Blocker {sorted(blocker)} decken die freien Felder "
                         f"{sorted(felder - belegt)} nicht genau ab")
        # Mehrfeldrige Objekte sind fuer die Hex-Paritaet des ersten Platzes gerendert
        if len(felder) > 1:
            paritaet = obj["platz"][0] % 200 % 2
            for p in obj["platz"]:
                if p % 200 % 2 != paritaet:
                    raise Fehler(f"{name}: Platz {p} hat eine andere Spaltenparitaet als {obj['platz'][0]}")
    return aus


def einfuegen(art_lst, proto_lst, pro_scen, grafik=GRAFIK):
    """Listen und Texte eines RPU-Releases um unsere Stuecke erweitern.
    art_lst, proto_lst: Inhalt von art/scenery/scenery.lst und proto/scenery/scenery.lst.
    pro_scen: {sprache: Inhalt von text/<sprache>/game/pro_scen.msg}.
    Rueckgabe: (dateien {pfad im Mod-Ordner: bytes}, nummern {datei: (fid, pid)})."""
    teile = stuecke(grafik)
    art_n = len(lst_zeilen(art_lst))
    pro_n = len(lst_zeilen(proto_lst))
    if art_n + len(teile) > 0xFFF or pro_n + len(teile) > 0xFFFFFF:
        raise Fehler("Szenerielisten zu lang")
    namen_art = {z.strip().lower() for z in lst_zeilen(art_lst)}
    namen_pro = {z.strip().lower() for z in lst_zeilen(proto_lst)}
    dateien, nummern = {}, {}
    neue_art, neue_pro = [], []
    for i, t in enumerate(teile):
        if f"{t['datei']}.frm" in namen_art or f"{t['datei']}.pro" in namen_pro:
            raise Fehler(f"{t['datei']}: Name gibt es im RPU schon")
        fid = TYP_SZENERIE | (art_n + i)
        pid = TYP_SZENERIE | (pro_n + 1 + i)
        obj = katalog.OBJEKTE[t["name"]]
        weite, staerke = obj.get("licht", (0, 0))
        # Prototyp und Kartenobjekt mit denselben Flags
        flags = katalog.FLAGS_FLACH if obj.get("flach") else katalog.FLAGS_MOEBEL
        neue_art.append(f"{t['datei']}.frm")
        neue_pro.append(f"{t['datei']}.pro")
        dateien[f"art/scenery/{t['datei']}.frm"] = t["frm"]
        dateien[f"proto/scenery/{t['datei']}.pro"] = frm.szenerie_pro(
            pid, fid, obj["material"], weite, staerke, flags=flags)
        nummern[t["datei"]] = (fid, pid)
    dateien["art/scenery/scenery.lst"] = anhaengen(art_lst, neue_art)
    dateien["proto/scenery/scenery.lst"] = anhaengen(proto_lst, neue_pro)
    for sprache, basis in pro_scen.items():
        vorhanden = {int(m) for m in re.findall(rb"\{(\d+)\}\{", basis)}
        neu = []
        for t in teile:
            obj = katalog.OBJEKTE[t["name"]]
            n = (nummern[t["datei"]][1] & 0xFFFFFF) * 100
            for nr, text in ((n, obj["titel"]), (n + 1, obj["text"])):
                if nr in vorhanden:
                    raise Fehler(f"pro_scen.msg ({sprache}): Nummer {nr} gibt es schon")
                if not text.isascii() or "{" in text or "}" in text:
                    raise Fehler(f"{t['name']}: Text nicht reines ASCII oder mit Klammern")
                neu.append(f"{{{nr}}}{{}}{{{text}}}")
        dateien[f"text/{sprache}/game/pro_scen.msg"] = anhaengen(basis, neu)
    return dateien, nummern


def kartenobjekte(nummern, naechste_id, grafik=GRAFIK):
    """Objekte fuer die Gosse (Ebene 0): je Platz eines Katalogobjekts seine Stuecke
    und unsichtbare Blocker auf den uebrigen Feldern. Rueckgabe: Liste von Objekten
    im Format von fomap (kopf, inv, daten, inventar)."""
    liste = json.loads((Path(grafik) / "stuecke.json").read_text())
    objekte = []

    def neu(tile, pid, fid, flags, licht=(0, 0)):
        nonlocal naechste_id
        if flags >= 1 << 31:                 # Karten speichern Flags als int32 mit Vorzeichen
            flags -= 1 << 32
        kopf = dict(id=naechste_id, tile=tile, x=0, y=0, sx=0, sy=0, frame=0, rotation=0, fid=fid,
                    flags=flags, elevation=0, pid=pid, cid=-1, light_distance=licht[0],
                    light_intensity=licht[1], outline=0, sid=-1, script_index=-1)
        naechste_id += 1
        objekte.append({"kopf": kopf, "inv": [0, 0, 0], "daten": [0], "inventar": []})

    for name, obj in katalog.OBJEKTE.items():
        flags = katalog.FLAGS_FLACH if obj.get("flach") else katalog.FLAGS_MOEBEL
        for platz in obj["platz"]:
            for e in liste[name]["stuecke"]:
                fid, pid = nummern[e["datei"]]
                neu(geometrie.versatz(platz, *e["feld"]), pid, fid, flags, obj.get("licht", (0, 0)))
            for f in liste[name]["blocker"]:
                neu(geometrie.versatz(platz, *f), katalog.PID_BLOCKER, katalog.FID_BLOCKER, katalog.FLAGS_BLOCKER)
    return objekte


def pruefe_paket(mod, karte, protos_db, sprachen, grafik=GRAFIK):
    """Das fertige Paket gegenlesen, wie die Engine es liest: Grafikliste -> FRM,
    Prototypliste -> .pro (PID, FID, Textnummer), pro_scen.msg, Objekte auf der Karte.
    mod: Ordner mods/rotlicht, karte: Dateiname der Gosse. Rueckgabe: Anzahl Stuecke."""
    import fomap
    import struct
    mod = Path(mod)
    teile = stuecke(grafik)
    art = [z.strip().lower() for z in lst_zeilen((mod / "art/scenery/scenery.lst").read_bytes())]
    pro = [z.strip().lower() for z in lst_zeilen((mod / "proto/scenery/scenery.lst").read_bytes())]
    texte = {s: dict((int(a), b) for a, b in re.findall(
        r"\{(\d+)\}\{[^}]*\}\{([^}]*)\}", (mod / f"text/{s}/game/pro_scen.msg").read_bytes().decode("cp1252")))
        for s in sprachen}
    pids = {}
    for t in teile:
        name = f"{t['datei']}.pro"
        if pro.count(name) != 1:
            raise Fehler(f"{name}: {pro.count(name)}-mal in der Prototypliste")
        index = pro.index(name) + 1
        d = (mod / "proto/scenery" / name).read_bytes()
        pid, text_nr, fid = struct.unpack_from(">iii", d, 0)
        untertyp = struct.unpack_from(">i", d, 32)[0]
        if pid != TYP_SZENERIE | index or text_nr != index * 100 or untertyp != 5 or len(d) != 45:
            raise Fehler(f"{name}: PID {pid:#x}, Text {text_nr}, Untertyp {untertyp} passen nicht zu Zeile {index}")
        if not (fid >> 24 == 2 and art[fid & 0xFFF] == f"{t['datei']}.frm"):
            raise Fehler(f"{name}: FID {fid:#x} zeigt nicht auf {t['datei']}.frm")
        if (mod / "art/scenery" / f"{t['datei']}.frm").read_bytes() != t["frm"]:
            raise Fehler(f"{t['datei']}.frm im Paket weicht von grafik/frm ab")
        obj = katalog.OBJEKTE[t["name"]]
        for s in sprachen:
            if texte[s].get(text_nr) != obj["titel"] or texte[s].get(text_nr + 1) != obj["text"]:
                raise Fehler(f"pro_scen.msg ({s}): Text {text_nr} fuer {t['datei']} fehlt oder falsch")
        pids[pid] = (fid, t)
    k = fomap.Karte.lesen((mod / "maps" / karte).read_bytes(), protos_db)
    gesetzt = {}
    for _, o in k.alle_objekte():
        p = o["kopf"]["pid"]
        if p in pids:
            if o["kopf"]["fid"] != pids[p][0]:
                raise Fehler(f"Karte: Objekt {p:#x} hat FID {o['kopf']['fid']:#x}, Prototyp {pids[p][0]:#x}")
            gesetzt.setdefault(p, []).append(o["kopf"]["tile"])
    for p, (_, t) in pids.items():
        soll = sorted(geometrie.versatz(pl, *t["feld"]) for pl in katalog.OBJEKTE[t["name"]]["platz"])
        if sorted(gesetzt.get(p, [])) != soll:
            raise Fehler(f"Karte: {t['datei']} auf {sorted(gesetzt.get(p, []))}, erwartet {soll}")
    return len(teile)


def main():
    teile = stuecke()
    print(f"OK    {len(teile)} Stuecke aus {len(katalog.OBJEKTE)} Objekten gelesen und geprueft")
    # Probelauf mit kuenstlichen Listen
    art = CRLF.join(b"x%d.frm" % i for i in range(10))            # ohne letzten Zeilenumbruch
    pro = CRLF.join(b"%08d.pro" % i for i in range(1, 8)) + CRLF
    msg = b"{700}{}{Alt}\r\n"
    dateien, nummern = einfuegen(art, pro, {"english": msg})
    assert len(lst_zeilen(dateien["art/scenery/scenery.lst"])) == 10 + len(teile)
    assert len(lst_zeilen(dateien["proto/scenery/scenery.lst"])) == 7 + len(teile)
    erst = teile[0]["datei"]
    assert nummern[erst] == (TYP_SZENERIE | 10, TYP_SZENERIE | 8)
    assert lst_zeilen(dateien["art/scenery/scenery.lst"])[10] == f"{erst}.frm"
    assert lst_zeilen(dateien["proto/scenery/scenery.lst"])[7] == f"{erst}.pro"
    assert b"{800}{}{" in dateien["text/english/game/pro_scen.msg"]
    objekte = kartenobjekte(nummern, 1000)
    hexe = [o["kopf"]["tile"] for o in objekte if o["kopf"]["pid"] != katalog.PID_BLOCKER]
    print(f"OK    Listen, Prototypen, Texte; {len(objekte)} Kartenobjekte auf {len(set(hexe))} Feldern")


if __name__ == "__main__":
    try:
        main()
    except Fehler as e:
        sys.exit(f"FEHLER {e}")
