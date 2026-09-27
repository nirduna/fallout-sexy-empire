# Phase 1 – Core Gameplay Loop & Wirtschaftssystem

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Freigegeben (siehe Entscheidungen unten). Weiter in [Phase 2](phase-2-standorte-und-ausbau.md).

> **Freigabe-Entscheidungen**
> 1. **Ansatz:** der empfohlene Hybrid (Abschnitt 4): C als Rückgrat, Den-Prolog und Vor-Ort-Krisen aus A, schlankes Hauptbuch aus B.
> 2. **Familien-Paten** in New Reno bleiben wie beschrieben.
> 3. **Tyrannen-Route:** auf Vanilla-Niveau, also angedeutet und mit schweren Konsequenzen.
> 4. **Ton:** düster und stimmig, deutlich weniger Humor. Zynismus nur als Haltung einzelner Figuren, nie als Gag. Säule 3 ist entsprechend angepasst.
> 5. **Wirtschaftsziel:** ordentlicher Nebenverdienst (3.000–5.000 $/Woche im voll ausgebauten Endgame).
> 6. **Städte:** alle sechs bleiben.
> 7. **Keine generischen Immobilien:** Jeder Standort ist ausdrücklich ein **Bordell**. Bar, Spieltische und Bühne sind Teile eines Bordells, keine eigenen Geschäftszweige.

---

## 0. Rolle & Design-Leitplanken

Ab hier arbeite ich als Lead Game Designer, Writer und Technical Director. Das Addon bringt **keine neue Hauptstory**. Es bringt eine neue, tief verzahnte Gameplay-Schicht: ein Imperium aus Bordellen, das in der bestehenden Welt lebt und sich mit ihr verändert.

**Vier Säulen, an denen sich jede Entscheidung messen lassen muss:**

1. **Eingewoben statt aufgeklebt.** Jede Mechanik hängt an einem Vanilla-Zustand: am Familienkrieg in New Reno, am Jet-Handel, an Metzgers Schicksal, am Gecko-Reaktor oder an der NCR-Politik. Die Welt verändert das Geschäft, und das Geschäft verändert die Welt.
2. **Moral kostet, in beide Richtungen.** Ausbeutung zahlt sich nach Wochen aus, Fairness nach Monaten. Beides ist spielbar, und keines von beiden gibt es umsonst (Belege in Abschnitt 3.8).
3. **Düster und stimmig, nicht schmuddelig.** Der Ton ist nüchtern und hart, wie die Den und New Reno im Original. Zynismus gibt es nur als Haltung einzelner Figuren, nie als Gag. Intime Szenen bleiben beim Vanilla-Fade-to-Black. Die Mechanik dreht sich um Geld, Macht, Abhängigkeit und Menschen, nicht um explizite Inhalte.
4. **Ehrlich zur Engine.** Alles muss mit Fallout 2 und sfall 4.x machbar sein und darf die Kompatibilität mit dem Restoration Project nicht brechen. Jeder Ansatz nennt deshalb seinen Umsetzungsaufwand.

*Leitlinie für die Produktion:* Alle Beschäftigten sind erwachsen. Zwangsarbeit gibt es nur als klar bestrafte Tyrannen-Option (Karma, Slaver-Tag, Rangers als Gegner). Das entspricht der Art, wie Vanilla mit Sklaverei umgeht.

---

## 1. Drei Ansätze für den Core Loop

### Ansatz A – „Der Wanderpatron“ (dezentral, physisch, von NPCs geführt)

**Pitch:** Jedes Haus ist ein kleiner Kosmos mit eigener Madame oder eigenem Manager. Du bist der Patron, der durchs Ödland zieht, kassiert, Brände löscht und weiterreist. Verwaltet wird nur im Dialog, und das Geld liegt tatsächlich im Tresor.

#### Akquise: „Die Gosse“ (The Den)

