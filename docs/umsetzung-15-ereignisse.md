# Umsetzung 15 – Ereignisse vollständig

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt und gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 77 Tests, davon 3 neu.
- Jedes Krisenmenü wird zweimal erkundet, einmal mit allen Optionen zugleich. So ist geprüft, dass alles ins Optionsfenster passt.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 4](phase-4-personal-talente-ereignisse.md), Abschnitte 4.1–4.3, Leitlinie 5 (Tod mit Vorwarnung)
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 5 (Totengräber)
- [Fahrplan](fahrplan.md), Schritt 15

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_ereignisse.h`](../scripts_src/headers/rl_ereignisse.h) | **neu:** Tod im Haus, Razzien je Stadt (Beweise, Frühwarnung, Folgen), Inspektion der Liga |
| [`rl_manager.h`](../scripts_src/headers/rl_manager.h) | Das Krisenmenü mit allen Lösungswegen je Krise |
| [`_rl_krisen.inc`](../text_src/english/dialog/_rl_krisen.inc) | **neu:** Beschreibungen, Optionen und Ausgänge (1100–1220) |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | Ereigniswahl mit acht neuen Arten, `rl_krise_woche` (Eskalation je Art), `rl_ereignisse_woche` (die Soldaten kommen wieder), Abwerbung und Überfall als Krisen |
| [`rotlicht.h`](../scripts_src/headers/rotlicht.h) | Ein Stammkunde mit Geheimnis kostet keine Kunden |
| [`intvm.py`](../tools/intvm.py) | `add_obj_to_inven` für die erbeutete Rüstung |

---

## 2. Die Krisen und ihre Lösungen

| Krise | Wege | Nicht gelöst nach 3 Wochen |
|---|---|---|
| **Soldaten ohne Krieg** | 200 $ (50 %: in 4 Wochen wieder da) · unter den Tisch trinken (Bar II im Haus, Barter 50), dann die Rüstung nehmen (K −5, eine Powerrüstung) oder laufen lassen · Speech 70 · anwerben (Speech 90 oder CH 8): Deserteur, Sicherheit +50 · Kampf (Talus im Haus oder Kampfwert 80): 300 $ für die Teile, H +20, Leichen für den Totengräber | eine Person stirbt: Moral −20, Ruf −10, Tod im Haus |
| **Der Stoff** | Doctor 60 · Krankenstube im Haus · 200 $ · Entzugsstube der Schlacke · Myrons Antidot · an der Leine · entlassen | ab der zweiten Woche jede Woche 25 % Überdosis: Tod im Haus |
| **Gewalttätiger Freier** | Unarmed 50 selbst (H +5) · Hausverbot (Ruf −2) · Talus erledigt ihn ohnehin | eine Person stirbt |
| **Seuche** | Doctor 60 · ein Arzt aus der Stadt (300 $) · zwei Wochen schließen | zwei Wochen geschlossen, Moral −10 |
| **Griff in die Kasse** | IN 7: die Bücher (+100 $) · Sneak 50: beschatten (+100 $, die Diebin geht) · hinnehmen | noch einmal 300 $ weg |
| **Flucht / Kündigung** | ziehen lassen · zurückholen (Outdoorsman 60 oder Kampfwert 60, K −10 bei Zwang) | eine Person weg. Beim Zwangspersonal stirbt sie auf der Flucht |
| **Metzgers Vergeltung** | wie bisher: 300 $, Kampf, die Rangers | Moral −10, Ruf −10 |
| **Tod im Haus** | Beerdigung (100 $, Moral +5) · Schweigen (Moral −15) · Rache, nur nach Gewalt (H +10, Moral +5) | wie Schweigen |
| **Stammkunde mit Geheimnis** (VIP-Trakt) | in die Akte (E +5) · sein Schweigen verkaufen (+200 $, K −5) · vergessen. Kostet keine Kunden | die Gelegenheit ist vorbei |
| **Abwerbung** (Kitty als Rivalin) | Gegenangebot (Barter 60, 100 $) · ziehen lassen | die Person geht zu Kitty |
| **Überfall auf die Läufer** | die Spur verfolgen (Outdoorsman 60): das Geld kommt zurück · abschreiben | das Geld ist weg |
| **Ghul im Haus** (Vesper) | hinauswerfen (Unarmed 60 oder Kampfwert 60): Vesper +5 · Speech 60: den Saal beruhigen · dem Rausschmeißer überlassen: Vesper −20 | Vesper −20 |
| **Der Richter** (Abigail) | heilen (K +5, Abigail +5) · bloßstellen (H +10, Abigail +10) · vergiften (K −20, Abigail +10, H +15, Leiche) | Abigail stellt ihn allein bloß: H +10, Abigail −10 |
| **Besuch aus dem Bunker** (der Deserteur) | ausliefern (Sicherheit −50, K +5) · Sneak 60: verstecken · Kampfwert 80: wegschicken (H +20, E +5) | die Brotherhood holt ihn |

**Die Soldaten** kommen vor dem Fall der Enklave nur ins Strumpfband mit Salvatore als Paten und in die Bilge. Danach kommen sie in jedes Haus, dreimal so oft. Die Madame kann sie nicht allein lösen, und das gilt für alle neuen Krisen.

**Die Inspektion der Liga** unter der Lex Neun wird sofort entschieden:
- Bestanden bei Moral ≥ 60 ohne Zwangspersonal: Ruf +2.
- Sonst ist die Ausnahme verwirkt, und die Tränke hat für immer −15 %.

---

## 3. Razzien je Stadt

| Stadt | Wer | Was gefunden wird | Folge | Beweise beseitigen (angekündigt) |
|---|---|---|---|---|
| The Den | Männer der Sklavengilde | Flüchtlinge: Mara versteckt oder die Transporte, ohne Zuflucht | Mara wird verschleppt, Metzger wird Feind, Moral −15 | Sneak 60 oder Outdoorsman 60: für eine Nacht fortbringen |
| New Reno | „Besuch“ einer Familie | Schwäche | 200 $ Schaden, E −10 | 200 $ für Leute mit Waffen, oder Kampfwert 60 selbst (H +10, E +5) |
| Redding | Sheriff Marion | gezinkte Waage, Schutzgeld | Revolte der Kumpel (Umsetzung 8). Schutzgeld: Marion wird Feind, H +20 | die Waage tauschen, das Schutzgeld einstellen |
| NCR | Polizei, Rangers | ohne Papiere, Zwangspersonal | 500 $ Strafe. Zwangspersonal: Lizenzentzug, die Rangers werden Feinde, die Menschen sind frei | Sneak 60: Vortis' Leute verstecken |
| Vault City | Garde | – | unverändert (Umsetzung 9) | – |
| San Francisco | Inspektoren der Shi | – | unverändert (Umsetzung 11) | – |

**Frühwarnung:**
- Bei E ≥ 60, mit Tyler auf der Lohnliste (Den) oder mit dem Polizisten (NCR) ist die Razzia eine Woche angekündigt. Sie steht dann als Krise im Menü der Madame, und in der nächsten Woche kommt sie.
- Ohne Frühwarnung kommt sie sofort.

---

## 4. Entscheidungen (meine Empfehlungen)

1. **Die Madame löst nur die alten kleinen Ereignisse.** Soldaten und alle neuen Krisen brauchen den Spieler. Phase 4 sagt es für die Soldaten („normale Rausschmeißer haben keine Chance“), und die neuen Krisen sind Entscheidungen, keine Routine.
2. **„Besuch“ in New Reno:** Phase 4 nennt „Schäden am Haus, 2 Wochen Ausfall eines Moduls“. Ich setze das als 200 $ Reparatur um. Ein Modul für zwei Wochen abzuschalten und wieder einzuschalten, wäre fehleranfällig und im Spiel kaum sichtbar.
3. **Die Beute der Soldaten:**
   - Beim Trinken gibt es eine Powerrüstung, denn Phase 4 sagt „die Rüstung abnehmen“.
   - Beim Kampf gibt es 300 $ für die Teile. Powerrüstungsteile gibt es in Fallout 2 nicht als Gegenstand.
4. **Tod im Haus ersetzt die Krise,** aus der er kommt. So hat jedes Haus immer nur eine Krise, und der Tod bleibt nicht unbemerkt hinter einer anderen.
5. **Abwerbung als Krise:**
   - Kittys Angebot steht im Menü der Madame. Wer nichts tut, verliert die Person nach drei Wochen.
   - Hat das Haus schon eine Krise, geht sie sofort wie bisher.
6. **Überfall auf die Läufer** wird eine Krise im Hauptquartier. Die Spur führt nach New Reno, wo die Läufer ankommen.
7. **Die Seuche** schließt das Haus nach drei Wochen ohne Lösung von selbst für zwei Wochen.

---

## 5. Welt-Felder

Welt 137–144:
- Soldaten: Haus und Woche der Rückkehr
- Deserteur: Haus und Woche
- Beute des Überfalls
- Tod durch Gewalt (Bits je Haus)
- Ereignis-Flags: Richter gewesen, Lex Neun verwirkt
- Beweise vor der Razzia beseitigt (Bits je Haus)

---

## 6. Testen im Spiel

| Test | Erwartung |
|---|---|
| Debug-Build, Krise über das Hauptbuch abwarten | Die Madame bietet die Wege aus Abschnitt 2 an. „Later.“ ist immer sichtbar |
| Gosse mit E ≥ 60 oder Tyler auf der Lohnliste | Eine Razzia kommt angekündigt: Meldung, Krise, eine Woche Zeit |
| Soldaten unter den Tisch trinken, Rüstung nehmen | Powerrüstung im Inventar |

---

## 7. Nächste Schritte

Weiter mit **Schritt 16** des [Fahrplans](fahrplan.md): Abschluss.
