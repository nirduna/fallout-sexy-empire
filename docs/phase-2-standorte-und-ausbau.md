# Phase 2 – Map-Integration, Standorte & Ausbaustufen

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Entwurf – wartet auf Freigabe, bevor Phase 3 beginnt.
**Grundlage:** die Freigabe aus [Phase 1](phase-1-core-loop-und-wirtschaft.md): Hybrid mit C-Kern, Familien-Paten, düsterer Ton, ordentlicher Nebenverdienst, alle sechs Städte, ausdrücklich Bordelle.

---

## 0. Leitlinien für die Welt

1. **Jedes Haus ist ein Bordell.** Bar, Spieltische und Karawanenhof gehören zum Bordell. Getarnt wird nur dort, wo die Tarnung selbst Teil der Geschichte ist (Vault City).
2. **Jedes Haus erzählt seine Stadt.**
   - In der Den riecht es nach Ketten.
   - In New Reno ist es der verblasste Glanz der Familien.
   - In Redding ist es Goldstaub und Jet.
   - In Vault City ist es Heuchelei.
   - In der NCR ist es Bürokratie.
   - In San Francisco ist es Nebel und Flucht.
3. **Minimal-invasiv auf den Vanilla-Maps.** Auf der Original-Karte ändern wir nur die Fassade, eine Tür mit Exit-Grid und ein Schild. Das Innere ist jeweils eine **eigene Map**. Das schützt die Kompatibilität mit dem Restoration Project und bestehenden Spielständen und gibt uns Platz für sichtbare Ausbauten.
4. **Drei Ebenen pro Haus.** Jede neue Map nutzt die drei Fallout-Ebenen:
   - Ebene 0 ist das Erdgeschoss.
   - Ebene 1 öffnet sich mit Hausklasse 2.
   - Ebene 2 ist Keller, Hinterhof oder Tunnel und trägt die stadtspezifischen Module.
5. **Vorher/Nachher sichtbar.** Vor der Übernahme ist das Gebäude verschlossen oder vernagelt. Nach der Übernahme brennt Licht, ein Schild hängt, und jeder Ausbau verändert den Raum.

---

## 1. Die sechs Häuser im Überblick

| Stadt | Haus | Lage in der Vanilla-Welt | Integration | Max. Hausklasse | Rolle im Imperium |
|---|---|---|---|---|---|
| The Den | **Die Rostige Laterne** | East Side, zwischen Mom's Diner und der Sklavengilde | baufälliges Haus → eigene Map | 2 | Prolog, erstes Geld |
| New Reno | **Das Silberne Strumpfband** | Virgin Street, schräg gegenüber dem Cat's Paw, in Sichtweite des Desperado | leerstehendes Vorkriegshotel → eigene Map | **3** | Flaggschiff & Familiensitz |
| Redding | **Zur Letzten Schicht** | Mining Camp, hinter dem Last Gasp Saloon | umgebauter Erzschuppen → eigene Map | 2 | Goldader, Jet-Brennpunkt |
| Vault City | **Haus Stille** | Courtyard, Viertel der Außenweltler, als Pension getarnt | Keller-Erweiterung + Tunnel ins alte Vault-8-System | 2 | Luxus bei höchstem Risiko |
| NCR | **Haus Neun** | Bazaar vor den Stadtmauern, neben dem Rawhide Saloon | lizenziertes Haus → eigene Map | 2 | legal und stabil |
| San Francisco | **Das Fährhaus** | Shi-town Docks, halb abgesoffenes Fährterminal | eigene Map mit Anlegesteg | 2 | Spätspiel-Hafen |

---

## 2. Die Häuser im Einzelnen

Die Ausbaupfade am Ende jedes Abschnitts stammen aus [`tools/ausbau_sim.py`](../tools/ausbau_sim.py).

**Annahmen der Rechnung:**
- fairer Personal-Anteil
- eingeschwungener Betrieb (Wochen 13–24 nach dem Kauf)
- automatisch die beste erlaubte Preisstufe
- **ohne** Paten-Boni und Ereignisse

**Kategorien der Module:**
- **R = Rendite:** Die Amortisation wird ausgewiesen.
- **A = Absicherung:** senkt Risiko und Ereignisse, amortisiert sich nicht direkt.
- **M = Moral:** wirkt vor allem bei branchenüblichem Anteil (siehe Abschnitt 5).

### 2.1 The Den – Die Rostige Laterne

**Ort.** Eine Gasse auf der East Side. Links liegt Mom's Diner, rechts hört man die Pferche der Sklavengilde, und hinten sieht man den Friedhof. Früher war das Haus eine Absteige für Karawanenführer. Essie hat es mit Laken und Bretterwänden in Verschläge geteilt. Ruß an der Decke, Kerzenstummel, eine einzige Laterne über der Tür, verrostet und rot vom Dreck der Jahre.