Madame Esther „Essie“ Kowalski hat früher im Cat's Paw gearbeitet. Heute ist sie zu alt für New Reno und zu stur für den Ruhestand. Ihr baufälliges Haus in der Den steckt bei Metzger mit **1.200 $** in der Kreide, und die Zinsen wachsen jede Woche.

> **Essie:** „Schätzchen, in der Den gibt's zwei Sorten Geschäftsleute: die, die Metzger bezahlen, und die, die Metzger verkauft.“

| Lösungsweg | Check | Ergebnis |
|---|---|---|
| Schulden bezahlen | – (Barter ≥ 50: −25 %) | Sauberer Start, Metzger bleibt neutral |
| Metzger überzeugen | Speech ≥ 60 | Die Schulden werden zu einer **Partnerschaft**: 10 % Dauerabgabe an die Sklavengilde, keine Startkosten |
| Eintreiber verprügeln | Unarmed ≥ 60 **oder** STR ≥ 7 (Faustkampf, nicht tödlich) | Schulden halbiert, Metzger respektiert dich, Hitze +10 |
| Schuldschein stehlen | Steal ≥ 50 / Sneak ≥ 60 (Gildenhaus bei Nacht) | Schulden weg. Wer erwischt wird, hat die Gilde zum Feind |
| Essie an Metzger ausliefern | – | Das Haus gehört dir, aber es fehlt eine Managerin. **Die Tyrannen-Route beginnt**, Karma stürzt ab |

#### Management

- **Manager-NPC pro Standort** (Dialog): Preisstufe, Personal-Anteil, Security-Budget, Upgrades (Phase 2), Personal (Phase 4).
- **Physischer Tresor** auf der Map. Er fasst etwa 4 Wochen Gewinn. Was darüber hinausgeht, „verschwindet“.
  > **Manager:** „Was nicht im Tresor liegt, gehört dem, der es zuerst findet. So ist die Den.“
- **Ereignisse** werden beim Betreten der Map ausgelöst und müssen vor Ort gelöst werden.

#### Loop

```
Reisen ──► Standort betreten ──► Bericht & Kassieren ──► Problem vor Ort lösen
   ▲                                                            │
   └──── Vanilla-Quests ◄──── Reinvestieren / Einstellen ◄──────┘
```

**Stärken:** maximale Immersion. Reine Vanilla-Technik (Dialog und Map-Scripts), kein UI-Modding. Jeder Standort fühlt sich lebendig an.
**Schwächen:** viel Backtracking. Man weiß nie, was gerade woanders passiert. Im Spätspiel wird es zum Mikromanagement, und Einnahmen gehen über das Tresorlimit verloren.
**Technischer Aufwand:** niedrig bis mittel.

---

### Ansatz B – „Das Hauptbuch“ (zentral, über ein Item, Fernverwaltung)

**Pitch:** Ein Tycoon im Taschenformat. Ein fleckiges Kassenbuch im Inventar *ist* dein Imperium. Du verwaltest alle Häuser von überall aus, sogar vom Beifahrersitz des Highwayman.

> *Item-Beschreibung:* „Ein abgegriffenes Kassenbuch mit Wasserflecken. Hinter jeder Zahl steht ein Name.“

#### Akquise: „Wendell Pryces Konzessionen“

In Beckys Bar in der Den sitzt Wendell P. Pryce, ein Bordellbetreiber, dem alles entglitten ist: pleite, auf der Flucht, mit zitternden Händen. Für 300 $ verkauft er dir das Hauptbuch und drei Konzessionsurkunden (mit Barter für 150 $). Mit Speech ≥ 55 verrät er dir, welche davon echt sind:

| Urkunde | Wahrheit | Folge |
|---|---|---|
| Lagerhaus, The Den | echt, aber ausgebrannt | Startstandort, Renovierung 800 $ |
| „Gesundheitsbad“, Vault City | gefälscht | Mit Science ≥ 60 vervollständigst du die Fälschung. Das öffnet dir später Vault City |
| Grundstück, NCR | echt, gehört inzwischen aber Westin | Quest-Hook für Phase 3 |

