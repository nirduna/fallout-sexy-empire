# Umsetzung 7 – New Reno: Das Silberne Strumpfband und das Hauptquartier

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt und gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 36 Tests, davon 11 neu für New Reno, und 297 erkundete Dialogzustände im Strumpfband.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 1](phase-1-core-loop-und-wirtschaft.md), Ansatz C: Paten, Consigliere, Läufer, Familientreffen
- [Phase 2](phase-2-standorte-und-ausbau.md), Abschnitt 2.2: Strumpfband, Spieltische, Jet-Theke
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 2.2: „Der Segen“
- [Fahrplan](fahrplan.md), Schritt 7

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_newreno.h`](../scripts_src/headers/rl_newreno.h) | **neu:** Urkunde, Segen, Paten, Misstrauen, Figuren im Strumpfband, Familientreffen, HQ-Kasse |
| [`rl_kampf.h`](../scripts_src/headers/rl_kampf.h) | **neu:** Kämpfe in den Häusern. Jedes Haus hat eigene Angreifer-Felder, damit sich Kämpfe in zwei Häusern nicht überschreiben |
| [`rlwitwe.ssl`](../scripts_src/rotlicht/rlwitwe.ssl) | **neu:** Loretta Varga, die Witwe. Die Urkunde per Kauf, Überreden oder Grab |
| [`rlfixer.ssl`](../scripts_src/rotlicht/rlfixer.ssl) | **neu:** Frankie „Two Chairs“ Pagano. Vermittelt den Segen der vier Familien, die Fälschung und die Eröffnungsnacht |
| [`rlroz.ssl`](../scripts_src/rotlicht/rlroz.ssl) | **neu:** Roz Mercer, Madame des Strumpfbands (Führung 55). Hat das gemeinsame Manager-Menü |
| [`rlconsig.ssl`](../scripts_src/rotlicht/rlconsig.ssl) | **neu:** Leopold Asch, Consigliere. Zahlt die HQ-Kasse aus, gibt den Bericht über alle Häuser und leitet die Familientreffen |
| [`rlren01.ssl`](../scripts_src/rotlicht/rlren01.ssl) | setzt die Figuren je nach Stand. Ist Pagano tot, beginnt die Eröffnungsnacht von selbst |
| [`rlangreifer.ssl`](../scripts_src/rotlicht/rlangreifer.ssl) | Angreifer für jedes Haus. Das Haus kommt aus `RL_W_HAUS_HIER`, das jedes Kartenskript setzt |
| [`rl_sonder.h`](../scripts_src/headers/rl_sonder.h) | Sondermodul **Jet-Theke** |
| [`rl_manager.h`](../scripts_src/headers/rl_manager.h) | Jet-Theke im Ausbau. Neuer Haken `RLM_EXTRA_OPTIONEN` für eigene Optionen im Hauptmenü |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_nr_woche`: aufgeflogene Fälschung, Treffen, Shark Club, Jet-Vertrag, Misstrauen. `rl_nr_brief`: Bishops Brief auf Westins Ranch. Stoff-Ereignisse je nach Pate |
| `text_src/english/dialog/_rl_manager.inc` | **neu:** neutrale Texte des Manager-Menüs. Neue Madames schreiben nur noch ihre eigene Stimme (etwa 30 Sätze) |
| [`tools/intvm.py`](../tools/intvm.py) | Inventar (`obj_is_carrying_obj_pid`), Sichtbarkeit, Abblenden. Beim Kartenwechsel läuft das Kartenskript zuerst, wie in der Engine |

---

## 2. „Der Segen“: so wird das Strumpfband übernommen

Zwei Dinge braucht der Spieler: **die Urkunde** und **den Segen einer Familie**. Sobald beides da ist, gehört ihm das Haus. Pagano schickt dann Roz und Asch.

### 2.1 Die Urkunde

| Weg | Wo | Check | Folge |
|---|---|---|---|
| Kaufen | Witwe | 1.000 $, mit Barter 60 750 $ | sauber, E New Reno +5 |
| Überreden | Witwe | Speech 60 | sauber, E New Reno +5 |
| Das Grab in Golgotha | Witwe (bei ihrem Tod Pagano) | Schaufel im Inventar | Titel **Grave Digger**, Karma −10. Ohne Sneak 40 sieht ihn jemand: H New Reno +10 |
| Fälschung | Pagano | Science 60 und 100 $ für Papier | H +5. Mit 15 % fliegt sie nach 2 Wochen auf |

**Fliegt die Fälschung auf,** kommt die Witwe zurück und will 500 $:
- Zahlt der Spieler, ist die Sache erledigt.
- Weigert er sich oder lässt er 2 Wochen verstreichen, erzählt sie es ganz Virgin Street: E New Reno −10, H +10.

### 2.2 Der Segen

