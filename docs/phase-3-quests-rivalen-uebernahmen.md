# Phase 3 – Quests, Rivalen & feindliche Übernahmen

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Freigegeben (siehe Entscheidungen unten). Weiter in [Phase 4](phase-4-personal-talente-ereignisse.md).

> **Freigabe-Entscheidungen**
> 1. Die drei Questlines bleiben, mit Ruth Calloway als Gegenspielerin, die in vielem recht hat.
> 2. „Der neue Metzger“ bleibt das dunkelste Ende.
> 3. Der Grave-Digger-Weg über das Grab in Golgotha bleibt.
> 4. **Miss Kitty** verschwindet nach einer Übernahme durch Druck, Sabotage oder Verrat nicht aus dem Spiel. Sie kehrt in Phase 4 als Rivalin zurück (Empfehlung des Lead Designers, vom Auftraggeber übernommen).
> 5. Mara verbindet die Den und die NCR.
**Grundlage:** [Phase 1](phase-1-core-loop-und-wirtschaft.md) und [Phase 2](phase-2-standorte-und-ausbau.md) sind freigegeben. Der Ton ist düster und unbarmherzig, alle dunklen Module bleiben im Spiel.

---

## 0. Quest-Architektur

| Ebene | Inhalt | Umfang | Zweck |
|---|---|---|---|
| **Übernahme-Quests** | eine pro Bordell | 6 | öffnet die Tür zum Haus |
| **Rivalen-Questlines** | drei große Linien in je 5 Akten | 3 | Rückgrat des Addons, verändert die Welt |
| **Feindliche Übernahmen** | Cat's Paw, Malamute Saloon, Hubologen | 3 | schaltet die Konkurrenz aus (die Abzüge aus Phase 2) |
| **Jobs** | Bestechung, Schutzgeld, Sabotage, Gefälligkeiten | wiederholbar | steuert Einfluss und Hitze |
| **Sonderquest** | Die Läuferroute durch Broken Hills | 1 | sichert den Geldfluss ins Hauptquartier |

**Grundregeln**

1. **Vier Wege, nicht vier Knöpfe.** Fast jede Quest lässt sich lösen durch Reden, Geld, Heimlichkeit oder Gewalt. Nicht jeder Weg steht jeder Figur offen, und jeder hinterlässt andere Spuren.
2. **Scheitern ist kein Ende.** Ein misslungener Check öffnet den nächsten Weg, und der ist teurer, lauter oder schmutziger.
3. **Jede Lösung hat einen Preis.** In den Tabellen steht bei jeder Lösung, was sie an Einfluss (E), Hitze (H), Karma (K) und Geld ($) kostet oder bringt.
4. **Vanilla hat Vorrang.** Hat der Spieler eine Fraktion schon mit Vanilla-Quests zerschlagen, passt sich die Questline an (siehe die „Anpassung“ bei jeder Linie). Nichts macht einen Vanilla-Fortschritt rückgängig.

**Zur Erinnerung aus Phase 1:**
- **Einfluss (E)** 0–100 pro Stadt. Ab 20 kannst du gründen, ab 40 feindlich übernehmen, ab 60 warnen dich die Behörden vor Razzien, ab 80 machst du Politik.
- **Hitze (H)** 0–100 pro Stadt, sinkt um 5 pro Woche.

---

## 1. Skill-Gating

**Schwierigkeitsstufen**

| Stufe | Skill | Attribut | Wann |
|---|---|---|---|
| Leicht | 40 % | 5 | früh im Spiel, als Hauptfertigkeit gewählt |
| Mittel | 60 % | 6 | Mitte des Spiels |
| Schwer | 80 % | 7 | spezialisierte Figur |
| Meister | 100 % | 8+ | späte Schlüsselmomente |

**Welche Fertigkeit wofür**

| Fertigkeit | Wofür | Beispiele |
|---|---|---|
| **Speech** | überzeugen, drohen, verhandeln | Metzger umstimmen, Anhörung vor dem NCR-Rat, Sit-down mit den Mordinos |
| **Barter** | Preise, Tribute, Bestechungssummen | Schulden drücken, Beteiligung am Malamute, Schmiergeld verhandeln |
| **Charisma** (Attribut) | Vertrauen, Führung | Familientreffen, Personal zum Reden bringen, Miss Kitty gewinnen |
| **Sneak** | beschatten, einschleichen, verstecken | Dealer im Haus stellen, Flüchtlinge durch die Wüste bringen, die Akte stehlen |
| **Steal** | Beweise und Papiere | Schuldschein, Brandbeweise, Kundenlisten |
| **Lockpick** | Tresore, Aktenschränke | Vortis' Büro, Ascortis Schreibtisch |
| **Unarmed / Melee** | schmutzige Arbeit ohne Leichen | Eintreiber verprügeln, Schutzgeld „einsammeln“ |
| **Science** | Fälschungen, Beweisanalyse | Pensionsurkunde in Vault City, Brandbeschleuniger bestimmen |
| **Doctor** | Sucht und Seuche | Jet-Entzug beim Personal, gepanschter Schnaps |
| **Outdoorsman** | Routen durch die Wüste | Fluchtroute nach Süden, Läuferroute |
| **Traps / Repair** | Anschläge verhindern oder verüben | Brandsatz entschärfen, Goldwaage manipulieren |
| **Gambling** | Spieltische im Strumpfband | Falschspieler entlarven, Schulden erspielen |

