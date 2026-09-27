# Phase 4 – Personal, Unique Talent & Ereignisse

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Freigegeben (siehe Entscheidungen unten). Weiter in [Phase 5](phase-5-technik.md).

> **Freigabe-Entscheidungen** (alle Empfehlungen übernommen)
> 1. Die fünf Unique-Figuren bleiben: Vesper, Abigail Kessler, Talus, Julian Rook, Mara.
> 2. Werben gegen Zwingen ist die zweite Moralachse.
> 3. „An der Leine halten“ und alle Tyrannen-Quellen bleiben im Spiel.
> 4. „Tod im Haus“ bleibt als Ereignis.
> 5. Unique-Figuren können endgültig sterben, aber erst nach einer Vorwarnung: Sie sind eine Woche lang schwer verletzt, und in dieser Zeit kann der Spieler sie retten.
**Grundlage:** [Phase 1](phase-1-core-loop-und-wirtschaft.md) bis [Phase 3](phase-3-quests-rivalen-uebernahmen.md) sind freigegeben. Der Ton ist düster und unbarmherzig, alle dunklen Optionen bleiben im Spiel.

---

## 0. Leitlinien

1. **Menschen, nicht Zahlen.** Hinter der Personalqualität aus Phase 1 stehen Menschen. Die meisten bleiben namenlos, aber jede Entscheidung trifft jemanden. Die Unique-Figuren geben dem Personal ein Gesicht.
2. **Alle Beschäftigten sind erwachsen.** Intime Szenen bleiben beim Vanilla-Fade-to-Black. Die Härte liegt in den Folgen, nicht in der Darstellung.
3. **Wer anwirbt, entscheidet über Freiwilligkeit.** Ob jemand freiwillig im Haus arbeitet, entscheidet sich beim Anwerben. Das ist die zweite große Moralachse neben dem Personal-Anteil.
4. **Ereignisse sind Geschichten, keine Strafzettel.** Jedes Ereignis bietet Entscheidungen. Kleine löst die Madame, große brauchen dich vor Ort (das Prinzip aus Ansatz A).

---

## 1. Rollen im Haus

| Rolle | Aufgabe | Wichtige Werte | Wirkung | Lohn/Woche |
|---|---|---|---|---|
| **Madame / Manager** | führt das Haus, löst kleine Ereignisse | CH, Speech | Führung = CH × 5 + Speech ÷ 4. Das ist die Chance, kleine Ereignisse allein zu lösen. Dazu Grundqualität +(CH − 5) × 2 | 50–150 $ |
| **Rausschmeißer** | Sicherheit, Gewalt-Ereignisse | STR, EN, Unarmed/Melee | Sicherheit = STR × 2 + EN + Unarmed ÷ 5 (z. B. STR 7, EN 6, Unarmed 60 → 32) | ca. 3 $ je Sicherheitspunkt (40–120 $) |
| **Buchhalter** | Kasse, Kontor | IN | Schwund 4 % bei IN ≥ 7, 6 % bei IN 5–6 (ohne Buchhalter 10 %) | 80 $ |
| **Doc** | Krankenstube | Doctor | Ab Doctor 50: Moral +1/Woche, keine Seuchen. Ab Doctor 80: auch halb so viele Sucht-Ereignisse | 60 $ |
| **Barkeeper** | Bar | – | schaltet die Bar frei (Phase 2) | 30 $ |
| **Anwerber** | bringt neues Personal ins Haus | CH/Speech **oder** STR/Unarmed | siehe 2.2: Er entscheidet, ob Menschen freiwillig kommen | 40 $ + 50 $ je Anwerbung |
| **Arbeiterinnen & Arbeiter** | die Arbeit, um die sich alles dreht | Grundqualität 20–85 | Personal-Anteil (Phase 1), Moral, Qualität | Anteil statt Lohn |

**Personal und Kapazität.** Ein Zimmer braucht eine Person. Die Kapazitätsregel aus Phase 2 wird damit genauer:

```
Kapazität = min(Zimmer, Arbeitende) × 12 Kunden/Woche
```

