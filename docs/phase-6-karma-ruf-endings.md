# Phase 6 – Karma, Ruf & Endings

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Freigegeben. Mit dieser Phase ist das Konzept vollständig. Die Umsetzung läuft, beginnend mit dem [Prolog und dem Ausbau-Dialog](umsetzung-1-prolog-und-ausbau.md).

> **Freigabe-Entscheidungen** (alle Empfehlungen übernommen)
> 1. Fünf echte GVARs, damit die Titel im Charakterbogen erscheinen.
> 2. Fair zu führen ist karmaneutral.
> 3. Die Endtexte bleiben wie geschrieben.
> 4. Vorerst Vanilla-Endbilder, eigene Grafiken später.
> 5. Als Nächstes werden der Prolog „Essies Schulden“ und der Ausbau-Dialog programmiert.
**Grundlage:** [Phase 1](phase-1-core-loop-und-wirtschaft.md) bis [Phase 5](phase-5-technik.md) sind freigegeben. Zielinstallation ist das Restoration Project (RPU).

Das Imperium hinterlässt Spuren auf drei Ebenen und am Ende einen Abschied:

| Ebene | Was sie misst | Wo man sie sieht |
|---|---|---|
| **Karma** | wie der Spieler handelt | Vanilla-Karma, Karma-Titel, Reaktionen im ganzen Spiel |
| **Stadtruf** | was eine Stadt über den Spieler denkt | Reaktionen und Preise der Vanilla-NPCs in dieser Stadt |
| **Titel** | wofür der Spieler bekannt ist | Charakterbogen, Dialogoptionen |
| **Epilog** | was vom Imperium bleibt | Endslides nach dem Fall der Enklave |

Die Engine-Details dieser Phase sind gegen den Quellcode von fallout2-ce und die Datendateien des RPU geprüft. Die Rechnung für Enden, Titel und Stadtruf ist im globalen Skript umgesetzt und kompiliert.

---

## 1. Karma

### 1.1 Grundregel: Fairness ist karmaneutral

Ein Bordell wird im Ödland nicht zur Tugend, nur weil es fair geführt wird. Wer anständig bezahlt, wird deshalb **nicht belohnt, nur nicht bestraft**. Karma gibt es für Taten, die über das Geschäft hinausgehen: Menschen verstecken, Ketten durchtrennen, Gesetze erkämpfen. Karma kostet alles, was Menschen zur Ware macht.

### 1.2 Laufende Quellen (pro Woche und Haus)

| Quelle | Karma/Woche | Phase |
|---|---|---|
| Personal-Anteil „ausbeuterisch“ | −1 | 1 |
| Zwangspersonal hinter dem Riegel außen | −5 | 2, 4 |
| „An der Leine halten“ (Jet statt Lohn) | −3 | 4 |
| Anwerber mit der Methode „Zwingen“ | −3 | 4 |
| Schutzgeld (pro Stand) | −2 | 3 |

### 1.3 Einmalige Quellen

| Tat | Karma | Phase |
|---|---|---|
| Essie an Metzger ausliefern | −25 | 1 |
| Mara an Metzger ausliefern | −25 | 3 |
| Mara verstecken | +10 | 3 |
| Transport auf der Fluchtroute | +5 je Durchgang | 3 |
| Lieferung an Metzgers Kette | −15 je Durchgang | 3 |
| Die Gilde fällt | +50 | 3 |
| Der neue Metzger | −100 | 3 |
| Die Umarmung (Mordinos) | −30 | 3 |
| Das Musterhaus (Lex Neun) | **+20** (neu) | 3 |
| Die Liga anhängen, Calloway ruinieren | −30, mit Mord −60 | 3 |
| Cat's Paw: Druck / Sabotage / Verrat | −10 / −10 / −20 | 3 |
| Gezinkte Waage | −2/Woche solange aktiv | 2 |
| Schuldknechtschaft über die Hubologen | −20 | 3 |
| Spende an eine Krankenstation oder die Rangers | +10 | 3 |