**Titel und Ruf als Schlüssel**
- **Made Man** (einer Familie in New Reno): öffnet Dialoge mit den Familien, macht Drohungen glaubwürdiger.
- **Slaver:** öffnet bei Metzger und Vortis Türen und verschließt sie bei den Rangers, bei Marcus und bei der Liga.
- **Prizefighter:** Respekt auf der Virgin Street. Kann Unarmed-Checks ersetzen.
- **Grave Digger:** neu erreichbar über „Das Grab in Golgotha“ (Abschnitt 2.2).
- **Karma-Titel:** Guter Ruf öffnet Wege bei Marcus, Calloway und den Rangers. Schlechter Ruf öffnet sie bei Metzger, Vortis und den Mordinos.

---

## 2. Übernahme-Quests

### 2.1 The Den – „Essies Schulden“ (Prolog)

Siehe Phase 1: fünf Lösungswege von „bezahlen“ bis „Essie ausliefern“. Neu ist, dass Essie auf jeden Weg reagiert, und das prägt den Start der Questline „Ketten“ (3.2):

| Weg | Essie danach | Metzger danach | Einstieg in „Ketten“ |
|---|---|---|---|
| Bezahlt | loyal | neutral | Akt 1 normal |
| Partnerschaft | misstrauisch („Du hast uns an ihn verpachtet.“) | Geschäftspartner | Akt 1 mit höherem Druck |
| Eintreiber verprügelt | beeindruckt | respektvoll, nachtragend | Akt 1, H +10 |
| Schuldschein gestohlen | loyal | feindlich, sobald er es bemerkt | Akt 1 wird zur Drohung |
| Essie ausgeliefert | – | Freund | Die Linie startet im Tyrannen-Zweig |

### 2.2 New Reno – „Der Segen“

Das Silberne Strumpfband ist leer, seit sein letzter Besitzer in Golgotha liegt. Zwei Dinge brauchst du: **die Urkunde** und **den Segen einer Familie**.

**Teil A: Die Urkunde**

| Weg | Check | Folge |
|---|---|---|
| Das Grab in Golgotha | Schaufel, nachts, Sneak 40 | Die Urkunde lag im Sarg. Titel **Grave Digger**, K −10 |
| Die Witwe des Besitzers | Speech 60 oder 1.000 $ (Barter senkt) | sauber, E New Reno +5 |
| Fälschung | Science 60 + Urkundenpapier von den Golden Globes | H +5. Fliegt sie auf (Zufall 15 %), fordert die Witwe später Geld |

**Teil B: Der Segen**

| Pate | Auftrag | Check | Folge |
|---|---|---|---|
| **Mordino** | Eine Jet-Lieferung an den Wright-Leuten vorbei in die Stables bringen | Sneak 60 **oder** Kampf | Wright misstrauisch, H +10 |
| **Wright** | Beweisen, dass Mordino-Jet im Cat's Paw kursiert | Perception 7 **oder** Steal 60 | Mordino misstrauisch. Miss Kitty erfährt, wer geschnüffelt hat |
| **Salvatore** | Eine nächtliche Übergabe in der Wüste bewachen. Hat der Spieler Salvatores Vanilla-Auftrag „Übergabe bewachen“ schon erledigt, gilt der Segen sofort | Kampf **oder** Vanilla-Vorleistung | Salvatore-Respekt, Enklave-Hook für Phase 4 |
| **Bishop** | Eine Nachricht an Westin in der NCR überbringen, ohne sie zu öffnen | – (öffnen: Lockpick 60, dann weißt du mehr als gut für dich ist) | E NCR +10. Geöffnet: Erpressungsmaterial gegen Bishop, H +15 |
| **Unabhängig** | Die Eröffnungsnacht überleben: Männer ohne Farben stürmen das Haus | Kampf, Sicherheit des Hauses | alle vier Familien misstrauisch, E New Reno +10 (Respekt) |

### 2.3 Redding – „Ascortis Lizenz“

