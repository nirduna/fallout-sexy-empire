#!/usr/bin/env python3
"""Ausbaustufen-Prototyp fuer Phase 2.

Rechnet fuer jedes Bordell einen Ausbaupfad durch: Startzustand nach der
Uebernahme, dann Upgrades in empfohlener Reihenfolge. Fuer jeden Schritt
wird der durchschnittliche Wochengewinn (Wochen 1-12 nach dem Kauf) und
die Amortisationszeit berechnet.

Aufruf:  python3 tools/ausbau_sim.py [stadt|alle] [fair|branchenueblich|ausbeuterisch]
         python3 tools/ausbau_sim.py --md [anteil]     (Markdown-Tabellen fuer die Doku)
"""
import sys

from economy_sim import simulate

# Allgemeine Module: Kosten $, Kategorie, Effekte auf den Hauszustand.
# Kategorien: R = Rendite, A = Absicherung (Risiko/Ereignisse), M = Moral
UPGRADES = {
    "hausklasse_2":   dict(cost=2000, cat="R", rooms=2, furnishing=15, levels=1, klasse=1),
    "hausklasse_3":   dict(cost=4000, cat="R", rooms=2, furnishing=15, levels=1, klasse=1),
    "einrichtung_1":  dict(cost=500,  cat="R", furnishing=10, levels=1),
    "einrichtung_2":  dict(cost=1200, cat="R", furnishing=15, levels=1),
    "einrichtung_3":  dict(cost=2500, cat="R", furnishing=20, levels=1),
    "bar_1":          dict(cost=800,  cat="R", bar_level=1, wages=30, levels=1),
    "bar_2":          dict(cost=2000, cat="R", bar_level=1, levels=1),
    "sicherheit_1":   dict(cost=400,  cat="A", security=10, levels=1),
    "sicherheit_2":   dict(cost=1000, cat="A", security=20, levels=1),
    "sicherheit_3":   dict(cost=2000, cat="A", security=25, levels=1),
    "quartiere_1":    dict(cost=700,  cat="M", moral_bonus=1, levels=1),
    "quartiere_2":    dict(cost=1500, cat="M", moral_bonus=1, levels=1),
    "krankenstube":   dict(cost=1000, cat="A", doc=True, wages=60, levels=1),
    "kontor":         dict(cost=600,  cat="R", accountant=True, wages=80, levels=1),
    "vip_trakt":      dict(cost=3000, cat="R", furnishing=10, vip=True, levels=1),
}

# Stadtspezifische Module
UPGRADES.update({
    "den_riegel_innen":   dict(cost=400,  cat="M", security=10, moral_bonus=1, levels=1),
    "nr_spieltische":     dict(cost=2000, cat="R", side=4, furnishing=5, levels=1),
    "red_goldwaage":      dict(cost=400,  cat="R", city_mod=10, levels=1),
    "red_entzugsstube":   dict(cost=1200, cat="A", moral_bonus=1, city_mod=5, levels=1),
    "vc_wartungstunnel":  dict(cost=2500, cat="R", security=25, city_mod=20, levels=1),
    "ncr_karawanenhof":   dict(cost=1200, cat="R", rooms=1, city_mod=15, levels=1),
    "sf_anlegesteg":      dict(cost=1500, cat="R", city_mod=15, levels=1),
    "sf_shi_siegel":      dict(cost=1000, cat="R", security=10, tribute=-5, levels=1),
})

# Startzustand nach der Uebernahme (Hausklasse 1) und maximale Hausklasse
START = {
    "den":        dict(rooms=3, furnishing=20, rep=35, staff_q=50, security=45, wages=80,  max_klasse=2,
                       city_mod=20),   # Sklavengilde aktiv: +20 % Kunden
    "new_reno":   dict(rooms=3, furnishing=30, rep=40, staff_q=55, security=50, wages=150, max_klasse=3),
    "redding":    dict(rooms=3, furnishing=20, rep=35, staff_q=50, security=50, wages=110, max_klasse=2),
    "vault_city": dict(rooms=2, furnishing=40, rep=40, staff_q=55, security=60, wages=150, max_klasse=2,
                       bribe_per_klasse=200),   # Schweigegeld waechst mit dem Haus
    "ncr":        dict(rooms=3, furnishing=30, rep=40, staff_q=55, security=40, wages=120, max_klasse=2),
    "san_fran":   dict(rooms=3, furnishing=25, rep=40, staff_q=55, security=45, wages=130, max_klasse=2),
}

# VIP-Trakt: eigene Kundschaft mit dreifachem Basispreis (Kunden/Woche)
VIP_DEMAND = {"new_reno": 10, "vault_city": 2, "ncr": 6, "san_fran": 5}
VIP_PRICE_MULT = 3
VIP_MIN_MORAL = 65