**Zum Maßstab:** Ein Tyrann mit drei Häusern voller Zwangspersonal verliert allein dadurch 15 Karma pro Woche, im Spieljahr also etwa 780. Das reicht, um jeden guten Ruf zu begraben, den man sich in Vanilla erarbeitet hat.

---

## 2. Stadtruf

Jedes Haus färbt auf den Ruf des Spielers in seiner Stadt ab. Das Addon nutzt die Vanilla-Variablen `GVAR_TOWN_REP_*`. Ihre Schwellen stammen aus `reppoint.h`:

- 15 = gemocht
- 30 = verehrt
- −15 = gehasst
- −30 = verachtet

Vanilla-NPCs reagieren darauf in Dialogen und Preisen.

| Regel | Wirkung | Grund |
|---|---|---|
| Zwangspersonal oder Leine im Haus | −1 alle 2 Wochen | Zwang spricht sich herum |
| Hitze ≥ 60 | −1 alle 2 Wochen | Gewalt und Razzien |
| Moral ≥ 70, kein Zwang | +1 alle 4 Wochen, **höchstens bis 15 (gemocht)** | Ein anständiges Haus ist gern gesehen, macht aber niemanden zum Helden |

Die Regeln laufen im Wochentakt (`rl_stadtruf` in `gl_rotlicht.ssl`). Betroffen sind die Städte der sechs Häuser: Den, New Reno, Redding, Vault City, NCR und San Francisco.

---

## 3. Titel

### 3.1 Drei neue Titel im Charakterbogen

Die Engine zeigt einen Titel an, solange seine GVAR ungleich 0 ist (geprüft im Charakter-Editor von fallout2-ce). Jeder Titel braucht deshalb eine eigene GVAR, einen Eintrag in `karmavar.txt` und zwei Texte in `editor.msg`.

| Titel | Bedingung | Wirkung im Spiel |
|---|---|---|
| **Seelenverkäufer** | mindestens 4 Wochen Zwangspersonal oder Leine, **oder** 26 Wochen ausbeuterischer Anteil, **oder** „Der neue Metzger“, „Metzgers Mann“, „Die Umarmung“ | Metzger und Vortis: +10 auf Speech und Barter, Tyrannen-Quellen 20 % billiger. Marcus, die Rangers, Calloway, Mara, Talus und Vesper verweigern sich (wie in Phase 3/4). Alle Checks bei anständigen NPCs −10 |
| **Anständiges Haus** | mindestens 3 Häuser, alle mit Moral ≥ 60, und **nie** Zwangspersonal oder Leine | Werben doppelt so schnell. Marcus, die Rangers und Calloway: +10. Kittys Abwerbung halbiert. Eine gerettete Mara kommt ohne Check |
| **Die Fünfte Familie** | Familiensitz (Hausklasse 3) und Einfluss in New Reno ≥ 80 | Zählt bei den Familien wie Made Man. Tribut in New Reno −5 Prozentpunkte. Checks bei den Familientreffen +10 |

**Texte** (`text_src/german/game/editor.msg.add`)

| Titel | Beschreibung im Charakterbogen |
|---|---|
| Seelenverkäufer | „Du verkaufst, was dir nicht gehört: Menschen. In den Kellern deiner Häuser sitzen die Riegel außen, und jeder, der dort war, weiß es.“ |
| Anständiges Haus | „Wer in deinen Häusern arbeitet, bekommt seinen Teil, einen Arzt und eine Tür, die sich von innen verschließen lässt. Im Ödland reicht das für einen guten Namen.“ |
| Die Fünfte Familie | „New Reno hatte vier Familien. Jetzt hat es fünf, und die fünfte trägt deinen Namen. Die anderen grüßen, wenn du vorbeigehst. Sie meinen es nicht so.“ |

„Seelenverkäufer“ und „Anständiges Haus“ schließen sich aus. Wie die Tätowierung des Sklavenhändlers bleibt „Seelenverkäufer“ für immer: Wer einmal Menschen hinter den Riegel gesperrt oder ein halbes Jahr lang ausgebeutet hat, bekommt „Anständiges Haus“ nie mehr.