Später kaufst oder pachtest du weitere Häuser bei den lokalen Eigentümern und baust sie zu Bordellen um. Jeder Kauf wird im Hauptbuch eingetragen.

#### Management

- **Hauptbuch benutzen** öffnet den Verwaltungsbildschirm. Dafür gibt es zwei Varianten:
  - *Luxus:* ein eigenes sfall-Fenster mit Art-Frame und Reitern.
  - *Low-Tech:* ein Pseudo-Dialog über einen unsichtbaren Dummy-Critter (ein bewährter Modding-Trick).
- **Reiter:** Übersicht (Wochenbilanz) · Häuser (Preis, Anteil, Security) · Personal · Finanzen · Meldungen.
- **Geldfluss:** Gewinne landen auf einem Konto. Abheben kannst du bei jedem eigenen Haus oder per **Brahmin-Express-Kurier** (10 % Gebühr). Überfälle auf den Kurier sind eigene Begegnungen auf der Weltkarte.
- **Ereignisse** erscheinen als Meldungen mit Auswahl, zum Beispiel: *„Razzia in Vault City: 300 $ Schmiergeld / 2 Wochen schließen / selbst hinreisen“*. Nur große Ereignisse erfordern, dass du vor Ort bist.

#### Loop

```
Vanilla spielen ──► Hauptbuch öffnen ──► Stellschrauben ──► Meldungen entscheiden ──► Geld abheben ──┐
      ▲                                                                                              │
      └──────────────────────────────────────────────────────────────────────────────────────────────┘
```

**Stärken:** echte Tiefe wie in einer Management-Sim, guter Überblick, skaliert auf viele Standorte, kaum Backtracking.
**Schwächen:** hoher Aufwand für sfall und UI (Art-Assets, Fensterlogik). Es fühlt sich wie ein Tycoon-Minispiel neben dem RPG an. Die Welt tritt in den Hintergrund, und Ereignisse bleiben abstrakter Text.
**Technischer Aufwand:** hoch.

---

### Ansatz C – „Die Fünfte Familie“ (Hub & Spoke, Einfluss & Hitze)

**Pitch:** New Reno hat vier Familien. Du wirst die fünfte. Dein Imperium ist eine Organisation mit Hauptquartier, Consigliere und lokalen Capos. Expandiert wird nicht über Kaufverträge, sondern über **Einfluss**, und jede harte Aktion erzeugt **Hitze**.

#### Akquise: „Das Silberne Strumpfband“ (New Reno)

Ein leerstehendes Haus nahe der Virgin Street (die genaue Position auf der Map klären wir in Phase 2). Wer darin aufmachen will, braucht den **Segen einer Familie**, oder er riskiert es ohne:

| Pate | Startbonus | Preis | Misstrauisch |
|---|---|---|---|
| **Mordino** | Jet-Konzession im Haus: +15 % Kunden, Nebenumsatz | 25 % Tribut, doppelt so viele Jet-Ereignisse beim Personal | Wright |
| **Wright** | Schnaps zum Selbstkostenpreis: Bar-Umsatz +50 % | 20 % Tribut, „Keine Chems im Haus!“ | Mordino |
| **Salvatore** | Salvatore-Schläger als Security: Sicherheit +30 | 30 % Tribut, gelegentliche „Gefallen“ (Enklave-Hook, Phase 3) | Bishop |
| **Bishop** | NCR-Kontakte: Einfluss in der NCR +20, Lizenz −50 % | 20 % Tribut, Beteiligung am Shark-Club-Geschäft | Salvatore |
| **Unabhängig** | kein Tribut | Alle vier Familien misstrauisch, Hitze in New Reno +20, ein Anschlag ist garantiert | alle |

#### Zwei Leisten pro Stadt