**Kundschaft.** Sklavenhändler nach dem Zahltag, Karawanenwachen, Tylers Leute. Hier wird bar bezahlt und nicht geredet.

**Vanilla-Anknüpfung**
- **Metzger:** Schulden, Partnerschaft oder Feindschaft (Prolog aus Phase 1).
- **Tylers Bande:** Schutz gegen Anteil.
- **Lara:** Gegenkraft und Verbündete, wenn die Gilde fällt.
- **Mom:** Essie isst bei ihr. Mom weiß, wer in der Den was schuldet, und ist damit eine Informantin.

**Übernahme.** Prolog aus Phase 1, fünf Lösungswege. Einfluss braucht es dafür nicht.

**Map `RLDEN01`**

| Ebene | Inhalt |
|---|---|
| 0 | Schankraum mit Empfang, drei Verschläge hinter Bretterwänden |
| 1 | Obergeschoss mit zwei Zimmern mit echten Türen (ab Hausklasse 2) |
| 2 | **Der Keller:** Hier fällt die moralische Entscheidung der Den (siehe unten) |

**Stadtspezifische Module**

| Modul | Kosten | Wirkung |
|---|---|---|
| **Riegel innen** (M) | 400 $ | Das Personal kann sich einschließen. Sicherheit +10, Moral +1/Woche. |
| **Riegel außen** (Tyrannen-Route) | 200 $ | Der Keller wird zum Pferch. Metzger liefert Zwangspersonal, ein Personal-Anteil entfällt. Karma −5/Woche, dazu Flucht-Ereignisse, Slaver-Ruf und NCR-Rangers als späterer Gegner. Schließt „Riegel innen“ aus. |
| **Die Zuflucht** (Hook für Phase 3) | 600 $ | Eine versteckte Kammer für entlaufene Sklaven. Karma +, aber Metzger wird feindlich, wenn er es herausfindet. Schließt „Riegel außen“ aus. |

**Ausbaupfad (fair)**

| Schritt | Kosten | Gewinn/Woche | Preisstufe | Kunden/Woche | Amortisation |
|---|---|---|---|---|---|
| Start (Hausklasse 1) | – | 54 $ | Standard | 36 | – |
| Bar I (R) | 800 $ | 146 $ | Standard | 36 | 8 Wo. |
| Sicherheit I (A) | 400 $ | 121 $ | Standard | 36 | – |
| Riegel innen (M) | 400 $ | 96 $ | Standard | 36 | – |
| Hausklasse 2 (R) | 2.000 $ | 198 $ | Standard | 54 | 19 Wo. |
| Sicherheit II (A) | 1.000 $ | 207 $ | Standard | 58 | – |
| **Endausbau** | **4.600 $** | **207 $** | | | |

*Hinweis:* Die Den ist arm. Gehobene Preise lohnen sich hier nicht, und es gibt keinen VIP-Trakt. Die Laterne ist die Schule, nicht die Goldgrube. Die Sicherheitsmodule rechnen sich nicht in Geld, aber in der Den (Bedrohung 80) verhindern sie die Überfälle, die ein unbewachtes Haus sonst Woche für Woche treffen.

---

### 2.2 New Reno – Das Silberne Strumpfband

**Ort.** Virgin Street, schräg gegenüber dem Cat's Paw, wenige Schritte vom Desperado, dem Sitz der Mordinos. Ein Hotel aus der Zeit vor dem Krieg. Von der Neonschrift flackert nur noch die Hälfte. Seit einer Familienfehde vor Jahren steht es leer. Der letzte Besitzer liegt in Golgotha, und niemand wollte das Haus seitdem anfassen.

**Kundschaft.** Spieler aus den Casinos, Männer der Familien, Boxfans aus dem Jungle Gym, Leute vom Set der Golden Globes. Hier wird mit Chips und Gefälligkeiten bezahlt, und mit Schweigen.