Bürgermeister Ascorti verkauft die Lizenz nur im Paket, zusammen mit der Urkunde für die von Wanamingos verseuchte Mine (der Vanilla-Betrug um 1.000 $). Danach kassiert er die laufende „Lizenz“ von 75 $/Woche aus Phase 2.

| Weg | Check | Folge |
|---|---|---|
| Paket kaufen | 1.000 $ (Barter 60: −40 %) | Lizenz, danach 75 $/Woche. Die Mine ist ein Problem, das sich in Vanilla lösen lässt: gesäubert = Minen-Boom (Phase 1) |
| Aufschlag statt Kaufpreis | Speech 70 | kein Paketpreis, dafür 125 $/Woche statt 75 $ |
| Ascorti bloßstellen | Steal 60 oder Lockpick 60 (Schreibtisch) + Speech 60 bei Sheriff Marion | Marion wird Schutzherr (Sicherheit +10 in Redding) und nimmt kein Geld: Die 75 $/Woche entfallen. Ascorti wird Feind |
| Einschüchtern | Unarmed 60 **oder** STR 7 | kein Paketpreis, und Ascorti traut sich nicht, die 75 $/Woche einzufordern. H Redding +20, Marion beobachtet dich |

### 2.4 Vault City – „Ein Keller im Courtyard“

Die Pension gehört **Hanne Voss**, einer Witwe von draußen. Sie weiß längst, dass ihr Keller Besuch aus Downtown bekommt. Der erste Stammkunde ist **Amtsleiter Sorensen** aus dem Amenities Office, und er darf nie auffliegen.

| Schritt | Wege | Folge |
|---|---|---|
| Hanne gewinnen | Speech 60 (Anteil 10 % für sie) **oder** 1.500 $ Kaufpreis | Sie wird die Wirtin der Tarnung |
| Papiere | Bürgerschaft (Vanilla) **oder** Sorensen bestechen (Barter, 500 $) **oder** Fälschung (Science 60) | Mit der Bürgerschaft sinkt das Schweigegeld um 50 $ |
| Ein Auge am Tor | Eine Wache anwerben: Charisma 6 + 50 $/Woche **oder** Sorensen drängt die Wache zu Diensten (dunkel: Sorensen ist ab jetzt erpressbar) | Frühwarnung vor Razzien |

### 2.5 NCR – „Etablissement Nr. 9“

Der Rat vergibt die Lizenz. Die Bürokratie der Republik ist langsam, gründlich und käuflich, wenn man weiß, bei wem.

| Weg | Check | Folge |
|---|---|---|
| Antrag über den Dienstweg | 500 $ (Bishop-Pate −50 %), Krankenstube (Auflage), 3 Wochen Wartezeit | sauber, E NCR +5 |
| Den Schreiber beschleunigen | Barter 40, 300 $ | 1 Woche Wartezeit, H +5 |
| Westins Fürsprache | Speech 60 | Westin verlangt VIP-Vorrechte und 5 % Anteil, E NCR +10 |
| Ohne Lizenz eröffnen | – | illegales Haus: Risiko 1 → 4, H +30. Die Questline „Die Reinen“ beginnt verschärft |

### 2.6 San Francisco – „Die Duldung“

**Aufseher Wen** verwaltet für die Shi die Docks. Die Shi dulden nichts, was sie nicht kontrollieren. Sein erstes Angebot: 15 % Tribut.

| Weg | Check | Folge |
|---|---|---|
| Augen der Shi werden | Die Bilge meldet jede Woche, wer an den Docks ein- und ausgeht | Tribut 10 %, „Siegel der Shi“ wird verfügbar. Die Tanker-Leute werden misstrauisch, sobald sie es merken (Sneak-Checks halten es geheim) |
| Tribut drücken | Barter 60 | Tribut 10 % ohne Spitzeldienste. Das Siegel gibt es erst nach einem späteren Gefallen |
| Die Tanker-Vagabunden als Rückendeckung | Speech 60 beim Tanker | kein Tribut, aber keine Duldung der Shi: H SF +15, Schmuggelkammer sofort verfügbar |

---

## 3. Die drei Rivalen-Questlines

### 3.1 „Blut auf der Virgin Street“ – die Mordinos & das Cat's Paw (New Reno)

**Start:** Das Strumpfband ist eröffnet (Mitte des Spiels).
**Gegenspieler:** **Carlo Venuti**, Mordino-Capo der Virgin Street. Im Hintergrund steht Big Jesus Mordino.
**Motiv:** Die Virgin Street gehört dem Desperado. Ein Bordell ohne Jet ist ein Bordell, das den Mordinos Umsatz kostet.
**Variante bei Mordino-Paten:** Der Konflikt wird zur **„Umarmung“**. Venuti ist dein Betreuer, und jede Gefälligkeit kostet mehr. Die Akte sind dieselben, nur die Drohungen kommen von innen.

