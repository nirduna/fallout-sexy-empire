# Umsetzung 5 – „Ketten“, Akt 2–5, und Mara

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Umgesetzt, kompiliert und im [Prüfwerkzeug](pruefwerkzeug.md) durchgespielt (24 Tests, 170 erkundete Dialogzustände allein für Akt 2–5). **Test im Spiel offen.**

**Grundlage:**
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 3.2: Questline „Ketten“
- [Phase 4](phase-4-personal-talente-ereignisse.md), Abschnitt 3.5 (Mara) und 4.3 (Metzgers Vergeltung)
- [Phase 2](phase-2-standorte-und-ausbau.md), Abschnitt 2.1: Modul „Die Zuflucht“
- [Phase 6](phase-6-karma-ruf-endings.md): Karma, Nachsätze „Ketten“ und „Die Überlebende“
- [Fahrplan](fahrplan.md), Schritt 5

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`scripts_src/headers/rl_ketten.h`](../scripts_src/headers/rl_ketten.h) | **neu:** Zustände und gemeinsame Prozeduren der Akte 2–5, zum Beispiel:<br>- Mara verstecken, retten oder ausliefern<br>- Aufträge<br>- Enden<br>- Kampf im Haus<br>- wer wann in der Gosse steht |
| [`scripts_src/headers/rl_sonder.h`](../scripts_src/headers/rl_sonder.h) | **neu:** Sondermodule außerhalb des Simulator-Katalogs. Als erstes „Die Zuflucht“. Später folgen gezinkte Waage, Jet-Theke, Akte, Schmuggelkammer und Registratur |
| [`scripts_src/rotlicht/rlmara.ssl`](../scripts_src/rotlicht/rlmara.ssl) | **neu:** Mara. Akt 2, versteckt in der Gosse, Rückkehr, Madame mit dem gemeinsamen Manager-Menü |
| [`scripts_src/rotlicht/rldeke.ssl`](../scripts_src/rotlicht/rldeke.ssl) | **neu:** Deke, einer von Tylers Leuten. Akt 4 im Fluchtzweig |
| [`scripts_src/rotlicht/rljess.ssl`](../scripts_src/rotlicht/rljess.ssl) | **neu:** Jess, Laras Leutnant. Akt 4 im Tyrannen-Zweig |
| [`scripts_src/rotlicht/rlangreifer.ssl`](../scripts_src/rotlicht/rlangreifer.ssl) | **neu:** Angreifer bei Kämpfen im Haus |
| [`rlessie.ssl`](../scripts_src/rotlicht/rlessie.ssl) | Essie zeigt Mara, warnt vor der Durchsuchung und kündigt, wenn Mara ausgeliefert wird. In Akt 5 fällt bei ihr die Entscheidung Sturm oder stiller Krieg |
| [`rlkolbe.ssl`](../scripts_src/rotlicht/rlkolbe.ssl) | Kolbe im Tyrannen-Zweig: Er findet Mara, vergibt Lieferungen nach Norden, warnt vor Lara und bringt Metzgers Partnerschaft oder den Verrat |
| [`rlden01.ssl`](../scripts_src/rotlicht/rlden01.ssl) | Das Kartenskript setzt Kolbe, Mara, Deke und Jess nach dem Stand der Questline |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | Wochentakt: Akt-Übergänge, Aufträge, Durchsuchung, Vergeltung, Einnahmen, Maras Rückkehr und Abschied. Bei jedem Tick: die Enden, die an Metzgers Tod hängen, und Tylers Tod in Vanilla |
| [`rl_manager.h`](../scripts_src/headers/rl_manager.h) | Menüpunkt „The route south“, Sondermodule im Ausbau, Lösungen für Metzgers Vergeltung |
| [`rotlicht.h`](../scripts_src/headers/rotlicht.h) | 96 Welt-Felder statt 32; ältere Spielstände werden beim Laden erweitert |
| Texte | Mara, Deke, Jess, Angreifer, Essie 800–836, Kolbe 700–761, alle Madames 174–177, 188 und 600–611, `rotlicht.msg` 130–144, `_rl_sonder.inc` |
| Werkzeuge | `bau_karten.py`: Laufzeit-Positionen für Mara, Deke/Jess und zwei Angreifer, geprüft gegen Wände. `intvm.py`: `float_msg`. `check_msg.py`: Sondermodule, Krise 8 |

---

## 2. Ablauf

### Akt 2 – Die im Keller

Eine Woche nach der Antwort auf Metzgers Angebot versteckt sich Mara in der Gosse. Die Meldung lautet „Essie wants to see you. It can't wait.“ Essie zeigt sie beim nächsten Gespräch. Führt Essie das Haus nicht mehr, meldet stattdessen Kolbe den Fund.

