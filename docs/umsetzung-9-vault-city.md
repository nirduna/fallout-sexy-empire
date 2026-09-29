# Umsetzung 9 – Vault City: Die Kloake

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt und gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 50 Tests, davon 7 neu für Vault City, und 157 erkundete Dialogzustände.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 2](phase-2-standorte-und-ausbau.md), Abschnitt 2.4: Kloake, Schweigegeld, Wartungstunnel, Die Akte
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 2.4: „Ein Keller im Courtyard“
- [Phase 3](phase-3-quests-rivalen-uebernahmen.md), Abschnitt 5.1: Lynette nur über Erpressung
- [Phase 4](phase-4-personal-talente-ereignisse.md): Abschnitt 2.3 (Dienstboten-Pacht) und 4.2 (Razzia in Vault City)
- [Fahrplan](fahrplan.md), Schritt 9. **Abigail Kessler** folgt mit den Talenten in Schritt 13.

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_vaultcity.h`](../scripts_src/headers/rl_vaultcity.h) | **neu:** Übernahme, Schweigegeld, Razzia mit Dienstboten-Folge, Freikaufen, Aufgeben, Dienstboten-Pacht, Figuren |
| [`rlhanne.ssl`](../scripts_src/rotlicht/rlhanne.ssl) | **neu:** Hanne Voss. Vor der Übernahme Wirtin, danach Madame (Führung 50) mit Wache, Razzia-Vorsorge, Gefassten und Lynette |
| [`rlsorens.ssl`](../scripts_src/rotlicht/rlsorens.ssl) | **neu:** Amtsleiter Sorensen. Papiere, Wache (dunkel), Freikaufen, Dienstboten-Pacht |
| [`rlvct01.ssl`](../scripts_src/rotlicht/rlvct01.ssl) | setzt Hanne und Sorensen |
| [`rl_sonder.h`](../scripts_src/headers/rl_sonder.h) | Sondermodul **Die Akte** |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_vc_woche`: Schweigegeld, Akte, angekündigte Razzia. Eine Razzia in Vault City geht nicht an die Madame, sondern direkt ins Haus. Mit Lynette gibt es keine Razzien |

---

## 2. „Ein Keller im Courtyard“

Zwei Dinge braucht der Spieler: **Hanne** und **Papiere**. Mit beidem gehört ihm die Kloake. Sie startet mit zwei Zimmern und der Preisstufe „Gehoben“, denn Vault City zahlt für Schweigen.

| Schritt | Weg | Folge |
|---|---|---|
| Hanne gewinnen | Speech 60 | Sie bekommt 10 % (Tribut +10 Punkte) |
| | 1.500 $ | Das Haus gehört dem Spieler, Hanne bleibt als Wirtin |
| Papiere | Bürgerschaft (Vanilla, auch Skeeves falsche Papiere; nicht nach dem Rauswurf) | Schweigegeld −50 $ |
| | Sorensen: Barter 40 und 500 $ | – |
| | Fälschung bei Hanne: Science 60 | H +5 |

**Schweigegeld:** 200 $ je Hausklasse und Woche. Die Bürgerschaft spart 50 $, die angeworbene Wache kostet 50 $ extra.

---

## 3. Die Razzia

Ein Razzia-Ereignis in Vault City geht nicht an die Madame. Die Garde kommt ins Haus:
- Die **Hälfte des Personals** (mindestens eine Person) kommt ins Corrections Center.
- Gepachtete Dienstboten gehen als Zeugen an die Stadt zurück (H +20).
- Die Akte wird beschlagnahmt.
- Der Keller ist eine Woche versiegelt. Dazu kommen Moral −15 und E −10.

**Danach:**

| Weg | Wo | Folge |
|---|---|---|
| Freikaufen | Sorensen | 300 $ je Person. Umsonst, wenn Sorensen erpressbar ist |
| Befreien | Hanne, Sneak 70 **und** Lockpick 70 | alle zurück, H +30 |
| Aufgeben | Hanne | Moral −30 in allen Häusern, Karma −10 |