Wer Zimmer baut, aber niemanden findet, verdient nichts daran. Flucht und Kündigung (Moral < 25) kosten deshalb unmittelbar Kapazität.

---

## 2. Anwerben

### 2.1 Wo man wen findet

| Stadt | Rausschmeißer | Doc / Buchhalter | Arbeitende (freiwillig) |
|---|---|---|---|
| The Den | Karawanenwachen, abtrünnige Leute aus Tylers Bande | – (nur über Durchreisende) | Frauen und Männer, die aus der Den weg wollen und nicht wissen, wohin |
| New Reno | Boxer aus dem Jungle Gym, arbeitslose Familienschläger | Buchhalter der Familien (teuer, loyal zur Familie) | Aussteigerinnen und Aussteiger aus dem Cat's Paw und den Golden Globes |
| Redding | entlassene Kumpel | ein Stadtarzt, der selbst am Jet hängt (billig, unzuverlässig) | Witwen und Witwer aus den Minen |
| Vault City | – (Mutanten und Ghule sind verboten) | verbannte Bürger mit Vault-Ausbildung | Außenweltler aus dem Courtyard |
| NCR | NCR-Veteranen, Karawanenwachen | Pfleger aus dem Hospital in Downtown | Zuzügler aus dem Bazaar |
| San Francisco | Schüler aus den Kampfschulen von Dragon und Lo Pan | Assistenten aus Dr. Fungs Klinik | Leute vom Tanker, gestrandete Hubologen |

### 2.2 Der Anwerber – die Figur, die man „Zuhälter“ nennt

Jedes Haus kann einen Anwerber beschäftigen. Er entscheidet, **wie** Menschen ins Haus kommen. Zwei Methoden schließen sich pro Haus aus:

| Methode | Check des Anwerbers | Tempo | Qualität der Neuen | Start-Moral | Folgen |
|---|---|---|---|---|---|
| **Werben** | CH 6 / Speech 50 | 1 Person alle 2 Wochen | 40–60 | 50 | keine. Ab Moral 75 im Haus kommen zusätzlich Menschen von selbst (Talent-Zulauf aus Phase 1) |
| **Zwingen** | STR 7 / Unarmed 60 **oder** Slaver-Kontakte | 1 Person pro Woche | 30–50 | 15 | Schulden, Jet, Drohungen. K −3/Woche pro Haus, H +5/Woche. Die Moral-Obergrenze liegt bei 50. Es gibt Flucht-Ereignisse, und die Rangers ermitteln, wenn es in der NCR geschieht. |

### 2.3 Tyrannen-Quellen

Diese Quellen stehen nur auf der Tyrannen-Route offen. Das Personal arbeitet ohne Anteil hinter dem „Riegel außen“ (Phase 2).

| Quelle | Preis | Qualität | Risiko |
|---|---|---|---|
| **Metzger** (Den) | 150 $ je Person | 30–45 | Flucht, Lara, Rangers |
| **Vortis** (NCR-Bazaar) | 200 $ je Person | 35–50 | Rangers: Beweise führen zum Lizenzentzug der Tränke |
| **Dienstboten-Pacht** (Vault City, über Amtsleiter Sorensen) | 50 $/Woche je Person | 40–55 | Die Menschen gehören weiter der Stadt. Eine Razzia macht sie zu Zeugen. |
| **Hubologen-Schuldner** (San Francisco) | Schuldschein übernehmen, 100 $ | 30–50 | Die Shi beobachten, der Kult verlangt Nachschub |

Zwangspersonal kostet **K −5/Woche pro Haus** (wie „Riegel außen“) und hebt die Chance auf Ereignisse um +10 %.

---

## 3. Unique Talent

Fünf Figuren mit Namen, Geschichte und eigener Anwerbe-Quest. Dazu kommt Miss Kitty, deren Rolle vom Ausgang in Phase 3 abhängt. Jede Unique-Figur hat eine **Loyalität** (0–100). Fällt sie unter 30, geht die Figur, oder sie wendet sich gegen dich.

### 3.1 Vesper – die Stimme des Strumpfbands (Ghul)

