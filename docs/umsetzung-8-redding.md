# Umsetzung 8 – Redding: Die Schlacke

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt und gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 43 Tests, davon 7 neu für Redding, und 140 erkundete Dialogzustände.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 2](phase-2-standorte-und-ausbau.md), Abschnitt 2.3: Schlacke, Goldwaage, Entzugsstube
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 2.3: „Ascortis Lizenz“
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 4.2: der Malamute Saloon
- [Phase 4](phase-4-personal-talente-ereignisse.md), Abschnitt 4.2: die Razzia in Redding
- [Fahrplan](fahrplan.md), Schritt 8

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_redding.h`](../scripts_src/headers/rl_redding.h) | **neu:** Lizenz, Sheriff Marion, Revolte, Entzugsstube, Figuren der Schlacke |
| [`rlschreib.ssl`](../scripts_src/rotlicht/rlschreib.ssl) | **neu:** Otis Pruett, Ascortis Schreiber. Verkauft die Lizenz; stirbt er, schickt Ascorti den nächsten |
| [`rlnell.ssl`](../scripts_src/rotlicht/rlnell.ssl) | **neu:** Nell Harrow, Madame der Schlacke (Führung 50). Manager-Menü und der Malamute Saloon |
| [`rlred01.ssl`](../scripts_src/rotlicht/rlred01.ssl) | setzt Schreiber oder Nell |
| [`rl_sonder.h`](../scripts_src/headers/rl_sonder.h) | Sondermodul **gezinkte Waage** |
| [`rotlicht.h`](../scripts_src/headers/rotlicht.h) | drei neue Hausfelder in der Wochenrechnung: Preisaufschlag, abweichendes Schmiergeld, „geschlossen“. Welt-Array jetzt 160 Felder |
| [`economy_sim.py`](../tools/economy_sim.py) | dieselben drei Stellschrauben (`price_mod`, `bribe_mod`, `closed`). Der Paritätstest würfelt sie mit |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_red_woche`: Waage und Revolte, Preiskrieg, Beteiligung, Marion nach der Wanamingo-Mine. Geschlossene Häuser zählen ihre Wochen herunter und haben keine Ereignisse. Die Entzugsstube halbiert Stoff-Ereignisse |
| [`rl_haeuser.h`](../scripts_src/headers/rl_haeuser.h) | `rl_figur_da` zählt tote Figuren nicht mehr |

---

## 2. „Ascortis Lizenz“

Ascorti spricht nicht selbst. Sein Schreiber Otis Pruett sitzt in der leeren Schlacke. Mit der Lizenz gehört die Schlacke dem Spieler (E Redding mindestens 20), und Nell übernimmt.

| Weg | Check | Folge |
|---|---|---|
| Paket | 1.000 $, mit Barter 60 600 $ | 75 $/Woche an Ascorti |
| Aufschlag | Speech 70 | kein Paketpreis, 125 $/Woche |
| Bloßstellen | Steal 60 **oder** Lockpick 60 (Ascortis Kassenbuch), dann Speech 60 (zu Marion) | Marion wird Schutzherr: Sicherheit +10, kein Schmiergeld. Ascorti wird Feind |
| Einschüchtern | Unarmed 60 **oder** ST 7 | kein Schmiergeld, H Redding +20, Marion wird wachsam |

- Das Kassenbuch bekommt man auch ohne Speech 60. Dann ist es wertlos, bis der Spieler reden kann.
- **Marion als Schutzherr** gibt es auch über Vanilla: Ist die Wanamingo-Mine gesäubert, nimmt Marion die Schlacke unter seinen Schutz. Das gilt auch rückwirkend bei der Übernahme, und der Bonus zählt nur einmal.

---

## 3. Die Waagen

| Modul | Kosten | Wirkung |
|---|---|---|
| Ehrliche Goldwaage (Katalog) | 400 $ | Kunden +10 % |
| **Gezinkte Waage** (Sondermodul) | 150 $, 1 Woche | Preis +15 %, H +10, Karma −2/Woche |

Die beiden Waagen schließen sich aus.

**Marion sucht jede Woche.** Die Chance ist 5 % + Hitze ÷ 5. Ist Marion wachsam oder Feind, verdoppelt sie sich. Findet er die gezinkte Waage, folgt die **Revolte der Kumpel**:
- Die Waage ist weg.
- Die Schlacke ist 3 Wochen geschlossen: keine Kunden, keine Ereignisse, die Kosten laufen weiter.
- Moral −10, Ruf −15, E −10.
- Wer Ascorti bezahlt, zahlt jetzt das Doppelte (+75 $/Woche).
- Marion wird wachsam. War er Schutzherr, wird er Feind und der Sicherheitsbonus fällt weg.