**Frühwarnung** mit einer Wache am Tor oder bei E Vault City ≥ 60:
- Die Razzia kommt eine Woche angekündigt.
- Schließt der Spieler über Hanne den Keller für diese Woche, findet die Garde nichts. Das kostet nur die Kunden dieser Woche.

**Die Wache am Tor** gibt es auf zwei Wegen:
- über Hanne: CH 6 und 50 $/Woche
- dunkel über Sorensen: Er drängt eine Wache. Danach ist Sorensen erpressbar.

---

## 4. Die Akte

- Sondermodul für 1.000 $: E Vault City +2/Woche, einmalig H +10.
- Jede Woche wird sie mit 3 % + Hitze ÷ 10 gefunden. Dann kommt die Garde sofort, ohne Warnung.
- **Lynette:** Mit der Akte kann Hanne drei Seiten an die First Citizen schicken. Die Razzien in Vault City enden für immer, dazu E +20 und H +20. Lynette ist unbestechlich (Phase 3, 5.1); das hier ist Erpressung.

---

## 5. Dienstboten-Pacht (Tyrannen-Quelle)

- Sorensen verpachtet Menschen aus dem Servant Allocation Center: 50 $/Woche je Person, nur mit freiem Zimmer.
- Sie zählen als Zwangspersonal: Karma −5/Woche, Moral-Deckel 50, Mara geht.
- Bei einer Razzia gehen sie als Zeugen zurück.
- Sorensen nimmt sie jederzeit zurück.

---

## 6. Entscheidungen (meine Empfehlungen)

1. **Hanne ist Wirtin und Madame zugleich.** Die Pension oben ist die Tarnung, sie führt beides. Eine eigene Madame im Keller würde die Tarnung schwächen.
2. **Sorensen ist Figur im Keller.** Er ist der Stammkunde aus Phase 3 und die Tür zur Bürokratie: Papiere, Wache, Freikauf, Pacht.
3. **Die Razzia trifft das Haus direkt.** Phase 4 nennt sie den schwersten Verlust im Spiel. Eine Madame, die sie „mit ihrer Führung löst“, passt nicht dazu.
4. **Die Hälfte des Personals** wird gefasst, mindestens eine Person. Das ist hart, aber umkehrbar: Freikaufen ist bezahlbar, und die Frühwarnung hilft.
5. **Die gepachteten Dienstboten** sind Zwangspersonal im Sinne von Phase 4 und zählen für die Tyrannen-Route.
6. **McClures Spende** (Phase 3, 5.1) und **Abigail Kessler** folgen in den Schritten 14 und 13.

---

## 7. Welt-Felder

Welt 83–90: Hanne, Papiere, Wache, Sorensen (Bits: erpressbar, tot, kennt den Spieler), Gefasste, angekündigte Razzia, Lynette, Hanne tot.

---

## 8. Testen im Spiel

| Test | Erwartung |
|---|---|
| Die Kloake betreten (Courtyard, Kellertreppe hinter Cassidy's) | Hanne und Sorensen im Gewölbe |
| Hanne: „I'll buy the house“, Sorensen: [Barter] 500 $ | Übernahme. Hanne übergibt den Schlüssel |
| Hanne: „We need an eye at the gate“ mit CH 6 | Die Wache kostet 50 $/Woche |
| Warten, bis eine Razzia kommt | mit Wache: „A guard at the gate says …“. Keller schließen: „found clean sheets and a locked, empty cellar“ |
| ohne Wache | „The Garde came down the cellar stairs …“. Bei Sorensen freikaufen |
| Ausbau → „Something you only get in Vault City“ → Die Akte | E steigt jede Woche. Hanne bietet „Use the File“ an |

**Nicht im Prüfwerkzeug sichtbar:** Sorensen nutzt das Vault-Bürger-Proto (`PID_MALE_VAULT_CITIZEN`). Ob Grafik und Team im Courtyard passen, zeigt erst das Spiel.

---

## 9. Nächste Schritte

Weiter mit **Schritt 10** des [Fahrplans](fahrplan.md): NCR, Die Tränke und „Die Reinen“.
