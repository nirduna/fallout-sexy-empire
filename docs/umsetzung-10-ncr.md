# Umsetzung 10 – NCR: Die Tränke und „Die Reinen“

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt und gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 58 Tests, davon 8 neu für die NCR, und 351 erkundete Dialogzustände.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 2](phase-2-standorte-und-ausbau.md), Abschnitt 2.5: Tränke, Karawanenhof, Registratur, Vortis' Angebot
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 2.5 („Etablissement Nr. 9“) und 3.3 („Die Reinen“)
- [Phase 4](phase-4-personal-talente-ereignisse.md), Abschnitt 2.3: Vortis als Tyrannen-Quelle
- [Fahrplan](fahrplan.md), Schritt 10

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_ncr.h`](../scripts_src/headers/rl_ncr.h) | **neu:** Lizenz, Auflage, Legalität, Enden der Reinen, Rangers-Razzia, Figuren |
| [`rlgrieve.ssl`](../scripts_src/rotlicht/rlgrieve.ssl) | **neu:** Inspektorin Marta Grieve vom Lizenzamt. Vier Wege zur Lizenz |
| [`rldora.ssl`](../scripts_src/rotlicht/rldora.ssl) | **neu:** Dora Quist, Madame der Tränke (Führung 50). Manager-Menü, Akte 1–4 der Reinen, Vortis' Angebot |
| [`rlcalloway.ssl`](../scripts_src/rotlicht/rlcalloway.ssl) | **neu:** Ruth Calloway. In Akt 1 und 2 in der Tränke; mit Speech 60 erzählt sie ihre Geschichte |
| [`rlncr01.ssl`](../scripts_src/rotlicht/rlncr01.ssl) | setzt Grieve, Dora und Calloway |
| [`rl_sonder.h`](../scripts_src/headers/rl_sonder.h) | Sondermodul **Registratur** |
| [`rotlicht.h`](../scripts_src/headers/rotlicht.h), [`economy_sim.py`](../tools/economy_sim.py) | Risiko je Haus (`RL_F_RISIKO_MOD`, `risk_mod`). Der Paritätstest würfelt es mit |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_ncr_woche`: Legalität, Rangers, Schweigegeld von Vortis, die fünf Akte. Die Lizenz kommt auch, wenn noch kein Haus gehört. Die Kampagne wirkt nach Registratur, Brand und Lex Neun. Vault City folgt dem Ausgang der Liga |

---

## 2. „Etablissement Nr. 9“

| Weg | Check | Folge |
|---|---|---|
| Dienstweg | 500 $, mit Bishop als Paten 250 $ | 3 Wochen Wartezeit, E NCR +5 |
| beschleunigt | dazu Barter 40 und 300 $ | 1 Woche, H +5 |
| Westins Fürsprache | Speech 60, nur solange Westin lebt | sofort. Westin verlangt die privaten Räume und 5 % (Tribut +5 Punkte), E NCR +10 |
| ohne Lizenz | – | sofort, aber illegal: Risiko 1 → 4, H +30. „Die Reinen“ beginnen sofort |

- **Auflage Krankenstube:** Ist 4 Wochen nach der Eröffnung keine Krankenstube gebaut, ist die Lizenz ausgesetzt, und die Tränke gilt als illegal. Mit Krankenstube ist sie wieder legal.
- **Illegal** heißt: Risiko +3 in der Wochenrechnung und bei den Ereignissen (mehr Razzien, mehr gewalttätige Freier).

---

## 3. Vortis' Angebot (Tyrannen-Route)

- Über Dora kauft der Spieler Menschen aus Vortis' Pferch: 200 $ je Person, nur mit freiem Zimmer. Sie sind Zwangspersonal.
- Solange Vortis' Leute im Haus sind, finden die Rangers sie jede Woche mit 5 % + Hitze ÷ 10:
  - Razzia, die Menschen sind frei.
  - Die Lizenz wird entzogen.
  - Die Rangers werden dauerhaft Feinde. Dazu H +30 und E −20.
- Ist Vortis Feind (nach „Die Gilde fällt“) oder verhaftet, gibt es kein Angebot.

---

## 4. „Die Reinen“

Die Linie beginnt zwei Wochen nach der Eröffnung, ohne Lizenz sofort. Zwischen den Akten liegen zwei Wochen. Wartet ein Akt vier Wochen auf den Spieler, geht die Geschichte ohne ihn weiter.

