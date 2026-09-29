# Umsetzung 6 – Technik für die weiteren Häuser

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt, gebaut und im [Prüfwerkzeug](pruefwerkzeug.md) getestet (25 Tests).
- Alle sechs Karten sind gegen RPU 2.3.34, 2.4.34 und den aktuellen RPU-Stand geprüft.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 2](phase-2-standorte-und-ausbau.md): Lage der Häuser
- [Fahrplan](fahrplan.md), Schritt 6 und Grundsätze 2–3
- das Vorgehen der Gosse aus [Umsetzung 2](umsetzung-2-die-gosse.md), im Spiel bestätigt

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`tools/bau_karten.py`](../tools/bau_karten.py) | `HAEUSER`: fünf weitere Häuser mit Eingang, Vorlage, Rückweg und Figurenplätzen. `baue_haus` baut die Innenkarten, `pruefe_haus` und `pruefe_eingang` prüfen sie. `bilder` zeichnet alle Eingänge und Innenkarten |
| [`scripts_src/headers/rl_haeuser.h`](../scripts_src/headers/rl_haeuser.h) | **neu:** Tabellen je Haus (Stadtkarte, Eingang, Innenkarte, Plätze) und `rl_figur` für Figuren zur Laufzeit |
| [`scripts_src/rotlicht/rltuer.ssl`](../scripts_src/rotlicht/rltuer.ssl) | **neu:** Eingangstreppe der fünf Häuser. Sie führt nur den Spieler hinein und nur außerhalb des Kampfs |
| `rlren01.ssl`, `rlred01.ssl`, `rlvct01.ssl`, `rlncr01.ssl`, `rlsfr01.ssl` | **neu:** Kartenskripte. Sie setzen das Licht und zeigen beim ersten Besuch einen Satz. Figuren folgen mit den Madames |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_eingaenge` setzt die Treppe auf der Stadtkarte, wie bei der Gosse |
| [`rl_manager.h`](../scripts_src/headers/rl_manager.h) | In der Gosse: „Where else could we open a house?“ Essie, Kolbe und Mara erzählen von den fünf Städten und sagen, wo der Eingang liegt |
| `install/` | `maps.txt.add` mit sechs Karten, `city.txt.add` mit einem Eintrag je Stadt, `scripts.lst.add` |
| [`tools/paket.py`](../tools/paket.py) | nummeriert alle Karten fortlaufend, trägt jede Karte in ihre Stadt ein, baut alle Innenkarten aus demselben Release |

---

## 2. Die Häuser

| Haus | Eingang (Vanilla-Karte) | Innenkarte, Vorlage | Rückweg |
|---|---|---|---|
| **Das Silberne Strumpfband** | New Reno 1 (Virgin Street), Hex 23296, an der Außenwand des Cat's Paw | `rlren01.map`: Saal im Obergeschoss aus New Reno 3 (`newr3`, Ebene 1) | Treppe der Vorlage |
| **Die Schlacke** | Redding Mine Entrance (Bergbaulager), Hex 16483, zwischen den Schuppen | `rlred01.map`: die Minentunnel (`redmtun`) | Leiter der Vorlage |
| **Die Kloake** | Vault City Courtyard, Hex 15671, hinter Cassidy's | `rlvct01.map`: Gewölbe des Abtei-Kellers (`abbasem`) | Treppe der Vorlage |
| **Die Tränke** | NCR Bazaar, Hex 24947, am Rawhide Saloon | `rlncr01.map`: Obergeschoss im Bazaar (`ncrent`, Ebene 1) | Treppe der Vorlage |
| **Die Bilge** | San Francisco Dock, Hex 25075 | `rlsfr01.map`: Unterdeck des Tankers (`sftanker`, Ebene 2) | Treppe der Vorlage |

**Aus der Vorlage bleiben** Boden, Wände und Einrichtung.

**Weg fallen:**
- Figuren und lose Gegenstände
- Inhalte von Behältern (keine doppelte Beute)
- Kartenausgänge
- **alle Vanilla-Skripte**, damit auf unseren Karten keine Quest-Logik anderer Orte läuft

**Bilder** der Eingänge und Innenkarten liegen in [`docs/bilder`](bilder/):
- Eingänge: `strumpf_eingang.png`, `schlacke_eingang.png` usw.
- Innenkarten mit allen Plätzen: `rlren01.png` usw.

---

## 3. Prüfungen beim Bauen

| Prüfung | Wo |
|---|---|
| Eingang und Ankunft auf der Stadtkarte frei und nicht unter einem Dach | `pruefe_eingang` |
| Round-Trip byte-gleich, keine Skriptsätze außer dem Kartenskript | `pruefe_haus` |
| Startpunkt und alle sieben Plätze frei, **vom Startpunkt aus erreichbar** (Breitensuche über das Hexraster der Engine) | `pruefe_haus` |
| Der Rückweg führt auf die richtige Stadtkarte | `pruefe_haus` |
| Alles gilt für RPU 2.3.34, 2.4.34 und den aktuellen Stand | hier geprüft; die Vorlagen unterscheiden sich zwischen den Releases |

**Figurenplätze** je Haus:
- `MADAME`: 4–10 Schritte vom Eingang
- `GAST1`–`GAST4`: verteilt bis 16 Schritte
- `ANGREIFER1/2`: 2–8 Schritte, für Kämpfe im Haus

---

## 4. Entscheidungen (meine Empfehlungen)

1. **Eine Treppe für alle Eingänge:**
   - Es ist dieselbe Steintreppe wie bei der Gosse, die im Spiel funktioniert.
   - Türen mit Kartenwechsel lassen sich zur Laufzeit nicht sicher erzeugen.
   - Im Text heißt es je nach Stadt Dienstbotentreppe, Stollen, Kellertreppe, „Nr. 9“ oder Fährterminal.
2. **Vorlagen aus der eigenen Stadt**, wo es eine gibt. Für Vault City kommt die Vorlage aus der Abtei, weil Vault City keinen passenden Keller hat.
3. **Die Häuser sind vor der Übernahme offen.** Drinnen wartet, wer die Übernahme-Quest vergibt. So findet der Spieler die Quest am Ort des Hauses.
4. **Karten gehören zu ihrer Stadt** (city.txt ohne Koordinaten), wie die Gosse zur Den.

---

## 5. Testen im Spiel

| Test | Erwartung |
|---|---|
| New Reno 1 betreten | An der Wand des Cat's Paw liegt eine Steintreppe nach unten. „Look“: „Stairs down to the old hotel's service entrance.“ |
| Treppe benutzen | Man steht im Saal des Silbernen Strumpfbands. Beim ersten Besuch erscheint der Satz über Staub und Kronleuchter |
| Treppe im Saal benutzen | zurück auf der Virgin Street, neben der Treppe |
| Dasselbe in Redding (Bergbaulager), Vault City (Courtyard), NCR (Bazaar), San Francisco (Docks) | je eine Treppe; drinnen Tunnel, Gewölbe, Obergeschoss oder Unterdeck |
| Essie: „Where else could we open a house?“ | Beschreibung der fünf Städte mit dem Ort des Eingangs |
| Pip-Boy auf den Innenkarten | Stadt und Kartenname stimmen (z. B. „The Silver Garter“) |

---

## 6. Nächste Schritte

Weiter mit **Schritt 7** des [Fahrplans](fahrplan.md): das Silberne Strumpfband mit „Der Segen“ und dem Hauptquartier.