- **Einfluss (0–100):** steigt durch Quests, Spenden, Bestechung und Gefallen.
  - Ab 20: Standort gründen oder pachten.
  - Ab 40: feindliche Übernahme von Konkurrenten.
  - Ab 60: Autoritäten „in der Tasche“, du wirst vor Razzien gewarnt.
  - Ab 80: Stadtpolitik, etwa ein Lizenzgesetz in der NCR oder ein Toleranzerlass in Vault City.
- **Hitze (0–100):** steigt durch Gewalt, Erpressung, Ausbeutung und Skandale und sinkt um 5 pro Woche. Hohe Hitze bringt Razzien, Rivalen-Anschläge und Rangers.

*Einfluss öffnet Türen, Hitze schließt sie.*

#### Management

- **Consigliere im Hauptquartier:** zentrale Kasse, Tribute, Budgets pro Standort und Strategie.
- **Capos vor Ort:** lokale Entscheidungen und Ereignisse.
- **Läufer:** bringen die Gewinne jede Woche ins Hauptquartier. Ein Tresorlimit gibt es nicht, aber bei hoher Hitze werden Läufer überfallen.
- **Familientreffen:** Alle 4 Wochen findet im Hauptquartier ein Treffen mit einer echten Entscheidung statt, zum Beispiel: *„Salvatore will 10 % mehr. Zahlen oder Krieg?“*

#### Loop

```
Einfluss aufbauen ──► Gründen / Übernehmen ──► Betreiben (Profit vs. Hitze) ──► Rivalen reagieren ──┐
        ▲                                                                                          │
        └──────────────────── Expandieren ◄──── Familientreffen (Meta-Entscheidung) ◄──────────────┘
```

**Stärken:** tiefste Verzahnung mit den Fraktionen, maximaler Quest-Hebel für Phase 3, klare Macht-Fantasie („Der Pate“ trifft Fallout). Moralische Entscheidungen sind im System verankert.
**Schwächen:** New Reno kommt erst in der Mitte des Spiels. Zwei Leisten pro Stadt erfordern mehr Balancing.
**Technischer Aufwand:** mittel.

---

## 2. Vergleich

| Kriterium | A – Wanderpatron | B – Hauptbuch | C – Fünfte Familie |
|---|---|---|---|
| Immersion / Fallout-Feeling | ★★★★★ | ★★☆☆☆ | ★★★★☆ |
| Strategische Tiefe | ★★☆☆☆ | ★★★★★ | ★★★★☆ |
| Backtracking-Last | hoch | niedrig | mittel |
| Verzahnung mit Fraktionen | ★★★☆☆ | ★★☆☆☆ | ★★★★★ |
| Quest-Potenzial (Phase 3) | ★★★☆☆ | ★★☆☆☆ | ★★★★★ |
| Technischer Aufwand | niedrig | hoch | mittel |
| Spielstart | früh (Level 3–5) | früh | Spielmitte (Level 8–12) |

---

## 3. Gemeinsames Wirtschaftsmodell (gilt für alle drei Ansätze)

Die Ansätze unterscheiden sich darin, *wie* du das Imperium steuerst. Die Rechnung darunter ist dieselbe. Einen ausführbaren Prototyp gibt es unter [`tools/economy_sim.py`](../tools/economy_sim.py). Alle Zahlen unten stammen daraus.

### 3.1 Zeittakt

- **Wochenabrechnung** alle 7 Spieltage. Die Woche ist die natürliche Einheit, weil Reisen auf der Weltkarte oft Tage bis Wochen dauern.
- Wochen, in denen du abwesend warst, werden **nachgerechnet**, höchstens 12 am Stück (Schutz vor Exploits, geringere Script-Last).

### 3.2 Einnahmen