### 3.2 Vanilla-Titel und das Imperium

| Vanilla-Titel (RPU) | GVAR | Wirkung im Imperium |
|---|---|---|
| Sklavenhändler | `GVAR_REPUTATION_SLAVER` | wie „Seelenverkäufer“, dazu Start von „Ketten“ im Tyrannen-Zweig (Phase 3) |
| Mafioso (je Familie) | `GVAR_MADE_MAN_*` | Sit-down im Desperado möglich, Gebühren-Schutz (Phase 3) |
| Pornostar | `GVAR_NEW_RENO_PORN_STAR` | Julians Vertrag leichter (Phase 4). Neu: VIP-Kundschaft im Strumpfband +2 |
| Preisboxer | `GVAR_NEW_RENO_HAS_REP_PRIZEFIGHTER` | ersetzt Unarmed-Checks auf der Virgin Street (Phase 3). Neu: Sicherheit im Strumpfband +10 |
| Totengräber | `GVAR_GRAVES_UNEARTHED` | über das Grab in Golgotha erreichbar (Phase 3) |
| Sexperte | `GVAR_SEXPERT` | Neu: Personalqualität in allen Häusern +5 (du weißt, wovon die Leute reden) |

---

## 4. Die Endslides

### 4.1 Welches Ende?

Die Werte werden bei **jedem Tick** neu berechnet (`rl_ende_und_titel`). So sind sie aktuell, wenn nach der Zerstörung der Ölplattform der Abspann beginnt. Die Reihenfolge der Prüfung ist:

1. **Bankrott**, wenn kein Haus mehr dem Spieler gehört, **oder** wenn die Häuser in der letzten Woche zusammen Verlust gemacht haben und in allen Kassen weniger als 1.000 $ liegen.
2. **Tyrann**, wenn die Bedingungen für „Seelenverkäufer“ erfüllt sind.
3. **Geschäftsmann** in allen übrigen Fällen, fair oder branchenüblich.

Wer nie ein Haus übernommen hat, bekommt keine Slide.

### 4.2 Die drei Haupt-Slides

Geschrieben in der zweiten Person, wie die deutschen Vanilla-Endtexte („Deine Hilfe mit Vault 15 …“). Das macht sie unabhängig vom Geschlecht der Spielfigur.

#### Tyrann (`rl_tyr`, Bild vorläufig: Den 2)

> Die Enklave fiel, und mit ihr die letzte Macht, die sich über die ganze Westküste stellen wollte. In die Lücke traten andere. Du warst unter den Ersten.
>
> Deine Häuser brauchten keine Schilder mehr. Jeder wusste, was hinter den Riegeln geschah, und jeder wusste, wem die Riegel gehörten.
>
> Als die Karawanen der Republik nach Norden zogen, fanden sie an jeder Kreuzung ein Haus, das ihnen Schnaps, Jet und Menschen verkaufte. Die Republik wuchs. Deine Kasse wuchs mit ihr.
>
> Die Rangers führten Listen, und auf den meisten stand dein Name. Verhaftet wurdest du nie. Es fand sich immer jemand, der an deiner Stelle in Golgotha lag.
>
> Man sagt, die Westküste habe nach dem Krieg ihre Freiheit wiedergefunden. In deinen Kellern hat sie niemand gesucht.

#### Geschäftsmann (`rl_ges`, Bild vorläufig: New Reno 2)

> Nach dem Fall der Enklave kehrte das Geld an die Westküste zurück: Gold aus Redding, Brahmin aus der Republik, Handel über die Docks von San Francisco.
>
> Wo Geld fließt, sind Menschen, die es ausgeben wollen. Deine Häuser standen an allen Straßen, auf denen es floss.
>
> Sauber waren sie nicht. Aber wer dort arbeitete, bekam seinen Teil, einen Arzt und eine Tür, die sich von innen verschließen ließ.
>
> Im Ödland war das mehr, als die meisten je gekannt hatten. Es sprach sich herum. Die anderen Häuser mussten nachziehen oder schließen.
>
> Als die Republik schließlich Gesetze für das Gewerbe schrieb, lasen sie sich wie deine Kassenbücher. Niemand sprach es aus, und du hast nie darauf bestanden.
>
> Reich bist du geworden. Ob du ein guter Mensch warst, darüber stritt man in der Den noch lange. Es war das erste Mal, dass dort jemand über so etwas stritt.

