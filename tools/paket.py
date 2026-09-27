#!/usr/bin/env python3
"""Packt einen Build als sfall-Mod-Ordner mods/rotlicht zum Testen im Spiel.

Das Restoration Project (RPU) liegt in mods/rpu.dat und mods/rpu_<sprache>.dat.
Darin stecken auch die Systemdateien, in die das Addon Zeilen einfuegt
(scripts.lst, vault13.gam, maps.txt, city.txt, endgame.txt, karmavar.txt,
map.msg, editor.msg). Ein Mod-Ordner, der in mods_order.txt nach diesen
Archiven steht, ueberschreibt sie. Darum enthaelt das Paket vollstaendige
Kopien aus genau dem RPU-Release, das installiert ist, mit unseren Zeilen.

Das Werkzeug liest die Dateien aus einem Klon des RPU-Repositorys (git show
<release>:...), prueft die Zaehlungen gegen die Build-Einstellungen, fuegt
die Zeilen aus install/ ein und baut die Innenkarte aus der Vorlage desselben
Releases (die Vorlagen unterscheiden sich zwischen 2.3 und 2.4).

Aufruf (vorher tools/build_scripts.sh mit denselben Basen):
  python3 tools/paket.py --rpu /pfad/rpu-klon --release v2.4.34 [--build build]
                         [--out build/paket] [--sprache german]
"""
import argparse
import re
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

import bau_karten
import fomap

ROOT = Path(__file__).resolve().parent.parent
MOD = "rotlicht"
CRLF = b"\r\n"


class Fehler(Exception):
    pass


# ------------------------------------------------------------------ RPU-Dateien
class Release:
    """Dateien eines RPU-Releases aus dem Git-Klon, in der Kodierung des Spiels."""

    def __init__(self, klon, ref):
        self.klon, self.ref = Path(klon), ref
        self.kodierung = {}
        for zeile in self._git(".gitattributes").decode().splitlines():
            m = re.match(r"(data/text/\w+)/\*\*\s+working-tree-encoding=(\S+)", zeile)
            if m:
                self.kodierung[m.group(1)] = m.group(2)

    def _git(self, pfad):
        r = subprocess.run(["git", "-C", str(self.klon), "show", f"{self.ref}:{pfad}"],
                           capture_output=True)
        if r.returncode:
            raise Fehler(f"{pfad} fehlt in {self.ref}: {r.stderr.decode().strip()}")
        return r.stdout

    def datei(self, pfad):
        """Inhalt wie im Spiel: Texte in der Kodierung aus .gitattributes (Git speichert UTF-8)."""
        daten = self._git(pfad)
        for praefix, kod in self.kodierung.items():
            if pfad.startswith(praefix + "/"):
                return daten.decode("utf-8").encode(kod)
        return daten


def zeilen(daten):
    return daten.decode("cp1252").splitlines()


def anhaengen(basis, neu):
    """Zeilen anhaengen. Fehlt der Basis der letzte Zeilenumbruch (wie bei
    scripts.lst im RPU), wuerde die erste neue Zeile sonst angeklebt."""
    if basis and not basis.endswith(b"\n"):
        basis += CRLF
    return basis + CRLF.join(z.encode("cp1252") for z in neu) + CRLF


def add_datei(name):
    return (ROOT / "install" / name).read_text(encoding="utf-8").splitlines()


# ------------------------------------------------------------------ Einfuegen
def scripts_lst(basis, skript_basis):
    n = len(zeilen(basis))
    if n != skript_basis - 1:
        raise Fehler(f"scripts.lst hat {n} Zeilen, der Build erwartet {skript_basis - 1} "
                     f"(RL_SCRIPT_BASE={skript_basis}). Mit RL_SCRIPT_BASE={n + 1} neu bauen.")
    return anhaengen(basis, [z for z in add_datei("scripts.lst.add") if z.strip()])


def vault13_gam(basis, gvar_basis):
    n = sum(1 for z in zeilen(basis) if ":=" in z and not z.lstrip().startswith("//"))
    if n != gvar_basis:
        raise Fehler(f"vault13.gam hat {n} GVARs, der Build erwartet {gvar_basis} "
                     f"(RL_GVAR_BASE). Mit RL_GVAR_BASE={n} neu bauen.")
    return anhaengen(basis, [z for z in add_datei("vault13.gam.add") if z.strip()])


