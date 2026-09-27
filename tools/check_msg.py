#!/usr/bin/env python3
"""Prueft die Dialogtexte gegen die Skripte.

Fuer jedes Skript in scripts_src/rotlicht/*.ssl (plus eingebundene
Rotlicht-Header) werden alle festen Textnummern gesucht, die in Reply,
den Options-Makros, mstr und display_mstr vorkommen, dazu die berechneten
Bereiche (Preisstufe, Krisen, Module). Jede Nummer muss in der .msg-Datei
des Skripts stehen (nach Aufloesen von "# @include").

Ausserdem: doppelte Nummern und geschweifte Klammern im Text.

Aufruf:  python3 tools/check_msg.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIALOG = ROOT / "text_src/german/dialog"
MODULE_ANZAHL = 23

# Berechnete Nummern: Basis + Wertebereich
BERECHNET = {
    r"mstr\(135 \+": range(135, 139),                 # Preisstufen 0..3
    r"mstr\(180 \+": range(181, 188),                 # Krisen 1..7
    r"mstr\(RL_MSG_MODUL_NAME \+": range(400, 400 + MODULE_ANZAHL),    # Modulnamen
    r"mstr\(RL_MSG_MODUL_EFFEKT \+": range(500, 500 + MODULE_ANZAHL),  # Moduleffekte
}
MUSTER = [
    r"\bReply\((\d+)\)",
    r"\b(?:NOption|GOption|BOption)\((\d+),",
    r"\bNLowOption\((\d+),",
    r"\bmstr\((\d+)\)",
    r"\bdisplay_mstr\((\d+)\)",
]


def quelltext(ssl):
    text = ssl.read_text(encoding="utf-8")
    for inc in re.findall(r'#include "\.\./headers/(rl_[a-z_]+\.h)"', text):
        text += (ROOT / "scripts_src/headers" / inc).read_text(encoding="utf-8")
    return text


def msg_nummern(msg):
    zeilen = []
    for line in msg.read_text(encoding="utf-8").splitlines():
        if line.startswith("# @include "):
            zeilen += (msg.parent / line.split()[2]).read_text(encoding="utf-8").splitlines()
        else:
            zeilen.append(line)
    nummern, fehler = {}, []
    for line in zeilen:
        m = re.match(r"^\{(\d+)\}\{[^{}]*\}\{([^{}]*)\}\s*$", line)
        if m:
            n = int(m.group(1))
            if n in nummern:
                fehler.append(f"doppelte Nummer {n}")
            nummern[n] = m.group(2)
        elif line.startswith("{"):
            fehler.append(f"kaputte Zeile: {line[:60]}")
    return nummern, fehler


def main():
    gesamt = 0
    for ssl in sorted((ROOT / "scripts_src/rotlicht").glob("*.ssl")):
        msg = DIALOG / (ssl.stem + ".msg")
        text = quelltext(ssl)
        genutzt = set()
        for muster in MUSTER:
            genutzt |= {int(n) for n in re.findall(muster, text)}
        for muster, bereich in BERECHNET.items():
            if re.search(muster, text):
                genutzt |= set(bereich)
        # Reaktion 330 + Weg: Weg 5 (ausgeliefert) hat keine Reaktion, Essie ist dann weg
        if re.search(r"Reply\(330 \+", text):
            genutzt |= set(range(331, 335))
        nummern, fehler = msg_nummern(msg)
        fehlend = sorted(genutzt - set(nummern))
        for f in fehler:
            print(f"{msg.name}: {f}")
        if fehlend:
            print(f"{msg.name}: fehlende Nummern {fehlend}")
        gesamt += len(fehler) + len(fehlend)
        print(f"{ssl.name}: {len(genutzt)} Nummern genutzt, {len(nummern)} vorhanden")
    if gesamt:
        print(f"{gesamt} Problem(e)")
        sys.exit(1)
    print("Alle Texte vorhanden.")


if __name__ == "__main__":
    main()
