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
                         [--out build/paket] [--sprachen english]

Die Spieltexte des Addons sind englisch (reines ASCII). Sie landen in jedem
Sprachordner aus --sprachen, standardmaessig nur in text/english.
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
    """Unsere Karten ans Ende, fortlaufend ab der naechsten freien Nummer."""
    n = sum(1 for z in zeilen(basis) if re.match(r"\[Map \d+\]", z))
    if n != karten_index:
        raise Fehler(f"maps.txt hat {n} Karten, der Build erwartet Nummer {karten_index} "
                     f"fuer die Gosse. Mit RL_MAP_INDEX={n} neu bauen.")
    neu = ["; Rotlicht ueber dem Oedland: Innenkarten der Haeuser"]
    nr = karten_index
    for z in add_datei("maps.txt.add"):
        if z.startswith(";"):
            continue
        if z.startswith("[Map "):
            neu.append(f"[Map {nr:03d}]")
            nr += 1
        else:
            neu.append(z)
    return anhaengen(basis, [""] + neu)


def city_txt(basis):
    """Je Haus ein Eingang ohne Koordinaten im Abschnitt seiner Stadt, mit der
    naechsten freien Nummer (Zeilen "area_name|entrance_N=..." in city.txt.add)."""
    z = zeilen(basis)
    for zeile in add_datei("city.txt.add"):
        if zeile.startswith(";") or "|" not in zeile:
            continue
        gebiet, vorlage = zeile.split("|", 1)
        start = next((i for i, l in enumerate(z) if l.strip() == f"area_name={gebiet}"), None)
        if start is None:
            raise Fehler(f"city.txt: Abschnitt area_name={gebiet} nicht gefunden")
        ende = next((i for i in range(start + 1, len(z)) if z[i].startswith("[")), len(z))
        eingaenge = [i for i in range(start, ende) if re.match(r"entrance_\d+=", z[i])]
        naechste = max(int(re.match(r"entrance_(\d+)", z[i]).group(1)) for i in eingaenge) + 1
        z.insert(eingaenge[-1] + 1, re.sub(r"entrance_\d+", f"entrance_{naechste}", vorlage.strip()))
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
    sprachen = [x.strip() for x in a.sprachen.split(",") if x.strip()]
    build = Path(a.build)
    txt = build / "text" / "english"          # Quelle: der Build

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
    for sprache in sprachen:
        dateien[f"text/{sprache}/game/map.msg"] = msg_anhaengen(
            rel.datei(f"data/text/{sprache}/game/map.msg"), txt / "game" / "map.msg.add",
            lambda n: n - 719 + 200 + 3 * ki)
        dateien[f"text/{sprache}/game/editor.msg"] = msg_anhaengen(
            rel.datei(f"data/text/{sprache}/game/editor.msg"), txt / "game" / "editor.msg.add")
        dateien[f"text/{sprache}/game/rotlicht.msg"] = (txt / "game" / "rotlicht.msg").read_bytes()

    # Innenkarten aus den Vorlagen desselben Releases, Eingaenge gegen dessen Stadtkarten geprueft
    with tempfile.TemporaryDirectory() as tmp:
        noetig_karten = {bau_karten.RLDEN01["vorlage"]} | {h["vorlage"] for h in bau_karten.HAEUSER} \
            | {h["stadtkarte"] for h in bau_karten.HAEUSER}
        for name in noetig_karten:
            (Path(tmp) / f"{name}.map").write_bytes(rel.datei(f"data/maps/{name}.map"))
        db = fomap.ProtoDB()
        dateien[f"maps/{bau_karten.RLDEN01['datei']}"] = bau_karten.baue_rlden01(tmp, db, sb, ki).schreiben()
        for i, h in enumerate(bau_karten.HAEUSER, 1):
            stadt = fomap.Karte.lesen((Path(tmp) / f"{h['stadtkarte']}.map").read_bytes(), db)
            bau_karten.pruefe_eingang(stadt, db, h)
            dateien[f"maps/{h['datei']}"] = bau_karten.baue_haus(h, tmp, db, sb, ki + i).schreiben()

    # Skripte und Texte aus dem Build
    noetig = {"gl_rotlicht.int"} | {z.split()[0].lower() for z in add_datei("scripts.lst.add") if z.strip()}
    fehlend = sorted(n for n in noetig if not (build / "scripts" / n).exists())
    if fehlend:
        raise Fehler(f"im Build fehlen {', '.join(fehlend)}: tools/build_scripts.sh meldet warum")
    for p in sorted((build / "scripts").glob("*.int")):
        dateien[f"scripts/{p.name}"] = p.read_bytes()
    for sprache in sprachen:
        for p in sorted((txt / "dialog").glob("*.msg")):
            dateien[f"text/{sprache}/dialog/{p.name}"] = p.read_bytes()
        for p in sorted((txt / "cuts").glob("*.txt")):
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
DEBUG-TASTEN (nur in diesem Testpaket)
  F11  von überall direkt in die Gosse (The Gutter)
  F8   auf Den Business 2 neben die Kellertreppe (nur dort)
  F9   Essie und Kolbe erscheinen neben dir (Notlösung ohne Karte)
  F12  Bildschirmfoto (Spiel), landet im Fallout-2-Ordner als SCR*.BMP
  Bei jeder Madame unter "Let's go over how the house is run.":
       "[Debug] Add two empty rooms." und "[Debug] Show me the ending."