def maps_txt(basis, karten_index):
    n = sum(1 for z in zeilen(basis) if re.match(r"\[Map \d+\]", z))
    if n != karten_index:
        raise Fehler(f"maps.txt hat {n} Karten, der Build erwartet Nummer {karten_index} "
                     f"fuer die Gosse. Mit RL_MAP_INDEX={n} neu bauen.")
    neu = ["; Rotlicht ueber dem Oedland: Innenkarte der Gosse"]
    neu += [f"[Map {karten_index:03d}]" if z.startswith("[Map ") else z
            for z in add_datei("maps.txt.add") if z.strip() and not z.startswith(";")]
    return anhaengen(basis, [""] + neu)


def city_txt(basis):
    """Eingang ohne Koordinaten im Abschnitt der Den, mit der naechsten freien Nummer."""
    z = zeilen(basis)
    start = next((i for i, l in enumerate(z) if l.strip() == "area_name=Den"), None)
    if start is None:
        raise Fehler("city.txt: Abschnitt area_name=Den nicht gefunden")
    ende = next((i for i in range(start + 1, len(z)) if z[i].startswith("[")), len(z))
    eingaenge = [i for i in range(start, ende) if re.match(r"entrance_\d+=", z[i])]
    naechste = max(int(re.match(r"entrance_(\d+)", z[i]).group(1)) for i in eingaenge) + 1
    vorlage = next(l for l in add_datei("city.txt.add") if l.startswith("entrance_"))
    z.insert(eingaenge[-1] + 1, re.sub(r"entrance_\d+", f"entrance_{naechste}", vorlage))
    return CRLF.join(l.encode("cp1252") for l in z) + CRLF


def gvar_verschieben(zeile, gvar_basis):
    """Erste Zahl (GVAR 791 ...) auf die tatsaechliche GVAR-Basis umrechnen."""
    m = re.match(r"(\d+)(.*)", zeile)
    return f"{int(m.group(1)) - 791 + gvar_basis}{m.group(2)}" if m else zeile


def endgame_txt(basis, gvar_basis):
    """Unsere Slides nach dem New-Reno-Block (letzte Zeile mit GVAR 412)."""
    z = zeilen(basis)
    letzte = max((i for i, l in enumerate(z) if l.startswith("412,")), default=None)
    if letzte is None:
        raise Fehler("endgame.txt: New-Reno-Block (412, ...) nicht gefunden")
    neu = ["#####", "# Rotlicht ueber dem Oedland", "#####"]
    neu += [gvar_verschieben(l, gvar_basis) for l in add_datei("endgame.txt.add")
            if l.strip() and not l.startswith("#")]
    z[letzte + 1:letzte + 1] = neu
    return CRLF.join(l.encode("cp1252") for l in z) + CRLF


def karmavar_txt(basis, gvar_basis):
    neu = [gvar_verschieben(l, gvar_basis) if not l.startswith("#") else l
           for l in add_datei("karmavar.txt.add")]
    return anhaengen(basis, [""] + neu)


def msg_anhaengen(basis, add_pfad, umnummern=None):
    """Zeilen {n}{}{text} anhaengen; vorhandene Nummern sind ein Fehler."""
    vorhanden = {int(m) for m in re.findall(rb"\{(\d+)\}\{", basis)}
    neu = []
    for l in add_pfad.read_bytes().decode("cp1252").splitlines():
        m = re.match(r"\{(\d+)\}(.*)", l)
        if not m:
            continue
        n = umnummern(int(m.group(1))) if umnummern else int(m.group(1))
        if n in vorhanden:
            raise Fehler(f"{add_pfad.name}: Nummer {n} gibt es schon")
        neu.append(f"{{{n}}}{m.group(2)}")
    return anhaengen(basis, neu)


# ------------------------------------------------------------------ Paket
def build_info(build):
    """Einstellungen, mit denen tools/build_scripts.sh gebaut hat."""
    p = Path(build) / "scripts" / "rl_build.txt"
    if not p.exists():
        raise Fehler(f"{p} fehlt: zuerst tools/build_scripts.sh laufen lassen")
    return dict(l.split("=", 1) for l in p.read_text().split())


