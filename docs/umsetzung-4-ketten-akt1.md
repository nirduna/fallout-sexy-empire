# Umsetzung 4 – „Ketten“, Akt 1: Das Angebot

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Umgesetzt und kompiliert, **Test im Spiel offen**.
- Alle Skripte kompilieren gegen das RPU und den Unofficial Patch, mit und ohne Debug und mit Selbsttest.
- Die Soll-Werte des Selbsttests und die Ausbau-Tabellen aus Phase 2 sind unverändert.

**Grundlage:**
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 3.2: Questline „Ketten“, Akt 1
- [Phase 2](phase-2-standorte-und-ausbau.md), Abschnitt 2.1: Modul „Riegel außen“
- [Phase 4](phase-4-personal-talente-ereignisse.md), Abschnitt 2.3: Metzger als Tyrannen-Quelle
- [Phase 6](phase-6-karma-ruf-endings.md): Karma, Stadtruf, „Seelenverkäufer“

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`scripts_src/rotlicht/rlkolbe.ssl`](../scripts_src/rotlicht/rlkolbe.ssl) | Kolbe bringt Metzgers Angebot und bleibt bis zur Antwort. Annehmen, ablehnen, „Und wenn ich nein sage?“, zu wenig Geld. Stirbt er vorher, ist die Gilde Feind |
| [`scripts_src/rotlicht/rlessie.ssl`](../scripts_src/rotlicht/rlessie.ssl) | Essie reagiert einmal auf die Entscheidung |
| [`scripts_src/rotlicht/rlden01.ssl`](../scripts_src/rotlicht/rlden01.ssl) | Das Kartenskript holt Kolbe zurück, wenn das Angebot aussteht und er die Gosse schon verlassen hat (Spielstände aus Umsetzung 1–3) |
| [`scripts_src/headers/rotlicht.h`](../scripts_src/headers/rotlicht.h) | Zwangspersonal als Anzahl (`RL_F_ZWANG`).<br>`rl_riegel_aussen`, `rl_zwang_dazu`, `rl_ketten_akt1`.<br>`rl_personal_verlust` unterscheidet Kündigung und Flucht.<br>Die Wochenrechnung kennt den Anteil ohne Zwangspersonal und den Moral-Deckel |
| [`scripts_src/headers/rl_manager.h`](../scripts_src/headers/rl_manager.h) | Im Personal-Menü die Zahl im Keller und Metzgers Nachschub. „Riegel innen“ ist gesperrt, sobald außen verriegelt ist. Gemeinsame Bezahl-Hilfe `rlm_bezahlen` |
| [`scripts_src/global/gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | Flucht aus dem Pferch. Bei der Moral zählt nur, wer gehen kann |
| [`tools/bau_karten.py`](../tools/bau_karten.py) | schreibt jetzt auch Essies und Kolbes Hex nach `rl_karten.h` |
| [`tools/economy_sim.py`](../tools/economy_sim.py) | `staff` und `forced_labor`: Anteil ohne Zwangspersonal, Moral-Deckel, Karma −5 |
| Texte | Kolbe 350–364, Essie 350–352, beide 494–498, `rotlicht.msg` 121 |

---

## 2. Ablauf

1. **Kolbe bleibt:** Nach dem Prolog, egal auf welchem Weg, bleibt Kolbe in der Gosse. Im nächsten Gespräch bringt er Metzgers Angebot: „Two from the pens. Young, healthy, they don't talk back.“
   - **Preis:** 150 $ für beide, der halbe Preis.
   - **Umbau:** Metzgers Leute drehen die Riegel an der Kellertür um, für weitere 200 $.
   - **Bezahlung:** zuerst aus der Kasse, der Rest aus der Tasche.
2. **Annehmen** („Deal. Bring them.“): Tyrannen-Zweig.
   - **Pferch:** Der Keller wird zum Pferch, mit zwei Plätzen.
   - **Zwei Menschen:** Sie kommen aus den Pferchen, Qualität 30–45.
   - **Riegel innen:** Hatte das Haus ihn schon, bauen Metzgers Leute ihn zurück. Ein begonnener Bau wird abgebrochen.
   - **Metzger:** Er wird „Freund“.
   - **Essie:** Sie führt weiter, aber ihre Führung sinkt um 10.
   - **Kolbe:** Er geht beim nächsten Betreten der Karte.
3. **Ablehnen** („No. Not in my house.“): Fluchtzweig. „Metzger remembers who says no.“ Das merkt sich `RL_W_METZGER_NEIN` für Akt 4 („Tylers Preis“).
4. **Essie** reagiert beim nächsten Gespräch, einmalig:
   - **Angenommen:** „I heard every screw … I won't go down those stairs.“
   - **Abgelehnt:** „I've waited twenty years for somebody to say it to his face.“

**Sonderfälle**

| Lage | Folge |
|---|---|
| Metzger ist tot (Vanilla) | kein Angebot, weiter im Fluchtzweig („The Guild is finished.“). So will es die Anpassung an Vanilla in Phase 3 |
| Der Diebstahl ist aufgeflogen (Metzger ist Feind) | kein Angebot, Fluchtzweig |
| Zu wenig Geld | „Then get it. The offer stands.“ Kolbe wartet |
| Kolbe stirbt vorher | Die Gilde ist Feind, weiter im Fluchtzweig |
| Essie wurde ausgeliefert, Kolbe führt das Haus | Er macht dasselbe Angebot. Ablehnen geht, Metzger gefällt das nicht |

---

## 3. Riegel außen und Zwangspersonal

| Regel | Wert | Quelle |
|---|---|---|
| Plätze im Pferch | +2 Zimmer | Phase 2: „Der Keller wird zum Pferch“ |
| Anteil | Zwangspersonal bekommt keinen. Der Anteil des Hauses sinkt im Verhältnis (z. B. 35 % × 3/5 = 21 %) | Phase 2: „ein Personal-Anteil entfällt“ |
| Moral | Zwangspersonal zählt nicht mit. Die Moral des Hauses ist die der Leute, die gehen könnten, und liegt höchstens bei 50 | siehe Abschnitt 5 |
| Kündigung | Aus dem Pferch kündigt niemand | – |
| Flucht | Beim Flucht-Ereignis fliehen die aus dem Pferch zuerst („One of the ones in the cellar got out.“) | Phase 4 |
| Karma | −5 pro Woche und Haus | Phase 6 |
| Ereignisse | +10 % Chance, Flucht-Gewicht 20 | Phase 4 |
| Stadtruf | −1 alle 2 Wochen | Phase 6 |
| Titel und Ende | Nach 4 Wochen „Seelenverkäufer“, das Ende wird Tyrann | Phase 6 |
| Unterhalt | eine Ausbaustufe mehr (+25 $/Woche) | wie jedes Modul (Phase 2) |
| Nachschub | Im Personal-Menü: „Send word to Metzger“, 150 $ je Person, als „Seelenverkäufer“ 120 $ | Phase 4, 2.3, Phase 6 |

**Wann Metzger nachliefert:**
- solange Metzger lebt und nicht Feind ist
- solange ein Zimmer frei ist

---

## 4. Was es bringt: die Gosse zu Beginn

Hausklasse 1, eingeschwungen (Wochen 13–24, `economy_sim.py`):

| Anteil | ohne Pferch | mit Pferch | Karma in 24 Wochen |
|---|---|---|---|
| branchenüblich | 81 $/Woche | **126 $** | −120 |
| fair | 54 $/Woche (Moral 100) | **91 $** (Moral 50) | −120 |
| ausbeuterisch | −35 $/Woche | −27 $ | −144 |

- **Woher der Gewinn kommt:** Die Den ist arm, die Kundschaft (rund 30 pro Woche) stößt nicht an die Zimmer. Der Pferch bringt sein Geld deshalb vor allem über den gesparten Anteil, nicht über mehr Kunden.
- **Die Tyrannen-Route trägt sich:** Wie Phase 2 es vorsieht, hält sie sich über Zwangspersonal über Wasser.
- **Der Preis:** Titel, Tyrannen-Ende und ein Stadtruf, der jede zweite Woche sinkt.

---

## 5. Entscheidungen in dieser Umsetzung (meine Empfehlungen)

1. **Kolbe statt Metzger:** Kolbe überbringt das Angebot, Metzgers Vanilla-Skript bleibt unberührt, wie beim Prolog.
2. **Moral-Deckel 50 mit Pferch:**
   - „Wer oben arbeitet, hört den Keller.“
   - Ohne diesen Deckel wäre „fairer Anteil plus Pferch“ die beste Strategie des ganzen Hauses: 54 → 177 $ pro Woche bei Moral 100. Das passt weder zum Ton noch zu Phase 6, wo „Anständiges Haus“ nie Zwangspersonal erlaubt.
3. **Metzgers Haltung:**
   - Annehmen macht Metzger zum „Freund“.
   - Ablehnen lässt seine Haltung, wie sie ist, aber er merkt es sich (für Akt 4).
4. **Essie:** Annehmen kostet Essie 10 Führung. Sie bleibt, wie Phase 3 es für die Gosse vorsieht, aber sie „geht nicht mehr in den Keller“.

---

## 6. Testen

1. Testpaket mit Debug bauen ([Umsetzung 2, Abschnitt 4.1](umsetzung-2-die-gosse.md#41-testpaket-empfohlen)).
2. Ein **neues Spiel** ist nicht nötig.
3. Wer den Prolog im Spielstand schon hinter sich hat, findet Kolbe beim nächsten Betreten der Gosse wieder vor. Sonst: bei Essie „[Debug] Take over the Gutter“.

| Test | Erwartung |
|---|---|
| Kolbe ansprechen | Metzgers Angebot (350). Mit gebautem Riegel innen der Zusatz (351) |
| „And if I say no?“ | „Metzger remembers who says no.“, dann wieder die Wahl |
| Weniger als 350 $ (Kasse + Tasche) | Statt „Deal“: „I don't have that kind of money.“ → „The offer stands.“ |
| Annehmen | 350 $ weg. Im Personal-Menü: 5 Zimmer, 5 Leute, „And there are 2 in the cellar …“ |
| Danach Essie ansprechen | Ihre Reaktion (350), dann das Manager-Menü |
| Eine Woche warten | Karma −5, Moral höchstens 50, der Gewinn steigt (weniger Anteil) |
| 4 Wochen warten | Titel „Soul Seller“ im Charakterbogen |
| Flucht-Ereignis (Zufall) | „One of the ones in the cellar got out.“, dann „Send word to Metzger“ im Personal-Menü |
| Ablehnen (neuer Spielstand) | Kolbe: „Your call …“, Essie: „Good. I've waited twenty years …“ |
| Ausbau → Besonderes nach dem Annehmen | kein „Inside Bolts“ mehr im Angebot |

---

## 7. Nächste Schritte

1. **„Ketten“, Akt 2: Die im Keller.** Mara, Essies Versteck und die „Zuflucht“ im Fluchtzweig.
2. **Weitere Tyrannen-Quellen** (Vortis, Dienstboten-Pacht, Hubologen), sobald die Häuser dazukommen.
3. **Der Keller als eigene Ebene** der Gosse: Pferch oder Zuflucht, sichtbar auf der Karte.