| Akt | Was geschieht | Wege |
|---|---|---|
| 1 Flugblätter | Kampagne −15 %, Calloway steht in der Tränke | Calloway: Speech 60, ihre Geschichte. Mit Maras Bürgschaft −5 %. War Mara von dir gedrängt und ist zu ihr gegangen, hört sie nicht zu. · Dora: Gegenkampagne (Barter 60): −10 %, H +5 · Streikposten vertreiben (Unarmed 60): keine Kampagne, H +10, K −5, die Liga hat Märtyrer |
| 2 Anhörung | Sittengesetz im Rat | Rede (Speech 80) · Stimmen kaufen (Barter 60, 2.000 $; 20 % Skandal, H +30) · Westin (Speech 60) · Westin erpressen (mit VIP-Trakt; H +10, K −5) · ohne uns. Bonus: +10 mit E ≥ 60 (Tandi), +10 mit Registratur **und** Krankenstube, −10 mit Märtyrern |
| 3 Feuer | Die Tränke brennt | Löschen: Repair 60 oder Traps 60. Sonst −40 % Kunden für 4 Wochen und Moral −10. Ermitteln: Science 60, Speech 60 oder CH 6, Sneak 60 und Lockpick 60 |
| 4 Beweise | Vortis war es. Im Tyrannen-Zweig war es ein radikaler Flügel der Liga | den Rangers (Vortis verhaftet) · Vortis erpressen: 150 $/Woche, H +10, K −30 · der Liga anhängen: Science 60, K −30 |

**Die Enden:**

| Ende | Bedingung | Folge |
|---|---|---|
| **Das Musterhaus** | Beweise an die Rangers, Moral ≥ 60, kein Slaver-Titel | **Lex Neun:** Kunden NCR +20 %. Das gilt nur mit fairem Anteil, Krankenstube und ohne Zwangspersonal; sonst kommt Calloway zurück (−15 %) |
| **Die Diskreditierung** | erpresst oder angehängt | Die Liga zerbricht, normale Nachfrage. Über Dora kann Calloway sterben: H +40, K −30, die Rangers ermitteln |
| **Das Verbot** | Anhörung verloren, keine Rangers | Die Tränke ist illegal (Risiko 4), H +30 |
| **Gescheitert** | Anhörung gewonnen, aber kein Musterhaus | Das Gesetz fällt durch, die Liga bleibt leise: −5 % |

**Übergreifend für Vault City:** Siegt die Liga (Lex Neun, Verbot), kommen Razzien in der Kloake 50 % häufiger. Zerbricht sie, halb so oft.

**Die Registratur** (Sondermodul, 500 $) halbiert jede negative Kampagnen-Wirkung und zählt vor dem Rat.

---

## 5. Entscheidungen (meine Empfehlungen)

1. **Der Rat spricht über Grieve.** Das Lizenzamt sitzt als Inspektorin in der leeren Nr. 9. Westin, Tandi und Vortis sprechen nicht selbst.
2. **Die Aktionen gegen die Liga laufen über Dora,** das Gespräch über Calloway selbst. So bleibt Calloway eine Person mit Stimme, keine Menüfigur.
3. **Das vierte Ende „Gescheitert“** ist neu. Phase 3 lässt offen, was geschieht, wenn die Anhörung gewonnen ist, aber das Musterhaus fehlt. Das Gesetz fällt dann durch, die Liga bleibt klein.
4. **Lex Neun gilt dynamisch:** Kippt der Spieler später in die Ausbeutung, kommt Calloway zurück, wie Phase 3 es beschreibt.
5. **Illegal ist ein Zustand, kein Ereignis.** Er wird jede Woche aus Lizenz, Auflage, Entzug und Verbot neu berechnet.
6. **„Die Reinen“ ohne Lizenz beginnen sofort** („verschärft“ in Phase 3).

---

## 6. Welt-Felder

- **Welt 91–104:** Lizenz, Wartezeit, Eröffnung, Entzug, Aktwoche, Akt 1, Anhörung, Brand, Brandende, Beweis, Akt 4, Tote, Bekanntschaften, Legalitätsmeldung.
- **Haus 41:** Risiko-Abweichung.
- Aktstand in `RL_W_REINE`, Kampagne in `RL_W_LIGA` (beide seit Umsetzung 1 vorgesehen).

---

## 7. Testen im Spiel

| Test | Erwartung |
|---|---|
| Die Tränke betreten (NCR Bazaar, am Rawhide) | Inspektorin Grieve am Klapptisch |
| Dienstweg bezahlen, 3 Wochen warten | Meldung „The license came …“; drinnen steht Dora |
| 4 Wochen ohne Krankenstube | Meldung „… the license is suspended“ |
| 2 Wochen nach der Eröffnung | Meldung über die Flugblätter; Calloway steht in der Tränke |
| Dora: „The League …“ in jedem Akt | die Wege der Tabelle |
| Akt 3 | Meldung „The Trough is burning“; Dora bietet Löschen und Ermitteln |

**Nicht im Prüfwerkzeug sichtbar:** Calloway nutzt ein starkes Bürgerinnen-Proto (`PID_STRONG_PEASANT_FEMALE`). Ob sie in der Tränke gut steht und nicht angreift, zeigt erst das Spiel.

---

## 8. Nächste Schritte

Weiter mit **Schritt 11** des [Fahrplans](fahrplan.md): San Francisco, Die Bilge.
