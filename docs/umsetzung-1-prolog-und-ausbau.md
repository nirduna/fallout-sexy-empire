# Umsetzung 1 – Prolog „Essies Schulden“ und Ausbau-Dialog

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Umgesetzt. Alle Skripte kompilieren ohne Fehler und ohne Warnungen gegen das Restoration Project (RPU) und den Unofficial Patch. Alle Texte sind automatisch geprüft. **Im Spiel noch nicht getestet**, weil hier keine Spieldaten vorliegen. Die Debug-Taste in Abschnitt 6 ist dafür gebaut.
**Grundlage:** [Phase 1](phase-1-core-loop-und-wirtschaft.md) (Prolog, Ansatz A), [Phase 2](phase-2-standorte-und-ausbau.md) (Modulkatalog), [Phase 3](phase-3-quests-rivalen-uebernahmen.md) (Abschnitt 2.1), [Phase 5](phase-5-technik.md) (Technik).

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`scripts_src/rotlicht/rlkolbe.ssl`](../scripts_src/rotlicht/rlkolbe.ssl) | **neu:** Kolbe, Metzgers Eintreiber, mit den fünf Lösungswegen des Prologs |
| [`scripts_src/rotlicht/rlessie.ssl`](../scripts_src/rotlicht/rlessie.ssl) | Essie: Einstieg in den Prolog, Reaktion auf den gewählten Weg, danach Managerin |
| [`scripts_src/headers/rl_prolog.h`](../scripts_src/headers/rl_prolog.h) | **neu:** Schulden mit Zinsen, Start und Abschluss des Prologs mit allen Folgen |
| [`scripts_src/headers/rl_manager.h`](../scripts_src/headers/rl_manager.h) | **neu:** gemeinsame Dialogknoten aller Manager, mit Ausbau-Menü |
| [`scripts_src/headers/rl_katalog.h`](../scripts_src/headers/rl_katalog.h) | **neu, erzeugt:** die 23 Module aus Phase 2 |
| [`scripts_src/headers/rotlicht.h`](../scripts_src/headers/rotlicht.h) | 48 statt 32 Felder pro Haus (Baustelle, gekaufte Module), Welt-Felder für den Prolog, Übernahme alter Spielstände |
| [`scripts_src/global/gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | Bauwochen und Fertigstellung, Metzger bemerkt den Diebstahl, Debug-Taste F9 |
| [`text_src/german/dialog/rlkolbe.msg`](../text_src/german/dialog/rlkolbe.msg) | **neu:** Kolbes Texte, auch als Verwalter |
| [`text_src/german/dialog/rlessie.msg`](../text_src/german/dialog/rlessie.msg) | Prolog, Reaktionen und Ausbau in Essies Stimme |
| [`text_src/german/dialog/_rl_module.inc`](../text_src/german/dialog/_rl_module.inc) | **erzeugt:** Modulnamen und Effekte, wird in jede Manager-Textdatei eingefügt |
| [`tools/gen_katalog.py`](../tools/gen_katalog.py) | **neu:** erzeugt Katalog und Modultexte aus `tools/ausbau_sim.py` |
| [`tools/check_msg.py`](../tools/check_msg.py) | **neu:** prüft, ob jede im Code verwendete Textnummer existiert |

---

## 2. Der Prolog

### 2.1 Ablauf

1. **Essie** (erste Begegnung) erzählt von den Schulden bei Metzger. Wer „Ich regle das mit Kolbe“ wählt, startet den Prolog: 1.200 $ Schulden, dazu 50 $ Zinsen pro Woche.
2. **Kolbe** steht im Haus und verhandelt. Er ist eine neue Figur. Metzgers Vanilla-Skript bleibt unberührt, so wie in Phase 2 festgelegt („minimal-invasiv“). Kolbe richtet Metzger aus, was der Spieler anbietet.
3. Nach dem Abschluss gehört die Gosse dem Spieler. Essie reagiert einmal auf den gewählten Weg und führt danach das Haus.

### 2.2 Die fünf Wege

| Weg | Wie im Code | Check | Folgen |
|---|---|---|---|
| **Bezahlen** | Kolbe: „Hier ist das Geld.“ | – · einmal **Barter 50**: ein Viertel weniger | Metzger neutral, Essie loyal (Führung 45) |
| **Metzger überzeugen** | Kolbe: „[Speech] Ein volles Haus bringt ihm jede Woche Kunden …“ | **Speech 60**, ein Versuch | Keine Schulden, dafür dauerhaft 10 % zusätzliche Abgabe an die Gilde. Metzger wird Partner, Essie misstrauisch (Führung 35) |
| **Kolbe verprügeln** | „Verschwinde, oder ich werf dich raus.“ | **Unarmed 60 oder STR 7**, ein Versuch | Sieg: Der Grundbetrag der Schulden halbiert sich, dann bezahlen. Folge: Metzger respektiert dich, Hitze +10, Essie beeindruckt (Führung 50). Niederlage: 15 Schaden, der Weg ist verbraucht |
| **Schuldschein stehlen** | „[Steal] (in seine Jacke greifen)“ | Die Option erscheint ab **Steal 50 oder Sneak 60**. Erfolg mit einer Chance in Höhe des besseren Werts, ein Versuch | Erfolg: keine Schulden, Metzger merkt es **zwei Wochen später** und wird Feind. Erwischt: Die Gilde ist Feind, und Kolbe greift an |
| **Essie ausliefern** | „Nimm sie mit. Metzger kriegt Essie, ich kriege das Haus.“ + Rückfrage | – | Karma −25. Essie verschwindet, **Kolbe führt das Haus** (Führung 30, 10 % zusätzlich an Metzger). „Ketten“ startet im Tyrannen-Zweig, Metzger wird Freund |

Nach jedem Weg beginnt Akt 1 der Questline „Ketten“ (`RL_W_KETTEN = 1`, Phase 3).

---

## 3. Der Ausbau-Dialog

- **Einstieg:** Im Manager-Menü fragt man „Was ließe sich ausbauen?“.
- **Drei Gruppen**, jede mit höchstens vier Angeboten:
  - *Haus & Einrichtung:* Hausklasse, Einrichtung, Bar, VIP-Trakt.
  - *Betrieb:* Sicherheit, Personalquartiere, Krankenstube, Kontor.
  - *Besonderes:* die Module der jeweiligen Stadt.
- **Nächste Stufe je Kette:** Pro Kette wird nur die nächste freie Stufe angeboten, also erst Einrichtung I, dann II, dann III. Voraussetzungen und erlaubte Städte kommen aus dem Katalog: Hausklasse 3 nur in New Reno, den VIP-Trakt erst ab Hausklasse 2 und nur in New Reno, Vault City, NCR und San Francisco, die Entzugsstube erst mit Krankenstube, das Siegel der Shi erst nach deren Gefallen.
- **Bezahlen:** zuerst aus der Kasse des Hauses, der Rest aus der Tasche des Spielers.
- **Bauzeit** 1 Woche für ein Modul, 2 bzw. 3 Wochen für eine Hausklasse. So lange hat das Haus **halbe Kundschaft** (Phase 2, Abschnitt 3). Es läuft immer nur eine Baustelle pro Haus.
- **Fertigstellung** im Wochentakt: Die Effekte aus dem Katalog werden angewendet, und eine Meldung erscheint.
- **Vorläufig:** Neue Zimmer werden sofort besetzt, bis die Anwerbung aus Phase 4 umgesetzt ist.

**Eine Quelle für alle Werte:** Kosten und Effekte stehen nur in `tools/ausbau_sim.py`. `tools/gen_katalog.py` erzeugt daraus `rl_katalog.h` und die Modultexte. Der Build ruft das Skript bei jedem Lauf auf. Was der Simulator durchrechnet, ist damit genau das, was im Spiel gebaut wird.

---

## 4. Gemeinsame Manager-Knoten

Jede Madame und jeder Manager nutzt dieselben Knoten aus `rl_manager.h`: Bericht, Kasse, Preise, Anteil, Moral, Krisen und Ausbau. Die Texte stehen in der eigenen `.msg`-Datei, jeweils in der eigenen Stimme. Kolbe klingt deshalb anders als Essie, bei gleicher Funktion.

| Textnummern | Inhalt |
|---|---|
| 100–194 | Bericht, Kasse, Preise, Anteil, Moral, Krisen, Debug |
| 300–342 | eigene Szenen der Figur (Prolog …) |
| 400–422 / 500–522 | Modulnamen / Moduleffekte (aus `_rl_module.inc`, automatisch eingefügt) |
| 460–477 | Ausbau-Menü |

**Einen neuen Manager anlegen**

1. Skript mit `variable haus, welt, h`.
2. `NAME` definieren und `rl_manager.h` einbinden.
3. `call RLM_Start;` im Dialog aufrufen.
4. Nach `end_dialogue` das Makro `RLM_NACH_DIALOG` setzen.
5. In die Textdatei die Nummern 100–194 und 460–477 schreiben, dazu die Zeile `# @include _rl_module.inc`.
6. `tools/check_msg.py` meldet jede fehlende Nummer.

---

## 5. Was beim Umsetzen aufgefallen ist

- **Überschneidende Textnummern:** Der neue Textprüfer fand sofort eine Überschneidung. Die Moduleffekte (440 + ID) liefen in die Menüzeilen 460–462. Sie liegen jetzt bei 500–522, und der Code verwendet Konstanten statt Zahlen.
- **Groß-/Kleinschreibung:** `sslc` unterscheidet sie nicht. Die Variable `rlm_abspann` kollidierte deshalb mit der Prozedur `RLM_Abspann`. Die Variablen heißen jetzt anders.
- **Neues Speicherformat:** Das Haus-Array hat jetzt 48 Felder pro Haus. Ein Spielstand mit dem alten Format (32 Felder) wird beim Laden automatisch umkopiert.

---

## 6. Testen

1. Mit Debug bauen:

   ```bash
   RL_DEBUG=1 SSLC=... FO2_SCRIPTS_SRC=/pfad/rpu/scripts_src tools/build_scripts.sh
   ```

2. Installieren:
   - `build/scripts/*.int` nach `data/scripts/`
   - `build/text/german/dialog/*.msg` nach `data/text/german/dialog/`
   - die zwei Zeilen aus `install/scripts.lst.add` an `scripts.lst` anhängen
3. Im Spiel **F9** drücken: Essie und Kolbe erscheinen neben dir. Die Figuren sind vorläufig Vanilla-Figuren (Durchschnittsbäuerin, Schläger), bis es eigene Protos und die Innen-Map `RLDEN01` gibt.

| Test | Erwartung |
|---|---|
| Essie ansprechen, „Wie viel?“, dann „Ich regle das mit Kolbe“ | Prolog läuft, Essie nennt 1.200 $ |
| 1 Woche warten, Essie fragen | 1.250 $ |
| Kolbe: [Barter] mit Barter ≥ 50, dann bezahlen | Betrag −25 %, Haus gehört dir, Essie sagt Zeile 331 |
| Kolbe: [Speech] mit Speech ≥ 60 | kein Geld weg, Tribut der Gosse 20 %, Essie misstrauisch (332) |
| Kolbe: Faustkampf mit STR 7, dann bezahlen | halber Grundbetrag, Hitze 10, Essie beeindruckt (333) |
| Kolbe: Faustkampf mit STR 5 und Unarmed < 60 | 15 Schaden, Option verschwindet |
| Kolbe: [Steal] gelingt, zwei Wochen warten | Meldung „Metzger hat nachgezählt …“ |
| Kolbe: [Steal] misslingt | Kolbe greift an |
| Kolbe: Essie ausliefern | Abblende, Essie weg, Karma −25, Kolbe bietet das Manager-Menü |
| Manager: Ausbau → Betrieb → Sicherheit I kaufen | Kasse bzw. Geld −400 $, nach 1 Woche „Der Ausbau ist fertig“, Sicherheit +10 |
| Manager: Ausbau während einer Baustelle | „Es wird schon gebaut: …“ |
| Manager: „[Debug] Zeig mir den Abspann“ | Endslides mit unserer Slide nach dem New-Reno-Block (Phase 6) |

---

## 7. Nächste Schritte

1. **Innen-Map `RLDEN01`** und das Tür-Skript auf der Den-Map (Mapper-Arbeit), dazu Protos und Grafiken für Essie und Kolbe.
2. **Anwerbung** aus Phase 4 (Werben/Zwingen). Damit entfällt die vorläufige Sofortbesetzung neuer Zimmer.
3. **Questline „Ketten“**, Akt 1: Metzgers Angebot, aufbauend auf `RL_W_METZGER` und `RL_W_KETTEN_ZWEIG`.
4. **Dunkle Module** (Riegel außen, gezinkte Waage, Akte …) mit ihren Sonderregeln.
5. **Consigliere** im Strumpfband und die übrigen Manager, alle über `rl_manager.h`.
6. **Umlaute prüfen:** Zeigt Essie sie falsch an, mit `TEXT_ENCODING=UTF-8` bauen (siehe Phase 5, Abschnitt 8).