def packen(a):
    info = build_info(a.build)
    sb, gb, ki = int(info["RL_SCRIPT_BASE"]), int(info["RL_GVAR_BASE"]), int(info["RL_MAP_INDEX"])
    debug = info.get("RL_DEBUG") == "1"
    rel = Release(a.rpu, a.release)
    sprache = a.sprache
    build = Path(a.build)

    ziel = Path(a.out) / f"rpu-{a.release}"
    if ziel.exists():
        shutil.rmtree(ziel)
    mod = ziel / "mods" / MOD
    dateien = {}

    # Systemdateien mit unseren Zeilen
    dateien["scripts/scripts.lst"] = scripts_lst(rel.datei("data/scripts/scripts.lst"), sb)
    dateien["data/vault13.gam"] = vault13_gam(rel.datei("data/data/vault13.gam"), gb)
    dateien["data/maps.txt"] = maps_txt(rel.datei("data/data/maps.txt"), ki)
    dateien["data/city.txt"] = city_txt(rel.datei("data/data/city.txt"))
    dateien["data/endgame.txt"] = endgame_txt(rel.datei("data/data/endgame.txt"), gb)
    dateien["data/karmavar.txt"] = karmavar_txt(rel.datei("data/data/karmavar.txt"), gb)
    txt = build / "text" / sprache / "game"
    dateien[f"text/{sprache}/game/map.msg"] = msg_anhaengen(
        rel.datei(f"data/text/{sprache}/game/map.msg"), txt / "map.msg.add",
        lambda n: n - 719 + 200 + 3 * ki)
    dateien[f"text/{sprache}/game/editor.msg"] = msg_anhaengen(
        rel.datei(f"data/text/{sprache}/game/editor.msg"), txt / "editor.msg.add")

    # Innenkarte aus der Vorlage desselben Releases
    with tempfile.TemporaryDirectory() as tmp:
        vorlage = Path(tmp) / f"{bau_karten.RLDEN01['vorlage']}.map"
        vorlage.write_bytes(rel.datei(f"data/maps/{vorlage.name}"))
        karte = bau_karten.baue_rlden01(tmp, fomap.ProtoDB(), sb, ki)
    dateien[f"maps/{bau_karten.RLDEN01['datei']}"] = karte.schreiben()

    # Skripte und Texte aus dem Build
    noetig = {"gl_rotlicht.int"} | {z.split()[0].lower() for z in add_datei("scripts.lst.add") if z.strip()}
    fehlend = sorted(n for n in noetig if not (build / "scripts" / n).exists())
    if fehlend:
        raise Fehler(f"im Build fehlen {', '.join(fehlend)}: tools/build_scripts.sh meldet warum")
    for p in sorted((build / "scripts").glob("*.int")):
        dateien[f"scripts/{p.name}"] = p.read_bytes()
    for p in sorted((build / "text" / sprache / "dialog").glob("*.msg")):
        dateien[f"text/{sprache}/dialog/{p.name}"] = p.read_bytes()
    for p in sorted((build / "text" / sprache / "cuts").glob("*.txt")):
        for ordner in ("cuts", "cuts_female"):   # Untertitel auch fuer Spielerinnen
            dateien[f"text/{sprache}/{ordner}/{p.name}"] = p.read_bytes()

    for pfad, daten in dateien.items():
        (mod / pfad).parent.mkdir(parents=True, exist_ok=True)
        (mod / pfad).write_bytes(daten)
    anleitung = ziel / "ANLEITUNG.txt"
    anleitung.write_bytes(b"\xef\xbb\xbf" + anleitungstext(a.release, sb, gb, ki, debug).replace("\n", "\r\n").encode("utf-8"))

    zip_pfad = Path(a.out) / f"rotlicht_test_rpu-{a.release}.zip"
    with zipfile.ZipFile(zip_pfad, "w", zipfile.ZIP_DEFLATED) as z:
        for p in sorted(ziel.rglob("*")):
            if p.is_file():
                z.write(p, p.relative_to(ziel).as_posix())
    print(f"OK    {zip_pfad.relative_to(ROOT) if zip_pfad.is_relative_to(ROOT) else zip_pfad}: "
          f"{len(dateien) + 1} Dateien, RPU {a.release}, Basen {sb}/{gb}/{ki}, Debug {'an' if debug else 'aus'}")