**Akt 1 – Nachbarschaftsgebühr.** Venuti verlangt zusätzlich zum Paten-Tribut 200 $/Woche.

| Weg | Check | Folge |
|---|---|---|
| Zahlen | – | −200 $/Woche, Akt 2 normal |
| Halbieren | Barter 60 | −100 $/Woche |
| Über seinen Kopf hinweg | Speech 80 bei Big Jesus: „Streit auf der Virgin Street verschreckt die Spieler.“ | Gebühr fällt weg, E +5, Venuti gedemütigt (Akt 4 persönlicher) |
| Verweigern | – | H +10, Akt 3 beginnt sofort |
| Made Man einer anderen Familie | Titel | deine Familie greift ein: Gebühr weg, aber Spannungen zwischen den Familien |

**Akt 2 – Miss Kittys Angebot.** Die Mordinos drücken auch das Cat's Paw. Miss Kitty kommt zu dir. Details zu allen Optionen stehen bei den feindlichen Übernahmen (4.1).

**Akt 3 – Jet im Blut.** Das Personal wird süchtig, denn ein Mordino-Dealer arbeitet im Haus.

| Schritt | Wege |
|---|---|
| Den Dealer finden | Perception 7 **oder** Sneak 60 (nachts beschatten). Liegt die Moral bei 70 oder mehr, sagt es dir das Personal selbst: Wer fair behandelt wird, redet. |
| Mit ihm umgehen | Rauswerfen (Unarmed 60) · umdrehen (Speech 70: er wird Spitzel, du bekommst Beweise für Akt 4) · verschwinden lassen (H +20, Golgotha) |
| Das Personal heilen | Doctor 60 pro Person **oder** Myrons Jet-Antidot aus den Stables (Vanilla-Anknüpfung) |

**Akt 4 – Die Nacht der langen Messer.** Venuti schlägt zu.

| Weg | Check | Folge |
|---|---|---|
| Verteidigen | Kampf im Strumpfband. Sicherheit und Rausschmeißer zählen. | Schäden am Haus je nach Ausgang (Module fallen 2 Wochen aus) |
| Zuvorkommen | Beweise aus Akt 3 + Bündnis mit den Wrights (Speech 60 bei Orville Wright) | Die Wrights schlagen im Desperado zu. Du hältst dich im Hintergrund, E +10 |
| Sit-down im Desperado | Speech 90 **oder** Charisma 8 + Made Man | Waffenstillstand ohne Blut |

**Akt 5 – Enden**

| Ende | Bedingung | Folgen |
|---|---|---|
| **Der leere Stuhl** | Die Mordinos fallen, durch diese Linie oder durch Vanilla | Machtvakuum 4 Wochen, danach werden die Tribute neu verhandelt. E New Reno +20. In Redding gibt es kein Mordino-Jet mehr (Jet-Index: Knappheit) |
| **Waffenstillstand** | Sit-down oder Zahlung | Gebühr fällt weg, H −20, die Virgin Street bleibt geteilt |
| **Die Umarmung** (dunkel) | Du wirst der Bordell-Arm der Mordinos | Jet-Theke in allen Häusern Pflicht, Einnahmen +20 %, doppelt so viele Sucht-Ereignisse überall. Die Wrights werden Feinde, K −30, Made Man (Mordino) |

**Anpassung an Vanilla:** Sind die Mordinos schon gefallen, wenn das Strumpfband öffnet, führt Venuti einen Rest der Familie und will Rache statt Gebühr. Die Linie beginnt dann bei Akt 3.

---

### 3.2 „Ketten“ – Metzger & die Sklavengilde (The Den)

**Start:** direkt nach dem Prolog (früh im Spiel).
**Gegenspieler:** **Metzger**.
**Motiv:** Für Metzger ist die Gosse ein Absatzmarkt. Er will, dass sie ein Glied seiner Kette wird: Den → Vault City (Servant Allocation Center) → NCR (Vortis im Bazaar).

**Akt 1 – Das Angebot.** Metzger bietet „Ware“ zum halben Preis an, als Zwangspersonal hinter dem Riegel außen.
- **Annehmen:** Die Linie läuft im **Tyrannen-Zweig (T)** weiter.
- **Ablehnen:** Die Linie läuft im **Fluchtzweig (F)** weiter. Metzger merkt es sich.

**Akt 2 – Die im Keller.** **Mara**, eine Frau Mitte zwanzig, ist aus einer Karawane der Gilde entkommen. Essie hat sie im Keller der Gosse versteckt.

