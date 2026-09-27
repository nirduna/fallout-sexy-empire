#!/usr/bin/env python3
"""Balancing-Prototyp fuer das Wirtschaftsmodell aus Phase 1.

Deterministische Erwartungswert-Simulation eines einzelnen Standorts
ueber N Wochen. Rechnet bewusst nur mit Ganzzahlen/Prozentwerten, damit
die Formeln 1:1 nach SSL (sfall) uebertragbar bleiben.

Aufruf:  python3 tools/economy_sim.py [wochen] [stadt]
"""
import sys

# Stadtprofile: Basis-Kunden/Woche, Basispreis $, Abgaben % vom Umsatz,
# fixe Pflicht-Bestechung $/Woche, Grundrisiko 1-5, Kaufkraft-Klasse
CITIES = {
    "den":        dict(clients=30, price=20, tribute=10, bribe=0,   risk=4, wealth="arm"),
    "new_reno":   dict(clients=55, price=25, tribute=20, bribe=0,   risk=3, wealth="mittel"),
    "redding":    dict(clients=35, price=20, tribute=0,  bribe=75,  risk=3, wealth="mittel"),
    "ncr":        dict(clients=45, price=22, tribute=15, bribe=0,   risk=1, wealth="mittel"),
    "vault_city": dict(clients=15, price=70, tribute=0,  bribe=200, risk=5, wealth="reich"),
    "san_fran":   dict(clients=40, price=30, tribute=10, bribe=0,   risk=2, wealth="mittel"),
}

# Preisstufen: (Preis-%, Nachfrage-% je Kaufkraft arm/mittel/reich, Hausruf/Woche)
PRICE_TIERS = {
    "ramsch":   (60,  {"arm": 140, "mittel": 140, "reich": 100}, -1),
    "standard": (100, {"arm": 100, "mittel": 100, "reich": 100},  0),
    "gehoben":  (150, {"arm": 50,  "mittel": 70,  "reich": 85},   1),
    "exklusiv": (250, {"arm": 20,  "mittel": 40,  "reich": 60},   2),
}

# Personal-Anteil: (Anteil % vom Dienstleistungsumsatz, Moral/Woche, Karma/Woche)
SHARE_TIERS = {
    "ausbeuterisch":   (25, -4, -1),
    "branchenueblich": (35,  0,  0),
    "fair":            (45,  3,  0),
}
# Moral-Obergrenze je Anteil (Phase 2): Quartiere & Co. heben die Moral nur bis
# hierhin. Ueber 70 (Talent-Zulauf ab 75) kommt nur, wer fair teilt.
MORAL_CAP = {"ausbeuterisch": 50, "branchenueblich": 70, "fair": 100}

CONSUMABLES_PER_CLIENT = 3    # $ Verbrauch je Kunde (Schnaps, Waesche, Medizin)
UPKEEP_PER_LEVEL = 25         # $ Unterhalt je Ausbaustufe
BAR_PER_CLIENT_PER_LEVEL = 5  # $ Nebenumsatz je Kunde und Bar-Stufe
FLIGHT_MORAL = 25             # unter dieser Moral: Flucht/Kuendigungen
FLIGHT_COST = 30              # erwartete Anwerbekosten $/Woche bei Fluchtgefahr
ROOM_CAPACITY = 12            # Kunden je Zimmer und Woche (Phase 2)


def clamp(v, lo, hi):
    return max(lo, min(hi, v))


def simulate(city, weeks=12, staff_q=60, furnishing=50, rep=55, moral=50,
             price_tier="standard", share_tier="branchenueblich",
             security=70, heat=0, accountant=True, doc=False, bar_level=1,
             upgrade_levels=4, fixed_wages=310, city_mod=100,
             rooms=None, side_per_client=0, moral_bonus=0):
    c = CITIES[city]
    p_mult, demand_by_wealth, rep_tick = PRICE_TIERS[price_tier]
    d_mult = demand_by_wealth[c["wealth"]]
    share_pct, moral_tick, karma_tick = SHARE_TIERS[share_tier]
    rows, karma, total = [], 0, 0
    for week in range(1, weeks + 1):
        # Moral skaliert die effektive Personalqualitaet (Faktor 0.4 .. 1.2)
        q_eff = staff_q * (40 + 8 * moral // 10) // 100
        score = (50 * q_eff + 30 * furnishing + 20 * rep) // 100
        attr = 40 + score * 2                             # Attraktivitaet in %
        threat = c["risk"] * 20 + heat
        sec = 100 if security >= threat else max(60, 100 - (threat - security) // 2)
        clients = c["clients"] * attr * d_mult * sec * city_mod // 100 ** 4
        if rooms is not None:                             # Phase 2: Kapazitaet
            clients = min(clients, rooms * ROOM_CAPACITY)
        rev_service = clients * c["price"] * p_mult // 100
        rev_bar = clients * (BAR_PER_CLIENT_PER_LEVEL * bar_level + side_per_client)
        revenue = rev_service + rev_bar
        shrink_pct = ((4 if accountant else 10) + max(0, 40 - moral) // 3
                      - (2 if moral >= 70 else 0))
        costs = (rev_service * share_pct // 100 + fixed_wages
                 + clients * CONSUMABLES_PER_CLIENT
                 + upgrade_levels * UPKEEP_PER_LEVEL
                 + revenue * c["tribute"] // 100 + c["bribe"]
                 + revenue * shrink_pct // 100
                 + (FLIGHT_COST if moral < FLIGHT_MORAL else 0))
        profit = revenue - costs
        total += profit
        rows.append((week, moral, staff_q, clients, revenue, costs, profit, total))
        # Zustandsfortschreibung
        moral = clamp(moral + moral_tick + (1 if doc else 0) + moral_bonus,
                      0, max(moral, MORAL_CAP[share_tier]))
        rep = clamp(rep + (score - rep) // 8 + rep_tick
                    + (1 if moral >= 70 else 0) - (2 if moral < 30 else 0), 0, 100)
        if moral < FLIGHT_MORAL:
            staff_q = max(20, staff_q - 2)   # gute Leute hauen ab
        if moral >= 75:
            staff_q = min(85, staff_q + 1)   # zufriedenes Personal wirbt Talente an
        karma += karma_tick
    return rows, total, karma


def main():
    weeks = int(sys.argv[1]) if len(sys.argv) > 1 else 24
    city = sys.argv[2] if len(sys.argv) > 2 else "new_reno"
    for share in SHARE_TIERS:
        rows, total, karma = simulate(city, weeks=weeks, share_tier=share)
        print(f"\n== {city}, mittlerer Ausbau, Personal-Anteil: {share} ==")
        print("Woche Moral Qual. Kunden Umsatz Kosten Gewinn  Kumuliert")
        for r in rows:
            print("{:>5} {:>5} {:>5} {:>6} {:>6} {:>6} {:>6} {:>10}".format(*r))
        print(f"Summe Gewinn: ${total}   Karma: {karma}")


if __name__ == "__main__":
    main()