# Empfohlene Ausbaureihenfolge je Stadt
PATHS = {
    "den": ["bar_1", "sicherheit_1", "den_riegel_innen", "hausklasse_2",
            "sicherheit_2"],
    "new_reno": ["einrichtung_1", "sicherheit_1", "hausklasse_2", "bar_1", "kontor",
                 "nr_spieltische", "hausklasse_3", "einrichtung_2", "bar_2",
                 "vip_trakt"],
    "redding": ["sicherheit_1", "bar_1", "hausklasse_2", "red_goldwaage",
                "einrichtung_1", "red_entzugsstube"],
    "vault_city": ["sicherheit_1", "vc_wartungstunnel", "hausklasse_2", "kontor",
                   "einrichtung_2", "einrichtung_3", "vip_trakt", "krankenstube"],
    "ncr": ["krankenstube", "hausklasse_2", "bar_1", "ncr_karawanenhof", "kontor",
            "bar_2", "vip_trakt"],
    "san_fran": ["bar_1", "hausklasse_2", "sf_anlegesteg", "einrichtung_1", "kontor",
                 "sf_shi_siegel", "vip_trakt"],
}

BASE_TRIBUTE = {"den": 10, "new_reno": 20, "redding": 0,
                "vault_city": 0, "ncr": 15, "san_fran": 10}


PRICE_ORDER = ["standard", "gehoben", "exklusiv"]


def allowed_tiers(h, moral):
    tiers = ["standard"]
    if h["furnishing"] >= 40 and moral >= 50:
        tiers.append("gehoben")
    if h["furnishing"] >= 70 and h.get("vip") and moral >= 65:
        tiers.append("exklusiv")
    return tiers


def run(city, h, tier, share_tier, weeks):
    from economy_sim import CITIES
    saved = CITIES[city]["tribute"], CITIES[city]["bribe"]
    CITIES[city]["tribute"] = max(0, BASE_TRIBUTE[city] + h["tribute"])
    if h.get("bribe_per_klasse"):
        CITIES[city]["bribe"] = h["bribe_per_klasse"] * h["klasse"]
    try:
        rows, _, _ = simulate(
            city, weeks=weeks, staff_q=h["staff_q"], furnishing=min(100, h["furnishing"]),
            rep=h["rep"], price_tier=tier, share_tier=share_tier,
            security=h["security"], accountant=h["accountant"], doc=h["doc"],
            bar_level=h["bar_level"], upgrade_levels=h["levels"],
            fixed_wages=h["wages"], city_mod=100 + h["city_mod"], rooms=h["rooms"],
            side_per_client=h["side"], moral_bonus=h["moral_bonus"])
    finally:
        CITIES[city]["tribute"], CITIES[city]["bribe"] = saved
    return rows


STEADY_FROM, STEADY_TO = 13, 24


def vip_profit(city, h, share_tier, moral):
    """Zusatzgewinn des VIP-Trakts: eigene Kundschaft, dreifacher Preis."""
    from economy_sim import CITIES, SHARE_TIERS, CONSUMABLES_PER_CLIENT
    if not h.get("vip") or moral < VIP_MIN_MORAL:
        return 0
    n = VIP_DEMAND.get(city, 0)
    revenue = n * CITIES[city]["price"] * VIP_PRICE_MULT
    share = SHARE_TIERS[share_tier][0]
    tribute = max(0, BASE_TRIBUTE[city] + h["tribute"])
    shrink = 4 if h["accountant"] else 10
    return revenue * (100 - share - tribute - shrink) // 100 - n * CONSUMABLES_PER_CLIENT * 2   # eingeschwungener Betrieb


def house_profit(city, h, share_tier="fair"):
    """Wochengewinn im eingeschwungenen Betrieb (Wochen 13-24), beste erlaubte Preisstufe."""
    best = None
    for tier in PRICE_ORDER:
        rows = run(city, h, tier, share_tier, STEADY_TO)
        moral_at_steady = rows[STEADY_FROM - 1][1]
        if tier not in allowed_tiers(h, moral_at_steady):
            continue
        steady = rows[STEADY_FROM - 1:STEADY_TO]
        avg = sum(r[6] for r in steady) // len(steady)
        avg += vip_profit(city, h, share_tier, moral_at_steady)
        clients = steady[-1][3]
        if best is None or avg > best[0]:
            best = (avg, tier, clients)
    return best


def city_of(h):
    return h["city"]


def start_house(city):
    h = dict(city=city, bar_level=0, levels=1, accountant=False, doc=False, city_mod=0,
             side=0, moral_bonus=0, tribute=0, klasse=1)
    h.update(START[city])
    return h


def apply(h, name):
    if "klasse" in UPGRADES[name]:
        assert h["klasse"] < h["max_klasse"], f"{name}: Hausklasse-Grenze"
    if name == "vip_trakt":
        assert h["klasse"] >= 2 and city_of(h) in VIP_DEMAND, "VIP-Trakt nicht erlaubt"
    for k, v in UPGRADES[name].items():
        if k in ("cost", "cat"):
            continue
        if isinstance(v, bool):
            h[k] = v
        else:
            h[k] = h.get(k, 0) + v


