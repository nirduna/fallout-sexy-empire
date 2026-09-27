# Rotlicht über dem Ödland (Arbeitstitel)

Konzept und Skripte für eine Addon-Modifikation für **Fallout 2** (sfall 4.x). Die Mod bringt keine neue Hauptstory. Sie fügt eine tief verzahnte Management-Schicht hinzu: Der Spieler baut in den Vanilla-Städten ein Imperium aus Bordellen auf, verwaltet es und verteidigt es gegen Rivalen.

## Phasen

| Phase | Inhalt | Status |
|---|---|---|
| 1 | Core Gameplay Loop & Wirtschaftssystem | freigegeben: [docs/phase-1-core-loop-und-wirtschaft.md](docs/phase-1-core-loop-und-wirtschaft.md) |
| 2 | Map-Integration & Standorte, Ausbaustufen | freigegeben: [docs/phase-2-standorte-und-ausbau.md](docs/phase-2-standorte-und-ausbau.md) |
| 3 | Quests, Rivalen & feindliche Übernahmen | freigegeben: [docs/phase-3-quests-rivalen-uebernahmen.md](docs/phase-3-quests-rivalen-uebernahmen.md) |
| 4 | Personal, Unique Workers & Zufallsereignisse | freigegeben: [docs/phase-4-personal-talente-ereignisse.md](docs/phase-4-personal-talente-ereignisse.md) |
| 5 | Technische Umsetzung (GVARs, Timer, SSL-Skripte) | Entwurf, wartet auf Freigabe: [docs/phase-5-technik.md](docs/phase-5-technik.md) |
| 6 | Karma, Ruf & Endings (Epilog-Slides) | offen |

## Werkzeuge

- `tools/economy_sim.py`: Balancing-Prototyp des Wirtschaftsmodells. Er rechnet nur mit Ganzzahlen, damit er nach SSL übertragbar bleibt.

  ```
  python3 tools/economy_sim.py [wochen] [stadt]
  # stadt: den | new_reno | redding | ncr | vault_city | san_fran
  ```

- `tools/ausbau_sim.py`: Ausbaupfade der sechs Bordelle (Phase 2). Er rechnet Gewinn und Amortisation je Upgrade aus und erzeugt die Tabellen für die Doku.

  ```
  python3 tools/ausbau_sim.py [stadt|alle] [fair|branchenueblich|ausbeuterisch]
  python3 tools/ausbau_sim.py --md fair
  ```

## Skripte bauen

Die Skripte liegen in `scripts_src/` (SSL, sfall-Dialekt), die Texte in `text_src/` (UTF-8). Gebaut wird mit dem sfall-Compiler `sslc` gegen die Header des Fallout 2 Unofficial Patch und die sfall-Header. Die genaue Anleitung steht in [Phase 5, Abschnitt 10](docs/phase-5-technik.md#10-bauen-und-testen).

```
SSLC=/pfad/zu/sslc FO2_SCRIPTS_SRC=/pfad/zu/upu/scripts_src tools/build_scripts.sh
```