**Wer sie ist.** Evelyn Marsh, genannt Vesper, sang vor dem Krieg im Silver Garter Hotel in Reno, dem Haus, das heute das Silberne Strumpfband ist. Dann fielen die Bomben. Seit fast zweihundert Jahren lebt sie als Ghul in Gecko, zwischen Reaktor und Schrott, und singt nur noch für sich.

**Fundort:** Gecko. Erwähnt der Spieler das Strumpfband, horcht sie auf.

**Anwerbe-Quest „Ein Lied für die Virgin Street“**

| Schritt | Wege |
|---|---|
| Sie will das Hotel wiedersehen, aber der Weg führt an Vault-City-Patrouillen vorbei, die Ghule erschießen | Geleitschutz (Kampf) · Umweg (Outdoorsman 60) · Passierschein fälschen (Science 60) |
| Sie bleibt nur, wenn die Bühne wieder steht | Bar II muss gebaut sein. Die Bühne kommt als Teil davon hinzu |
| Sie fragt, was aus dem Haus geworden ist | Ehrlichkeit (Speech 40) hält die Loyalität. Lügen fliegen auf, sobald sie die Zimmer sieht (Loyalität −20) |

**Wirkung:** Nur im Strumpfband. Personalqualität +10, Ausstattung +10, Nebenumsatz +2 $ je Kunde (die Gäste kommen für ihre Stimme). Dazu kommt eigene Kundschaft: Ghul-Händler aus Gecko.
**Eigenheit:** Ereignis „Ghul im Haus“: Ein Gast greift sie an, weil sie ein Ghul ist. Der Rausschmeißer muss schneller sein als die Stimmung im Saal.
**Tyrannen-Variante:** Sie hat keine Angst vor dem Tod und geht einfach. Wer sie festhält, bekommt eine Stimme, die nicht mehr singt: Alle Boni entfallen.

### 3.2 Abigail Kessler – die gelöschte Bürgerin (Vault City)

**Wer sie ist.** Medizintechnikerin aus Vault City. Sie hat einen Außenweltler im Courtyard mit Vault-Medizin behandelt und dafür die Bürgerschaft verloren. Heute lebt sie im Courtyard, gleich neben der Pension von Hanne Voss. Sie weiß, welche Bürger nachts in die Kloake kommen. Einige davon haben damals über sie abgestimmt.

**Fundort:** Courtyard, Vault City.

**Anwerbe-Quest „Die gelöschte Bürgerin“**

| Weg | Check | Folge |
|---|---|---|
| Bürgerschaft wiederherstellen | Speech 70 bei Councilor McClure **oder** E VC ≥ 60 | Sie arbeitet für dich und bleibt Bürgerin. Loyalität 80 |
| Akte vernichten | Sneak 60 + Lockpick 60 im Amenities Office | Sie ist frei von ihrer Vergangenheit, H VC +10, Loyalität 70 |
| Mit der alten Tat erpressen (Tyrannen-Variante) | – | Sie arbeitet, weil sie muss. Loyalität 20, K −10, jederzeit Verrat möglich |

**Wirkung:** Sie ist der **Doc der Kloake** und verlangt statt 60 $ Lohn einen Anteil (+60 $/Woche gegenüber einem normalen Doc). Doctor 85: Seuchen verhindert, Sucht-Ereignisse halbiert. Sie kennt die Schichtpläne der Garde: Razzia-Proben in Vault City −25 %.
**Eigenheit:** Ereignis „Der Richter“: Einer der Bürger, die sie verurteilt haben, liegt im VIP-Trakt. Sie kann ihn heilen, bloßstellen oder vergiften. Die Entscheidung liegt bei dir und ihr.

### 3.3 Talus – der Stein von Broken Hills (Supermutant)

**Wer er ist.** Ein Supermutant, früher ein Soldat des Masters, heute Arbeiter in der Uranmine von Broken Hills. Er spricht langsam und schlägt selten. Als Menschen in Broken Hills verschwanden, fiel der Verdacht auf ihn, weil er ein Mutant ist und groß und schweigsam. Er sitzt in Marcus' Zelle, und Marcus glaubt selbst nicht an seine Schuld.

**Fundort:** Broken Hills, im Gefängnis.

**Anwerbe-Quest „Der Stein von Broken Hills“**