| Weg | Bedingung | Folge |
|---|---|---|
| **Verstecken** | Essie führt das Haus, kein Pferch im Keller | Karma +10, Akt 3. Metzgers Leute durchsuchen die Den nach einer Woche. **Ohne Zuflucht finden sie Mara:** Sie wird verschleppt, Metzger wird Feind, die Moral sinkt um 15. Eine Zuflucht im Bau genügt schon |
| **In Sicherheit bringen** | Sneak 60 oder Outdoorsman 60 | Mara geht in die NCR und kommt später wieder (Akt 3 „Die Reinen“, Fahrplan 10) |
| **Ausliefern** | – | 500 $, Metzger wird Freund, Karma −25. Die Linie läuft **im Tyrannen-Zweig** weiter. Essie kündigt, außer sie ist längst gebrochen (Pferch). Dann führt Kolbe das Haus |

### Akt 3 – Die Kette

| Zweig | Auftrag | Probe | Folge je Auftrag |
|---|---|---|---|
| **Flucht: Nach Süden** | Im Manager-Menü „The route south“. Braucht das Versteck der Rangers (Maras Wissen oder Perception 7) und die Zuflucht | bessere von Sneak und Outdoorsman, mit Mara als Madame +25. Höchstens 95 % | **Gelingt:** Hitze Den +10, Karma +5, Einfluss NCR +3.<br>**Misslingt:** Metzger wird Feind, Moral −10 |
| **Tyrann: Nach Norden** | Kolbe: Vault City (Dienstboten-Zuteilung) oder Vortis | bessere von Speech und Barter | **Immer:** Karma −15.<br>**Gelingt:** 300–600 $ in die Kasse, Hitze NCR +10.<br>**Misslingt:** Hitze NCR +20 |

- **Zeit:** Die Probe fällt beim Annehmen, das Ergebnis kommt nach einer Woche.
- **Akt 4:** Nach drei gelungenen Aufträgen beginnt Akt 4.

### Akt 4 – Tylers Preis / Laras Sturm

| Zweig | Figur | Wege |
|---|---|---|
| Flucht | **Deke** (Tylers Mann) | abkaufen (Barter 60, 400 $) · Lara auf Tyler hetzen (Speech 60) · umdrehen (Speech 80) · **Kampf**: Deke und zwei Schläger |
| Tyrann | **Jess** (Laras Leutnant) | ziehen lassen: Der Pferch wird leer, Karma +10, Metzger ist nicht mehr Freund · **Kampf** gegen Jess und zwei Kämpferinnen, Karma −10 |

- **Kampf im Haus:** Die Angreifer greifen auch nach einem Kartenwechsel wieder an. Fällt der letzte, endet der Akt.
- **Vanilla:** Ist Tyler schon tot, entfällt Akt 4 im Fluchtzweig.

### Akt 5 – Die Enden

| Ende | Zweig | Wie | Folgen |
|---|---|---|---|
| **Die Gilde fällt** | Flucht | Bei Essie „Tonight. Tell them we go in.“ Laras Leute und die Rangers halten die Wachen auf, **Metzger tötet der Spieler selbst** (Vanilla-Kampf in der Gilde). Stirbt Metzger auf anderem Weg, gilt es genauso | Karma +50, Hitze Den −20, Einfluss NCR +15. Die Rangers werden Verbündete, Vortis wird Feind. Den-Kunden −25 % (Vanilla-Modifikator) |
| **Der stille Krieg** | Flucht | „Not yet. We keep the route running.“ | Die Route läuft weiter. Alle 6 Wochen schlägt Metzger zu (Krise „Metzgers Vergeltung“: bezahlen, selbst kämpfen bei Waffe/Nahkampf/Unbewaffnet 60, oder die Rangers rufen). Stirbt Metzger später, wird daraus „Die Gilde fällt“ |
| **Metzgers Mann** | Tyrann | Kolbe: „Tell him yes.“ | 200 $ pro Woche in die Kasse der Gosse, Vanilla-Titel **Sklavenhändler**, Ende Tyrann |
| **Der neue Metzger** | Tyrann | Kolbe: „And if Metzger had an accident?“, dann Metzger töten. Stirbt Metzger im Tyrannen-Zweig, erbt der Spieler die Gilde | Karma −100, Sklavenhändler, Rangers werden Feinde, Kunden der Den +50 % (Modifikator 70 statt 20). Nachsatz „Ketten“ im Abspann |

### Mara als Madame (Phase 4, 3.5)