```
Kunden        = Basis-Kunden(Stadt) × Attraktivität × Nachfrage(Preisstufe) × Sicherheitsfaktor × Stadtmodifikator
Attraktivität = 40 % + 2 × Score                        (Score 0–100 → 40 %–240 %)
Score         = 50 % Personalqualität(eff.) + 30 % Ausstattung + 20 % Hausruf
Qualität(eff.)= Grundqualität × (0,4 + 0,8 × Moral/100)  (Moral 0 → ×0,4 · Moral 100 → ×1,2)

Umsatz        = Kunden × Basispreis × Preisstufe                 (Dienstleistung)
              + Kunden × 5 $ × Bar-Stufe                         (Nebenumsatz)
              + weitere Nebenumsätze aus Upgrades                (Phase 2: Bühne, Spieltische …)
```

### 3.3 Ausgaben

```
Kosten = Personal-Anteil × Dienstleistungsumsatz
       + Fixlöhne (Manager, Rausschmeißer, Barkeeper, Buchhalter, Doc)
       + 3 $ Verbrauch je Kunde (Schnaps, Wäsche, Medizin)
       + 25 $ Unterhalt je Ausbaustufe (Modulkatalog in Phase 2)
       + Abgaben: Tribut/Steuer in % vom Gesamtumsatz + Pflicht-Bestechung
       + Schwund in % vom Gesamtumsatz
```

**Schwund:** 10 % ohne Buchhalter, 4 % mit Buchhalter. Dazu +1 Prozentpunkt je 3 Moralpunkte unter 40 und −2 Prozentpunkte ab Moral 70.

| Fixlohn | $/Woche | Effekt |
|---|---|---|
| Manager / Madame | 50–150 | Pflicht, hebt die Ereignis-Lösungen (Phase 4) |
| Rausschmeißer | 40–120 | Sicherheit, je nach Werten (Phase 4) |
| Barkeeper | 30 | Schaltet den Bar-Umsatz frei |
| Buchhalter | 80 | Schwund 10 % → 4 % |
| Doc | 60 | Moral +1/Woche, verhindert Krankheits-Ereignisse |

### 3.4 Stadtprofile

| Stadt | Basis-Kunden/Woche | Basispreis | Kaufkraft | Abgaben | Grundrisiko | Typischer Einstieg |
|---|---|---|---|---|---|---|
| **The Den** | 30 | 20 $ | arm | 10 % Sklavengilde | 4 | früh |
| **New Reno** | 55 | 25 $ | mittel | 20–30 % Tribut an die Familie | 3 | Mitte |
| **Redding** | 35 | 20 $ (zum Teil in Gold) | mittel | 75 $/Woche „Lizenz“ an den Bürgermeister | 3 | Mitte |
| **Vault City** | 15 | 70 $ | reich | 200 $/Woche Schweigegeld je Hausklasse | 5 | Mitte |
| **NCR** | 45 | 22 $ | mittel | 15 % Steuer + 500 $ Lizenz (einmalig) | 1 | spät-mittel |
| **San Francisco** | 40 | 30 $ | mittel | 10 % an die Shi | 2 | spät |

### 3.5 Lokale Wirtschaft: dynamische Modifikatoren aus der Vanilla-Welt

- **Redding: Jet-Index**
  - *Jet-Flut* (Standard, die Mordinos liefern): Kunden −20 %, weil die Minenarbeiter ihren Lohn für Jet ausgeben. Doppelt so viele Ereignisse mit Jet-süchtigem Personal.
  - *Jet-Knappheit* (die Mordino-Lieferkette ist gekappt): Kunden +10 %, dazu 2 Wochen Entzugsrandale (Security-Probe).
  - *Antidot im Umlauf:* Kunden +25 %, halb so viele Personal-Ereignisse.
- **Redding: Minen & Machtfrage**
  - Wanamingo-Mine gesäubert: Minen-Boom, Kunden +30 %.
  - Redding fällt an die NCR: 15 % Steuer statt der Bürgermeister-Lizenz, Risiko −1.
  - Redding fällt an New Reno: 20 % Tribut an die zuständige Familie.