| Weg | Check | Folge |
|---|---|---|
| Die Wahrheit finden | Vanilla-Quest „Find the missing people for Marcus“ lösen (der Täter ist Francis) | Talus ist frei und folgt dir aus Dankbarkeit. Loyalität 90. Zählt auch als Vertrauen bei Marcus (Läuferroute, Phase 3) |
| Freikaufen | nicht möglich, Marcus nimmt kein Geld | – |
| Ausbrechen lassen | Lockpick 80 **oder** Kampf | Talus ist frei, Marcus wird zum Feind, Läuferroute gesperrt, Loyalität 60 |

**Wirkung:** Rausschmeißer mit Sicherheit +45 bei nur 50 $ Lohn (er will ein Dach und Respekt, nicht Geld). **Gewalt-Ereignisse löst er automatisch.** In der Gosse zu Spielbeginn bringt das +28 $/Woche bei branchenüblichem Anteil (Simulator), und die Überfälle bleiben aus.
**Eigenheit:** Er will lesen lernen (IN 7 des Spielers **oder** ein Buch aus Renescos Laden). Tust du es, steigt die Loyalität dauerhaft auf 100.
**Einschränkung:** Er darf nicht nach Vault City (Mutanten verboten). In der NCR senkt er die Nachfrage um 5 % (Vorurteile).
**Tyrannen-Variante:** Er hat für den Master Menschen in Käfige gesperrt und tut es nie wieder. Wer ihn an den „Riegel außen“ stellt, verliert ihn, und er zeigt dich bei Marcus an.

### 3.4 Julian Rook – der Aussteiger aus den Golden Globes

**Wer er ist.** Julian war der bekannteste Name der Golden Globes, des Pornostudios in New Reno. Heute ist er dreißig, sieht aus wie fünfzig und hängt am Jet. Das Studio hält ihn mit einem Vertrag und mit dem Stoff. Er weiß, wie Menschen angesehen werden wollen, und das ist eine seltene Gabe in einem Haus.

**Fundort:** Golden Globes, New Reno.

**Anwerbe-Quest „Letzte Klappe“**

| Schritt | Wege |
|---|---|
| Den Vertrag lösen | Barter 60 (800 $) · Gambling 70 (den Vertrag beim Pokern gewinnen) · mit dem Titel **Porn Star** respektiert dich das Studio: Speech 50 |
| Ihn vom Jet holen | Doctor 60 über drei Wochen **oder** Myrons Antidot **oder** Entzugsstube in Redding |
| Tyrannen-Variante | Du übernimmst den Vertrag und den Stoff. Er arbeitet, solange du lieferst. K −10, Loyalität bleibt 30, doppelt so viele Sucht-Ereignisse im Haus |

**Wirkung:** In jedem Haus mit VIP-Trakt: VIP-Kundschaft +3/Woche (in der Tränke +53 $/Woche laut Simulator), Hausruf +1/Woche.
**Eigenheit:** Ereignis „Rückfall“: Jede Woche 3 % Chance, in einem Haus mit Jet-Theke 10 %. Ein Rückfall ohne Doc endet im schlimmsten Fall tödlich.

### 3.5 Mara – die Überlebende (nur im Fluchtzweig von „Ketten“)

**Wer sie ist.** Die Frau aus dem Keller der Gosse (Phase 3). Hat der Spieler sie gerettet und die Linie „Ketten“ im Fluchtzweig beendet, kehrt sie zurück. Sie kommt nicht als Arbeiterin, sondern als **Madame**. Sie kennt jede Angst im Haus, weil sie sie selbst gehabt hat.

**Anwerbung:** nur mit einem Gespräch (Speech 50 oder Charisma 6) und nur, wenn der Spieler kein Zwangspersonal hält. **Sie entscheidet selbst.** Wer sie drängt (Speech-Option „Du schuldest mir das“), verliert sie an Ruth Calloway in der NCR.