Die **Entzugsstube** stand schon im Katalog (braucht die Krankenstube, also einen Doc). Neu ist: Sobald sie gebaut ist, halbiert sie die Stoff-Ereignisse in der Schlacke.

---

## 4. Der Malamute Saloon

Nell bietet an, solange der Malamute seine Mädchen noch oben hat (−10 % Kunden für die Schlacke):

| Weg | Check | Folge |
|---|---|---|
| Beteiligung | Barter 60, 1.500 $ | +60 $/Woche in die Kasse, der Abzug entfällt |
| Preiskrieg | Preisstufe „Ramsch“ | Nach 4 Wochen mit Ramsch-Preisen gibt der Malamute auf. Wochen mit anderen Preisen zählen nicht |
| Sabotage | Sneak 60 | gepanschter Whiskey, Karma −10. Die Entdeckung wird mit dem Sneak-Wert gewürfelt; erwischt wird Marion Feind |
| Übernahme | E Redding ≥ 40, 3.000 $ | +2 Zimmer für die Schlacke (leer, bis angeworben ist) |

---

## 5. Entscheidungen (meine Empfehlungen)

1. **Der Schreiber statt Ascorti und Marion:** Kein Vanilla-Skript wird verändert. Die Wege zu Marion und in Ascortis Schreibtisch laufen als erzählte Aktionen im Dialog mit Pruett.
2. **Die Lizenz ist die Übernahme.** Phase 2 verlangt E Redding ≥ 20; mit der Lizenz steigt E auf mindestens 20.
3. **Schmiergeld, Aufschlag und Schließung** stehen in der Wochenrechnung selbst, nicht in Nebenrechnungen. So bleibt der Simulator die Referenz, und der Paritätstest deckt sie ab. Vault City (Schweigegeld je Hausklasse) und die Seuche („2 Wochen geschlossen“) nutzen dieselben Felder.
4. **Der Malamute wird über die Madame gelöst,** nicht über eine eigene Figur im Saloon. Die Vanilla-Figuren des Malamute (Lou, Fannie) bleiben unberührt.
5. **Der Preiskrieg zwingt die Preisstufe nicht fest.** Der Spieler kann sie ändern, dann ruht der Krieg.
6. **Tote zählen nicht als anwesend** (`rl_figur_da`). Figuren mit Tot-Bit (Roz, Asch, Nell …) kommen trotzdem nicht wieder; nur Ascortis Schreiber rückt nach.

---

## 6. Welt- und Hausfelder

- **Welt 73–82:** Lizenz, Marion, Kassenbuch, Schreiber, Malamute-Weg, Preiskriegswochen, Nell tot, Nell kennt den Spieler, Marion-Bonus, Ascorti Feind.
- **Haus 38–40:** Schmiergeld-Abweichung, Preisaufschlag, Wochen geschlossen.
- Das Welt-Array wächst auf 160 Felder. Ältere Spielstände werden beim Laden erweitert.

---

## 7. Testen im Spiel

| Test | Erwartung |
|---|---|
| Die Schlacke betreten (Bergbaulager, Treppe zwischen den Schuppen) | Pruett sitzt auf einer Erzkiste |
| „What does the package cost?“ → 1.000 $ | Pruett blendet aus, Nell steht da |
| Nell: Ausbau → „Something you only get in Redding“ | ehrliche und gezinkte Waage zur Wahl |
| gezinkte Waage bauen, Wochen vergehen | Karma sinkt. Irgendwann: „Sheriff Marion found the rigged scale …“ und 3 Wochen ohne Kunden |
| Nell: „About the Malamute“ | vier Wege, je nach Skills und Einfluss |
| Wanamingo-Mine in Vanilla säubern | Meldung „The Wanamingo mine is clean …“, Sicherheit der Schlacke +10 |

**Nicht im Prüfwerkzeug sichtbar:** wie Pruett und Nell mit ihren Bürger-Grafiken im Tunnel wirken und ob der Platz der Madame im Tunnel gut erreichbar ist.

---

## 8. Nächste Schritte

Weiter mit **Schritt 9** des [Fahrplans](fahrplan.md): Vault City, Die Kloake.