**Vanilla-Anknüpfung**
- **Die vier Familien:** Mordino (Desperado), Bishop (Shark Club), Salvatore (Salvatore's Bar), Wright (Anwesen auf der East Side).
- **Das Cat's Paw:** unabhängig, Hauptrivale (−15 % Kunden bis zur Auflösung in Phase 3).
- **Golgotha** als Drohkulisse.

**Übernahme.** Einfluss in New Reno ≥ 20 und der Segen eines Paten, oder unabhängig mit allen Folgen (Phase 1). Die Übernahme-Quest folgt in Phase 3.

**Map `RLREN01`**

| Ebene | Inhalt |
|---|---|
| 0 | Hotellobby mit Bar und Spieltischen, drei Zimmer im Erdgeschoss |
| 1 | Hotelflur mit zwei Zimmern (Hausklasse 2) |
| 2 | **Familiensitz** (Hausklasse 3): zwei weitere Zimmer, Büro des Consigliere, Konferenzraum für die Familientreffen, Tresorraum. Die VIP-Suiten haben eine eigene Hintertreppe. |

**Stadtspezifische Module**

| Modul | Kosten | Wirkung |
|---|---|---|
| **Spieltische** (R) | 2.000 $ | +4 $ Nebenumsatz je Kunde, Ausstattung +5. Die Familie des Viertels will ihren Anteil. |
| **Jet-Theke** (nur mit Mordino-Pate) | 800 $ | +6 $ Nebenumsatz je Kunde. Doppelt so viele Sucht-Ereignisse beim Personal, die Wrights werden feindlich. Das Haus verdient an der Droge, die Richard Wright getötet hat. |

**Ausbaupfad (fair)**

| Schritt | Kosten | Gewinn/Woche | Preisstufe | Kunden/Woche | Amortisation |
|---|---|---|---|---|---|
| Start (Hausklasse 1) | – | −40 $ | Standard | 36 | – |
| Einrichtung I (R) | 500 $ | 57 $ | Gehoben | 36 | 5 Wo. |
| Sicherheit I (A) | 400 $ | 32 $ | Gehoben | 36 | – |
| Hausklasse 2 (R) | 2.000 $ | 178 $ | Gehoben | 60 | 13 Wo. |
| Bar I (R) | 800 $ | 339 $ | Gehoben | 60 | 4 Wo. |
| Kontor (R) | 600 $ | 387 $ | Gehoben | 60 | 12 Wo. |
| Spieltische (R) | 2.000 $ | 550 $ | Gehoben | 60 | 12 Wo. |
| Hausklasse 3 – Familiensitz (R) | 4.000 $ | 724 $ | Gehoben | 77 | 22 Wo. |
| Einrichtung II (R) | 1.200 $ | 767 $ | Gehoben | 81 | 27 Wo. |
| Bar II (R) | 2.000 $ | 1.040 $ | Gehoben | 81 | 7 Wo. |
| VIP-Trakt (R) | 3.000 $ | 1.244 $ | Gehoben | 84 | 14 Wo. |
| **Endausbau** | **16.500 $** | **1.244 $** | | | |

*Hinweis:* New Reno beginnt ohne Paten-Bonus im Minus, denn Tribut und Löhne fressen das kleine Haus. Der Familiensitz amortisiert sich langsam, ist aber die Voraussetzung für die Familientreffen des C-Kerns.

---

### 2.3 Redding – Zur Letzten Schicht

**Ort.** Mining Camp, am Weg zwischen der Kokoweef- und der Morningstar-Mine, hinter dem Last Gasp Saloon. Ein ehemaliger Erzschuppen mit Wänden aus Wellblech und Staub in jeder Ritze. Gearbeitet wird im Takt der Schichtsirene.

**Kundschaft.** Minenarbeiter nach der Schicht. Sie bezahlen mit Goldstaub und Nuggets, und viele haben den Rest ihres Lohns schon in Jet umgesetzt.

**Vanilla-Anknüpfung**
- **Bürgermeister Ascorti:** Die „Lizenz“ ist ein Schmiergeld von 75 $/Woche.
- **Sheriff Marion:** hält Außenseiter an der kurzen Leine.
- **Marge LeBarge** (Kokoweef) **und Dan McGrew** (Morningstar): Arbeitgeber der Kundschaft.
- **Great Wanamingo Mine:** Wird sie gesäubert, gibt es einen Boom.
- **Jet-Index:** siehe Phase 1.
- **Malamute Saloon** in Downtown: bietet schon käufliche Liebe an und ist die Konkurrenz (−10 % Kunden bis Phase 3).

**Übernahme.** Einfluss in Redding ≥ 20 und Ascortis Lizenz. Alternativ bringt dir der Sheriff das Haus mit Gewalt ein (Phase 3).

**Map `RLRED01`**

| Ebene | Inhalt |
|---|---|
| 0 | Schuppen mit Tresen, drei Verschläge |
| 1 | Schlafbaracke im Hinterhof mit zwei Zimmern (Hausklasse 2) |
| 2 | Stillgelegter Stollen hinter dem Schuppen: Platz für die Entzugsstube oder ein Versteck |

**Stadtspezifische Module**

| Modul | Kosten | Wirkung |
|---|---|---|
| **Ehrliche Goldwaage** (R) | 400 $ | Die Kumpel vertrauen dem Haus: Kunden +10 %. |
| **Gezinkte Waage** (dunkle Alternative) | 150 $ | Umsatz +15 %, Karma −2/Woche, Hitze +10. Wird die Waage entdeckt, folgt eine Revolte der Minenarbeiter. Schließt die ehrliche Waage aus. |
| **Entzugsstube** (A) | 1.200 $ | Braucht einen Doc. Halbiert die Jet-Ereignisse beim Personal, Moral +1/Woche, Kunden +5 %. |

**Ausbaupfad (fair)**

| Schritt | Kosten | Gewinn/Woche | Preisstufe | Kunden/Woche | Amortisation |
|---|---|---|---|---|---|
| Start (Hausklasse 1) | – | 21 $ | Standard | 36 | – |
| Sicherheit I (A) | 400 $ | −4 $ | Standard | 36 | – |
| Bar I (R) | 800 $ | 106 $ | Standard | 36 | 7 Wo. |
| Hausklasse 2 (R) | 2.000 $ | 252 $ | Standard | 56 | 13 Wo. |
| Ehrliche Goldwaage (R) | 400 $ | 283 $ | Standard | 60 | 12 Wo. |
| Einrichtung I (R) | 500 $ | 305 $ | Gehoben | 45 | 22 Wo. |
| Entzugsstube (A) | 1.200 $ | 330 $ | Gehoben | 49 | – |
| **Endausbau** | **5.300 $** | **330 $** | | | |

---

### 2.4 Vault City – Haus Stille

**Ort.** Im Courtyard, dem Viertel der Außenweltler, unweit von Cassidy's Spittoon. Nach außen ist es eine Pension mit sauberen Laken und einer strengen Wirtin. Das eigentliche Haus liegt im Keller. Die Kunden kommen nachts aus Downtown, Bürger, die tagsüber im Rat über Moral reden. Niemand spricht hier, deshalb der Name.

**Kundschaft.** Bürger mit Tagespass in umgekehrter Richtung, Ärzte, Beamte aus dem Amenities Office. Sie zahlen viel, denn sie bezahlen für das Schweigen mit.

**Vanilla-Anknüpfung**
- **First Citizen Lynette:** Moralpolitik, Razzien.
- **Councilor McClure:** Pragmatiker und möglicher stiller Beschützer.
- **Amenities Office:** Bürokratie.
- **Corrections Center:** Hier landet, wer bei einer Razzia gefasst wird.
- **Servant Allocation Center:** In Vault City werden aus Verhafteten „Dienstboten“ gemacht.
- **Gecko:** Die Lösung des Reaktorkonflikts bestimmt den Wohlstand.
- **Bürgerschaftstest:** Wer Bürger ist, zahlt weniger.

**Übernahme.** Einfluss in Vault City ≥ 20, über Bestechung, Bürgerschaft oder einen Informanten in der Garde (Phase 3).

**Besondere Regeln**
- **Schweigegeld:** 200 $/Woche **je Hausklasse**. Je größer das Haus, desto mehr Mitwisser.
- **Razzia-Folge:** Personal, das gefasst wird, geht über das Corrections Center an das Servant Allocation Center und wird zu Dienstboten. Du kannst sie freikaufen, befreien oder aufgeben (Hook für Phase 3/4). Das ist der schwerste Verlust im ganzen Spiel.

**Map `RLVCT01`**

| Ebene | Inhalt |
|---|---|
| 0 | Die Pension: Empfang, zwei Gästezimmer, nichts Verdächtiges. Diese Ebene wird bei Razzien durchsucht. |
| 1 | Kellergewölbe mit zwei Zimmern, zwei weitere ab Hausklasse 2 |
| 2 | **Wartungstunnel** ins alte Vault-8-System. Bürger gelangen aus Downtown hinein, ohne das Tor zu passieren. |

**Stadtspezifische Module**

| Modul | Kosten | Wirkung |
|---|---|---|
| **Wartungstunnel** (R) | 2.500 $ | Sicherheit +25, Kunden +20 %. Weniger Augen am Tor. |
| **Die Akte** (dunkle Option) | 1.000 $ | Du führst Buch über jeden Bürger, der kommt. Einfluss in Vault City +2/Woche und Erpressungsmaterial (Phase 3). Hitze +10. Wird die Akte gefunden, folgt sofort eine Razzia. |

**Ausbaupfad (fair)**

| Schritt | Kosten | Gewinn/Woche | Preisstufe | Kunden/Woche | Amortisation |
|---|---|---|---|---|---|
| Start (Hausklasse 1) | – | 375 $ | Gehoben | 17 | – |
| Sicherheit I (A) | 400 $ | 396 $ | Gehoben | 18 | – |
| Wartungstunnel (R) | 2.500 $ | 665 $ | Gehoben | 24 | 9 Wo. |
| Hausklasse 2 (R) | 2.000 $ | 532 $ | Gehoben | 27 | – |
| Kontor (R) | 600 $ | 588 $ | Gehoben | 27 | 10 Wo. |
| Einrichtung II (R) | 1.200 $ | 655 $ | Gehoben | 29 | 17 Wo. |
| Einrichtung III (R) | 2.500 $ | 740 $ | Gehoben | 31 | 29 Wo. |
| VIP-Trakt (R) | 3.000 $ | 1.324 $ | Exklusiv | 23 | 5 Wo. |
| Krankenstube (A) | 1.000 $ | 1.284 $ | Exklusiv | 23 | – |
| **Endausbau** | **13.200 $** | **1.284 $** | | | |

*Hinweis:* Hausklasse 2 senkt hier zunächst den Gewinn, weil das Schweigegeld von 200 auf 400 $ steigt. Sie ist aber die Voraussetzung für den VIP-Trakt. Mit ihm wird Vault City zum einzigen Haus, in dem sich der Preis „Exklusiv“ für das ganze Haus lohnt. Höchster Gewinn, höchstes Risiko: Eine einzige Razzia kostet mehr als ein Monat Einnahmen.

---

### 2.5 NCR – Haus Neun

**Ort.** Im Bazaar vor den Stadtmauern, zwischen dem Rawhide Saloon und den Pferchen, in denen die Sklavenhändler ihre Ware zeigen. Offiziell heißt es „Lizenziertes Etablissement Nr. 9 der Republik“. Die Nummer steht in Schablonenschrift über der Tür. Drinnen hängt eine Liste mit Namen und Untersuchungsdaten. Die Republik will Ordnung, keine Menschen.

**Kundschaft.** Karawanenleute, Brahmintreiber, Polizisten außer Dienst, Westins Vorarbeiter. Die Brahmin-Barone kommen in den VIP-Trakt.

**Vanilla-Anknüpfung**
- **Präsidentin Tandi und der Rat** (Council Hall): vergeben die Lizenz.
- **Westin:** VIP-Kundschaft und Machtfaktor.
- **NCR-Polizei** in Downtown.
- **Die Rangers:** verstecktes Hauptquartier in der stillgelegten Autowerkstatt, Feinde jeder Sklaverei.
- **Vortis:** Sklavenhändler im Bazaar.
- **Hubologen-Außenposten** in Downtown.

**Übernahme.** Einfluss in der NCR ≥ 20, dazu die Lizenz (500 $, mit Bishop-Pate −50 %). Eine **Krankenstube ist Lizenzauflage**, denn wöchentliche Untersuchungen sind Pflicht.

**Map `RLNCR01`**

| Ebene | Inhalt |
|---|---|
| 0 | Empfang mit Registrierpult, Bar, drei Zimmer |
| 1 | Obergeschoss mit zwei Zimmern (Hausklasse 2) |
| 2 | Karawanenhof im Hinterhof: Brahminpferch und ein Gästezimmer |

**Stadtspezifische Module**

| Modul | Kosten | Wirkung |
|---|---|---|
| **Karawanenhof** (R) | 1.200 $ | +1 Zimmer, Kunden +15 %. Die Karawanen machen hier Halt. |
| **Registratur** (A) | 500 $ | Saubere Papiere für jede Arbeiterin und jeden Arbeiter. Halbiert die Wirkung der Sittlichkeitskampagnen (Phase 3). |
| **Vortis' Angebot** (Tyrannen-Route) | – | Billiges Personal aus dem Sklavenpferch nebenan. Karma −5/Woche. Entdecken es die Rangers, folgen Razzia, Lizenzentzug und die Rangers als dauerhafte Feinde. |

**Ausbaupfad (fair)**

| Schritt | Kosten | Gewinn/Woche | Preisstufe | Kunden/Woche | Amortisation |
|---|---|---|---|---|---|
| Start (Hausklasse 1) | – | 2 $ | Standard | 36 | – |
| Krankenstube (A, Lizenzauflage) | 1.000 $ | −83 $ | Standard | 36 | – |
| Hausklasse 2 (R) | 2.000 $ | 152 $ | Gehoben | 57 | 8 Wo. |
| Bar I (R) | 800 $ | 304 $ | Gehoben | 57 | 5 Wo. |
| Karawanenhof (R) | 1.200 $ | 372 $ | Gehoben | 65 | 17 Wo. |
| Kontor (R) | 600 $ | 408 $ | Gehoben | 65 | 16 Wo. |
| Bar II (R) | 2.000 $ | 640 $ | Gehoben | 65 | 8 Wo. |
| VIP-Trakt (R) | 3.000 $ | 768 $ | Gehoben | 68 | 23 Wo. |
| **Endausbau** | **10.600 $** | **768 $** | | | |

---

### 2.6 San Francisco – Das Fährhaus

**Ort.** Shi-town Docks. Ein Fährterminal, halb im Wasser versunken. Der Nebel zieht durch die zerbrochenen Scheiben der Wartehalle. Von hier fährt keine Fähre mehr, aber die Leute kommen trotzdem, um zu vergessen, wohin sie nicht mehr können.

**Kundschaft.** Leute vom Tanker, Fischer, Händler der Shi, Deserteure, Hubologen, die zu zweifeln beginnen.

**Vanilla-Anknüpfung**
- **Die Shi:** der Emperor im Steel Palace. Sie dulden das Haus gegen Tribut.
- **Die Tanker-Vagabunden:** Kundschaft und Schmuggler.
- **Die Hubologen:** werben um dieselben Verlorenen.
- **Dr. Fungs Klinik:** Quelle für einen Doc.
- **Die Kampfschulen von Dragon und Lo Pan:** Quelle für Rausschmeißer (Phase 4).
- **Brotherhood of Steel:** meidet das Haus.
- **Nach dem Spiel:** San Francisco wird ein Handelszentrum. Das ist ein Hook für den Epilog.

**Übernahme.** Einfluss in San Francisco ≥ 20 und die Duldung der Shi (10 % Tribut).

**Map `RLSFR01`**

| Ebene | Inhalt |
|---|---|
| 0 | Wartehalle mit Bar, drei Kabinen |
| 1 | Ehemalige Büros auf dem Oberdeck, zwei Zimmer (Hausklasse 2) |
| 2 | Anlegesteg und der versunkene Rumpf einer alten Fähre. Dort liegt der VIP-Trakt, erreichbar per Boot, ungesehen. |

**Stadtspezifische Module**

| Modul | Kosten | Wirkung |
|---|---|---|
| **Anlegesteg** (R) | 1.500 $ | Kunden +15 %. Boote legen direkt an. |
| **Siegel der Shi** (R) | 1.000 $ | Tribut −5 %, Sicherheit +10. Erfordert einen Gefallen für die Shi (Phase 3). |
| **Schmuggelkammer** (dunkle Option) | 800 $ | Die Tanker-Schmuggler lagern hier. +3 $ Nebenumsatz je Kunde, Hitze +10, die Shi werden misstrauisch. |

**Ausbaupfad (fair)**

| Schritt | Kosten | Gewinn/Woche | Preisstufe | Kunden/Woche | Amortisation |
|---|---|---|---|---|---|
| Start (Hausklasse 1) | – | 137 $ | Standard | 36 | – |
| Bar I (R) | 800 $ | 230 $ | Standard | 36 | 8 Wo. |
| Hausklasse 2 (R) | 2.000 $ | 568 $ | Gehoben | 48 | 5 Wo. |
| Anlegesteg (R) | 1.500 $ | 663 $ | Gehoben | 56 | 15 Wo. |
| Einrichtung I (R) | 500 $ | 685 $ | Gehoben | 58 | 22 Wo. |
| Kontor (R) | 600 $ | 744 $ | Gehoben | 58 | 10 Wo. |
| Siegel der Shi (R) | 1.000 $ | 856 $ | Gehoben | 58 | 8 Wo. |
| VIP-Trakt (R) | 3.000 $ | 1.059 $ | Gehoben | 60 | 14 Wo. |
| **Endausbau** | **9.400 $** | **1.059 $** | | | |

---

## 3. Hausklassen

| Klasse | Name | Zimmer | Kapazität (Kunden/Woche) | Kosten | Bauzeit | Was man sieht |
|---|---|---|---|---|---|---|
| 1 | **Absteige** | 3 (Vault City: 2) | 36 (24) | Übernahme | – | Nur Ebene 0 ist benutzbar. Die Treppe ist eingestürzt oder vernagelt, Matratzen liegen auf dem Boden, Laken ersetzen Türen. |
| 2 | **Etablissement** | +2 | +24 | 2.000 $ | 2 Wochen | Die Treppe ist repariert und Ebene 1 offen. Echte Türen, verhängte Fenster, Licht und das Schild an der Fassade. |
| 3 | **Familiensitz** (nur New Reno) | +2 | +24 | 4.000 $ | 3 Wochen | Ebene 2 ist offen: Büro des Consigliere, Konferenzraum, Tresorraum, VIP-Hintertreppe. |

**Neue Regel: Kapazität.** Ein Zimmer bedient höchstens 12 Kunden pro Woche:

```
Kunden = min(Nachfrage, Zimmer × 12)
```

Ein volles Haus gewinnt deshalb nicht mehr durch schönere Möbel, sondern durch **mehr Zimmer oder höhere Preise**.

**Bauzeit.** Ein Modul braucht 1 Woche, eine Hausklasse 2–3 Wochen. In dieser Zeit hat das Haus −50 % Kunden.

---

## 4. Allgemeiner Modulkatalog

Jede Modulstufe kostet laufend 25 $/Woche Unterhalt (wie in Phase 1).

| Modul | Stufe | Kosten | Kat. | Wirkung | Was man sieht |
|---|---|---|---|---|---|
| **Einrichtung** | I | 500 $ | R | Ausstattung +10. Erreicht meist die 40er-Schwelle für „Gehoben“. | Bettgestelle statt Matratzen, Vorhänge statt Bretter |
| | II | 1.200 $ | R | Ausstattung +15. Füllt große Häuser. | Vorkriegsbetten, Teppiche, Spiegel |
| | III | 2.500 $ | R | Ausstattung +20. Nötig für „Exklusiv“ (70). | Samt, eine Waschschüssel in jedem Zimmer, Kronleuchter-Reste |
| **Bar** | I | 800 $ | R | +5 $ je Kunde. Braucht einen Barkeeper (30 $/Woche). | Tresen aus Schrott, Schnapsregal, der Barkeeper erscheint |
| | II | 2.000 $ | R | weitere +5 $ je Kunde | mehr Sitzplätze, ein Radio mit Vorkriegsmusik |
| **Sicherheit** | I | 400 $ | A | Sicherheit +10 | verstärkte Tür, Guckloch |
| | II | 1.000 $ | A | Sicherheit +20. Waffenkontrolle: Vorfälle mit Waffen −50 %. | Schrank am Eingang, Kontrolleur |
| | III | 2.000 $ | A | Sicherheit +25. Alarmglocke: Die Rausschmeißer greifen sofort ein. | Wachstube, Glockenzug |
| **Personalquartiere** | I | 700 $ | M | Moral +1/Woche | Schlafsaal mit Spinden |
| | II | 1.500 $ | M | weitere Moral +1/Woche | eigene Kammern mit Schloss |
| **Krankenstube** | – | 1.000 $ | A | Braucht einen Doc (60 $/Woche). Moral +1/Woche, verhindert Seuchen-Ereignisse. In der NCR Pflicht. | Pritsche, Medizinschrank, der Doc erscheint |
| **Kontor** | – | 600 $ | R | Buchhalter (80 $/Woche): Schwund 10 → 4 %. Das Hauptbuch zeigt Details zum Haus. | Schreibtisch, Stahlschrank |
| **VIP-Trakt** | – | 3.000 $ | R | Ab Hausklasse 2, nur in New Reno, Vault City, NCR und San Francisco. Eigene Kundschaft zum dreifachen Preis (ab Moral 65). Einfluss +1/Woche in der Stadt, denn wer hier liegt, redet (Material für Phase 3). | separater Eingang, schallgedämpfte Räume |

---

## 5. Wirtschaftliche Einordnung

### 5.1 Imperium im Endausbau (eingeschwungen, ohne Ereignisse)

| Personal-Anteil | Den | New Reno | Redding | Vault City | NCR | San Francisco | **Gesamt/Woche** |
|---|---|---|---|---|---|---|---|
| fair | 207 $ | 1.244 $ | 330 $ | 1.284 $ | 768 $ | 1.059 $ | **4.892 $** |
| branchenüblich | 178 $ | 968 $ | 276 $ | 686 $ | 615 $ | 765 $ | **3.488 $** |
| ausbeuterisch | −40 $ | 484 $ | −29 $ | −94 $ | 145 $ | 263 $ | **729 $** |

Das Ziel „ordentlicher Nebenverdienst“ (3.000–5.000 $/Woche) ist erreicht. Ausbeutung ist im Endausbau mit Abstand die schlechteste Wahl. Die Tyrannen-Route kann sich nur über Zwangspersonal über Wasser halten (Riegel außen, Vortis), mit den Karma- und Ruf-Folgen aus Phase 1.

### 5.2 Zwei anständige Wege

Neu in Phase 2 ist eine **Moral-Obergrenze je Anteilsstufe**: ausbeuterisch 50, branchenüblich 70, fair 100. Quartiere heben die Moral nur bis zu dieser Grenze. Talente wirbt das Personal erst ab Moral 75 an, und das schafft nur, wer fair teilt.

Daraus ergeben sich zwei gleichwertige, anständige Strategien:

| Haus | Fairer Anteil | Branchenüblich + Quartiere I+II (2.200 $) |
|---|---|---|
| The Den | **207 $** | 161 $ |
| Redding | **330 $** | 266 $ |
| NCR | **768 $** | 749 $ |
| San Francisco | 1.059 $ | **1.071 $** |
| New Reno | 1.244 $ | **1.330 $** |
| Vault City | 1.284 $ | **1.318 $** |

In kleinen, armen Häusern wirkt Geld am stärksten. In großen, vollen Häusern lohnen gute Lebensbedingungen etwas mehr. Beide Wege liegen innerhalb von ±7 %, und beide schlagen die Ausbeutung deutlich. So wird Moral zu einer echten Entscheidung und nicht zu einer Pflichtübung.

### 5.3 Anpassungen an Phase 1

- **Den-Basispreis** 15 → 20 $. Sonst trägt sich das Starthaus nicht. Starthaus bei branchenüblichem Anteil: ca. 80 $/Woche, wie in Phase 1 als Ziel gesetzt.
- **Vault City:** Die Pflicht-Bestechung wird zum Schweigegeld von 200 $ je Hausklasse.
- **Neue Regeln:** Kapazitätsgrenze (Zimmer × 12) und Moral-Obergrenze je Anteil.
- Die Beispielrechnung und die Fairness-Tabelle aus Phase 1 bleiben unverändert gültig.

---

## 6. Technische Umsetzung der Karten (Vorschau auf Phase 5)

- **Neue Maps:** `RLDEN01`, `RLREN01`, `RLRED01`, `RLVCT01`, `RLNCR01`, `RLSFR01`, jeweils mit drei Ebenen. Kurze Dateinamen, passend zur Vanilla-Konvention. Einträge in `maps.txt`, Namen in `map.msg`.
- **Eingriffe in Vanilla-Maps:**
  - Betroffen sind die Den-Maps (`denbus*`/`denres1`), New Reno (`newr1`–`newr4`), Vault City (`vctycocl`) sowie Redding, NCR und San Francisco. Welche Datei genau, wird im Mapper verifiziert.
  - Pro Stadt ändern wir **eine Tür mit Exit-Grid**, ein Schild und ein Platzhalter-Objekt („vernagelt“). Die Tür bleibt per Script verschlossen, bis das Haus übernommen ist.
- **Stadtkarte:** Neue Einträge in `city.txt` sind zunächst verborgen. Nach der Übernahme werden sie per `mark_area_known` freigeschaltet.
- **Sichtbare Ausbauten:**
  - Platzhalter (Bretter, Schutt, eingestürzte Treppe) und Ausbau-Objekte liegen vorplatziert auf der Map.
  - Das Map-Script schaltet sie in `map_enter_p_proc` anhand einer Bitmaske pro Haus (eine GVAR) um: Platzhalter werden entfernt, Ausbauten erzeugt bzw. sichtbar gemacht.
  - Ein Merker in einer Map-Variable verhindert, dass Objekte doppelt erzeugt werden.
- **Grafiken:**
  - Überwiegend Vanilla-Assets: Casino-Tiles aus New Reno, Vault-Wände für Vault City, Ruinen der Den, Chinatown-Tiles aus San Francisco.
  - Neu nötig sind nur sechs Schilder (FRM) und einige umgefärbte Einrichtungsobjekte.
- **Kompatibilität:** Weil der Eingriff in Vanilla-Maps so klein ist, bleibt ein Patch für das Restoration Project überschaubar. Bestehende Spielstände laden die geänderten Außen-Maps beim nächsten Betreten. Das prüfen wir in Phase 5 im Einzelnen.

---

## 7. Offene Entscheidungen (für die Freigabe von Phase 3)

1. **Häuser & Lagen:** Passen Namen und Orte der sechs Bordelle, oder willst du einzelne verlegen (z. B. das Strumpfband auf die Second Street zwischen die Familien)?
2. **Vault City:** Ist die Razzia-Folge „Personal wird zu Dienstboten gemacht“ in dieser Härte gewünscht?
3. **Dunkle Module:** Riegel außen, Jet-Theke, gezinkte Waage, Die Akte, Vortis' Angebot, Schmuggelkammer. Alle behalten, oder einzelne streichen?
4. **Hausklasse 3 nur in New Reno** als Familiensitz: einverstanden?
5. **Zwei anständige Wege** (fairer Anteil gegen Quartiere): so beibehalten?