| Pate | Auftrag bei Pagano | Check | Folge beim Auftrag |
|---|---|---|---|
| **Mordino** | Jet an den Wrights vorbei in die Stables | Sneak 60 **oder** Kampf 60 | H +10, mit Kampf H +15 |
| **Wright** | Beweis, dass Mordino-Jet im Cat's Paw kursiert | PE 7 **oder** Steal 60 | Miss Kitty weiß, wer geschnüffelt hat (`RL_W_KITTY_WEISS`, für Schritt 12) |
| **Salvatore** | eine Übergabe in der Wüste bewachen | Kampf 60, **oder** die Vanilla-Übergabe ist schon erledigt | – |
| **Bishop** | ein Brief an Westin | Abgabe beim Betreten von Westins Ranch. Öffnen mit Lockpick 60 | E NCR +10. Geöffnet H +15 und Erpressungsmaterial |
| **Made Man** einer Familie | – | Vanilla-Titel | Segen dieser Familie sofort |
| **Unabhängig** | Die Eröffnungsnacht: drei Männer ohne Farben stürmen das Haus | echter Kampf im Haus, nur mit Urkunde | E New Reno +10 |

„Kampf 60“ ist der beste Kampf-Skill (Small Guns, Big Guns, Energy Weapons, Melee, Unarmed). Nur die Eröffnungsnacht ist ein echter Kampf, so wie es Grundsatz 4 des Fahrplans verlangt.

Familien, deren Oberhaupt in Vanilla tot ist, bietet Pagano nicht mehr an.

### 2.3 Die Paten

Wirkung ab der Übernahme ([Phase 1](phase-1-core-loop-und-wirtschaft.md), Tabelle der Paten). Grundtribut in New Reno: 20 %.

| Pate | Tribut | Bonus | misstrauisch |
|---|---|---|---|
| Mordino | 25 % | Kunden +15 %, Nebenumsatz +3 $, Stoff-Ereignisse ×2, Jet-Theke erlaubt | Wright |
| Wright | 20 % | Nebenumsatz +3 $ (Schnaps zum Selbstkostenpreis), Stoff-Ereignisse ×½, keine Jet-Theke | Mordino |
| Salvatore | 30 % | Sicherheit +30 | Bishop |
| Bishop | 20 % | E NCR +20 | Salvatore |
| Unabhängig | 0 % | – | alle vier, H New Reno +20 |

**Misstrauen:** Jede misstrauische Familie, deren Oberhaupt noch lebt, bringt dem Strumpfband H +2 pro Woche.

---

## 3. Das Hauptquartier

- **Läufer** bringen jede Woche die Kassen aller anderen Häuser ins Strumpfband. Das gab es schon seit Umsetzung 1; jetzt gibt es jemanden, der auszahlt.
- **Leopold Asch** zahlt die HQ-Kasse aus und berichtet:
  - je eigenem Haus Kunden, Gewinn und Hitze
  - den Paten und die misstrauischen Familien
- **Familientreffen:** ab dem Familiensitz (Hausklasse 3) alle 4 Wochen. Der Spieler hat 2 Wochen Zeit hinzugehen. Die fünf Themen kommen der Reihe nach, Themen toter Familien entfallen:

| Thema | Wahl | Folge |
|---|---|---|
| Salvatore will mehr | zahlen | Tribut +5 Punkte |
| | Speech 70 | nichts ändert sich, E +5 |
| | nein | Salvatore misstrauisch, H +20, 300 $ Schaden an der Bar |
| Die Mordinos wollen durch die Hintertür verkaufen | annehmen | +300 $/Woche in die Kasse, Karma −10, Stoff-Ereignisse ×2, Wright misstrauisch. Endet, wenn Big Jesus tot ist |
| | ablehnen | Mordino misstrauisch |
| Wright will wissen, wer das Jet verkauft hat | helfen | E +10, H +10, Mordino misstrauisch |
| | schweigen | Wright misstrauisch |
| Bishops Anteil am Shark Club | 1.000 $ (erst HQ-Kasse, dann Tasche) | +100 $/Woche in die HQ-Kasse, solange Bishop lebt |
| | mit dem geöffneten Brief | Anteil umsonst, Bishop misstrauisch, H +10 |
| | ablehnen | – |
| Ein Läufer zweigt ab | PE 7 | 200 $ zurück |
| | Speech 60 | E +5 |
| | ein Exempel | H +10, Karma −5 |

- **Verpasst der Spieler ein Treffen,** entscheiden die Familien ohne ihn. Es gelten die Folgen des Nein: Salvatore wie „nein“, Mordino und Wright werden misstrauisch, der Läufer behält 200 $.
- Mit dem Titel **„Die Fünfte Familie“** bekommen alle Checks beim Treffen +10 (Speech +10, PE +1), wie in [Phase 6](phase-6-karma-ruf-endings.md) vorgesehen.

---

## 4. Die Jet-Theke

- Sondermodul für 800 $ mit 2 Wochen Bauzeit.
- Nur im Strumpfband, nur mit Mordino als Paten oder mit dem Jet-Vertrag, nie unter Wrights Segen.
- Wirkung: Nebenumsatz +6 $ je Kunde und Stoff-Ereignisse ×2. Die Wrights werden misstrauisch und bleiben es.

Die **Spieltische** stehen schon im Modulkatalog und sind verfügbar, sobald das Strumpfband dem Spieler gehört.

---