**Wirkung:** Madame der Gosse (Nachfolgerin von Essie oder an ihrer Seite). Führung 70. Moral +1/Woche in der Gosse, keine Flucht-Ereignisse. Transporte der Fluchtroute (Phase 3) gelingen um 25 % öfter.
**Eigenheit:** Ihre Loyalität hängt am ganzen Imperium, nicht an einem Haus. Setzt du irgendwo Zwangspersonal ein, geht sie und bringt den Rangers Beweise.

### 3.6 Miss Kitty – Partnerin oder Rivalin

Entschieden in Phase 3: Kitty verschwindet nicht.

| Ausgang in Phase 3 | Kittys Rolle |
|---|---|
| **Bündnis** | Verbündete. Einmal pro Monat schickt sie einen Hinweis über die Mordinos (Warnung vor Ereignissen in New Reno). |
| **Fusion** | Unique-Madame der Filiale. Führung 85, Personalqualität in New Reno +10, Anwerben in New Reno doppelt so schnell. |
| **Druck, Sabotage oder Verrat** | **Rivalin.** Sie eröffnet in Redding „Kittys Kralle“ unter dem Schutz der Wrights: zusätzlich −10 % Kunden für die Schlacke. Dazu kommt das Ereignis „Abwerbung“: Liegt die Moral eines Hauses unter 60, wirbt sie jeden Monat eine Person ab. Läuft „Die Reinen“, sagt sie bei der Anhörung gegen dich aus: alle Checks in Akt 2 −10. |

Als Rivalin lässt sich Kitty nur mit einer eigenen Quest beenden („Die Kralle“, Phase-5-Skripting). Möglich sind Versöhnung (Speech 80 + Wiedergutmachung 2.000 $), die Übernahme ihres neuen Hauses (E Redding ≥ 40) oder Gewalt (K −20, die Wrights werden feindlich).

### 3.7 Wirtschaftliche Einordnung der Unique-Figuren

| Figur | Haus | Endausbau ohne | mit | Unterschied |
|---|---|---|---|---|
| Vesper | Strumpfband | 1.244 $ | 1.441 $ | +16 % |
| Abigail Kessler | Kloake | 1.284 $ | 1.344 $ | +5 % |
| Julian Rook | Tränke | 768 $ | 821 $ | +7 % |
| Talus | Gosse (Start, branchenüblich) | 81 $ | 109 $ | +35 % und keine Überfälle |

Mit allen Unique-Figuren kommt das Imperium auf etwa 5.200 $/Woche. Das liegt knapp über dem Zielkorridor und ist bewusst so gewählt: Wer alle fünf Anwerbe-Quests löst, soll es merken. Mara und Miss Kitty wirken vor allem über Moral, Ereignisse und Kapazität. Das bildet der Simulator nur indirekt ab.

---

## 4. Ereignisse

### 4.1 Das System

- **Wöchentlicher Wurf pro Haus:**

  ```
  Chance = 10 % + Hitze ÷ 5 + max(0, Bedrohung − Sicherheit) ÷ 2
         + 10 % bei Moral < 40 + 10 % bei Zwangspersonal       (höchstens 60 %)
  ```

  Das Ziel ist etwa ein Ereignis alle 4–6 Wochen in einem gut geführten Haus. In einem schlecht geführten Haus kommt fast jede Woche eins.
- **Klein oder Krise:**
  - *Kleine Ereignisse* löst die Madame mit der Chance ihrer Führung. Gelingt es nicht, wird eine Krise daraus.
  - *Krisen* erscheinen im Hauptbuch als **KRISE** und brauchen dich vor Ort. Jede Woche ohne Lösung kostet −20 % Kunden, nach 3 Wochen eskaliert die Krise (Schließung, Tote, Abwanderung).
- **Das Ereignis hängt vom Zustand ab:** Jet-Flut macht Sucht wahrscheinlicher, hohe Hitze Razzien, der Fall der Enklave die Soldaten.

### 4.2 Die drei Kern-Ereignisse

#### „Soldaten ohne Krieg“ – randalierende Enklave-Soldaten

**Wann:** Vor dem Fall der Enklave selten, nur im Strumpfband mit Salvatore-Paten und in der Bilge. Nach der Zerstörung der Ölplattform dreimal so häufig und in jedem Haus.
**Lage:** Zwei oder drei Soldaten in Powerrüstung, betrunken, bewaffnet. Nach dem Fall der Enklave haben sie keinen Befehl mehr und keinen Grund, morgen aufzuwachen. Normale Rausschmeißer haben keine Chance.

