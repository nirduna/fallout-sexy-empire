#!/usr/bin/env python3
"""Erzeugt den Modulkatalog fuer die SSL-Skripte aus dem Simulator.

Eine Quelle der Wahrheit: Kosten und Effekte stehen in tools/ausbau_sim.py
(UPGRADES). Dieses Skript schreibt daraus

  scripts_src/headers/rl_katalog.h          (Werte fuer den Ausbau-Dialog)
  text_src/german/dialog/_rl_module.inc     (Namen 400-422, Effekte 500-522)

Aufruf:  python3 tools/gen_katalog.py
"""
from pathlib import Path

import ausbau_sim as sim

ROOT = Path(__file__).resolve().parent.parent
STAEDTE = ["den", "new_reno", "redding", "vault_city", "ncr", "san_fran"]
ALLE = list(range(len(STAEDTE)))

# Zusatzangaben, die der Simulator nicht braucht:
# Menuegruppe (0 Haus & Ausstattung, 1 Betrieb, 2 Besonderes), Voraussetzung,
# erlaubte Staedte, Bauwochen, Sonderbedingung (1 = Gefallen der Shi, Phase 3)
META = {
    "hausklasse_2":      dict(gruppe=0, voraus=None,            wochen=2),
    "hausklasse_3":      dict(gruppe=0, voraus="hausklasse_2",  wochen=3),
    "einrichtung_1":     dict(gruppe=0, voraus=None),
    "einrichtung_2":     dict(gruppe=0, voraus="einrichtung_1"),
    "einrichtung_3":     dict(gruppe=0, voraus="einrichtung_2"),
    "bar_1":             dict(gruppe=0, voraus=None),
    "bar_2":             dict(gruppe=0, voraus="bar_1"),
    "vip_trakt":         dict(gruppe=0, voraus="hausklasse_2"),
    "sicherheit_1":      dict(gruppe=1, voraus=None),
    "sicherheit_2":      dict(gruppe=1, voraus="sicherheit_1"),
    "sicherheit_3":      dict(gruppe=1, voraus="sicherheit_2"),
    "quartiere_1":       dict(gruppe=1, voraus=None),
    "quartiere_2":       dict(gruppe=1, voraus="quartiere_1"),
    "krankenstube":      dict(gruppe=1, voraus=None),
    "kontor":            dict(gruppe=1, voraus=None),
    "den_riegel_innen":  dict(gruppe=2, voraus=None),
    "nr_spieltische":    dict(gruppe=2, voraus=None),
    "red_goldwaage":     dict(gruppe=2, voraus=None),
    "red_entzugsstube":  dict(gruppe=2, voraus="krankenstube"),
    "vc_wartungstunnel": dict(gruppe=2, voraus=None),
    "ncr_karawanenhof":  dict(gruppe=2, voraus=None),
    "sf_anlegesteg":     dict(gruppe=2, voraus=None),
    "sf_shi_siegel":     dict(gruppe=2, voraus=None, bedingung=1),
}

STADT_PREFIX = {"den_": 0, "nr_": 1, "red_": 2, "vc_": 3, "ncr_": 4, "sf_": 5}


def erlaubte_staedte(key):
    """Bitmaske der Staedte, abgeleitet aus dem Simulator."""
    for prefix, stadt in STADT_PREFIX.items():
        if key.startswith(prefix):
            return 1 << stadt
    if key == "hausklasse_3":
        return sum(1 << i for i, s in enumerate(STAEDTE) if sim.START[s]["max_klasse"] >= 3)
    if key == "vip_trakt":
        return sum(1 << STAEDTE.index(s) for s in sim.VIP_DEMAND)
    return sum(1 << i for i in ALLE)


def effekt_text(u, wochen):
    teile = []
    if u.get("klasse"):
        teile.append("Hausklasse +1")
    if u.get("rooms"):
        teile.append(f"+{u['rooms']} Zimmer")
    if u.get("furnishing"):
        teile.append(f"Ausstattung +{u['furnishing']}")
    if u.get("bar_level"):
        teile.append(f"Bar-Stufe +1 (+{sim_bar()} $ je Kunde)")
    if u.get("security"):
        teile.append(f"Sicherheit +{u['security']}")
    if u.get("moral_bonus"):
        teile.append(f"Moral +{u['moral_bonus']} pro Woche")
    if u.get("doc"):
        teile.append("ein Doc im Haus")
    if u.get("accountant"):
        teile.append("Buchhalter, Schwund 4 %")
    if u.get("vip"):
        teile.append("eigene VIP-Kundschaft")
    if u.get("side"):
        teile.append(f"+{u['side']} $ Nebenumsatz je Kunde")
    if u.get("city_mod"):
        teile.append(f"Kunden +{u['city_mod']} %")
    if u.get("tribute"):
        teile.append(f"Tribut {u['tribute']} Prozentpunkte")
    if u.get("wages"):
        teile.append(f"Lohn +{u['wages']} $/Woche")
    teile.append(f"Unterhalt +{u.get('levels', 0) * 25} $/Woche")
    teile.append(f"Bauzeit {wochen} Woche{'n' if wochen != 1 else ''}")
    return ", ".join(teile)


