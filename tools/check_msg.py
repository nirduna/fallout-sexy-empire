#!/usr/bin/env python3
"""Prueft die Dialogtexte gegen die Skripte.

Fuer jedes Skript in scripts_src/rotlicht/*.ssl (plus eingebundene
Rotlicht-Header) werden alle festen Textnummern gesucht, die in Reply,
den Options-Makros, mstr und display_mstr vorkommen, dazu die berechneten
Bereiche (Preisstufe, Krisen, Module). Jede Nummer muss in der .msg-Datei
des Skripts stehen (nach Aufloesen von "# @include").

Das globale Skript holt seine Texte mit rl_text(n) aus game/rotlicht.msg;
auch diese Nummern werden geprueft.

Ausserdem: doppelte Nummern, geschweifte Klammern im Text und Zeichen
ausserhalb von ASCII (die englischen Fallout-2-Schriften haben keine Umlaute
und keine typografischen Anfuehrungszeichen).

Aufruf:  python3 tools/check_msg.py
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEXTE = ROOT / "text_src/english"
DIALOG = TEXTE / "dialog"
MODULE_ANZAHL = 23
SONDER_ANZAHL = int(re.search(r"#define RL_SM_ANZAHL\s+\((\d+)\)",
                              (ROOT / "scripts_src/headers/rl_sonder.h").read_text()).group(1))

# Berechnete Nummern: Basis + Wertebereich
BERECHNET = {
    r"mstr\(135 \+": range(135, 139),                 # Preisstufen 0..3
    r"mstr\(180 \+": range(181, 189),                 # Krisen 1..8
    r"mstr\(483 \+": range(483, 486),                 # Anwerber-Methode 0..2
    r"mstr\(RL_MSG_MODUL_NAME \+": range(400, 400 + MODULE_ANZAHL),    # Modulnamen
    r"mstr\(RL_MSG_MODUL_EFFEKT \+": range(500, 500 + MODULE_ANZAHL),  # Moduleffekte
    r"Reply\(630 \+ stadt - 1\)": range(630, 635),                # die anderen Staedte
    r"display_mstr\(100 \+ 10 \* h\)": range(110, 160, 10),        # Eingaenge (rltuer)
    r"display_mstr\(101 \+ 10 \* h\)": range(111, 161, 10),
    r"mstr\(RL_MSG_SONDER_NAME \+": range(430, 430 + SONDER_ANZAHL),   # Sondermodule
    r"mstr\(190 \+ pate\)": range(191, 195),                 # Segen der vier Familien (rlfixer)
    r"mstr\(130 \+ h\)": range(130, 136),                    # Hausnamen (rlconsig)
    r"mstr\(141 \+ welt\[RL_W_NR_SEGEN\]\)": range(141, 147),  # der Pate (rlconsig)
    r"mstr\(150 \+ f\)": range(151, 155),                    # misstrauische Familien (rlconsig)
    r"mstr\(RL_MSG_SONDER_EFFEKT \+": range(530, 530 + SONDER_ANZAHL),
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


def nicht_ascii():
    fehler = []
    for f in sorted(TEXTE.rglob("*")):
        if f.is_file():
            for nr, zeile in enumerate(f.read_text(encoding="utf-8").splitlines(), 1):
                if not zeile.isascii():
                    fehler.append(f"{f.relative_to(ROOT)}:{nr}: Zeichen ausserhalb von ASCII")
    return fehler


def main():
    gesamt = 0
    for f in nicht_ascii():
        print(f)
        gesamt += 1
    # Globales Skript: rl_text(n) und Hausnamen rl_text(100 + h)
    gl = (ROOT / "scripts_src/global/gl_rotlicht.ssl").read_text(encoding="utf-8")
    genutzt = {int(n) for n in re.findall(r"\brl_text\((\d+)\)", gl)}
    if re.search(r"rl_text\(100 \+ h\)", gl):
        genutzt |= set(range(100, 107))                  # sechs Haeuser und das Testhaus
    nummern, fehler = msg_nummern(TEXTE / "game/rotlicht.msg")
    fehlend = sorted(genutzt - set(nummern))
    for f in fehler + ([f"fehlende Nummern {fehlend}"] if fehlend else []):
        print(f"rotlicht.msg: {f}")
        gesamt += 1
    print(f"gl_rotlicht.ssl: {len(genutzt)} Nummern genutzt, {len(nummern)} vorhanden")
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