| Weg | Check | Folge |
|---|---|---|
| Verstecken | – | Modul „Zuflucht“ wird frei, K +10. Metzgers Leute durchsuchen die Den |
| Sofort in Sicherheit bringen | Sneak 60 **oder** Outdoorsman 60 | Mara erreicht die NCR und taucht in Linie 3.3 wieder auf |
| An Metzger ausliefern | – | 500 $, Metzgers Vertrauen, K −25. Essie kündigt (oder schweigt, falls sie längst gebrochen ist) |

**Akt 3 – Die Kette**

| Zweig | Inhalt | Checks | Folge je Durchgang |
|---|---|---|---|
| **F: Nach Süden** | Du findest das versteckte Hauptquartier der Rangers in der NCR (Perception oder Maras Wissen). Die Gosse wird eine Station auf der Fluchtroute. Jeder Transport ist ein wiederholbarer Job. | Sneak 60 / Outdoorsman 60 | H Den +10, K +5, E NCR +3 |
| **T: Nach Norden** | Metzger will, dass du „Ware“ liefert: über Sorensens Kontakte an die Dienstboten-Zuteilung in Vault City und an Vortis in der NCR. | Speech/Barter für die Übergaben | +300–600 $, K −15, H NCR +10 (die Rangers zählen mit) |

**Akt 4 – Tylers Preis**

| Zweig | Lage | Wege |
|---|---|---|
| F | Tylers Bande, Metzgers Muskeln, bedroht die Gosse | abkaufen (Barter 60, 400 $) · Lara auf Tyler hetzen (Speech 60; der Vanilla-Konflikt um die Kirche) · umdrehen (Speech 80) · Kampf |
| T | Laras Bande stürmt die Gosse, um die Gefangenen zu befreien | verteidigen (Kampf, K −10) · Lara ziehen lassen (Metzger erfährt davon) |

**Akt 5 – Enden**

| Ende | Zweig | Folgen |
|---|---|---|
| **Die Gilde fällt** | F | Sturm auf die Sklavengilde mit Rangers und Lara (oder Vanilla-Zerschlagung). Kunden in der Den −25 %, H Den −20, K +50. Die Rangers werden Verbündete (E NCR +15), Vortis wird Feind. Mara entscheidet selbst, wie es für sie weitergeht (Phase 4). |
| **Der stille Krieg** | F | Die Route läuft weiter, die Gilde steht noch. Transporte bleiben ein Dauerrisiko, Metzger schlägt irgendwann zurück (Ereignis Phase 4). |
| **Metzgers Mann** | T | stabile, schmutzige Partnerschaft. Einnahmen aus Lieferungen, Slaver-Titel |
| **Der neue Metzger** | T | Du verrätst Metzger oder beerbst ihn und übernimmst die Gilde. Einnahmen aus der Den +50 %, K −100. Die Rangers jagen deine Läufer. Finden sie Beweise, verliert die Tränke ihre Lizenz. Dunkelstes Ende des Addons (Epilog in Phase 6). |

**Anpassung an Vanilla:** Ist die Gilde schon zerschlagen, beginnt die Linie mit Akt 2 (Mara entkommt einer Resttruppe) und endet in „Tylers Rache“. Ist der Spieler selbst Slaver geworden, startet die Linie im Tyrannen-Zweig.

---

### 3.3 „Die Reinen“ – moralische Kreuzritter (NCR)

**Start:** Die Tränke ist eröffnet (spätere Mitte des Spiels).
**Gegenspielerin:** **Ruth Calloway**, Anführerin der **Liga für eine reine Republik**.
**Wer sie ist:** Calloway ist vor zehn Jahren aus den Pferchen der Den geflohen. Sie hat gesehen, was Häuser wie die Gosse aus Menschen machen. **Sie ist keine Heuchlerin, und in vielem hat sie recht.** Sie irrt sich nur darin, was aus den Arbeiterinnen und Arbeitern wird, wenn die Häuser schließen: Sie landen auf der Straße oder in Vortis' Pferch.
**Verbündete der Liga:** Teile des NCR-Rats, Sympathisanten in Vault City (Lynette).
**Gegner der Liga:** Westin, die Karawanengilden, bestechliche Polizisten.

**Akt 1 – Flugblätter.** Die Sittlichkeitskampagne startet: Kunden in der NCR −15 %, Streikposten vor der Tränke.

| Weg | Check | Folge |
|---|---|---|
| Mit Calloway reden | Speech 60 | Sie erzählt ihre Geschichte. Hast du Mara gerettet (3.2), bürgt Mara für dich: Calloway hört zu, die Kampagne fällt auf −5 % |
| Gegenkampagne | Barter 60 (Rawhide Saloon und Karawanenführer bezahlen) | Kampagne −10 % statt −15 %, H +5 |
| Streikposten vertreiben | Unarmed 60 | Kampagne weg, H +10, K −5. Die Liga hat jetzt Märtyrer |