""" if debug else ""
    return f"""Rotlicht über dem Ödland – Testpaket
=====================================

Für: Fallout 2 Restoration Project {release}, Spiel auf Englisch
Build: Skriptbasis {sb}, GVAR-Basis {gb}, Kartennummer der Gosse {ki}{", mit Debug-Tasten" if debug else ""}
Stand: alle 16 Schritte des Fahrplans. Im Spiel getestet ist bisher nur die
Gosse (Eingang, Karte, Prolog). Alles andere ist nur im Prüfwerkzeug geprüft.

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
SO FÄNGT ES AN
In der Den, auf Den Business 2 (Ruine zwischen Sklavengilde und Mom's
Diner), führt eine Kellertreppe hinab in die Gosse (The Gutter). Essie
schuldet Metzgers Mann Kolbe Geld: Das ist der Prolog. Danach gehört dir
das Haus, und Essie erzählt dir unter "Business outside these walls." ->
"Where else could we open a house?" von den anderen fünf Städten.

DIE SECHS HÄUSER
  The Gutter        The Den, Keller auf Den Business 2        Prolog mit Essie und Kolbe
  The Silver Garter New Reno 1, Treppe am Cat's Paw           Urkunde bei der Witwe, Segen einer
                                                              Familie über Pagano
  The Slag          Redding, Bergbaulager (Mine Entrance)     Ascortis Lizenz über den Schreiber
  The Cesspit       Vault City Courtyard, hinter Cassidy's    Hanne Voss, dann die Papiere
  The Trough        NCR Bazaar, am Rawhide Saloon             Lizenz bei der Inspektorin Grieve
  The Bilge         San Francisco, Dock                       die Duldung bei Aufseher Wen

DAS MENÜ DER MADAME
  Give me the till.                      Kasse auszahlen
  Let's go over how the house is run.    Preise, Anteil, Moral, Personal, Ausbau
  There's a problem?                     Krisen und ihre Lösungswege
  Business outside these walls.          andere Städte, Talente, Jobs (Bestechung,
                                         Schutzgeld, Sabotage, Spenden), Läuferroute
  Later.                                 Gespräch beenden
Dazu je Haus eigene Themen (Razzien, Rivalen, Questlinien).

DIE WOCHE
Abgerechnet wird jede Woche, aber nur auf Stadtkarten, nicht auf der
Weltkarte. Die Zeit dazwischen wird beim nächsten Betreten nachgerechnet
(höchstens ein paar Wochen). Zum Testen: im Pip-Boy ruhen lassen.

WAS PRÜFEN (ausführlich jeweils im Abschnitt "Testen im Spiel" von
docs/umsetzung-*.md)
  1. Gosse: Treppe, Karte, Prolog, alle Wege; Anwerbung; Metzgers Angebot.
  2. Jedes Menü: Ist "Later." immer sichtbar? Nirgends "Error"?
  3. Jedes Haus: Eingang auf der Stadtkarte, Innenkarte, Madame, Übernahme.
  4. Ein paar Wochen ruhen: Meldungen, Kasse, Läufer ins Hauptquartier
     (sobald das Strumpfband dir gehört).
  5. Krisen: Wenn die Madame eine meldet, die Wege durchprobieren.
  6. Das Ende: bei einer Madame "[Debug] Show me the ending." zeigt die
     Endslides des Addons (Hauptslide und höchstens ein Nachsatz).

WENN ETWAS NICHT GEHT
- Keine Treppe in der Ruine, F11 tut nichts: Steht  rotlicht  wirklich als
  LETZTE Zeile in mods_order.txt? (Braucht sfall 4.4 oder neuer; das
  aktuelle RPU bringt es mit.)
- Absturz oder Unsinn beim Laden: War es ein alter Spielstand? Dann ein
  neues Spiel beginnen.
- Statt Text steht "Error": Datei unter mods\\rotlicht\\text\\english fehlt,
  oder das Spiel läuft in einer anderen Sprache (fallout2.cfg, language=).

RÜCKMELDUNG
Was stimmt nicht und wo. Am besten mit Bildschirmfoto (F12).
"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--rpu", required=True, help="Klon des RPU-Repositorys")
    ap.add_argument("--release", required=True, help="Release-Tag, z. B. v2.4.34")
    ap.add_argument("--build", default=str(ROOT / "build"))
    ap.add_argument("--out", default=str(ROOT / "build" / "paket"))
    ap.add_argument("--sprachen", default="english",
                    help="Sprachordner, in die die (englischen) Texte kommen")
    a = ap.parse_args()
    try:
        packen(a)
    except Fehler as e:
        print(f"FEHLER {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
