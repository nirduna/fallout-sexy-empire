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

**Spielsprache:** Das Addon läuft komplett auf Englisch, die Doku bleibt deutsch. Die Zuordnung der Namen steht in [docs/spieltexte-englisch.md](docs/spieltexte-englisch.md).

| Schritt | Inhalt | Status |
|---|---|---|
| 1 | Prolog „Essies Schulden“, Ausbau-Dialog, gemeinsame Manager-Knoten | umgesetzt, kompiliert, Test im Spiel offen: [docs/umsetzung-1-prolog-und-ausbau.md](docs/umsetzung-1-prolog-und-ausbau.md) |
| 2 | Die Gosse: Kellertreppe in der Den, Innenkarte `RLDEN01` mit Essie und Kolbe, Karten-Werkzeuge | umgesetzt, **im Spiel getestet**: [docs/umsetzung-2-die-gosse.md](docs/umsetzung-2-die-gosse.md) |
| 3 | Anwerbung: Anwerber mit Werben oder Zwingen, Zulauf, Abgänge, Personal-Menü | umgesetzt, kompiliert, Test im Spiel offen: [docs/umsetzung-3-anwerbung.md](docs/umsetzung-3-anwerbung.md) |
| 4 | „Ketten“, Akt 1: Metzgers Angebot, Riegel außen, Zwangspersonal | umgesetzt, kompiliert, Test im Spiel offen: [docs/umsetzung-4-ketten-akt1.md](docs/umsetzung-4-ketten-akt1.md) |
| – | Prüfwerkzeug: Skripte ohne das Spiel ausführen und testen | fertig: [docs/pruefwerkzeug.md](docs/pruefwerkzeug.md) |
| 5 | „Ketten“, Akt 2–5: Mara, Zuflucht, Route nach Süden, Lieferungen, Tylers Preis, Laras Sturm, vier Enden, Mara als Madame | umgesetzt, im Prüfwerkzeug getestet, Test im Spiel offen: [docs/umsetzung-5-ketten-akt2-5.md](docs/umsetzung-5-ketten-akt2-5.md) |
| 6 | Technik für die weiteren Häuser: fünf Innenkarten, Eingänge in fünf Städten, Karten-Prüfungen gegen alle RPU-Stände | umgesetzt, geprüft, Test im Spiel offen: [docs/umsetzung-6-haeuser-technik.md](docs/umsetzung-6-haeuser-technik.md) |
| 7 | New Reno: „Der Segen“ (Urkunde, vier Paten, Eröffnungsnacht), Madame Roz, Hauptquartier mit Consigliere und Familientreffen, Jet-Theke | umgesetzt, im Prüfwerkzeug getestet, Test im Spiel offen: [docs/umsetzung-7-new-reno.md](docs/umsetzung-7-new-reno.md) |
| 8 | Redding: „Ascortis Lizenz“ (vier Wege), Madame Nell, ehrliche oder gezinkte Waage mit Revolte, Entzugsstube, Malamute Saloon | umgesetzt, im Prüfwerkzeug getestet, Test im Spiel offen: [docs/umsetzung-8-redding.md](docs/umsetzung-8-redding.md) |
| 9 | Vault City: „Ein Keller im Courtyard“, Hanne Voss und Sorensen, Schweigegeld, Razzia mit Dienstboten-Folge, Die Akte, Lynette | umgesetzt, im Prüfwerkzeug getestet, Test im Spiel offen: [docs/umsetzung-9-vault-city.md](docs/umsetzung-9-vault-city.md) |
| 10 | NCR: „Etablissement Nr. 9“ (vier Wege, Auflage), Madame Dora, Vortis' Angebot, „Die Reinen“ mit Ruth Calloway in fünf Akten, Registratur | umgesetzt, im Prüfwerkzeug getestet, Test im Spiel offen: [docs/umsetzung-10-ncr.md](docs/umsetzung-10-ncr.md) |
| 11 | San Francisco: „Die Duldung“ (Wen, Tanker), Madame Kwan, Schmuggelkammer und Siegel, Razzia der Shi, Hubologen | umgesetzt, im Prüfwerkzeug getestet, Test im Spiel offen: [docs/umsetzung-11-san-francisco.md](docs/umsetzung-11-san-francisco.md) |
| 12 | „Blut auf der Virgin Street“: Carlo Venuti in vier Akten und drei Enden, Miss Kittys Angebot (fünf Wege), Kittys Kralle | umgesetzt, im Prüfwerkzeug getestet, Test im Spiel offen: [docs/umsetzung-12-virgin-street.md](docs/umsetzung-12-virgin-street.md) |
| 13 | Talente: Vesper, Abigail Kessler, Talus und Julian Rook mit Anwerbe-Wegen, Loyalität, Tyrannen-Varianten und einer Woche Vorwarnung vor dem Tod | umgesetzt, im Prüfwerkzeug getestet, Test im Spiel offen: [docs/umsetzung-13-talente.md](docs/umsetzung-13-talente.md) |