def build_path(city, share_tier="fair"):
    h = start_house(city)
    prev, tier, clients = house_profit(city, h, share_tier)
    lines = [("Start (Hausklasse 1)", 0, prev, tier, clients, None)]
    invested = 0
    for name in PATHS[city]:
        apply(h, name)
        cost = UPGRADES[name]["cost"]
        invested += cost
        now, tier, clients = house_profit(city, h, share_tier)
        gain = now - prev
        roi = cost // gain if gain > 0 and UPGRADES[name]["cat"] == "R" else None
        lines.append((name + " [" + UPGRADES[name]["cat"] + "]", cost, now, tier, clients, roi))
        prev = now
    return lines, invested, prev


NAMES = {
    "hausklasse_2": "Hausklasse 2", "hausklasse_3": "Hausklasse 3 (Familiensitz)",
    "einrichtung_1": "Einrichtung I", "einrichtung_2": "Einrichtung II",
    "einrichtung_3": "Einrichtung III", "bar_1": "Bar I", "bar_2": "Bar II",
    "sicherheit_1": "Sicherheit I", "sicherheit_2": "Sicherheit II",
    "sicherheit_3": "Sicherheit III", "quartiere_1": "Personalquartiere I",
    "quartiere_2": "Personalquartiere II", "krankenstube": "Krankenstube",
    "kontor": "Kontor", "vip_trakt": "VIP-Trakt",
    "den_riegel_innen": "Riegel innen", "nr_spieltische": "Spieltische",
    "red_goldwaage": "Ehrliche Goldwaage", "red_entzugsstube": "Entzugsstube",
    "vc_wartungstunnel": "Wartungstunnel", "ncr_karawanenhof": "Karawanenhof",
    "sf_anlegesteg": "Anlegesteg", "sf_shi_siegel": "Siegel der Shi",
}
# Namen im Spiel (englisch, reines ASCII fuer die englischen Schriften)
NAMES_EN = {
    "hausklasse_2": "House Class II", "hausklasse_3": "House Class III (Family Seat)",
    "einrichtung_1": "Furnishings I", "einrichtung_2": "Furnishings II",
    "einrichtung_3": "Furnishings III", "bar_1": "Bar I", "bar_2": "Bar II",
    "sicherheit_1": "Security I", "sicherheit_2": "Security II",
    "sicherheit_3": "Security III", "quartiere_1": "Staff Quarters I",
    "quartiere_2": "Staff Quarters II", "krankenstube": "Sickroom",
    "kontor": "Counting Room", "vip_trakt": "VIP Wing",
    "den_riegel_innen": "Inside Bolts", "nr_spieltische": "Gaming Tables",
    "red_goldwaage": "Honest Gold Scale", "red_entzugsstube": "Detox Room",
    "vc_wartungstunnel": "Maintenance Tunnel", "ncr_karawanenhof": "Caravan Yard",
    "sf_anlegesteg": "Jetty", "sf_shi_siegel": "Seal of the Shi",
}
TIER_NAMES = {"standard": "Standard", "gehoben": "Gehoben", "exklusiv": "Exklusiv"}


def markdown(city, share):
    lines, invested, final = build_path(city, share)
    out = ["| Schritt | Kosten | Gewinn/Woche | Preisstufe | Kunden/Woche | Amortisation |",
           "|---|---|---|---|---|---|"]
    for name, cost, profit, tier, clients, roi in lines:
        key = name.split(" [")[0]
        label = NAMES.get(key, name)
        cat = name[name.find("[") + 1:-1] if "[" in name else ""
        label = label + (f" ({cat})" if cat else "")
        cost_s = f"{cost:,} $".replace(",", ".") if cost else "–"
        roi_s = f"{roi} Wo." if roi is not None else "–"
        out.append(f"| {label} | {cost_s} | {profit} $ | {TIER_NAMES[tier]} | {clients} | {roi_s} |")
    out.append(f"| **Endausbau** | **{invested:,} $** | **{final} $** | | | |".replace(",", "."))
    return "\n".join(out)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--md":
        share = sys.argv[2] if len(sys.argv) > 2 else "fair"
        for city in PATHS:
            print(f"\n### {city}\n")
            print(markdown(city, share))
        return
    which = sys.argv[1] if len(sys.argv) > 1 else "alle"
    share = sys.argv[2] if len(sys.argv) > 2 else "fair"
    cities = list(PATHS) if which == "alle" else [which]
    empire = 0
    for city in cities:
        lines, invested, final = build_path(city, share)
        empire += final
        print(f"\n== {city} (Personal-Anteil {share}, eingeschwungen) ==")
        print(f"{'Schritt':<20}{'Kosten':>7}{'Gewinn/Wo':>10}{'Preis':>10}{'Kunden':>7}{'Amort.':>7}")
        for name, cost, profit, tier, clients, roi in lines:
            print(f"{name:<20}{cost:>7}{profit:>10}{tier:>10}{clients:>7}{(roi if roi is not None else '-'):>7}")
        print(f"Investiert: ${invested}, Endausbau: ${final}/Woche")
    if which == "alle":
        print(f"\nImperium gesamt (Endausbau): ${empire}/Woche")


if __name__ == "__main__":
    main()
