# Umsetzung 14 – Jobs und Läuferroute

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt und gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 74 Tests, davon 4 neu.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 5 (Bestechung, Schutzgeld, Sabotage, Gefälligkeiten) und Abschnitt 6 (Die Läuferroute)
- [Fahrplan](fahrplan.md), Schritt 14

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_jobs.h`](../scripts_src/headers/rl_jobs.h) | **neu:** Konstanten, Schmiergeld über die Wochenrechnung, Rivalen je Stadt, Gecko-Konflikt, anständige Häuser |
| [`rl_manager.h`](../scripts_src/headers/rl_manager.h) | Im Menü „Business outside these walls.“: „Work that needs doing outside.“ (Jobs) und „The runners' road through Broken Hills.“ |
| [`_rl_jobs.inc`](../text_src/english/dialog/_rl_jobs.inc) | **neu:** die Texte dazu (1000–1051), in Erzählerstimme für alle Madames |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_jobs_woche` (Tyler, Polizist, Schutzgeld), `rl_marcus_pruefen` (Sperre, Marcus tot), Umweg der Läufer, Besuch in Broken Hills, Gecko-Frieden |
| [`rljade.ssl`](../scripts_src/rotlicht/rljade.ssl) | Druck auf Kitty auch mit gestohlenen Büchern |
| [`rlhanne.ssl`](../scripts_src/rotlicht/rlhanne.ssl) | „Ein Auge am Tor“ steht jetzt unter „Business outside these walls.“ |
| [`rl_kampf.h`](../scripts_src/headers/rl_kampf.h), [`rl_ketten.h`](../scripts_src/headers/rl_ketten.h) | Nach jedem Kampf im Haus liegt ein Fall für den Totengräber vor |

---

## 2. Bestechung

| Stadt | Wer | Preis | Wirkung |
|---|---|---|---|
| The Den | Tyler | 100 $/Woche | H −5/Woche. Endet, wenn Tyler fällt (Vanilla oder „Ketten“) |
| New Reno | Totengräber von Golgotha | 300 $ einmalig, nach einem Kampf in einem eigenen Haus | H −15 in diesem Haus |
| Vault City | Torwache | 50 $/Woche | seit Umsetzung 9, bei Hanne |
| Vault City | Councilor McClure | 1.000 $, nur solange der Gecko-Konflikt offen ist | E VC +10 |
| NCR | Polizist in Downtown | 80 $/Woche | H −5/Woche |

Redding (Ascortis Lizenz), San Francisco (Wens Duldung), First Citizen Lynette (Die Akte) und Sheriff Marcus haben eigene Wege aus früheren Schritten oder aus Abschnitt 5.

Das Schmiergeld für Tyler und den Polizisten steht als Schmiergeld-Abweichung in der Wochenrechnung des Hauses, wie Venutis Gebühr.

---

## 3. Schutzgeld

- **Wo:** Die Den, Redding und die NCR, bei der Madame der Stadt.
- **Check:** Unarmed 60, ST 7 oder Speech 60.
- **Jede Woche:** 50–150 $ in die Kasse des Hauses, E +2, H +5, K −2. Die Woche zählt als Tyrannen-Woche.
- **NCR:** H +10 statt +5, weil die Rangers doppelt hinsehen.
- **Redding:** Sheriff Marion wird zum Feind. War er Schutzherr, fällt die Sicherheit um 10.
- **Aufhören:** „Leave the stalls alone.“

---

## 4. Sabotage und Gefälligkeiten

**Sabotage:** Nur gegen einen Rivalen in der Stadt des Hauses und höchstens einmal in vier Wochen.

| Stadt | Rivale |
|---|---|
| The Den | Metzger, solange er lebt und der Spieler nicht selbst der neue Metzger ist |
| New Reno | das Cat's Paw (offen oder bei den Mordinos), die Mordinos während „Blut auf der Virgin Street“ |
| Redding | der Malamute Saloon, Kittys Kralle |
| NCR | die Liga, solange ihre Kampagne läuft |
| San Francisco | die Hubologen, solange sie im Geschäft sind |

| Job | Check | Wirkung |
|---|---|---|
| Lieferung abfangen | Sneak 60 oder Kampfwert 60 | E +5, H +5 |
| Bücher stehlen | Steal 60 oder Lockpick 60 | Erpressungsmaterial, H +5 |

**Die Bücher** kann man einmal verwenden:
- bei Jade als Druck auf Kitty (statt des VIP-Trakts), oder
- für 300 $ an ihren Besitzer zurückverkaufen.