- **New Reno: Familienkrieg**
  - Der Tribut geht an die Familie, die das Viertel kontrolliert.
  - Wird eine Familie ausgelöscht, entsteht ein **Machtvakuum**: 4 Wochen lang Risiko +2, danach wird neu verhandelt. Das ist deine Chance für Übernahmen.
  - Solange das Cat's Paw unabhängig ist, kostet es dich 15 % Kunden (Phase 3: kaufen, fusionieren oder sabotieren).
- **The Den: Metzger**
  - Solange die Sklavengilde aktiv ist: Kunden +20 % (Sklavenhändler mit vollen Taschen), 10 % Abgabe, und Metzger bietet billiges Zwangspersonal an (Tyrannen-Route).
  - Nach Zerschlagung der Gilde: Kunden −25 %, keine Abgabe, Hitze −20. Die Den wird ein wenig menschlicher, und dein Umsatz schrumpft.
- **Vault City: Illegalität & Wohlstand**
  - Prostitution ist verboten. Dein Bordell, „die Kloake“, tarnt sich als Pension für Außenweltler im Courtyard, und die Bürger kommen nachts. Ohne Bürgerschaft oder Bestechung kommt jede Woche eine Razzia-Probe (Details in Phase 2).
  - Wird der Konflikt um den Gecko-Reaktor friedlich gelöst und ein Handelsvertrag geschlossen: Kunden +10 %.
- **NCR: Recht & Moral**
  - Ein legales Gewerbe mit Lizenz und Steuer bei niedrigstem Risiko, aber mit „Sittlichkeitskampagnen“ als Nachfragebremse (Kreuzritter, Phase 3).
  - Die Brahmin-Barone rund um Westin bilden die VIP-Kundschaft.
- **San Francisco: Hafen & Glaube**
  - Die Shi dulden das Haus gegen Tribut.
  - Die Hubologen werben um dieselben Verlorenen, die auch zu dir kommen, und kosten dich 10 % Kunden, bis die Quest in Phase 3 gelöst ist.
- **Global: Fall der Enklave**
  - Nach der Zerstörung der Ölplattform folgt ein Westküsten-Boom: Kunden +10 % überall, weil die NCR expandiert.
  - Versprengte Enklave-Soldaten werden zu einem eigenen Ereignis (Phase 4). Dieser Zustand speist den Epilog (Phase 6).

### 3.6 Stellschrauben des Spielers

**Preisstufe**

| Stufe | Preis | Nachfrage arm / mittel / reich | Hausruf/Woche | Voraussetzung |
|---|---|---|---|---|
| Ramsch | ×0,6 | 140 / 140 / 100 % | −1 | – |
| Standard | ×1,0 | 100 / 100 / 100 % | ±0 | – |
| Gehoben | ×1,5 | 50 / 70 / 85 % | +1 | Ausstattung ≥ 40, Moral ≥ 50 |
| Exklusiv | ×2,5 | 20 / 40 / 60 % | +2 | Ausstattung ≥ 70, VIP-Raum, Moral ≥ 65 |

Wichtig: Die Premium-Stufen setzen zufriedenes Personal voraus. **Fairness ist der Schlüssel zum großen Geld.**

*Nachtrag aus Phase 2:* Jede Anteilsstufe hat eine Moral-Obergrenze (ausbeuterisch 50, branchenüblich 70, fair 100). Quartiere und ähnliche Module heben die Moral nur bis zu dieser Grenze.

**Personal-Anteil (der Moral-Hebel)**

| Stufe | Anteil am Dienstleistungsumsatz | Moral/Woche | Karma/Woche | Nebenwirkung |
|---|---|---|---|---|
| Ausbeuterisch | 25 % | −4 | −1 | Unter Moral 25: Flucht, Diebstahl, gute Leute kündigen |
| Branchenüblich | 35 % | ±0 | ±0 | – |
| Fair | 45 % | +3 | ±0 | Ab Moral 70: Mundpropaganda (Hausruf +1). Ab 75: Das Personal wirbt Talente an (Qualität +1/Woche) |