Die übrigen Schritte 14–16 stehen im [Fahrplan](docs/fahrplan.md).

## Werkzeuge

- `tools/economy_sim.py`: Balancing-Prototyp des Wirtschaftsmodells. Er rechnet nur mit Ganzzahlen, damit er nach SSL übertragbar bleibt.

  ```
  python3 tools/economy_sim.py [wochen] [stadt]
  # stadt: den | new_reno | redding | ncr | vault_city | san_fran
  ```

- `tools/ausbau_sim.py`: Ausbaupfade der sechs Bordelle (Phase 2). Er rechnet Gewinn und Amortisation je Upgrade aus und erzeugt die Tabellen für die Doku. Seine Modulliste ist die einzige Quelle für Kosten und Effekte im Spiel.
- `tools/gen_katalog.py`: erzeugt daraus `scripts_src/headers/rl_katalog.h` und die Modultexte (läuft bei jedem Build mit).
- `tools/check_msg.py`: prüft, ob jede im Code verwendete Textnummer in der passenden `.msg` steht und ob alle Spieltexte reines ASCII sind (läuft bei jedem Build mit).
- `tools/fomap.py`: liest und schreibt Fallout-2-Karten (.MAP). `pruefen` liest Karten ein und schreibt sie byte-gleich zurück, `info` zeigt den Kopf.
- `tools/fomap_bild.py`: schematische Draufsicht einer Karte als PNG, mit Hexnummern zum Planen von Positionen.
- `tools/bau_karten.py`: alle Kartenpositionen an einer Stelle. Baut die Innenkarten aus Vorlagen des RPU und erzeugt `rl_karten.h` (läuft bei jedem Build mit).
- `tools/intvm.py` und `tools/test_skripte.py`: führen die kompilierten Skripte in Python aus und spielen Dialoge, Wochen und Kartenwechsel automatisch durch. Dazu gehört ein Abgleich der Wochenrechnung mit dem Simulator ([Prüfwerkzeug](docs/pruefwerkzeug.md)).
- `tools/paket.py`: packt einen Build als sfall-Mod-Ordner `mods/rotlicht` für ein bestimmtes RPU-Release, mit Anleitung ([Umsetzung 2, Abschnitt 4.1](docs/umsetzung-2-die-gosse.md#41-testpaket-empfohlen)).

  ```
  python3 tools/ausbau_sim.py [stadt|alle] [fair|branchenueblich|ausbeuterisch]
  python3 tools/ausbau_sim.py --md fair
  ```

## Skripte bauen

Die Skripte liegen in `scripts_src/` (SSL, sfall-Dialekt), die Spieltexte in `text_src/english/` (englisch, reines ASCII: Dialoge, Meldungen, Endslide-Untertitel, Titel; siehe [Spieltexte auf Englisch](docs/spieltexte-englisch.md)). Zeilen, die in Dateien der Basisinstallation eingefügt werden (`scripts.lst`, `vault13.gam`, `endgame.txt`, `karmavar.txt`, `maps.txt`, `city.txt`), liegen in `install/`. Gebaut wird mit dem sfall-Compiler `sslc` gegen die Header des Fallout 2 Restoration Project (RPU) und die sfall-Header. Die genaue Anleitung steht in [Phase 5, Abschnitt 10](docs/phase-5-technik.md#10-bauen-und-testen).

```
SSLC=/pfad/zu/sslc FO2_SCRIPTS_SRC=/pfad/zu/rpu/scripts_src tools/build_scripts.sh
```

`FO2_SCRIPTS_SRC` zeigt dabei in einen Klon des RPU-Repositorys. Aus dessen `data/maps` baut das Skript die Innenkarten nach `build/maps/` ([Umsetzung 2, Abschnitt 4](docs/umsetzung-2-die-gosse.md#4-installation)).

