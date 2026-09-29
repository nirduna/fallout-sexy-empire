# Umsetzung 12 – „Blut auf der Virgin Street“

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt und gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 66 Tests, davon 4 neu, und 336 erkundete Dialogzustände.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 3.1 (die Linie) und 4.1 (das Cat's Paw)
- [Phase 4](phase-4-personal-talente-ereignisse.md), Abschnitt 3.6: Miss Kitty als Partnerin oder Rivalin
- [Fahrplan](fahrplan.md), Schritt 12

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_virgin.h`](../scripts_src/headers/rl_virgin.h) | **neu:** Akte, Enden, Umarmung, Gebühr, Kitty als Rivalin |
| [`rlvenuti.ssl`](../scripts_src/rotlicht/rlvenuti.ssl) | **neu:** Carlo Venuti. Akt 1 (Gebühr) und Akt 4 (Ultimatum, Kampf) |
| [`rljade.ssl`](../scripts_src/rotlicht/rljade.ssl) | **neu:** Jade, Miss Kittys rechte Hand. Akt 2 mit fünf Wegen |
| [`rlroz.ssl`](../scripts_src/rotlicht/rlroz.ssl) | Akt 3: den Dealer finden, loswerden oder umdrehen, das Personal heilen |
| [`rlnell.ssl`](../scripts_src/rotlicht/rlnell.ssl) | „Kittys Kralle“ in Redding beenden |
| [`rl_kampf.h`](../scripts_src/headers/rl_kampf.h) | Die Nacht der langen Messer als Kampf im Strumpfband |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_virgin_woche` und `rl_kitty_woche`. Stoff ×2 mit dem Dealer, Kittys Warnungen (Führung +20 in New Reno), Anwerben ×2 nach der Fusion, Jet-Knappheit in Redding nach dem leeren Stuhl |

---

## 2. Der Ablauf

Die Linie beginnt zwei Wochen nach der Übernahme des Strumpfbands. Zwischen den Akten liegen zwei Wochen. Bleibt ein Akt vier Wochen liegen, geht er ohne den Spieler weiter.

| Akt | Wer | Wege |
|---|---|---|
| 1 Gebühr | Venuti | 200 $/Woche zahlen · Barter 60: 100 $ · Speech 80 „über seinen Kopf“: keine Gebühr, E +5, Venuti gedemütigt · Made Man einer anderen Familie: keine Gebühr, H +5 · Nein: H +10, Akt 3 sofort. Schweigen gilt als Nein |
| 2 Kittys Angebot | Jade | siehe Abschnitt 3 |
| 3 Jet im Blut | Roz | Moral −10, Stoff-Ereignisse ×2, solange der Dealer da ist. Finden: PE 7, Sneak 60, oder das Personal sagt es selbst ab Moral 70. Dann rauswerfen (Unarmed 60), umdrehen (Speech 70: Beweise) oder verschwinden lassen (H +20). Heilen: Doctor 60 oder Myrons Jet-Antidot: Moral +10 |
| 4 Die Nacht der langen Messer | Venuti | Sit-down (Speech 90, oder CH 8 mit Made Man) · zuvorkommen (Beweise, Speech 60, die Wrights leben) · zahlen (1.500 $) · Umarmung (nur mit Mordino als Paten) · „Get out of my house“: drei Angreifer im Strumpfband |

**Das Ultimatum liegen lassen:** Alle vier Wochen verwüsten Venutis Leute das Haus. Es ist dann 2 Wochen geschlossen (Moral −10), und das Ultimatum bleibt.

**Die Enden:**

| Ende | Wie | Folge |
|---|---|---|
| **Der leere Stuhl** | zuvorgekommen, Kampf gewonnen, Venuti getötet, oder die Mordinos fallen in Vanilla | Gebühr weg, E New Reno +20. Nach 4 Wochen Machtvakuum werden die Tribute neu verteilt. In Redding gilt Jet-Knappheit (+10 %) |
| **Waffenstillstand** | Sit-down oder 1.500 $ | Gebühr weg, H −20, die Virgin Street bleibt geteilt |
| **Die Umarmung** | Mordino als Pate, „Then make me family“ | Jet-Theke in **jedem** eigenen Haus, auch in später übernommenen, Einnahmen +20 % (Preisaufschlag), Jet-Vertrag, Wright misstrauisch, K −30, Made Man (Mordino) |

**Vanilla:**
- Sind die Mordinos schon gefallen, wenn die Linie beginnen soll, will Venuti mit einem Rest der Familie Rache. Die Linie beginnt dann bei Akt 3; Sit-down und Umarmung gibt es nicht.
- Fallen sie während der Linie, endet sie mit dem leeren Stuhl.

---

## 3. Miss Kitty

Jade verhandelt für Kitty. Kitty selbst ist eine Vanilla-Figur und bleibt unberührt.

| Weg | Check | Folge |
|---|---|---|
| Bündnis | Speech 60 | Cat's Paw −15 % → −5 %, E +5, keine Gebühr an Venuti. Kittys Warnungen: Roz löst kleine Ereignisse mit Führung +20 |
| Fusion | Speech 70 und 3.000 $, **oder** E New Reno ≥ 40 | +3 Zimmer mit Personal, Qualität +10, Führung 85, Anwerben doppelt so schnell. Kittys Hälfte: Tribut +10 Punkte |
| Druck | Unarmed 60 oder Erpressung (VIP-Trakt), 1.500 $ | Kitty verkauft: +3 leere Zimmer, K −10. **Rivalin** |
| Sabotage | Sneak 60 | K −10, fliegt es auf: E −15. **Rivalin** |
| Verrat | – | +1.000 $, Gebühr −100 $, K −20. Das Cat's Paw gehört den Mordinos (−15 % bleibt). **Rivalin** |

**Kitty als Rivalin** („Kittys Kralle“ in Redding):
- In der Schlacke −10 % Kunden.
- Einmal im Monat geht aus jedem Haus mit Moral < 60 eine Person zu ihr. Mit dem Titel „Anständiges Haus“ nur jeden zweiten Monat.
- Bei der Anhörung der Reinen sagt sie gegen den Spieler aus: −10 auf alle Checks.

**Die Kralle beenden,** über Nell:
- Versöhnung: Speech 80 und 2.000 $
- Übernahme ihres Hauses: E Redding ≥ 40, die Schlacke bekommt +2 Zimmer
- Gewalt: K −20, die Wrights werden misstrauisch

---

## 4. Entscheidungen (meine Empfehlungen)

1. **Jade statt Kitty:** Miss Kitty ist im Cat's Paw eine Vanilla-Figur mit eigenem Skript. Ihre rechte Hand verhandelt für sie. Die Kralle in Redding führt Kitty aus der Ferne.
2. **Venutis Gebühr** läuft über die Schmiergeld-Abweichung des Strumpfbands, also mitten in der Wochenrechnung.
3. **Kittys Hälfte bei der Fusion** ist ein Tribut von 10 Punkten. Die Filiale hat keine eigene Rechnung; so bleibt die Wochenrechnung eine Rechnung je Haus.
4. **Die Umarmung erfasst auch später übernommene Häuser.** „Jet-Theke in allen Häusern Pflicht“ gilt für das ganze Imperium.
5. **Wer Venuti in Akt 1 erschießt,** beendet die Linie mit dem leeren Stuhl, H +20. Fallout lässt diese Abkürzung zu.

---

## 5. Welt-Felder

Welt 110–117: Aktwoche, Gebühr, Flags (gedemütigt, Dealer, Beweise, geheilt, Rache …), Kittys Weg, Tote, letzte Abwerbung, Umarmungs-Häuser, letzte verwüstete Nacht. Aktstand in `RL_W_VIRGIN`, Cat's Paw in `RL_W_CATSPAW` (neuer Wert 3: bei den Mordinos).

---

## 6. Testen im Spiel

| Test | Erwartung |
|---|---|
| Zwei Wochen nach der Übernahme des Strumpfbands | Meldung über Venuti; er sitzt an der Bar (Platz Gast 1) |
| Venuti: „No.“ | Er geht. Die Meldung über Jet im Haus folgt sofort. Roz: „About the Jet in the house“ |
| Akt 2 | Jade (Platz Gast 2) mit den fünf Wegen |
| Akt 4: „Get out of my house“ | drei Angreifer im Saal |

---

## 7. Nächste Schritte

Weiter mit **Schritt 13** des [Fahrplans](fahrplan.md): die Talente.
