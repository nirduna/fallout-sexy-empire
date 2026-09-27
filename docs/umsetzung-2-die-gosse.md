# Umsetzung 2 – Die Gosse: Eingang in der Den und Innenkarte RLDEN01

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Umgesetzt und automatisch geprüft, aber **nicht im Spiel gesehen**, weil hier keine Spielgrafiken vorliegen:
- Die Skripte kompilieren gegen das Restoration Project (RPU) und den Unofficial Patch, mit und ohne Debug.
- Die Karte entsteht aus Beckys Keller im RPU, und das Werkzeug liest sie byte-gleich wieder ein.
- Die Sichtprüfung im Spiel übernimmst du mit der Prüfliste in Abschnitt 5.

**Grundlage:** [Phase 2](phase-2-standorte-und-ausbau.md) (Abschnitt 2.1, Map `RLDEN01`), [Phase 5](phase-5-technik.md) (Abschnitt Karten), [Umsetzung 1](umsetzung-1-prolog-und-ausbau.md) (Essie und Kolbe).

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`tools/fomap.py`](../tools/fomap.py) | **neu:** liest und schreibt Fallout-2-Karten (.MAP, Version 20). Alle 174 Karten des RPU liest es byte-gleich wieder ein |
| [`tools/fomap_bild.py`](../tools/fomap_bild.py) | **neu:** schematische Draufsicht einer Karte als PNG (Wände, Türen, Figuren, Scroll-Grenzen, Hexnummern) |
| [`tools/data/proto_extra.json`](../tools/data/proto_extra.json) | **neu:** Untertypen von 2.339 Protos, die `fomap.py` beim Lesen der RPU-Karten gelernt hat. Damit braucht es die Protos aus `master.dat` nicht. 390 davon lassen sich gegen die Protos im RPU-Repository prüfen, und alle stimmen |
| [`tools/bau_karten.py`](../tools/bau_karten.py) | **neu:** alle Kartenpositionen an einer Stelle. Baut `rlden01.map`, erzeugt `rl_karten.h` und die Bilder unten |
| [`scripts_src/headers/rl_karten.h`](../scripts_src/headers/rl_karten.h) | **neu, erzeugt:** Hexfelder und PIDs für die Skripte |
| [`scripts_src/rotlicht/rlgosse.ssl`](../scripts_src/rotlicht/rlgosse.ssl) | **neu:** die Kellertreppe auf Den Business 2 (Ansehen, Benutzen → RLDEN01) |
| [`scripts_src/rotlicht/rlden01.ssl`](../scripts_src/rotlicht/rlden01.ssl) | **neu:** Kartenskript der Gosse (Kellerlicht, Satz beim ersten Besuch) |
| [`scripts_src/global/gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | setzt die Treppe auf Den Business 2; Debug-Tasten F10 und F11 |
| [`scripts_src/headers/rotlicht.h`](../scripts_src/headers/rotlicht.h) | Skripte `SCRIPT_RLGOSSE` (Basis + 2) und `SCRIPT_RLDEN01` (Basis + 3), Welt-Feld `RL_W_GOSSE_TREPPE` |
| [`text_src/german/dialog/rlgosse.msg`](../text_src/german/dialog/rlgosse.msg), [`rlden01.msg`](../text_src/german/dialog/rlden01.msg) | **neu:** Texte der Treppe und der Karte |
| [`install/maps.txt.add`](../install/maps.txt.add), [`install/city.txt.add`](../install/city.txt.add), [`text_src/german/game/map.msg.add`](../text_src/german/game/map.msg.add) | **neu:** Karteneintrag, Zuordnung zur Den, Kartenname |
| [`install/scripts.lst.add`](../install/scripts.lst.add) | zwei Zeilen mehr (`rlgosse`, `rlden01`) |
| [`tools/build_scripts.sh`](../tools/build_scripts.sh) | baut jetzt auch die Karte (`build/maps/rlden01.map`) |
| [`docs/bilder/`](bilder/) | **neu:** Draufsichten für die Prüfliste |

---

## 2. Wie es funktioniert

### 2.1 Der Eingang: eine Kellertreppe in der Ruine

- **Ort:** Die Ruine auf der East Side von Den Business 2 liegt zwischen der Sklavengilde und Mom's Diner. In ihrem überdachten Rest steht die Treppe auf **Hex 18458**. Das ist die Gasse aus Phase 2: Mom's Diner auf der einen Seite, die Pferche der Gilde auf der anderen.
- **Objekt:** Die Treppe ist dieselbe wie Beckys Kellertreppe in denbus1 („Treppe“, PID `0x2000164`, Grafik `stway.frm`). Sie passt also zur Den.
- **Keine Änderung an der Vanilla-Karte:**
  - Beim Betreten von Den Business 2 setzt `gl_rotlicht` die Treppe, falls sie noch fehlt.
  - Wurde ein Spielstand geladen, bevor es die Treppe gab, holt der Wochentakt das nach (er läuft etwa alle 10 Sekunden).
  - Die Karten des RPU bleiben unberührt. Das Addon verträgt sich damit mit jeder RPU-Fassung.
- **Benutzen:**
  - Der Spieler geht zur Treppe, und `rlgosse.ssl` lädt `rlden01.map`.
  - Mitten im Kampf geht das nicht („Nicht mitten im Kampf.“).
- **Verlegen:** Ändert sich `GOSSE["treppe_hex"]` in einer späteren Fassung, entfernt das Skript die alte Treppe beim nächsten Besuch. Dafür merkt es sich den Hex in `RL_W_GOSSE_TREPPE`.

### 2.2 Die Innenkarte RLDEN01

`tools/bau_karten.py` baut die Karte aus **Beckys Keller** (denbus1, Ebene 1). Das ist ein Gewölbe im Stil der Den mit Holztür, Tischen, Couches, Bett und Laternen.

| Was | Wo | Woher |
|---|---|---|
| Boden, Wände, Einrichtung, Lichtquellen, Scroll-Grenzen | Ebene 0 | Beckys Keller, unverändert |
| Destille | – | **entfernt** (Vanilla-Quest um Beckys Schnaps, `diStill`) |
| Treppe nach oben | Hex 16666 | Beckys Treppe, Ziel geändert: Den Business 2, Hex 18658, Blick Südwest |
| Startpunkt | Hex 17066 | unten an der Treppe |
| **Essie** | Hex 17866, Blick zur Treppe | Figur wie Vanilla-Bäuerin (Grafik, Trefferpunkte, KI), Skript `rlessie` |
| **Kolbe** | Hex 17270, an der Tür zum hinteren Raum | Figur wie Vanilla-Schläger, Skript `rlkolbe` |
| Hinterer Raum mit Couches und Bett | hinter der Holztür (Hex 16872) | Beckys Keller. Die Tür ist nicht verschlossen (generisches Skript `ZIWodDor`) |

- **Die Karte liegt nicht im Repository.** Der Build liest die Vorlage aus dem RPU (`FO2_MAPS`, Standard `$FO2_SCRIPTS_SRC/../data/maps`), baut daraus die Karte und prüft sie selbst:
  - Das Werkzeug liest die Karte byte-gleich wieder ein.
  - Jede SID hat einen passenden Skriptsatz.
  - Essie und Kolbe haben eigene Objekt-IDs.
- Die Skriptnummern der Karte hängen von `RL_SCRIPT_BASE` ab. Darum entsteht die Karte bei jedem Build neu.
- Ohne Karte gibt es weiter die Debug-Taste F9 aus Umsetzung 1.

### 2.3 Zurück in die Den

Die Treppe in RLDEN01 führt ohne Skript zurück. Ihr Ziel steht in den Objektdaten: Karte 7 (Den Business 2), Hex 18658, Ebene 0. Der Spieler steht dann direkt neben der Kellertreppe.

---

## 3. Abweichung vom Entwurf (bitte bestätigen)

Phase 2 beschreibt die Gosse als **baufälliges Haus mit Tür und Laterne**, mit drei Ebenen:

| Ebene | Inhalt |
|---|---|
| 0 | Schankraum und drei Verschläge |
| 1 | Obergeschoss (ab Hausklasse 2) |
| 2 | Keller |

Umgesetzt ist jetzt Folgendes:

- **Die Gosse liegt im Gewölbe unter der Ruine.** Die alte Absteige ist oben eingestürzt, unten hat Essie ihr Haus eingerichtet. Die Laterne hängt über dem Abgang.
- **Grund:** Eine Tür müsste genau in eine bestehende Wand der Vanilla-Karte passen. Das lässt sich ohne Grafiken nicht prüfen. Die Kellertreppe steht frei und ist dieselbe wie bei Becky.
- **Ebenen:**
  - Ebene 0 ist das Gewölbe, mit dem vorderen Raum als Schankraum und dem hinteren als Verschläge.
  - Das „Obergeschoss“ für Hausklasse 2 würde zu einem **zweiten Gewölbe** mit zwei Zimmern mit echten Türen.
  - Der **Keller** für „Ketten“ Akt 2 wird Ebene 2.
  - Beide Ebenen kommen, wenn ihre Inhalte dran sind.
- **Nicht umgesetzt:** Phase 5 sah vor, dass die Tür verschlossen bleibt, bis das Haus dem Spieler gehört. Die Gosse ist aber ein öffentliches Haus, und der Prolog findet darin statt. Deshalb ist die Treppe immer offen.

Wenn dir ein echtes Haus mit Tür lieber ist, lässt sich das nach der Sichtprüfung nachrüsten. Dann setzen wir ein Türobjekt an eine Wand, die du im Spiel aussuchst.

---

## 4. Installation

1. **Bauen** (mit Debug für die Prüfliste):

   ```bash
   RL_DEBUG=1 SSLC=/pfad/sslc FO2_SCRIPTS_SRC=/pfad/rpu/scripts_src tools/build_scripts.sh
   ```

   `FO2_SCRIPTS_SRC` zeigt in einen Klon des RPU-Repositorys. Dessen `data/maps` dient als Vorlage. Wenn die Vorlage woanders liegt: `FO2_MAPS=/pfad/zu/maps`.

2. **Kopieren** ins Spielverzeichnis:

   | Quelle | Ziel |
   |---|---|
   | `build/scripts/*.int` | `data/scripts/` |
   | `build/text/german/dialog/*.msg` | `data/text/german/dialog/` |
   | `build/maps/rlden01.map` | `data/maps/` |

3. **Einfügen** in Dateien der Installation:

   | Quelle | Ziel | Wo |
   |---|---|---|
   | `install/scripts.lst.add` | `data/scripts/scripts.lst` | ans Ende. Die Reihenfolge ist wichtig: `rlessie`, `rlkolbe`, `rlgosse`, `rlden01` |
   | `install/maps.txt.add` | `data/data/maps.txt` | ans Ende, als `[Map 173]` |
   | `install/city.txt.add` | `data/data/city.txt` | im Abschnitt der Den (`[Area 01]`) nach `entrance_2` |
   | `build/text/german/game/map.msg.add` | `data/text/german/game/map.msg` | ans Ende |

   Stecken `maps.txt`, `city.txt` oder `map.msg` bei dir nur im Archiv des RPU, musst du sie zuerst herausziehen, zum Beispiel mit einem DAT-Werkzeug. Die Fassungen im RPU-Repository sollten gleich sein, **wenn sie zur installierten RPU-Version gehören**.

4. **Andere Kartennummer:** Hat deine `maps.txt` mehr oder weniger als 173 Einträge, nimm die nächste freie Nummer.
   - Trage sie in `maps.txt.add` ein.
   - Setze die Nummern in `map.msg.add` auf `200 + 3 × Nummer` (Ebenen 0 bis 2).
   - Baue mit `RL_MAP_INDEX=<Nummer>`.

---

## 5. Prüfliste für die Sichtprüfung

Die Bilder sind schematisch:

| Farbe | Bedeutung |
|---|---|
| braun | Wände |
| grau | Szenerie |
| gelb | Türen |
| rot | Figuren |
| magenta | Rand des Bereichs, in dem die Kamera scrollen kann |
| cyan | unsere Punkte |
| blaue Rauten | Dächer (96 Pixel höher gezeichnet, wie im Spiel) |

![Übersicht Den Business 2](bilder/gosse_eingang_uebersicht.png)

![Eingang in der Ruine](bilder/gosse_eingang.png)

![RLDEN01](bilder/rlden01.png)

**Den Business 2**

| # | Prüfen | Erwartung | Wenn nicht |
|---|---|---|---|
| 1 | Zur Ruine östlich der Sklavengilde gehen (mit Debug: **F11**) | Eine Kellertreppe steht in der Ruine, an Hex 18458 | Hexnummer des Ortes notieren (Mapper oder ungefähr per Bild) |
| 2 | Wie sieht die Treppe aus? | Sie ragt nicht in eine Wand, steht nicht halb im Schutt und ist ganz zu sehen | Beschreiben, was stört. Ich verlege sie |
| 3 | Unter das Dach der Ruine gehen | Das Dach blendet sich aus, die Treppe bleibt sichtbar | – |
| 4 | Maus über die Treppe | „Eine Treppe führt unter die Ruine.“ | Skript fehlt: Zeilen in `scripts.lst` prüfen |
| 5 | Treppe untersuchen | Text mit der Laterne über dem Abgang | – |
| 6 | Treppe benutzen | Der Spieler geht hin und landet in der Gosse | Meldung notieren. Meist fehlt der Eintrag in `maps.txt` |

**RLDEN01 (Die Gosse)**

| # | Prüfen | Erwartung | Wenn nicht |
|---|---|---|---|
| 7 | Ankunft (mit Debug direkt: **F10**) | Unten an der Treppe, gedämpftes Kellerlicht, beim ersten Mal der Satz „Die Gosse. Die Luft ist dick …“ | – |
| 8 | Wo die Destille stand (Hex 17062) | Nichts Schwebendes, kein Schatten ohne Objekt | Beschreiben. Dann entferne ich weitere Reste |
| 9 | Essie und Kolbe | Essie am Tisch, Blick zur Treppe. Kolbe an der Tür zum hinteren Raum. Beide ansprechbar, der Prolog läuft wie in Umsetzung 1 | Stehen sie in einer Wand? Hexnummern notieren |
| 10 | Holztür zum hinteren Raum | Lässt sich öffnen, dahinter Couches und Bett | – |
| 11 | Treppe nach oben benutzen | Zurück auf Den Business 2, direkt neben der Kellertreppe | – |
| 12 | Speichern und Laden in der Gosse | Der Spielstand heißt „Die Gosse“, Pip-Boy und Automap funktionieren | Eintrag in `map.msg` oder `city.txt` prüfen |
| 13 | Den Business 2 zweimal verlassen und wieder betreten | Es gibt nur **eine** Treppe | – |
| 14 | Prolog abschließen (nicht „ausliefern“), die Gosse verlassen und wieder betreten | Kolbe ist weg, Essie führt das Haus | – |

**Anpassen:** Alle Positionen stehen in `tools/bau_karten.py` (`GOSSE`, `RLDEN01`). Nach einer Änderung:

```bash
python3 tools/bau_karten.py header   # rl_karten.h
tools/build_scripts.sh               # Skripte und Karte neu
```

Eine verlegte Treppe verschwindet im Spielstand beim nächsten Betreten von der alten Stelle.

**Mit dem Mapper ansehen:**
1. Die Einträge aus Abschnitt 4 müssen installiert sein.
2. `rlden01.map` öffnen. Alle Objekte liegen auf Ebene 0.
3. Essie und Kolbe tragen die Skripte `rlessie` und `rlkolbe`.

Nicht im Mapper speichern: Der nächste Build würde die Änderungen überschreiben. Positionen gehören in `bau_karten.py`.

---

## 6. Technische Notizen

- **Kartenformat:** abgeleitet aus dem Quellcode von fallout2-ce (map.cc, scripts.cc, object.cc, proto.cc). Siehe Kopf von `tools/fomap.py`.
- **Kartenkopf:** Die Engine ermittelt die Kartennummer beim Laden über den Namen in `maps.txt`. Die Nummer im Kartenkopf ist nur Information.
- **Skriptindex im Kartenkopf:** zählt ab 1, wie `SCRIPT_*`. In Skriptsätzen und Objekten zählt er ab 0.
- **Lokale Variablen:** Der Build legt keine an. Die Engine vergibt sie beim ersten Start eines Skripts.
- **Objekt-IDs:** In Vanilla-Karten sind sie nicht eindeutig, auch nicht bei Objekten mit Skript. Die Engine verbindet Objekt und Skript über die SID.
- **Treppenziel** (Stairs, Ladder): `Hex | Ebene << 29 | Blickrichtung << 26`.
- **Globale Skripte** bekommen `map_enter_p_proc` bei jedem Kartenwechsel, in sfall und in fallout2-ce.

---

## 7. Nächste Schritte

1. **Sichtprüfung** nach Abschnitt 5, danach Positionen und gegebenenfalls die Abweichung aus Abschnitt 3 festlegen.
2. **Anwerbung** aus Phase 4 (Werben/Zwingen). Damit entfällt die vorläufige Sofortbesetzung neuer Zimmer.
3. **Questline „Ketten“**, Akt 1: Metzgers Angebot, aufbauend auf `RL_W_METZGER` und `RL_W_KETTEN_ZWEIG`.
4. **Eigene Figuren** für Essie und Kolbe (Protos, Namen im Spiel). Bis dahin tragen sie Vanilla-Grafiken.
5. **Weitere Ebenen** der Gosse (zweites Gewölbe, Keller), sobald Hausklasse 2 und „Ketten“ Akt 2 sie brauchen.