#### Bankrott (`rl_bank`, Bild vorläufig: Den 1)

> Das Ödland verzeiht keine Schwäche, und das Geld verzeiht noch weniger.
>
> Deine Häuser gingen eines nach dem anderen verloren: an Schulden, an Razzien, an Männer mit mehr Waffen, als du Rausschmeißer hattest.
>
> Als die Enklave fiel und das Geld an die Westküste zurückkehrte, standen in deinen Zimmern längst fremde Betten. Die Familien aus New Reno teilten unter sich auf, was von deinem Imperium übrig war.
>
> Geblieben ist ein Kassenbuch mit roten Zahlen. Und über einer Tür in der Den eine rostige Laterne, die niemand mehr anzündet.

### 4.3 Die Nachsätze

Nach der Haupt-Slide folgt höchstens **ein** Nachsatz. Es gewinnt der erste Treffer in dieser Reihenfolge:

| # | Nachsatz | Bedingung | Text |
|---|---|---|---|
| 1 | **Ketten** (`rl_n1`) | „Der neue Metzger“ | „Die Pferche der Den waren nie so voll wie in deinen Jahren. Metzger hatte mit Menschen gehandelt. Du hast einen Markt daraus gemacht. Es dauerte eine ganze Generation, bis die Rangers die letzte Kette durchtrennten. Dein Name steht bis heute auf ihrer Liste.“ |
| 2 | **Lex Neun** (`rl_n2`) | „Das Musterhaus“ | „Das Gesetz, das man in der Republik nur die Lex Neun nannte, überlebte dich. Wer in einem Haus arbeitete, hatte von nun an Rechte, die man einklagen konnte. Ruth Calloway kontrollierte die Häuser bis zu ihrem Tod. Sie fand selten etwas. Aufgehört zu suchen hat sie nie.“ |
| 3 | **Das Schweigen** (`rl_n3`) | Liga zerschlagen | „Ruth Calloway sprach nie wieder öffentlich. Mit ihr zerfiel die Liga. Mit der Liga verstummte die einzige Stimme, die für die Menschen in den Häusern gesprochen hatte, ohne an ihnen zu verdienen.“ |
| 4 | **Die Überlebende** (`rl_n4`) | Mara ist Madame der Gosse | „Mara führte die Gosse noch zwanzig Jahre. Wer bei ihr anklopfte, dem wurde geöffnet. Wer bei ihr arbeitete, konnte jederzeit gehen. Die wenigsten gingen.“ |
| 5 | **Die Kralle** (`rl_n5`) | Kitty als Rivalin | „Miss Kitty hat dir nie verziehen. Ihre Kralle in Redding überlebte dein Imperium um viele Jahre. In ihrem Kassenbuch stand dein Name ganz oben. Durchgestrichen.“ |
| 6 | **Die Stimme** (`rl_n6`) | Vesper singt im Strumpfband | „Im Silbernen Strumpfband sang Vesper jeden Abend die Lieder einer Welt, an die sich außer ihr niemand mehr erinnerte. Man sagt, sie singe dort noch immer, für alle, die zuhören, und für die, die nicht mehr zuhören können.“ |

### 4.4 Die Westküste nach der Enklave

