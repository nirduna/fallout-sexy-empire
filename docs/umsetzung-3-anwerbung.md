# Umsetzung 3 – Anwerbung: Werben oder Zwingen

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Umgesetzt und kompiliert, **Test im Spiel offen**.
- Alle Skripte kompilieren gegen das RPU und den Unofficial Patch, mit und ohne Debug und mit Selbsttest.
- Die Soll-Werte des Selbsttests (`economy_sim.py --vektoren`) und die Ausbau-Tabellen aus Phase 2 sind unverändert.
- Die Spieltexte sind englisch ([Spieltexte auf Englisch](spieltexte-englisch.md)).

**Grundlage:**
- [Phase 4](phase-4-personal-talente-ereignisse.md): Abschnitt 1 (Rollen, Kapazität) und Abschnitt 2.2 (der Anwerber)
- [Phase 6](phase-6-karma-ruf-endings.md): Karma −3 beim Zwingen, „Anständiges Haus“ wirbt doppelt so schnell

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`scripts_src/headers/rotlicht.h`](../scripts_src/headers/rotlicht.h) | Felder `RL_F_ANWERBER`, `RL_F_ANWERB_PUNKTE`, `RL_F_GEZWUNGEN`. Dazu `rl_anwerber_setzen` (einstellen, wechseln, entlassen) und `rl_personal_verlust` (Gezwungene fliehen zuerst). Die Wochenrechnung kennt jetzt Moral-Deckel, Karma und Hitze beim Zwingen. Neue Zimmer werden nicht mehr automatisch besetzt |
| [`scripts_src/global/gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_personalwechsel`: Abgänge unter Moral 25 und Anwerbung jede Woche. Gezwungene machen Flucht-Ereignisse wahrscheinlicher |
| [`scripts_src/headers/rl_manager.h`](../scripts_src/headers/rl_manager.h) | neues Personal-Menü bei jeder Madame und jedem Manager. Debug: „Add two empty rooms“ |
| [`text_src/english/dialog/rlessie.msg`](../text_src/english/dialog/rlessie.msg), [`rlkolbe.msg`](../text_src/english/dialog/rlkolbe.msg) | Texte 118 und 480–493, je in der Stimme von Essie und Kolbe |
| [`text_src/english/game/rotlicht.msg`](../text_src/english/game/rotlicht.msg) | Meldungen 116–119: jemand Neues, jemand geht, jemand flieht |
| [`tools/economy_sim.py`](../tools/economy_sim.py) | `forced_staff` und `forcing` spiegeln Moral-Deckel, Karma und Hitze. Die Standardwerte rechnen wie bisher |
| [`tools/check_msg.py`](../tools/check_msg.py) | prüft auch die berechneten Texte 483–485 |

---

## 2. Die Regeln

**Kapazität** (Phase 4, Abschnitt 1): Kunden je Woche = min(Zimmer, Arbeitende) × 12. Ein Zimmer ohne Person bringt nichts.

**Der Anwerber** wird bei der Madame eingestellt:

| | Werben | Zwingen |
|---|---|---|
| Wer | jemand, der den Leuten zuhört (bei Essie: eine Frau bei Mom's) | jemand, der nicht fragt: Schulden, Jet, Drohungen |
| Tempo | 1 Person alle 2 Wochen, mit dem Titel „Anständiges Haus“ jede Woche | 1 Person pro Woche |
| Qualität der Neuen | 40–60 | 30–50 |
| Moral der Neuen | 50 | 15 |
| Kosten | 40 $/Woche Lohn, 50 $ je Person aus der Kasse | ebenso |
| Folgen | keine | Karma −3 pro Woche. Hitze +5 pro Woche statt −5. Solange Gezwungene im Haus sind: Moral höchstens 50 und häufiger Flucht |

**Wann jemand kommt:**
- **Punkte:** Neue kommen nur, wenn ein Zimmer frei ist. Das Haus sammelt dann Punkte, je 4 Punkte kommt eine Person:
  - Werben: 2 Punkte pro Woche (mit „Anständiges Haus“ 4)
  - Zwingen: 4 Punkte pro Woche
- **Zulauf** (Phase 1/4): Ab Moral 75 kommt 1 Punkt pro Woche dazu, beim Zwingen nicht. Ohne Anwerber heißt das: Alle 4 Wochen kommt jemand von selbst, kostenlos.
- **Durchschnitt:** Neue fließen mit ihrer Qualität und Moral in den Hausdurchschnitt ein.

**Wer geht:**
- **Abgänge:** Unter Moral 25 geht jede Woche eine Person. Gezwungene fliehen zuerst, sie haben am wenigsten zu verlieren.
- **Ereignisse:** Regelt die Madame ein Flucht-Ereignis allein, ist trotzdem eine Person weg.
- **Unruhe:** Die 30 $ „Fluchtkosten“ der Wochenrechnung (Phase 1) bleiben als Kosten der Unruhe bestehen.

**Wechseln und entlassen:**
- Die Methoden schließen sich pro Haus aus. Wer wechselt, fängt mit den Punkten von vorn an.
- Ist jedes Zimmer besetzt, sagt die Madame, dass der Anwerber nur Geld kostet. Dann entlässt man ihn.

---

## 3. Beispiel: Die Gosse nach Hausklasse II

Ausgangslage:
- 5 Zimmer, 3 Leute, Moral 50, üblicher Anteil.
- Laut Phase 2 bringt Hausklasse II rund 100 $ pro Woche mehr, aber nur mit besetzten Zimmern.

| | Werben | Zwingen |
|---|---|---|
| beide Zimmer besetzt nach | 4 Wochen | 2 Wochen |
| Kosten (Lohn + Kopfgeld) | 4 × 40 + 2 × 50 = **260 $** | 2 × 40 + 2 × 50 = **180 $** |
| Moral danach | 50 | **35** (50 → 41 → 35) |
| Karma | 0 | −6 |
| Hitze | 0 | +10 |
| Danach | nichts | Solange die zwei im Haus sind: Moral höchstens 50, häufiger Flucht. Unter Moral 40 mehr Schwund und mehr Sucht-Ereignisse |

Zwingen ist schneller und billiger. Es drückt aber die Moral, und damit Kunden und Kasse, noch Wochen später. Die dunkle Abkürzung soll sich kurz lohnen und lange rächen.

---

## 4. Entscheidungen in dieser Umsetzung (meine Empfehlungen, bitte prüfen)

1. **Anwerber ohne Namen:**
   - Die Madame stellt sie ein. Die Checks aus Phase 4 (CH 6 / Speech 50 bzw. STR 7 / Unarmed 60) beschreiben, wen sie anheuert, und prüfen nicht den Spieler.
   - Figuren mit Namen je Stadt (Phase 4, Abschnitt 2.1) lassen sich später ergänzen.
2. **Zwingen zählt nicht als „Zwangspersonal“:**
   - Phase 4 unterscheidet Zwingen (Abschnitt 2.2, Karma −3) vom Zwangspersonal hinter dem Riegel außen (Abschnitt 2.3, Karma −5).
   - Der Titel „Seelenverkäufer“ und das Tyrannen-Ende zählen deshalb nur Zwangspersonal und Leine. Wer dauerhaft zwingt, verliert trotzdem viel Karma.
   - Soll Zwingen auch zum Seelenverkäufer führen, ist das eine Zeile.
3. **Hitze:** „+5 pro Woche“ heißt: Die Hitze steigt um 5, statt wie sonst um 5 zu sinken.
4. **Rangers in der NCR:** Sie ermitteln gegen Zwingen, sobald es das Haus in der NCR gibt (Übernahme, Phase 3).

---

## 5. Testen

1. Testpaket mit Debug bauen, wie in [Umsetzung 2, Abschnitt 4.1](umsetzung-2-die-gosse.md#41-testpaket-empfohlen).
2. Ein **neues Spiel** ist nicht nötig. Die neuen Felder sind in alten Häusern 0, also kein Anwerber.
3. In der Gosse bei Essie **„[Debug] Add two empty rooms“** wählen.
4. Für eine Woche ruhen, zum Beispiel über den Wecker im Pip-Boy.

| Test | Erwartung |
|---|---|
| Essie: „Let's talk about our people.“ | „We have 5 rooms and 3 people to work them. Nobody is out looking for new faces.“ |
| Werben wählen, 2 Wochen warten | Meldung „The Gutter: A new face in the house …“, im Menü 4 Leute |
| Weitere 2 Wochen | 5 Leute. Im Menü der Hinweis „Every room is taken …“ |
| Anwerber entlassen | Er verschwindet aus dem Menü, die Kosten sinken ab der nächsten Woche um 40 $ |
| Zwingen wählen (mit leeren Zimmern), 1 Woche warten | „Someone new was brought in …“, Moral sinkt deutlich, Karma −3 |
| Preis „Cheap“ und Anteil „A quarter“ über Wochen | Die Moral fällt unter 25, jede Woche geht jemand, Gezwungene zuerst („… ran off“) |
| Ausbau fertig (z. B. Hausklasse II) | Die neuen Zimmer bleiben leer, bis jemand angeworben ist |
| Bei Kolbe als Manager (Essie ausgeliefert) | dasselbe Menü mit Kolbes Texten („Rooms: 3. People: 3. Nobody's out hunting.“) |

---

## 6. Nächste Schritte

1. **Questline „Ketten“, Akt 1:** Metzgers Angebot, aufbauend auf `RL_W_METZGER` und `RL_W_KETTEN_ZWEIG`.
2. **Tyrannen-Quellen** (Phase 4, Abschnitt 2.3), zusammen mit dem dunklen Modul „Riegel außen“.
3. **Anwerber mit Namen** je Stadt, wenn die weiteren Häuser dazukommen.