| Weg | Check | Folge |
|---|---|---|
| Bezahlen | 200 $ | Sie gehen, kommen aber wieder (Wiederholung in 4 Wochen 50 %) |
| Unter den Tisch trinken | Bar II + Barter 50 | Sie schlafen ein. Du kannst ihnen die Rüstung abnehmen (K −5) oder sie laufen lassen |
| Reden | Speech 70 | Einer bricht zusammen, als du nach seiner Einheit fragst. Sie gehen still |
| Anwerben | Speech 90 **oder** Charisma 8 | Ein Deserteur bleibt: Rausschmeißer mit Sicherheit +50. Die Brotherhood of Steel sucht ihn (Ereignis „Besuch aus dem Bunker“ in San Francisco) |
| Kämpfen | Talus oder der Spieler selbst | Beute: Powerrüstungsteile. Bleibt die Leiche liegen: H +20 (Golgotha-Totengräber, Phase 3) |
| Nicht gelöst | – | Eine Person aus dem Personal wird schwer verletzt oder stirbt: Moral −20, Hausruf −10 |

#### „Der Stoff“ – Sucht im Personal

**Wann:** Grundchance ×2 bei Jet-Flut in Redding, bei Jet-Theke oder „Umarmung“ und solange der Mordino-Dealer im Haus ist (Phase 3, Akt 3). ×1,5 bei Moral < 40.
**Verlauf in drei Stufen:**
1. Verdacht: Moral −5.
2. Sucht: Die Person arbeitet mit Qualität −20 und stiehlt aus der Kasse (Schwund +3 %).
3. Überdosis: 25 % Todesrisiko pro Woche ohne Behandlung.

| Weg | Check | Folge |
|---|---|---|
| Behandeln | Doctor 60 **oder** Doc im Haus **oder** Entzugsstube (Redding) **oder** Myrons Antidot | Nach 2 Wochen geheilt, Loyalität und Moral +5 |
| Entlassen | – | Kapazität −1 Person. Moral −10 im Haus (alle haben es gesehen) |
| An der Leine halten (Tyrannen-Variante) | – | Jet als Lohn: Die Person flieht nie, arbeitet aber mit Qualität −20. K −3/Woche. Die Moral des Hauses kann nicht über 40 steigen |

#### „Die Razzia“

**Wann:** Die Chance hängt ab von Hitze, Grundrisiko und Bestechung.
**Frühwarnung:** Ab E ≥ 60 oder mit einer bestochenen Wache kommt die Razzia eine Woche angekündigt. Dann kannst du Beweise verschwinden lassen: die Akte auslagern, den Riegel außen vorübergehend abbauen, das Zwangspersonal verstecken.

| Stadt | Wer kommt | Was gesucht wird | Folgen, wenn etwas gefunden wird |
|---|---|---|---|
| **Vault City** | Garde | das Haus überhaupt | **Das Personal geht über das Corrections Center an die Dienstboten-Zuteilung** (Phase 2). Freikaufen: 300 $ je Person bei Sorensen. Befreien: Sneak 70 + Lockpick 70, H VC +30. Aufgeben: Moral −30 in allen Häusern, K −10 |
| **NCR** | Polizei (wenn illegal) · Rangers (bei Zwangsarbeit) | fehlende Papiere · Zwangspersonal | Strafe von 500 $ · Lizenzentzug, die Rangers werden dauerhaft Feinde, das Zwangspersonal wird befreit |
| **New Reno** | keine Polizei, sondern der „Besuch“ einer verfeindeten Familie | Schwäche | Schäden am Haus, 2 Wochen Ausfall eines Moduls, E −10 |
| **The Den** | Männer der Sklavengilde | Flüchtlinge (Zuflucht, Mara) | Gefundene Flüchtlinge werden verschleppt. Metzger wird feindlich, die Linie „Ketten“ eskaliert |
| **Redding** | Sheriff Marion | gezinkte Waage, Schutzgeld | Revolte der Kumpel, 3 Wochen geschlossen, Ascorti verlangt das Doppelte |
| **San Francisco** | Inspektoren der Shi | Schmuggelkammer | Tribut +5 %, das Siegel der Shi wird entzogen |

