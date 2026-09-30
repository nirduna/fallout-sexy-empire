# Umsetzung 16 – Abschluss

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Alle 16 Schritte des [Fahrplans](fahrplan.md) sind umgesetzt.
- Gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 79 Tests und etwa 3.700 erkundete Dialogzustände.
- Testpakete für RPU 2.4.34 und 2.3.34.
- **Im Spiel getestet ist nur die Gosse** (Umsetzung 2: Eingang, Karte, Prolog). Alles andere ist offen.

**Grundlage:** [Phase 6](phase-6-karma-ruf-endings.md), Abschnitte 3 und 4; [Fahrplan](fahrplan.md), Schritt 16

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_jobs.h`](../scripts_src/headers/rl_jobs.h) | `rl_seelenverkaeufer`, `rl_titel_bonus`, `rl_tyrann_preis`: die Titel-Wirkungen an einer Stelle |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | fünf weitere Nachsätze, Preisboxer, Pornostar, Vesper und Talus gehen beim Seelenverkäufer |
| [`rotlicht.h`](../scripts_src/headers/rotlicht.h) | Wochenrechnung: die Fünfte Familie zahlt 5 Punkte weniger Tribut, der Sexperte bringt Qualität +5 |
| [`install/endgame.txt.add`](../install/endgame.txt.add), [`cuts/`](../text_src/english/cuts/) | Nachsätze 7–11 mit Untertiteln |
| [`tools/paket.py`](../tools/paket.py) | Die Anleitung im Paket beschreibt jetzt die ganze Mod |

---

## 2. Titel-Wirkungen

| Titel | Wirkung | Wo |
|---|---|---|
| **Seelenverkäufer** (und der Vanilla-Titel Sklavenhändler) | Marcus sperrt die Läuferroute. Vesper und Talus lassen sich nicht anwerben und gehen, wenn sie schon da sind. Mara wird keine Madame. Calloway spricht nicht mit dir. Die Rangers nehmen keine Spende und kommen nicht zu Hilfe. Checks bei der Anhörung der Liga −10. Vortis und Metzger 20 % billiger | `rl_titel_bonus`, `rl_seelenverkaeufer`, `rl_tyrann_preis` |
| **Anständiges Haus** | Werben doppelt so schnell, Kittys Abwerbung halb so oft (seit Umsetzung 3 und 12). Checks bei Marcus, Calloway und der Liga +10. Mara ohne Check | `rl_titel_bonus` |
| **Die Fünfte Familie** | Checks bei den Familientreffen +10 (seit Umsetzung 7). Tribut in New Reno −5 Punkte. Zählt bei Venuti wie ein Made Man | Wochenrechnung, `rlvenuti.ssl` |
| Pornostar (Vanilla) | Julians Vertrag leichter (seit Umsetzung 13). VIP-Kundschaft im Strumpfband +2 | `rl_talente_woche` |
| Preisboxer (Vanilla) | Sicherheit im Strumpfband +10. Ersetzt die Unarmed-Checks auf der Virgin Street (Kitty unter Druck setzen, den Dealer hinauswerfen) | `rl_welt_modifikatoren`, `rljade.ssl`, `rlroz.ssl` |
| Sexperte (Vanilla) | Personalqualität in allen Häusern +5 | Wochenrechnung |

---

## 3. Der Epilog

**Hauptslide:** Tyrann, Geschäftsmann oder Bankrott, wie in Phase 6 festgelegt.

**Nachsatz:** Höchstens einer, der erste Treffer gewinnt. Die sechs aus Phase 6 haben Vorrang. Danach kommen die Linien, die nach Phase 6 dazukamen:

| # | Nachsatz | Bedingung | Bild |
|---|---|---|---|
| 7 | Der leere Stuhl | Virgin Street: Venuti ist erledigt | New Reno |
| 8 | Die Straße | Marcus' Eskorte | Broken Hills |
| 9 | Der Stein | Talus arbeitet und kann lesen | Broken Hills |
| 10 | Julian | Julian ist clean und geblieben | New Reno |
| 11 | Die Bürgerin | Abigail arbeitet und ist wieder Bürgerin | Vault City |

---

## 4. Gesamtprüfung

| Prüfung | Ergebnis |
|---|---|
| Kompilieren gegen RPU 2.4.34, RPU 2.3.34, Unofficial Patch | alle Skripte fehlerfrei |
| Karten gegen beide RPU-Stände (`bau_karten.py`) | Round-Trip, Skripte, Plätze, Eingänge in Ordnung |
| Textnummern und ASCII (`check_msg.py`) | jede verwendete Nummer vorhanden, alle Spieltexte reines ASCII |
| Prüfwerkzeug auf beiden RPU-Ständen | 79 von 79 Tests grün |
| Wochenrechnung gegen den Simulator | 400 zufällige Häuser über je 10 Wochen, auf den Dollar gleich |
| Optionsfenster | Kein Menü verliert Optionen, auch nicht mit allen Optionen zugleich |
| Endslides | jede Zeile in `endgame.txt.add` hat Untertitel im Format `n:Text` |

---

## 5. Was im Spiel noch offen ist

Das Prüfwerkzeug führt die Skripte aus, aber es ist nicht das Spiel. Nicht geprüft sind:
- **Grafik und Karten im Spiel:** ob die fünf weiteren Innenkarten sauber aussehen und die Eingänge in den Städten gut sitzen. Die Karten sind rechnerisch geprüft, nicht mit dem Auge.
- **Kämpfe:** die Angreifer in der Eröffnungsnacht, der Nacht der langen Messer und bei Tylers Preis. Das Prüfwerkzeug bildet nur ab, wer fällt, nicht den Kampf selbst.
- **Das Optionsfenster:** Die Grenze von etwa acht Zeilen ist nach dem Engine-Quelltext geschätzt. Die genaue Schriftbreite kennt das Werkzeug nicht.
- **Endslides:** ob die Engine die neuen Nachsätze ohne Sprachaufnahme sauber anzeigt.
- **Balancing über ein ganzes Spiel:** Die Wirtschaft stimmt mit dem Simulator überein, aber ob sich ein Imperium über 50 Stunden gut anfühlt, zeigt nur das Spielen.
- **Zusammenspiel mit Vanilla-Quests:** etwa mit Missing People in Broken Hills, dem Gecko-Kraftwerk, den Titeln oder Tylers Tod. Das Werkzeug setzt dafür nur die globalen Variablen.

---

## 6. Entscheidungen (meine Empfehlungen)

1. **Metzger bleibt Vanilla.** Seine +10 für den Seelenverkäufer gelten nur für die Preise (20 % billiger). Metzgers Dialog selbst gehört dem RPU (Fahrplan, Grundsatz 1).
2. **Sklavenhändler wirkt wie Seelenverkäufer.** So steht es in Phase 6, Abschnitt 3.2.
3. **Weitere Nachsätze nach den sechs aus Phase 6:** Die Linien aus den Umsetzungen 12–14 bekommen einen Abschluss. Die Reihenfolge aus Phase 6 bleibt vorne, damit die großen Linien Vorrang haben.
4. **Testpakete mit Debug-Tasten:** Solange im Spiel fast nichts getestet ist, helfen die Tasten mehr, als sie stören. Für eine Veröffentlichung baut man ohne `RL_DEBUG`.