1. **Rückkehr:** Nach einem Ende im Fluchtzweig kehrt Mara zurück.
   - War sie versteckt, sofort.
   - War sie in der NCR, nach zwei Wochen: „Someone is waiting for you in the Gutter.“
2. **Gespräch:** Sie wird Madame, wenn der Spieler Speech 50 oder Charisma 6 hat (mit „Anständiges Haus“ ohne Probe) **und nirgends Zwangspersonal hält**.
   - **Wirkung:** Führung 70, Moral +1 pro Woche, Transporte +25. Nachsatz „Die Überlebende“.
   - **Gedrängt** („You owe me this, Mara.“): Sie geht zu Ruth Calloway.
3. **Abschied:** Arbeitet irgendwo jemand gezwungen, geht sie und bringt den Rangers Beweise (Hitze NCR +20).

---

## 3. Entscheidungen in dieser Umsetzung (meine Empfehlungen)

1. **Ausliefern führt in den Tyrannen-Zweig.** Wer Mara Metzger übergibt, hat sein Vertrauen, und die Linie gibt ihm Lieferungen statt Transporte. Anders wäre der Fluchtzweig nach einem Verrat an Mara nicht glaubwürdig.
2. **Den Sturm auf die Gilde führt der Spieler selbst.**
   - Das Addon ändert Metzgers Vanilla-Skript nicht.
   - Laras Leute und die Rangers sind Erzählung und Kulisse. Der Kampf gegen Metzger ist der Vanilla-Kampf in der Gilde.
   - Das Ende tritt ein, sobald Metzger tot ist, egal auf welchem Weg.
3. **Im Tyrannen-Zweig macht Metzgers Tod den Spieler zum neuen Metzger.** Wer als sein Lieferant die Gilde stürzt, erbt sie. Eine saubere Seite gibt es für den Spieler hier nicht mehr.
4. **Aufträge statt Reisen.**
   - Transporte und Lieferungen sind Dialog-Aufträge mit einer Woche Laufzeit ([Fahrplan](fahrplan.md), Grundsatz 4).
   - Die Probe fällt beim Annehmen. So kann man sie nicht durch Neuladen der Woche umgehen.
5. **Die Zuflucht als Sondermodul im Ausbau-Menü** (600 $, eine Woche Bauzeit, +25 $ Unterhalt).
   - Sie schließt den Riegel außen aus.
   - Eine Zuflucht im Bau schützt schon vor der Durchsuchung. Sonst wäre die Warnung eine Falle ohne Ausweg.
6. **Kolbe im Tyrannen-Zweig:** Nach Akt 1 geht er und kommt mit Akt 3 als Metzgers Bote zurück.

---

## 4. Testen

**Automatisch:**
- **Aufruf:** `python3 tools/test_skripte.py`
- **Neue Tests:**
  - `test_akt2_verstecken_bis_madame`: der ganze Fluchtzweig bis Mara als Madame und zu ihrem Abschied
  - `test_suche_ohne_zuflucht`, `test_akt2_retten_stiller_krieg`, `test_akt2_ausliefern_essie_geht`
  - `test_tyrann_bis_metzgers_mann`, `test_neuer_metzger`
  - `test_kampf_deke_und_jess`, `test_tyler_tot_vanilla`
  - `test_alter_spielstand`
  - `test_erkundung_ketten`

**Im Spiel** (Testpaket mit Debug, Spielstand nach Akt 1):

| Test | Erwartung |
|---|---|
| Eine Woche warten | „Essie wants to see you.“ In der Gosse steht Mara (Hex 18466, unterhalb von Essie) |
| Mara verstecken, **keine** Zuflucht bauen, eine Woche warten | „… found Mara …“, Mara ist fort, Metzger ist Feind |
| Neuer Spielstand: verstecken, bei Essie „Build the hidden room“ | Ausbau-Menü → „Something you only get here in the Den“ → „The Hidden Room ($600)“ |
| Route nach Süden (Sneak 70) dreimal | je Woche eine Erfolgsmeldung, danach „Tyler's boys have been asking …“ |
| Gosse betreten | Deke steht in der Mitte des Raums |
| Deke: „Get out of my house.“ | Kampf gegen Deke und zwei Schläger. Die Schläger kommen die Treppe herunter |
| Essie: „Tonight.“, dann Metzger in der Gilde töten | Meldung „Metzger is dead. The Guild is finished.“ |
| Mara anreden (Speech 50) | Sie wird Madame, ihr Menü öffnet sich |

---

## 5. Nächste Schritte

Weiter mit **Schritt 6** des [Fahrplans](fahrplan.md): Technik für weitere Häuser, dann das Silberne Strumpfband in New Reno.