def anleitungstext(release, sb, gb, ki, debug):
    tasten = """
DEBUG-TASTEN
  F11  von überall direkt in die Gosse
  F8   auf Den Business 2 neben die Kellertreppe (nur dort)
  F9   Essie und Kolbe erscheinen neben dir (Notlösung ohne Karte)
  F12  Bildschirmfoto (Spiel), landet im Fallout-2-Ordner als SCR*.BMP
""" if debug else ""
    return f"""Rotlicht über dem Ödland – Testpaket
=====================================

Für: Fallout 2 Restoration Project {release}, deutsche Texte
Build: Skriptbasis {sb}, GVAR-Basis {gb}, Kartennummer der Gosse {ki}{", mit Debug-Tasten" if debug else ""}

WICHTIG
- Das Paket passt nur zu RPU {release}. Die Version steht im Namen des
  Installers, den du benutzt hast (z. B. rpu_{release}.exe).
- Neues Spiel nötig: Das Addon fügt fünf globale Variablen hinzu. Alte
  Spielstände laden damit nicht richtig. Sichere vorher den Ordner
  data\\SAVEGAME. Spielstände aus dem Test laden später nur mit dem Addon.

INSTALLIEREN
1. Den Ordner  mods\\rotlicht  aus diesem Paket nach  <Fallout 2>\\mods\\  kopieren.
2. <Fallout 2>\\mods\\mods_order.txt  im Editor öffnen und als LETZTE Zeile
   eintragen:
       rotlicht
3. Spiel starten und ein neues Spiel beginnen.

ENTFERNEN
Die Zeile  rotlicht  in mods_order.txt löschen (oder ein ; davorsetzen).
Danach wieder die alten Spielstände benutzen.
{tasten}
WAS PRÜFEN (ausführlich: docs/umsetzung-2-die-gosse.md, Abschnitt 5)
Den Business 2 (Ruine zwischen Sklavengilde und Mom's Diner):
  1. Steht die Kellertreppe sauber in der Ruine (nicht in einer Wand, nicht
     halb im Schutt)?
  2. Maus darüber: "Eine Treppe führt unter die Ruine."
  3. Benutzen: Du landest in der Gosse.
Die Gosse:
  4. Gedämpftes Licht, beim ersten Mal ein Satz zur Stimmung.
  5. Wo Beckys Destille stand: nichts Schwebendes, kein Schatten ohne Objekt.
  6. Essie am Tisch, Kolbe an der Tür zum hinteren Raum. Beide ansprechbar,
     der Prolog läuft.
  7. Holztür zum hinteren Raum lässt sich öffnen.
  8. Treppe nach oben: zurück in die Den, direkt neben die Kellertreppe.
  9. Speichern und Laden in der Gosse, der Spielstand heißt "Die Gosse".
 10. Umlaute (ä, ö, ü, ß) in den Texten richtig?

WENN ETWAS NICHT GEHT
- Keine Treppe in der Ruine, F11 tut nichts: Steht  rotlicht  wirklich als
  LETZTE Zeile in mods_order.txt? (Braucht sfall 4.4 oder neuer; das
  aktuelle RPU bringt es mit.)
- Absturz oder Unsinn beim Laden: War es ein alter Spielstand? Dann ein
  neues Spiel beginnen.
- Statt Text steht "Error": Datei unter mods\rotlicht\text\german fehlt.

RÜCKMELDUNG
Was stimmt nicht und wo. Am besten mit Bildschirmfoto (F12).
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rpu", required=True, help="Klon des RPU-Repositorys")
    ap.add_argument("--release", required=True, help="Release-Tag, z. B. v2.4.34")
    ap.add_argument("--build", default=str(ROOT / "build"))
    ap.add_argument("--out", default=str(ROOT / "build" / "paket"))
    ap.add_argument("--sprache", default="german")
    a = ap.parse_args()
    try:
        packen(a)
    except Fehler as e:
        print(f"FEHLER {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