| Ort | Tyrann | Geschäftsmann | Bankrott |
|---|---|---|---|
| **NCR** | Die Republik wächst mit einem Menschenmarkt an ihren Handelswegen. Die Rangers jagen, aber fassen nie | Die Gesetze für das Gewerbe folgen dem Muster deiner Häuser (mit Lex Neun ausdrücklich) | Die Republik reguliert ohne dich |
| **New Reno** | Die fünfte Familie herrscht durch Angst | Die fünfte Familie herrscht durch Geld | Die vier Familien teilen dein Erbe |
| **The Den** | Die Pferche sind voller denn je | Zum ersten Mal wird über Anstand gestritten | Die Laterne erlischt |
| **Redding, Vault City, San Francisco** | Handelsposten eines Netzes aus Riegeln und Jet | Stationen an den Geldwegen der neuen Zeit | Übernommen von den Familien und der Konkurrenz |

---

## 5. Technische Umsetzung

### 5.1 Echte GVARs

Fünf GVARs, am Ende von `vault13.gam` angehängt (`install/vault13.gam.add`):

| GVAR | RPU | Unofficial Patch | Zweck |
|---|---|---|---|
| `GVAR_RL_ENDE` | 791 | 696 | Haupt-Slide (1 Tyrann, 2 Geschäftsmann, 3 Bankrott) |
| `GVAR_RL_NACHSATZ` | 792 | 697 | Nachsatz 1–6 |
| `GVAR_RL_TITEL_SEELE` | 793 | 698 | Titel „Seelenverkäufer“ |
| `GVAR_RL_TITEL_ANSTAND` | 794 | 699 | Titel „Anständiges Haus“ |
| `GVAR_RL_TITEL_FAMILIE` | 795 | 700 | Titel „Die Fünfte Familie“ |

**Hinweis:** In Phase 5 waren nur die zwei GVARs für die Endslides vorgesehen. Für Titel im Charakterbogen kommen drei hinzu, weil die Engine sie anders nicht anzeigen kann. Die Alternative wäre, die Titel nur im Hauptbuch zu zeigen, ganz ohne zusätzliche GVARs (siehe offene Entscheidungen).

### 5.2 Endslides

- **Einträge** in `data/endgame.txt` (`install/endgame.txt.add`), einzufügen direkt nach dem New-Reno-Block (`412, …`):

  ```
  791, 1, 454, rl_tyr
  791, 2, 460, rl_ges
  791, 3, 442, rl_bank
  792, 1, 442, rl_n1
  ...
  792, 6, 459, rl_n6
  ```

- **Bilder:**
  - Vorläufig verwenden wir Vanilla-Endbilder aus `intrface.lst`: 442/454 Den, 455/456 NCR, 458 Redding, 459/460 New Reno.
  - Für die endgültige Fassung sind 9 eigene Bilder vorgesehen (640 × 480, Fallout-Palette).
- **Untertitel:**
  - Sie liegen in `text/german/cuts/rl_*.txt`, eine Zeile pro Absatz im Format `n:Text`.
  - Die Engine liest höchstens 50 Zeilen mit je 255 Byte. Unsere Zeilen sind höchstens 200 Zeichen lang.
- **Ohne Sprachaufnahme:**
  - Die Engine zeigt den Untertitel dann 0,08 s pro Zeichen an (fallout2-ce, `endgame.cc`). Das ergibt 42–67 s für die Haupt-Slides und 12–21 s für die Nachsätze.
  - **Sind die Untertitel in den Optionen ausgeschaltet, bleibt die Slide ohne Text.** Das gehört in die Readme.
  - Eine spätere Vertonung legt `narrator/rl_*.acm` daneben. Dann richtet sich die Dauer nach der Aufnahme.

### 5.3 Titel

- **`karmavar.txt`** (`install/karmavar.txt.add`): `793, 148, 1027, 1127` usw. Die Bilder sind vorläufig die von Sklavenhändler (148), Sexperte (130) und Mafioso (138).
- **`editor.msg`:** Die Nummern 1027–1029 (Namen) und 1127–1129 (Beschreibungen) sind im RPU frei. Die Texte stehen in `text_src/german/game/editor.msg.add`.

### 5.4 Code

- `gl_rotlicht.ssl` führt ab jetzt:
  - `rl_stadtruf` (wöchentlich pro Haus),
  - `rl_ende_und_titel` (bei jedem Tick).