**Gefälligkeiten:**

| Gefälligkeit | Preis | Wirkung |
|---|---|---|
| Krankenstube in der Den | 500 $ | K +10, E Den +5 |
| Spende an die NCR Rangers | 1.000 $ | E NCR +5, H NCR −10 |
| Gecko friedlich gelöst (Vanilla) | – | E VC +10, einmal |
| Wanamingo-Mine (Vanilla) | – | seit Umsetzung 8: Marion wird Schutzherr |

---

## 5. Die Läuferroute

Die Läufer tragen die Wochengewinne aus Redding, Vault City und der NCR ins Hauptquartier. Die Route führt durch Broken Hills. Die Madames dieser Häuser und des Strumpfbands bieten „The runners' road through Broken Hills.“ an, sobald das Strumpfband dem Spieler gehört.

| Weg | Bedingung | Folge |
|---|---|---|
| **Vertrauen** | Vanilla-Quest „Missing people“ gelöst, **oder** Speech 70 im Gespräch (nach einem Geldangebot 80). Nie mit Slaver-Titel | Relaisstation: Läuferverluste −50 % |
| **Anständigkeit** | Karma ≥ 250 und mindestens drei eigene Häuser mit Moral ≥ 60 | Eskorte: Läuferverluste −75 % |
| **Geld anbieten** | – | Er lehnt ab und merkt es sich: Speech 80 statt 70 |
| **Tyrannen-Route** | Slaver-Titel oder der neue Metzger | gesperrt |
| **Talus** | Ausbruch, oder er sieht einen Riegel (Umsetzung 13) | gesperrt |
| **Marcus tot** | Vanilla | gesperrt, H +10 in jedem eigenen Haus |

**Gesperrt:** Die Läufer nehmen den Umweg. Das Geld aus Redding, Vault City und der NCR kommt eine Woche später in der HQ-Kasse an, und die Verlustchance steigt um ein Viertel.

**Gespräch mit Marcus:** Es setzt voraus, dass der Spieler in Broken Hills war.

---

## 6. Entscheidungen (meine Empfehlungen)

1. **Alles bei der Madame.** Tyler, der Polizist, McClure und Marcus sind Vanilla-Figuren oder namenlos. Die Madame vermittelt, der Spieler entscheidet (Fahrplan, Grundsatz 1).
2. **Marcus nur nach einem Besuch.** Das Gespräch findet abstrahiert statt, aber erst, wenn der Spieler in Broken Hills war. So bleibt die Reise Teil der Quest.
3. **Karma ≥ 250** ist in Fallout 2 der Ruf „Defender“, also die erste gute Stufe. Das nehme ich für „guter Karma-Ruf“.
4. **Der Totengräber** hilft nach jedem Kampf in einem eigenen Haus, auch außerhalb von New Reno. Seine Leute haben einen Karren.
5. **Sabotage mit Pause:** Einmal in vier Wochen, damit Einfluss nicht beliebig kaufbar ist.
6. **Schutzgeld zählt als Tyrannen-Woche.** Phase 3 nennt es „Richtung Tyrann“, und so wirkt es auf Titel und Epilog.

---

## 7. Welt-Felder

Welt 132–136:
- `RL_W_JOBS`: Bits je Job, Besuch in Broken Hills, Geldangebot an Marcus, Marcus tot
- `RL_W_JOB_WOCHE`: ab wann wieder Sabotage möglich ist
- `RL_W_ERPRESSUNG`: gestohlene Bücher
- `RL_W_GEWALT_HAUS`: Haus mit Leichen
- `RL_W_HQ_UNTERWEGS`: Geld auf dem Umweg

---

## 8. Testen im Spiel

| Test | Erwartung |
|---|---|
| Gosse, Essie: „Business outside these walls.“ → „Work that needs doing outside.“ | Tyler, Schutzgeld (mit Check), Krankenstube, Sabotage gegen Metzger |
| Tyler bezahlen, eine Woche warten | Im Bericht 100 $ mehr Kosten, Hitze sinkt |
| Strumpfband nach der Eröffnungsnacht | Roz bietet den Totengräber an |
| Broken Hills betreten, dann Roz: „The runners' road …“ | Gespräch mit Marcus möglich |

---

## 9. Nächste Schritte

Weiter mit **Schritt 15** des [Fahrplans](fahrplan.md): alle Ereignisse vollständig.
