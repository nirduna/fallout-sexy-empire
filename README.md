# Rotlicht über dem Ödland (Arbeitstitel)

Konzept und Skripte für eine Addon-Modifikation für **Fallout 2** (sfall 4.x). Die Mod bringt keine neue Hauptstory. Sie fügt eine tief verzahnte Management-Schicht hinzu: Der Spieler baut in den Vanilla-Städten ein Imperium aus Bordellen auf, verwaltet es und verteidigt es gegen Rivalen.

## Phasen

| Phase | Inhalt | Status |
|---|---|---|
| 1 | Core Gameplay Loop & Wirtschaftssystem | freigegeben: [docs/phase-1-core-loop-und-wirtschaft.md](docs/phase-1-core-loop-und-wirtschaft.md) |
| 2 | Map-Integration & Standorte, Ausbaustufen | freigegeben: [docs/phase-2-standorte-und-ausbau.md](docs/phase-2-standorte-und-ausbau.md) |
| 3 | Quests, Rivalen & feindliche Übernahmen | freigegeben: [docs/phase-3-quests-rivalen-uebernahmen.md](docs/phase-3-quests-rivalen-uebernahmen.md) |
| 4 | Personal, Unique Workers & Zufallsereignisse | freigegeben: [docs/phase-4-personal-talente-ereignisse.md](docs/phase-4-personal-talente-ereignisse.md) |
| 5 | Technische Umsetzung (GVARs, Timer, SSL-Skripte) | freigegeben: [docs/phase-5-technik.md](docs/phase-5-technik.md) |
| 6 | Karma, Ruf & Endings (Epilog-Slides) | freigegeben: [docs/phase-6-karma-ruf-endings.md](docs/phase-6-karma-ruf-endings.md) |

## Umsetzung

| Schritt | Inhalt | Status |
|---|---|---|
| 1 | Prolog „Essies Schulden“, Ausbau-Dialog, gemeinsame Manager-Knoten | umgesetzt, kompiliert, Test im Spiel offen: [docs/umsetzung-1-prolog-und-ausbau.md](docs/umsetzung-1-prolog-und-ausbau.md) |
| 2 | Die Gosse: Kellertreppe in der Den, Innenkarte `RLDEN01` mit Essie und Kolbe, Karten-Werkzeuge | umgesetzt, gebaut, Sichtprüfung im Spiel offen: [docs/umsetzung-2-die-gosse.md](docs/umsetzung-2-die-gosse.md) |

## Werkzeuge

- `tools/economy_sim.py`: Balancing-Prototyp des Wirtschaftsmodells. Er rechnet nur mit Ganzzahlen, damit er nach SSL übertragbar bleibt.

  ```
  python3 tools/economy_sim.py [wochen] [stadt]
  # stadt: den | new_reno | redding | ncr | vault_city | san_fran
  ```

- `tools/ausbau_sim.py`: Ausbaupfade der sechs Bordelle (Phase 2). Er rechnet Gewinn und Amortisation je Upgrade aus und erzeugt die Tabellen für die Doku. Seine Modulliste ist die einzige Quelle für Kosten und Effekte im Spiel.
- `tools/gen_katalog.py`: erzeugt daraus `scripts_src/headers/rl_katalog.h` und die Modultexte (läuft bei jedem Build mit).
- `tools/check_msg.py`: prüft, ob jede im Code verwendete Textnummer in der passenden `.msg` steht (läuft bei jedem Build mit).
- `tools/fomap.py`: liest und schreibt Fallout-2-Karten (.MAP). `pruefen` liest Karten ein und schreibt sie byte-gleich zurück, `info` zeigt den Kopf.
- `tools/fomap_bild.py`: schematische Draufsicht einer Karte als PNG, mit Hexnummern zum Planen von Positionen.
- `tools/bau_karten.py`: alle Kartenpositionen an einer Stelle. Baut die Innenkarten aus Vorlagen des RPU und erzeugt `rl_karten.h` (läuft bei jedem Build mit).

  ```
  python3 tools/ausbau_sim.py [stadt|alle] [fair|branchenueblich|ausbeuterisch]
  python3 tools/ausbau_sim.py --md fair
  ```

## Skripte bauen

Die Skripte liegen in `scripts_src/` (SSL, sfall-Dialekt), die Texte in `text_src/` (UTF-8: Dialoge, Endslide-Untertitel, Titel). Zeilen, die in Dateien der Basisinstallation eingefügt werden (`scripts.lst`, `vault13.gam`, `endgame.txt`, `karmavar.txt`, `maps.txt`, `city.txt`), liegen in `install/`. Gebaut wird mit dem sfall-Compiler `sslc` gegen die Header des Fallout 2 Restoration Project (RPU) und die sfall-Header. Die genaue Anleitung steht in [Phase 5, Abschnitt 10](docs/phase-5-technik.md#10-bauen-und-testen).

```
SSLC=/pfad/zu/sslc FO2_SCRIPTS_SRC=/pfad/zu/rpu/scripts_src tools/build_scripts.sh
```

`FO2_SCRIPTS_SRC` zeigt dabei in einen Klon des RPU-Repositorys. Aus dessen `data/maps` baut das Skript die Innenkarten nach `build/maps/` ([Umsetzung 2, Abschnitt 4](docs/umsetzung-2-die-gosse.md#4-installation)).