- GVARs werden nur geschrieben, wenn sich der Wert ändert.
- Neue Welt-Felder:
  - `RL_W_TYRANN_WOCHEN`
  - `RL_W_AUSBEUTUNG_WOCHEN`
  - `RL_W_MARA`
  - `RL_W_VESPER`
  - Konstanten für die Enden der Questlines (z. B. `RL_KETTEN_NEUER_METZGER`, `RL_VIRGIN_UMARMUNG`, `RL_LIGA_ZERSCHLAGEN`). Die Quest-Skripte setzen sie später.
- **Debug:** Mit `RL_DEBUG=1` bietet Essie „[Debug] Zeig mir den Abspann“ an. Nach dem Dialog startet `endgame_slideshow`, mit allen Vanilla-Slides und unseren.

### 5.5 Korrektur am Build aus Phase 5

Beim Prüfen dieser Phase ist ein Fehler im Build aufgefallen: **sslc wertet nur einen `-m`-Schalter und nur einen `-I`-Pfad aus.**

- *Folge:* Bei kombinierten Schaltern (z. B. Selbsttest und Debug) wirkte nur der letzte.
- *Lösung:* `tools/build_scripts.sh` kompiliert jetzt eine Kopie von `scripts_src` und schreibt alle Einstellungen in deren `config/rl_build.h`.
- *Geprüft am Kompilat:*
  - Der Selbsttest ist nur mit `RL_SELBSTTEST=1` enthalten.
  - Die Debug-Optionen sind nur mit `RL_DEBUG=1` enthalten.
  - Skript- und GVAR-Basis verändern die erzeugten Dateien.

### 5.6 Prüfliste

| Test | Erwartung |
|---|---|
| Nur Geschäftsmann (Debug-Übernahme, fair, 4 Wochen), dann „[Debug] Abspann“ | Slide `rl_ges` erscheint nach dem New-Reno-Block |
| Anteil „ausbeuterisch“ 26 Wochen | Titel „Seelenverkäufer“ im Charakterbogen, Ende wird Tyrann |
| Drei Häuser, Moral ≥ 60, nie Zwang | Titel „Anständiges Haus“ |
| Alle Häuser verloren | Ende Bankrott |
| Haus mit Moral ≥ 70 über 12 Wochen | Stadtruf der Stadt +3, höchstens bis 15 |
| Untertitel in den Optionen aus | Slide ohne Text (erwartet, Hinweis in der Readme) |

---

## 6. Abschluss des Konzepts und Fahrplan

Mit Phase 6 sind alle sechs Phasen beschrieben. Beschlossen ist, jetzt mit der Umsetzung weiterzumachen:

1. Prolog „Essies Schulden“ mit den fünf Lösungswegen (Phase 1/3).
2. Ausbau-Dialog: Module kaufen, Bauzeit, sichtbare Ausbauten (Phase 2).
3. Innen-Map `RLDEN01` und das Tür-Skript auf der Den-Map.
4. Consigliere und Familientreffen im Strumpfband.
5. Die drei Questlines und die übrigen Manager.
6. Eigene Grafiken für die Endslides und die Titel, eventuell eine Vertonung.

---

## 7. Offene Entscheidungen

1. **Titel im Charakterbogen:** Drei weitere GVARs (insgesamt fünf) für sichtbare Titel? Die Alternative wären Titel nur im Hauptbuch, ohne zusätzliche GVARs. Meine Empfehlung: die fünf GVARs, weil die Titel dann dort stehen, wo Fallout-Spieler sie suchen.
2. **Fairness karmaneutral:** Anständig führen wird nicht belohnt, nur nicht bestraft. Einverstanden?
3. **Die Endtexte:** Passen Ton und Inhalt der drei Slides und der sechs Nachsätze?
4. **Bilder:** Vorläufig Vanilla-Endbilder, eigene Grafiken später. Einverstanden?
5. **Nächster Schritt:** Wie vereinbart zuerst den Prolog „Essies Schulden“ und den Ausbau-Dialog programmieren?
