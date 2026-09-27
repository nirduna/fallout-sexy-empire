# Rotlicht über dem Ödland (Arbeitstitel)

Konzept und Skripte für eine Addon-Modifikation für **Fallout 2** (sfall 4.x). Die Mod bringt keine neue Hauptstory. Sie fügt eine tief verzahnte Management-Schicht hinzu: Der Spieler baut in den Vanilla-Städten ein Bordell- und Entertainment-Imperium auf, verwaltet es und verteidigt es gegen Rivalen.

## Phasen

| Phase | Inhalt | Status |
|---|---|---|
| 1 | Core Gameplay Loop & Wirtschaftssystem | Entwurf, wartet auf Freigabe: [docs/phase-1-core-loop-und-wirtschaft.md](docs/phase-1-core-loop-und-wirtschaft.md) |
| 2 | Map-Integration & Standorte, Ausbaustufen | offen |
| 3 | Quests, Rivalen & feindliche Übernahmen | offen |
| 4 | Personal, Unique Workers & Zufallsereignisse | offen |
| 5 | Technische Umsetzung (GVARs, Timer, SSL-Skripte) | offen |
| 6 | Karma, Ruf & Endings (Epilog-Slides) | offen |

## Werkzeuge

- `tools/economy_sim.py`: Balancing-Prototyp des Wirtschaftsmodells. Er rechnet nur mit Ganzzahlen, damit er nach SSL übertragbar bleibt.

  ```
  python3 tools/economy_sim.py [wochen] [stadt]
  # stadt: den | new_reno | redding | ncr | vault_city | san_fran
  ```