**Akt 2 – Die Anhörung.** Der Rat berät ein **Sittengesetz**, das alle Lizenzen widerrufen würde.

| Weg | Check | Folge |
|---|---|---|
| Rede vor dem Rat | Speech 80. Registratur und Krankenstube zählen als Beleg für Ordnung (+10 auf den Check) | Stimmung kippt zu deinen Gunsten |
| Stimmen kaufen | 2.000 $, Barter 60 | wirkt. Fliegt es auf (Zufall 20 %), gibt es einen Skandal: H NCR +30 |
| Westin einspannen | Speech 60 (er fürchtet, als VIP-Gast bekannt zu werden) | öffentliche Unterstützung. Dunkel: Mit Gesprächen aus dem VIP-Trakt kannst du ihn erpressen, statt ihn zu überzeugen |
| Tandis Büro | E NCR ≥ 60 | Die Präsidentin lässt ausrichten: „Die Republik regelt, sie verbietet nicht.“ +10 auf alle Checks dieses Akts |

**Akt 3 – Feuer im Bazaar.** Nachts brennt die Tränke. Du kannst löschen (Repair 60 oder Traps 60 gegen einen zweiten Brandsatz). Sonst fällt das Haus 4 Wochen lang eine Hausklasse zurück. Alle verdächtigen die Liga.

| Ermittlung | Check | Wahrheit |
|---|---|---|
| Brandbeschleuniger bestimmen | Science 60 | Industrie-Brennstoff, wie ihn nur der Bazaar-Händler an Vortis verkauft |
| Zeugen befragen | Speech 60 / Charisma 6 | Ein Bettler hat Männer aus dem Pferch gesehen |
| In Vortis' Büro | Sneak 60 + Lockpick 60 | schriftlicher Auftrag |

**Die Wahrheit:** Vortis hat gelegt. Die Liga bekämpft auch den Sklavenhandel, und ein Brand, den man ihr anhängt, würde sie verbieten lassen.
**Im Tyrannen-Zweig** (du lieferst an Vortis) war es ein radikaler Flügel der Liga, von dem Calloway nichts wusste. Für deine Taten gibt es keine saubere Seite.

**Akt 4 – Beweise**

| Weg | Folge |
|---|---|
| Den Rangers übergeben | Vortis wird verhaftet, sein Pferch geschlossen. Die Liga steht öffentlich bei dir in der Schuld |
| Vortis erpressen | Er zahlt 150 $/Woche Schweigegeld an dich, H +10 |
| Der Liga anhängen | Science 60 (Beweise fälschen). Die Liga wird verboten, Calloway verhaftet, K −30 |

**Akt 5 – Enden**

| Ende | Bedingung | Folgen |
|---|---|---|
| **Das Musterhaus** | Beweise an die Rangers, Moral in der Tränke ≥ 60, kein Slaver-Titel | Das Sittengesetz kommt mit Ausnahme: Registrierte Häuser mit fairem Anteil, ohne Zwangsarbeit und mit Untersuchungen dürfen weiterarbeiten (**„Lex Neun“**). Illegale Konkurrenz schließt: Kunden NCR +20 %. Calloway wird eine unbequeme Verbündete und kontrolliert deine Häuser. Kippst du später in die Ausbeutung, kommt sie zurück. |
| **Die Diskreditierung** | Liga angehängt oder erpresst | Die Liga zerbricht, Calloway ist ruiniert. Auf Wunsch stirbt sie (H +40, die Rangers ermitteln). NCR-Nachfrage normal, K −30 bis −60 |
| **Das Verbot** | Anhörung verloren, keine Beweise | Das Sittengesetz ohne Ausnahme: Die Tränke verliert die Lizenz. Sie arbeitet illegal weiter (Risiko 1 → 4, H +30) oder schließt. |

**Übergreifende Folgen:** Siegt die Liga oder wird sie Verbündete, übernimmt Lynette ihre Linie in Vault City: 50 % mehr Razzia-Proben für die Kloake. Zerbricht die Liga, verliert Lynette eine Stimme, und die Razzien werden seltener.

---

## 4. Feindliche Übernahmen der Konkurrenz

### 4.1 Das Cat's Paw (New Reno) – im Rahmen von 3.1, Akt 2

**Miss Kitty** führt das einzige unabhängige Haus der Stadt. Die Mordinos drücken, du auch.