def sim_bar():
    from economy_sim import BAR_PER_CLIENT_PER_LEVEL
    return BAR_PER_CLIENT_PER_LEVEL


def main():
    keys = list(sim.UPGRADES)
    assert set(keys) == set(META), "META und UPGRADES stimmen nicht ueberein"
    idx = {k: i for i, k in enumerate(keys)}

    felder = {
        "KOSTEN":      [sim.UPGRADES[k]["cost"] for k in keys],
        "GRUPPE":      [META[k]["gruppe"] for k in keys],
        "VORAUS":      [idx[META[k]["voraus"]] if META[k]["voraus"] else -1 for k in keys],
        "STAEDTE":     [erlaubte_staedte(k) for k in keys],
        "WOCHEN":      [META[k].get("wochen", 1) for k in keys],
        "BEDINGUNG":   [META[k].get("bedingung", 0) for k in keys],
        "ZIMMER":      [sim.UPGRADES[k].get("rooms", 0) for k in keys],
        "AUSSTATTUNG": [sim.UPGRADES[k].get("furnishing", 0) for k in keys],
        "BAR":         [sim.UPGRADES[k].get("bar_level", 0) for k in keys],
        "SICHERHEIT":  [sim.UPGRADES[k].get("security", 0) for k in keys],
        "MORAL":       [sim.UPGRADES[k].get("moral_bonus", 0) for k in keys],
        "LOEHNE":      [sim.UPGRADES[k].get("wages", 0) for k in keys],
        "FLAGS":       [(1 if sim.UPGRADES[k].get("accountant") else 0)
                        | (2 if sim.UPGRADES[k].get("doc") else 0)
                        | (4 if sim.UPGRADES[k].get("vip") else 0) for k in keys],
        "NEBEN":       [sim.UPGRADES[k].get("side", 0) for k in keys],
        "STADTMOD":    [sim.UPGRADES[k].get("city_mod", 0) for k in keys],
        "TRIBUT":      [sim.UPGRADES[k].get("tribute", 0) for k in keys],
        "KLASSE":      [sim.UPGRADES[k].get("klasse", 0) for k in keys],
        "STUFEN":      [sim.UPGRADES[k].get("levels", 0) for k in keys],
    }

    h = ["/*",
         "   rl_katalog.h - Modulkatalog (Phase 2), ERZEUGT von tools/gen_katalog.py.",
         "   Nicht von Hand aendern: Werte stehen in tools/ausbau_sim.py (UPGRADES).",
         "*/",
         "#ifndef RL_KATALOG_H",
         "#define RL_KATALOG_H",
         "",
         f"#define RL_MODULE_ANZAHL            ({len(keys)})",
         "#define RL_MSG_MODUL_NAME           (400)   // + Modul-ID",
         "#define RL_MSG_MODUL_EFFEKT         (500)   // + Modul-ID (nicht 440: 460-477 sind Menuezeilen)",
         ""]
    for k in keys:
        h.append(f"#define RL_M_{k.upper():<24} ({idx[k]})")
    h.append("")
    for i, f in enumerate(felder):
        h.append(f"#define RL_MK_{f:<24} ({i})")
    h += ["",
          "procedure rl_modul(variable id, variable feld);",
          "",
          "procedure rl_modul(variable id, variable feld) begin",
          "   variable werte;"]
    erst = True
    for i, (f, werte) in enumerate(felder.items()):
        kw = "if" if erst else "else if"
        h.append(f"   {kw} (feld == RL_MK_{f}) then")
        h.append(f"      werte := [{', '.join(str(w) for w in werte)}];")
        erst = False
    h += ["   else",
          "      return 0;",
          "   return get_array(werte, id);",
          "end",
          "",
          "#endif",
          ""]
    (ROOT / "scripts_src/headers/rl_katalog.h").write_text("\n".join(h), encoding="utf-8")

    m = ["# _rl_module.inc - ERZEUGT von tools/gen_katalog.py, nicht von Hand aendern.",
         "# Wird vom Build in jede Manager-.msg eingefuegt (Zeile '# @include _rl_module.inc').",
         "# Modulnamen (400 + ID)"]
    for k in keys:
        m.append(f"{{{400 + idx[k]}}}{{}}{{{sim.NAMES[k]}}}")
    m.append("# Effekte (500 + ID)")
    for k in keys:
        m.append(f"{{{500 + idx[k]}}}{{}}{{{effekt_text(sim.UPGRADES[k], META[k].get('wochen', 1))}.}}")
    (ROOT / "text_src/german/dialog/_rl_module.inc").write_text("\n".join(m) + "\n", encoding="utf-8")
    print(f"{len(keys)} Module geschrieben.")


if __name__ == "__main__":
    main()