**Sicherheit**

- *Bedrohung* = Grundrisiko × 20 + Hitze.
- *Sicherheit* entsteht aus Rausschmeißern, Upgrades und Schutz durch Fraktionen.
- Liegt die Sicherheit unter der Bedrohung: Kunden −(Differenz ÷ 2) %, höchstens −40 %. Die Chance auf einen Vorfall beträgt dann Differenz % pro Woche.

### 3.7 Beispielrechnung: New Reno, mittlerer Ausbau, Woche 1

Annahmen: Grundqualität 60, Moral 50, Ausstattung 50, Hausruf 55, Preisstufe Standard, Personal-Anteil 35 %, Bar-Stufe 1, 4 Ausbaustufen, Sicherheit 70 gegen Bedrohung 60, mit Buchhalter, Tribut 20 %.

```
Qualität(eff.) = 60 × 0,8                     =    48
Score          = 24 + 15 + 11                 =    50   → Attraktivität 140 %
Kunden         = 55 × 1,40                    =    77

Umsatz         = 77 × 25 $  +  77 × 5 $       = 1.925 $ + 385 $ = 2.310 $

Personal-Anteil 35 % × 1.925 $                =   673 $
Fixlöhne (2 Rausschmeißer, Manager,
          Barkeeper, Buchhalter)              =   310 $
Verbrauch 77 × 3 $                            =   231 $
Unterhalt 4 × 25 $                            =   100 $
Tribut 20 % × 2.310 $                         =   462 $
Schwund 4 % × 2.310 $                         =    92 $
                                               ─────────
Kosten                                        = 1.868 $
GEWINN                                        =   442 $ / Woche
```

### 3.8 Beweis für Säule 2: Fairness gegen Ausbeutung (30 Wochen, gleicher Standort)

| Woche | Ausbeuterisch | Branchenüblich | Fair |
|---|---|---|---|
| 1 | **634 $** | 442 $ | 249 $ |
| 4 | **566 $** | 419 $ | 258 $ |
| 8 | 336 $ | **409 $** | 322 $ |
| 12 | 145 $ | **409 $** | 378 $ |
| 20 | 24 $ | 409 $ | **497 $** |
| 30 | −15 $ | 409 $ | **570 $** |
| **Summe 30 Wochen** | 5.418 $ | 12.353 $ | **12.493 $** |
| Karma | −30 | 0 | 0 |

In Worten: Ausbeutung bringt in den ersten Wochen rund +40 %, ab Woche 8 fällt sie hinter „branchenüblich“ zurück und kollabiert dann. Fair verdient ab Woche 14 pro Woche am meisten, überholt Ausbeutung in der Summe ab Woche 17 und schaltet dazu die Premium-Preise frei, die hier noch gar nicht eingerechnet sind. Der Tyrann kann sein Haus nur künstlich am Leben halten, indem er ständig Personal bei Metzger nachkauft. Das ist teuer und führt in einen Karma-Abgrund, und genau das ist die Tyrannen-Fantasie.

### 3.9 Balancing-Ziele

| Stufe | Gewinn/Woche |
|---|---|
| Starthaus in der Den (1 Rausschmeißer, kein Buchhalter) | ca. 80–100 $ |
| Mittlerer Ausbau, pro Standort | 250–500 $ |
| Voll ausgebautes Imperium (6 Häuser) | ca. 3.000–5.000 $ |

- **Amortisation** von Upgrades: 6–10 Wochen.
- **Wohin das Geld fließt:**
  - Upgrades, Bestechungen, Tribute
  - Übernahmen (Phase 3)
  - Stiftungen für Karma, zum Beispiel eine Klinik in der Den oder Spenden an die Rangers
  - Imperiumswert → Endings (Phase 6)