| Weg | Check | Folge |
|---|---|---|
| **Bündnis** | Speech 60 | Beide verweigern Venuti die Gebühr. Abzug durch das Cat's Paw −15 % → −5 %, E +5 |
| **Fusion** | Speech 70 + 3.000 $ **oder** E New Reno ≥ 40 | Das Cat's Paw wird Filiale: +3 Zimmer für das Strumpfband, Gewinnteilung 50/50 mit Kitty, der Abzug fällt weg |
| **Druck** | Unarmed 60 oder Erpressung (VIP-Trakt) | Kitty verkauft für 1.500 $ und verlässt New Reno als Feindin. K −10, Abzug weg, volle Übernahme |
| **Sabotage** | Sneak 60 (gepanschter Schnaps im Cat's Paw) | Kunden werden krank, Abzug weg, K −10. Fliegt es auf: E New Reno −15 |
| **Verrat** | – | Du lieferst Kitty an Venuti aus. Die Mordinos übernehmen das Cat's Paw, du bekommst 1.000 $ und Gebühren-Nachlass, K −20 |

### 4.2 Der Malamute Saloon (Redding)

Der Saloon in Downtown bietet schon käufliche Liebe an (−10 % für die Schlacke). Der Name des Betreibers wird in Phase 5 an Vanilla angeglichen.

| Weg | Check | Folge |
|---|---|---|
| **Beteiligung** | Barter 60, 1.500 $ | 30 % der Malamute-Gewinne (ca. +60 $/Woche), Abzug weg |
| **Preiskrieg** | 4 Wochen Preisstufe „Ramsch“ | eigener Gewinn sinkt, danach gibt der Malamute das Geschäft auf |
| **Sabotage** | Sneak 60 | gepanschter Schnaps, K −10. Erwischt: Sheriff Marion wird feindlich |
| **Übernahme** | E Redding ≥ 40 + 3.000 $ | Der Malamute wird Nebenhaus: +2 Zimmer für die Schlacke |

### 4.3 Die Hubologen (San Francisco)

Sie betreiben kein Bordell, aber sie werben um dieselben Verlorenen (−10 % für die Bilge).

| Weg | Check | Folge |
|---|---|---|
| **Entlarven** | Science 70 (die „Auditing“-Maschine ist wertlos) | Zweifler verlassen den Kult, Abzug weg, E SF +5 |
| **Unterwandern** | Speech 60 | Die Zweifler kommen zu dir: SF +10 % |
| **Absprache** (dunkel) | Barter 60 | Wer seine Auditing-Schulden nicht zahlen kann, landet in der Bilge: Schuldknechtschaft als Personal, K −20. Gilt als Zwangsarbeit (Tyrannen-Route) |
| **Vanilla** | Die Hubologen sind gefallen | Der Abzug entfällt automatisch |

---

## 5. Jobs: Bestechung, Schutzgeld, Sabotage, Gefälligkeiten

### 5.1 Bestechung – wer nimmt Geld, wer nicht

| Stadt | Wer | Preis | Wirkung | Besonderheit |
|---|---|---|---|---|
| The Den | Tyler | 100 $/Woche | H −5/Woche | endet, wenn Tyler fällt |
| New Reno | Totengräber in Golgotha | 300 $ einmalig | H −15 nach einem gewaltsamen Vorfall | Die Leichen verschwinden, die Fragen auch |
| Redding | Ascorti | 75 $/Woche (Lizenz) | Grundvoraussetzung | Sheriff Marion nimmt **kein Geld**, nur Gefälligkeiten (z. B. die Wanamingo-Mine säubern) |
| Vault City | Torwache | 50 $/Woche | Warnung vor Razzien (Razzia-Probe halbiert) | |
| Vault City | Councilor McClure | 1.000 $ „Spende“ für den Gecko-Frieden | E VC +10 | nur, wenn der Gecko-Konflikt noch offen ist |
| Vault City | **First Citizen Lynette** | **unbestechlich** | – | Beeinflussbar nur über Erpressung: Die Akte zeigt einen ihrer Verbündeten im Rat als Stammkunden. Dann enden die Razzien, E VC +20, H VC +20 |
| NCR | Polizist in Downtown | 80 $/Woche | H −5/Woche | Rangers-Hitze bleibt unberührt |
| San Francisco | Aufseher Wen | Tribut | Duldung | Bei einer Doppelrolle mit den Tanker-Leuten steigt der Preis |
| Broken Hills | **Sheriff Marcus** | **unbestechlich** | – | siehe Läuferroute (Abschnitt 6) |

### 5.2 Schutzgeld (Richtung Tyrann)

- **Ziele:** kleine Stände in der Den West Side, in Redding Downtown und im NCR-Bazaar. Das sind neue Händler, die wichtigen Vanilla-Händler bleiben unberührt.
- **Check:** Unarmed 60 **oder** STR 7 **oder** Speech 60 (Drohung).
- **Ertrag pro Stand:** 50–150 $/Woche, E +2/Woche, H +5/Woche, K −2/Woche.
- **Risiken:** In der NCR zählt jede Woche doppelte Hitze bei den Rangers. In Redding wird Sheriff Marion feindlich.

### 5.3 Sabotage und Gefälligkeiten

| Job | Check | Wirkung |
|---|---|---|
| Lieferung eines Rivalen abfangen | Sneak 60 / Kampf | E des Rivalen −5, H +5 |
| Buchhaltung eines Rivalen stehlen | Steal 60 / Lockpick 60 | Erpressungsmaterial (ein Mal verwendbar) |
| Spende für eine Krankenstation in der Den | 500 $ | K +10, E Den +5 |
| Die Wanamingo-Mine säubern (Vanilla) | Kampf | Marion wird Schutzherr, Minen-Boom (Phase 1) |
| Gecko friedlich lösen (Vanilla) | Vanilla-Quest | E VC +10, Wohlstand +10 % |
| Den Rangers spenden | 1.000 $ | E NCR +5, Rangers-Hitze −10 |

---

## 6. Sonderquest: „Die Läuferroute“ (Broken Hills)

Deine Läufer tragen die Wochengewinne aus Redding, Vault City und der NCR ins Hauptquartier nach New Reno. Die Route führt durch **Broken Hills**, und Broken Hills gehört **Sheriff Marcus**. Je höher die Hitze, desto öfter gehen Läufer auf der Route verloren.

> **Marcus:** „Du willst mir Geld geben, damit ich wegsehe? Ich sehe nie weg. Deshalb leben hier noch Menschen und Mutanten nebeneinander.“

| Weg | Bedingung | Folge |
|---|---|---|
| **Vertrauen verdienen** | Vanilla-Quest „Find the missing people for Marcus“ gelöst **oder** Speech 70, dazu kein Slaver-Titel | Broken Hills wird Relaisstation: Läuferverluste −50 % |
| **Anständigkeit beweisen** | Guter Karma-Ruf + mindestens drei Häuser mit Moral ≥ 60 | Marcus stellt Hilfssheriffs als Eskorte: Läuferverluste −75 % |
| **Geld anbieten** | – | Er lehnt ab und merkt es sich: Alle weiteren Checks bei ihm −10 |
| **Tyrannen-Route** | Slaver-Titel oder „Der neue Metzger“ | Marcus sperrt die Stadt für deine Läufer: Umweg (+1 Woche Verzögerung, Verluste +25 %) |
| **Gewalt gegen Marcus** | – | Vanilla-Folgen, die Stadt wird feindlich, H in allen Städten +10 |

---

## 7. Weltzustand & Übergaben an die nächsten Phasen

| Ausgang | Wirkt auf | Übergabe an |
|---|---|---|
| Mara gerettet / ausgeliefert | Calloways Haltung, Karma | Phase 4 (Mara als mögliche Madame der Gosse, freiwillig), Phase 6 |
| Der neue Metzger | Den-Einnahmen, Rangers, Lizenz der Tränke | Phase 6 (Tyrannen-Epilog) |
| Lex Neun / Verbot / Diskreditierung | NCR-Nachfrage, Razzien in Vault City | Phase 6 (Westküste nach der Enklave) |
| Cat's Paw: Fusion / Druck / Verrat | Kapazität in New Reno, Miss Kitty | Phase 4 (Miss Kitty als Unique-Figur oder Feindin) |
| Salvatores Segen | Enklave-Kontakt | Phase 4 (Ereignis „Enklave-Soldaten“) |
| Die Umarmung | Jet in allen Häusern | Phase 4 (Sucht-Ereignisse), Phase 6 |
| Die Akte / Lynette erpresst | Razzien in Vault City | Phase 4 (Razzia-Ereignis), Phase 6 |
| Marcus' Vertrauen | Läuferverluste | Phase 5 (Timer und Läufer-Logik) |

Alle Zustände werden in Phase 5 als GVARs geführt: eine pro Questline für den Aktstand, dazu Bitfelder für die Enden.

---

## 8. Offene Entscheidungen (für die Freigabe von Phase 4)

1. **Die drei Questlines:** Passt die Auswahl (Mordinos & Cat's Paw, Metzger & Gilde, Liga in der NCR)? Passt vor allem Calloway als Gegenspielerin, die in vielem recht hat?
2. **„Der neue Metzger“** als dunkelstes Ende: gewünscht in dieser Konsequenz?
3. **Grave Digger** über das Grab in Golgotha: behalten?
4. **Cat's Paw:** Soll die volle Übernahme (Weg „Druck“) Miss Kitty aus dem Spiel entfernen, oder soll sie als Rivalin weiterleben und in Phase 4 zurückkehren?
5. **Mara als Verbindung** zwischen der Den und der NCR: So beibehalten?
