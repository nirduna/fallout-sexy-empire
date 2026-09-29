# Umsetzung 11 – San Francisco: Die Bilge

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt und gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 62 Tests, davon 4 neu für San Francisco, und 105 erkundete Dialogzustände.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 2](phase-2-standorte-und-ausbau.md), Abschnitt 2.6: Bilge, Anlegesteg, Siegel der Shi, Schmuggelkammer
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 2.6 („Die Duldung“) und 4.3 (die Hubologen)
- [Phase 4](phase-4-personal-talente-ereignisse.md): Abschnitt 2.3 (Hubologen-Schuldner) und 4.2 (Razzia der Shi)
- [Fahrplan](fahrplan.md), Schritt 11

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_sanfran.h`](../scripts_src/headers/rl_sanfran.h) | **neu:** Duldung, Razzia der Shi-Inspektoren, Figuren |
| [`rlwen.ssl`](../scripts_src/rotlicht/rlwen.ssl) | **neu:** Aufseher Wen vom Hafenamt der Shi. Tribut, Spitzeldienst, Barter, der Gefallen für das Siegel |
| [`rlbootsmann.ssl`](../scripts_src/rotlicht/rlbootsmann.ssl) | **neu:** Bo Harlan, Bootsmann des Tankers. Rückendeckung ohne die Shi, das Lager für die Schmuggler |
| [`rlkwan.ssl`](../scripts_src/rotlicht/rlkwan.ssl) | **neu:** Tante Kwan, Madame der Bilge (Führung 50). Manager-Menü, Hubologen, Schuldscheine |
| [`rlsfr01.ssl`](../scripts_src/rotlicht/rlsfr01.ssl) | setzt Wen, Bootsmann und Kwan |
| [`rl_sonder.h`](../scripts_src/headers/rl_sonder.h) | Sondermodul **Schmuggelkammer** |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_sf_woche`: Der Spitzel fliegt auf. Eine Razzia in San Francisco findet die Schmuggelkammer, und die Shi sind misstrauisch, solange es sie gibt. Hubologen in Vanilla fort: Der Abzug entfällt |

---

## 2. „Die Duldung“

| Weg | Wo, Check | Folge |
|---|---|---|
| Wens Angebot | Wen | 15 % Tribut (Grundtribut 10 % + 5 Punkte) |
| Augen der Shi | Wen | 10 %, das Siegel der Shi wird sofort verfügbar. Die Tanker-Leute merken es irgendwann: je Woche 15 % − Sneak ÷ 10, mindestens 2 %. Dann H +10, Kunden −10 %, und der Bootsmann ist Feind |
| Tribut drücken | Wen, Barter 60 | 10 %. Das Siegel gibt es nach einem Gefallen: das Boot mit dem Geld der Hubologen finden (PE 7 oder Sneak 60) |
| Tanker | Bootsmann, Speech 60 | kein Tribut und keine Duldung der Shi, H +15, die Schmuggelkammer sofort. Später kann der Spieler zu Wens 15 % wechseln (H +10) |

Mit jedem Weg gehört die Bilge dem Spieler (E San Francisco mindestens 20). Kwan führt sie.

---

## 3. Schmuggelkammer und Siegel

- **Schmuggelkammer** (Sondermodul, 800 $): +3 $ Nebenumsatz je Kunde, H +10. Verfügbar mit dem Tanker im Rücken oder nachdem der Spieler dem Bootsmann das Lager angeboten hat.
- **Die Shi sind misstrauisch,** solange es die Kammer gibt: Das Razzia-Gewicht in der Bilge steigt um 10.
- **Finden die Inspektoren der Shi die Kammer:**
  - Tribut +5 Punkte, das Siegel wird entzogen (mit seinen Wirkungen), und für ein neues braucht es einen neuen Gefallen.
  - Die Kammer ist beschlagnahmt, E −10.
- **Ohne Kammer** bleibt eine Razzia in San Francisco eine gewöhnliche Krise für Kwan.

---

## 4. Die Hubologen

Über Kwan, solange die Hubologen um dieselben Verlorenen werben (−10 % Kunden):

| Weg | Check | Folge |
|---|---|---|
| Entlarven | Science 70 | Abzug weg, E SF +5 |
| Unterwandern | Speech 60 | Die Zweifler kommen zur Bilge: Kunden +10 % |
| Absprache | Barter 60 | Abzug weg, Karma −20. Danach Schuldscheine: 100 $ je Person, Zwangspersonal (Tyrannen-Quelle) |
| Vanilla | Die Hubologen fliegen mit dem betankten Schiff davon (`SF_GAS_ELRONS`) | Abzug weg |

---

## 5. Entscheidungen (meine Empfehlungen)

1. **Wen und der Bootsmann bleiben in der Bilge.** Die Duldung ist eine laufende Beziehung (Siegel, Wechsel zu den Shi, Lager), keine einmalige Übernahme.
2. **Der Spitzeldienst fliegt nicht sofort auf.** Sneak senkt die wöchentliche Chance; ganz sicher ist er nie.
3. **Die Razzia der Shi** trifft nur, wenn es etwas zu finden gibt. So bleibt die Schmuggelkammer ein kalkulierbares Risiko.
4. **Neutrale Figuren-Protos** (Bürger, Schläger) statt Shi- oder Lo-Pan-Protos. Deren Teams könnten feindlich sein, wenn der Spieler mit einer Fraktion Streit hat.
5. **Die Kampfschulen und Dr. Fung** als Quellen für Rausschmeißer und Doc gehören zum Personal (Schritt 15).

---

## 6. Welt-Felder

- **Welt 105–109:** Duldung, Spitzel aufgeflogen, Lager, Tote, Kwan kennt den Spieler.
- Hubologen in `RL_W_HUBOLOGEN` (jetzt mit Wert 3: Absprache), das Siegel in `RL_W_SHI_GEFALLEN`.

---

## 7. Testen im Spiel

| Test | Erwartung |
|---|---|
| Die Bilge betreten (San Francisco Docks) | Wen und der Bootsmann in der Wartehalle |
| Wen: „Fifteen percent“ | Kwan erscheint und führt das Haus |
| Bootsmann: „store things“, Ausbau → „Something you only get in San Francisco“ | Schmuggelkammer, Siegel (mit Gefallen), Anlegesteg |
| Kwan: „The Hubologists“ | drei Wege je nach Skills |

---

## 8. Nächste Schritte

Weiter mit **Schritt 12** des [Fahrplans](fahrplan.md): „Blut auf der Virgin Street“.