- **Schutz vor Exploits:** höchstens 12 Wochen Nachrechnung, nur ein Haus pro Stadt, Tresor- bzw. Läufer-Limits, Premium-Stufen an Bedingungen geknüpft.

### 3.10 Technische Machbarkeit (Vorschau auf Phase 5)

- **Globales sfall-Script** (`gl_*.int`, `set_global_script_repeat`): vergleicht `game_time` mit dem Zeitpunkt der letzten Abrechnung und rechnet fehlende Wochen nach.
- **Reine Ganzzahl-Arithmetik** in Prozentwerten. Der Prototyp ist bewusst so geschrieben, damit er 1:1 nach SSL übertragbar ist.
- **Zustand** liegt in eigenen GVARs bzw. sfall-Globals (Moral, Hausruf, Hitze, Einfluss, Kasse pro Stadt).
- **Physischer Tresor** (Ansatz A/C): Der Gewinn wird zunächst als Zahl gespeichert und erst in `map_enter_p_proc` als Geld-Item in den Container gelegt. Container auf nicht geladenen Maps lassen sich nicht zuverlässig beschreiben.
- **Vanilla-Hooks** (Metzger, Familien, Jet, Mine, Gecko, Enklave) lesen die vorhandenen Quest-GVARs. Die genauen Namen gleiche ich in Phase 5 mit den Fallout-2-Script-Quellen ab.

---

## 4. Empfehlung des Lead Designers: Hybrid „C-Kern, A-Seele, B-Brille“

1. **Rückgrat aus C:** Einfluss und Hitze, Hauptquartier in New Reno, Familien-Paten. Das ist der stärkste Hebel für die Rivalen-Questlines in Phase 3.
2. **Prolog aus A:** *Die Gosse* in der Den ist das frühe Tutorial (Level 3–5), rein dialogbasiert. Sie bringt Preis, Moral und Security bei, bevor New Reno das große Spiel eröffnet.
3. **Vor-Ort-Ereignisse aus A:** Große Krisen erfordern deine Anwesenheit, kleine regeln die Capos.
4. **Hauptbuch aus B, aber schlank:** Statusbericht und wenige Schnellbefehle per Pseudo-Dialog, kein teures Custom-UI. Die echten Entscheidungen triffst du im Gespräch mit Menschen (Consigliere, Capos). Das hält es Fallout.
5. **Geldfluss:** Läufer bringen die Gewinne ins Hauptquartier (Risiko abhängig von der Hitze). Wer beim Capo vor Ort abholt, bekommt 100 % ohne Läufer-Risiko. So wird Reisen belohnt, aber nicht erzwungen.

**Progression des Imperiums:**

| Akt | Ort | Rolle |
|---|---|---|
| I | The Den | Kleinunternehmer |
| II | New Reno | Gründer der fünften Familie |
| III | Redding, Vault City, NCR, San Francisco | Expansion |
| IV | nach dem Fall der Enklave | Mogul der Westküste → Epilog |

---

## 5. Offene Entscheidungen (für die Freigabe von Phase 2)

1. **Ansatz:** A, B, C oder der empfohlene Hybrid?
2. **Familien-Paten** in New Reno: übernehmen, abwandeln (z. B. nur zwei Familien wählbar) oder streichen?
3. **Tyrannen-Route:** Tonalität auf Vanilla-Niveau (angedeutet, schwere Konsequenzen; meine Empfehlung), oder soll sie noch zurückhaltender werden?
4. **Wirtschaftsziel:** „ordentlicher Nebenverdienst“ (3.000–5.000 $/Woche im Endgame, wie oben) oder bewusst eine Power-Fantasy, in der Geld irgendwann egal wird?
5. **Städte-Auswahl:** die sechs oben, oder San Francisco tauschen, etwa gegen Broken Hills (Sheriff Marcus!), Modoc oder Klamath?