### 4.3 Weitere Ereignisse

| Ereignis | Auslöser | Kurzbeschreibung | Lösungswege |
|---|---|---|---|
| **Gewalttätiger Freier** | Sicherheit < Bedrohung | Ein Gast schlägt zu | Rausschmeißer (automatisch mit Talus), Unarmed 50, Hausverbot und Ruf −2 |
| **Seuche** | keine Krankenstube, 5 % pro Woche | Krankheit im Haus | Doc/Krankenstube, Doctor 60, sonst 2 Wochen geschlossen |
| **Griff in die Kasse** | Moral < 40 oder Sucht | Geld fehlt | Buchhalter findet es (IN-Check), Sneak 50 zum Beschatten |
| **Flucht / Kündigung** | Moral < 25 oder Zwangspersonal | Personal verschwindet | Ziehen lassen, zurückholen (Outdoorsman/Kampf, K −10 bei Zwang) |
| **Abwerbung** | Kitty als Rivalin, Moral < 60 | Eine Person geht zu Kitty | Gegenangebot (Barter), Moral heben |
| **Metzgers Vergeltung** | „Der stille Krieg“ (Phase 3) | Die Gilde schlägt zu | Kampf, Tyler abkaufen, Rangers rufen |
| **Überfall auf Läufer** | Hitze auf der Route | Ein Wochengewinn ist weg | Spur verfolgen (Outdoorsman 60), Marcus' Eskorte verhindert es |
| **Stammkunde mit Geheimnis** | VIP-Trakt | Ein Gast redet zu viel | Material für die Akte (E +5), Schweigen verkaufen (+200 $), vergessen |
| **Inspektion der Liga** | „Lex Neun“ oder Calloway verbündet | Calloway prüft die Häuser | Bestehen bei Moral ≥ 60 und ohne Zwang, sonst ist die Ausnahme der Lex Neun weg |
| **Tod im Haus** | Überdosis, Gewalt, Zwangspersonal | Eine Person stirbt | Beerdigung (Moral +5, 100 $), Schweigen (Moral −15), Rache am Täter (H +10) |

---

## 5. Übergaben an die nächsten Phasen

| Element | Übergabe an Phase 5 (Technik) | Übergabe an Phase 6 (Ruf & Endings) |
|---|---|---|
| Rollen und Personal pro Haus | Array pro Haus: Anzahl, Grundqualität, Moral, Rollen-Stats | – |
| Unique-Figuren | eigene Critter-Skripte, Loyalität als Map- bzw. Globalvariable | ein eigener Satz im Epilog für jede Figur, die bis zum Ende bleibt |
| Anwerber-Methode | Flag pro Haus (Werben/Zwingen) | Tyrannen-Ruf, Slaver-Titel |
| Ereignissystem | Wurf im wöchentlichen Tick, Krisen-Timer, Hauptbuch-Anzeige | Tote im Haus zählen für den Epilog mit |
| Soldaten ohne Krieg | Hängt am Vanilla-Zustand „Ölplattform zerstört“ | Die Westküste nach der Enklave |

---

## 6. Offene Entscheidungen (für die Freigabe von Phase 5)

1. **Die fünf Unique-Figuren** (Vesper, Abigail Kessler, Talus, Julian Rook, Mara): So übernehmen, oder soll eine Figur ersetzt werden?
2. **Der Anwerber:** Ist die Trennung „Werben“ gegen „Zwingen“ als zweite Moralachse so richtig?
3. **„An der Leine halten“** und die Tyrannen-Quellen (Metzger, Vortis, Dienstboten-Pacht, Hubologen-Schuldner): alle im Spiel lassen?
4. **„Tod im Haus“** als Ereignis: gewünscht? Er macht die Welt härter, aber auch bitterer.
5. **Unique-Figuren und Tod:** Sollen Unique-Figuren sterben können (endgültig, wie Vanilla-Begleiter), oder nur schwer verletzt ausfallen?