## 5. Entscheidungen (meine Empfehlungen)

1. **Die Paten sprechen nicht selbst.** Frankie Pagano vermittelt, so wie Kolbe für Metzger (Grundsatz 1). Kein Vanilla-Skript wird verändert.
2. **Der Segen ersetzt die Einflussschwelle.** Phase 2 verlangt E New Reno ≥ 20 für die Übernahme. Mit dem Segen steigt E auf mindestens 20; ein eigenes Einfluss-Sammeln vorher gibt es nicht.
3. **Die Familienaufträge sind Dialog-Aufträge mit sofortigem Ergebnis.** Die Nacht vergeht hinter einer Blende. Wer den Check nicht hat, sieht die Option nicht. Nur der Brief an Westin verlangt eine echte Reise in die NCR.
4. **Das Grab** läuft über den Dialog mit der Witwe (oder mit Pagano, wenn sie tot ist). Die Vanilla-Karte Golgotha bleibt unberührt.
5. **Wer stirbt, bleibt tot, aber die Quest bricht nicht:**
   - Pagano tot und die Urkunde beschafft: Die Eröffnungsnacht beginnt beim nächsten Betreten von selbst.
   - Die Witwe tot: Pagano weiß vom Grab.
   - Roz tot: Führung 30, Asch zahlt die Kasse des Strumpfbands aus.
   - Asch tot: Roz öffnet seinen Safe mit der HQ-Kasse.
6. **Kämpfe je Haus.** Die Gosse behält ihre Welt-Felder aus Umsetzung 5. Die anderen Häuser haben `RL_F_ANGRIFF` und `RL_F_ANGREIFER`, damit die Virgin Street (Schritt 12) und die Soldaten (Schritt 15) dieselbe Technik nutzen.
7. **Salvatores „10 % mehr“** sind +5 Prozentpunkte Tribut. Zehn Punkte würden das Haus bei 40 % Tribut in die Verlustzone drücken, und das Treffen wäre keine echte Wahl mehr.
8. **Neue Madames** binden `_rl_manager.inc` ein und schreiben nur ihre eigenen Sätze. Das hält fünf weitere Madames in den folgenden Schritten überschaubar.

### Behobener Fehler aus früheren Schritten

`destroy_object(self_obj)` beendet das Skript sofort (Engine: `PROGRAM_FLAG_0x0100`).
- **Folge:** Bei Mara und Jess lief danach `gfade_in` nicht mehr. Der Bildschirm wäre schwarz geblieben, sobald eine der beiden geht.
- **Korrektur:** Jetzt wird zuerst ausgeblendet, die Figur unsichtbar gemacht, wieder eingeblendet und erst ganz am Schluss zerstört.
- **Absicherung:** Das Prüfwerkzeug meldet künftig jedes Abblenden ohne Einblenden.

---

## 6. Welt-Felder

Neue Felder 55–72 in `RL_W_*` (siehe [`rotlicht.h`](../scripts_src/headers/rotlicht.h)): Urkunde, Pate, Misstrauen, Brief, Eröffnung, Fälschung, Witwe, Kitty, Treffen (vier Felder), Shark Club, Jet-Vertrag, Haus hier, Tote, Bekanntschaften. Neue Hausfelder 36–37: Angriff und Angreifer.

Das Welt-Array hat weiterhin 96 Felder. Ältere Spielstände werden wie bisher beim Laden erweitert.

---

## 7. Testen im Spiel

| Test | Erwartung |
|---|---|
| Das Strumpfband zum ersten Mal betreten | Loretta Varga (Gast 1) und Frankie Pagano (Gast 2) sind da |
| Witwe: 1.000 $ | Urkunde. Die Witwe blendet aus, **der Bildschirm kommt zurück** |
| Pagano: „About the families“ → Mordino → [Sneak] | Segen und Übergabe: Pagano geht, Roz und Asch stehen im Saal |
| Roz ansprechen | erstes Gespräch, dann das Manager-Menü |
| Asch: „The treasury“ | zeigt, was die Läufer gebracht haben |
| Neues Spiel: Urkunde, dann „What if I don't want any of them?“ → „Let them come“ | Pagano geht, drei Angreifer greifen an. Sind alle tot, stehen Roz und Asch da |
| Bishops Brief nehmen, Westins Ranch in der NCR betreten | Meldung „Westin's people took Bishop's letter“. Zurück bei Pagano: Bishops Segen |
| Hausklasse 3 bauen, 4 Wochen warten | Meldung „The families are sitting down at the Garter“. Asch bietet das Treffen an |
| Jet-Theke mit Mordino als Pate | im Ausbau unter „Something you only get in New Reno“ |

**Nicht im Prüfwerkzeug sichtbar:**
- ob die Angreifer auf der Karte gut stehen und laufen
- ob `set_obj_visibility` vor dem Einblenden sauber aussieht
- wie die Figuren mit ihren Vanilla-Grafiken wirken (Pagano und Asch nutzen Bürger-Protos)

---

## 8. Nächste Schritte

Weiter mit **Schritt 8** des [Fahrplans](fahrplan.md): Redding, Die Schlacke.
