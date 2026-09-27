# Phase 5 – Technische Umsetzung (sfall & Scripting)

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:** Freigegeben (siehe Entscheidungen unten). Weiter in [Phase 6](phase-6-karma-ruf-endings.md).

> **Freigabe-Entscheidungen**
> 1. Speicherung in sfall-Arrays, echte GVARs nur dort, wo die Engine sie verlangt (Endslides; siehe Phase 6 für die Titel im Charakterbogen).
> 2. **Zielinstallation ist das Restoration Project (RPU).** Build-Standard ist jetzt RPU (`RL_SCRIPT_BASE` 1559). Alle Vanilla-Anknüpfungen sind gegen die RPU-Header geprüft, und der Code kompiliert gegen sie.
> 3. Der Wochentakt läuft nur auf lokalen Karten, mit Nachrechnung bei Ankunft.
> 4. Erst Phase 6 abschließen, dann Prolog „Essies Schulden“ und Ausbau-Dialog programmieren.
**Grundlage:** [Phase 1](phase-1-core-loop-und-wirtschaft.md) bis [Phase 4](phase-4-personal-talente-ereignisse.md) sind freigegeben.

Diese Phase liefert nicht nur ein Konzept, sondern **echten, kompilierbaren Code**:

| Datei | Inhalt |
|---|---|
| [`scripts_src/headers/rotlicht.h`](../scripts_src/headers/rotlicht.h) | Speicherlayout, Tabellen, Wochenrechnung eines Hauses |
| [`scripts_src/global/gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | globales Skript: Wochentakt, Vanilla-Anknüpfungen, Läufer, Ereignisse, Selbsttest |
| [`scripts_src/rotlicht/rlessie.ssl`](../scripts_src/rotlicht/rlessie.ssl) | Manager-Dialog: Essie in der Gosse, mit Auszahlung |
| [`text_src/german/dialog/rlessie.msg`](../text_src/german/dialog/rlessie.msg) | Essies Dialogtexte |
| [`tools/build_scripts.sh`](../tools/build_scripts.sh) | Build mit `sslc` und Text-Konvertierung |
| [`install/scripts.lst.add`](../install/scripts.lst.add) | Zeile für die `scripts.lst` der Zielinstallation |

**Stand:** Alle Skripte kompilieren mit sslc 4.5.1 (sfall edition) ohne Fehler und ohne Warnungen, sowohl gegen die Header des Restoration Project (RPU, Standard) als auch gegen die des Unofficial Patch. **Im Spiel ausgeführt wurden sie noch nicht**, weil hier keine Spieldaten vorliegen. Der Selbsttest in Abschnitt 10 ist genau dafür gebaut.

---

## 1. Architektur

```
            Vanilla-Welt (nur lesen)                       Spieler
   metzger_dead, GVAR_REDDING_JET_LEVEL, ...                  │
                    │                                         │ Dialog
                    ▼                                         ▼
 ┌─────────────────────────────────┐         ┌───────────────────────────────┐
 │ gl_rotlicht.int (globales Skript)│         │ Manager-Skripte (rlessie ...)  │
 │ • Wochentakt + Nachrechnung      │         │ • Bericht, Auszahlung          │
 │ • Stadt-Modifikatoren            │         │ • Preise, Anteil               │
 │ • Läufer ins Hauptquartier       │         │ • Krisen lösen                 │
 │ • Ereigniswurf                   │         └───────────────┬───────────────┘
 └────────────────┬────────────────┘                         │
                  │ lesen/schreiben                          │ lesen/schreiben
                  ▼                                          ▼
        ┌─────────────────────────────────────────────────────────────┐
        │ sfall-Arrays im Spielstand: "RL_HAUS" (7 × 32) · "RL_WELT" (32) │
        └─────────────────────────────────────────────────────────────┘
```

**Grundsätze**

1. **Ein Ort für den Zustand.** Alles, was das Addon sich merkt, steht in zwei gespeicherten sfall-Arrays. Kein Skript hält eigenen Wirtschaftszustand.
2. **Die Vanilla-Welt wird nur gelesen.** Das Addon ändert keine Vanilla-Variable außer dem Karma (`GVAR_PLAYER_REPUTATION`).
3. **Die Rechnung steht einmal.** `rl_rechne_woche` in `rotlicht.h` ist die einzige Implementierung der Wochenrechnung. Sie ist Zeile für Zeile identisch mit `tools/economy_sim.py`.

---

## 2. Speicherung: sfall-Arrays statt neuer GVARs

Klassisch würde man 200 neue GVARs an `vault13.gam` anhängen. Das ist fehleranfällig: Unofficial Patch und Restoration Project hängen selbst Variablen an, und jeder Index, den wir belegen, kann mit einer anderen Mod kollidieren. Deshalb:

- **`RL_HAUS`**: ein Array mit 7 × 32 Ganzzahlen (sechs Häuser plus ein Testhaus).
- **`RL_WELT`**: ein Array mit 32 Ganzzahlen für den Zustand, der nicht an einem Haus hängt.
- Beide werden mit `save_array` markiert und von sfall im Spielstand gesichert (`sfallgv.sav`). Beim ersten Zugriff legt `rl_lade_haeuser` bzw. `rl_lade_welt` sie an. Das Addon lässt sich deshalb **auch in einen laufenden Spielstand** installieren.
- **Ausnahme für Phase 6:** Die Endslides liest die Engine aus `data/endgame.txt`, und diese Datei kann nur echte GVARs abfragen (Format `gvar, value, art, narrator`). Für den Epilog brauchen wir deshalb **zwei echte GVARs** in `vault13.gam`, eine für das Imperium und eine für den Ton des Endes. Mehr nicht.

### 2.1 Felder pro Haus (`RL_HAUS`, Index = Haus × 32 + Feld)

| # | Name | Bereich | Bedeutung | Geschrieben von |
|---|---|---|---|---|
| 0 | `RL_F_BESITZ` | 0/1 | Haus gehört dem Spieler | Übernahme-Quest (`rl_haus_uebernehmen`) |
| 1 | `RL_F_KLASSE` | 1–3 | Hausklasse | Ausbau |
| 2 | `RL_F_ZIMMER` | 2–9 | Zimmer | Ausbau |
| 3 | `RL_F_PERSONAL` | 0–9 | Arbeitende (ein Zimmer braucht eine Person) | Anwerben, Flucht |
| 4 | `RL_F_QUALI` | 20–85 | Grundqualität des Personals | Tick, Anwerben |
| 5 | `RL_F_MORAL` | 0–100 | Moral | Tick, Dialoge, Ereignisse |
| 6 | `RL_F_RUF` | 0–100 | Hausruf | Tick, Ereignisse |
| 7 | `RL_F_AUSSTATTUNG` | 0–100 | Ausstattung | Ausbau |
| 8 | `RL_F_SICHERHEIT` | 0–150 | Sicherheit | Ausbau, Rausschmeißer |
| 9 | `RL_F_HITZE` | 0–100 | Hitze (−5 pro Woche) | Tick, Quests |
| 10 | `RL_F_EINFLUSS` | 0–100 | Einfluss in der Stadt | Quests, Jobs |
| 11 | `RL_F_PREISSTUFE` | 0–3 | Ramsch, Standard, Gehoben, Exklusiv | Manager-Dialog |
| 12 | `RL_F_ANTEIL` | 0–2 | ausbeuterisch, branchenüblich, fair | Manager-Dialog |
| 13 | `RL_F_BAR` | 0–2 | Bar-Stufe | Ausbau |
| 14 | `RL_F_NEBEN` | $ | zusätzlicher Nebenumsatz je Kunde (Spieltische …) | Ausbau, Unique-Figuren |
| 15 | `RL_F_MODULE` | Bitmaske | Kontor, Krankenstube, VIP, Jet-Theke, Riegel außen, Akte, Leine | Ausbau, Dialog |
| 16 | `RL_F_STUFEN` | Anzahl | Summe aller Modulstufen (Unterhalt 25 $ je Stufe) | Ausbau |
| 17 | `RL_F_LOEHNE` | $/Woche | Fixlöhne | Personal |
| 18 | `RL_F_MORALBONUS` | 0–3 | Quartiere, Riegel innen … | Ausbau |
| 19 | `RL_F_STADTMOD` | % | Kunden-Modifikator der Stadt | Tick (aus der Vanilla-Welt) |
| 20 | `RL_F_TRIBUTMOD` | %-Punkte | Abweichung vom Basis-Tribut | Quests (z. B. Siegel der Shi −5) |
| 21 | `RL_F_KASSE` | $ | Bargeld im Haus | Tick, Läufer, Auszahlung |
| 22 | `RL_F_GEWINN` | $ | Gewinn der letzten Woche | Tick |
| 23 | `RL_F_KUNDEN` | Anzahl | Kunden der letzten Woche | Tick |
| 24 | `RL_F_KRISE` | Ereignis-ID | offene Krise | Tick, Dialog |
| 25 | `RL_F_KRISENWOCHEN` | 0–n | Wochen ohne Lösung | Tick |
| 26 | `RL_F_FUEHRUNG` | 0–100 | Führung der Madame (CH × 5 + Speech ÷ 4) | Personal |
| 27 | `RL_F_ZWANG` | 0/1 | Zwangspersonal im Haus | Tyrannen-Route |
| 28–30 | – | – | frei für Phase 6 | – |
| 31 | `RL_F_ZUSTAND_TEST` | – | nur Selbsttest | – |

### 2.2 Welt-Felder (`RL_WELT`)

| # | Name | Bedeutung |
|---|---|---|
| 0 | `RL_W_WOCHE` | zuletzt abgerechnete Woche |
| 1 | `RL_W_AKTIV` | 1, sobald das erste Haus übernommen ist |
| 2 | `RL_W_HQ_KASSE` | Geld, das die Läufer ins Strumpfband gebracht haben |
| 3 | `RL_W_MARCUS` | Läuferroute: kein Vertrauen, Relais (−50 %), Eskorte (−75 %), gesperrt (+25 %) |
| 4 | `RL_W_LIGA` | Stand der Liga in der NCR (Kampagne, gebremst, Gegenkampagne, Lex Neun, Verbot) |
| 5 | `RL_W_CATSPAW` | Cat's Paw: offen, Bündnis, gelöst |
| 6 | `RL_W_MALAMUTE` | Malamute Saloon: offen, gelöst |
| 7 | `RL_W_HUBOLOGEN` | Hubologen: offen, gelöst, unterwandert |
| 8 | `RL_W_KITTY_RIVALIN` | 1 = „Kittys Kralle“ in Redding |
| 9–11 | `RL_W_KETTEN`, `RL_W_VIRGIN`, `RL_W_REINE` | Aktstände der drei Questlines |
| 12–31 | – | frei (Unique-Loyalitäten, Titel, Phase 6) |

---

## 3. Anknüpfungen an die Vanilla-Welt (gegen die Original-Skripte geprüft)

Geprüft gegen die Skriptquellen des Restoration Project (RPU) und des Unofficial Patch. Alle Namen existieren in beiden. Ein Wert unterscheidet sich: `MISSING_FINISHED_CASH` ist im RPU 9, im Unofficial Patch 7. Der Code verwendet den Namen, nicht die Zahl, und passt deshalb automatisch.

| Zweck (Phase) | Abfrage | Quelle | Wirkung im Addon |
|---|---|---|---|
| Metzger tot (1, 3) | `metzger_dead` | `den.h` | Den: +20 % Kunden, solange die Gilde lebt, −25 % danach |
| Big Jesus Mordino tot (1, 3) | `gvar_bit(GVAR_NEW_RENO_FLAG_2, bit_26)` | aus `newreno.h` übernommen | Redding: Jet-Knappheit +10 % |
| Jet-Antidot in Redding (1) | `GVAR_REDDING_JET_LEVEL` ist `JET_ON_CURE` oder `JET_CURED` | `global.h` | Redding: +25 % |
| Wanamingo-Mine gesäubert (1) | `GVAR_WANAMINGO_OCCUPADO == WANAMINGO_CLEARED_OUT` | `global.h` | Redding: +30 % |
| Gecko friedlich gelöst (1) | `GVAR_VAULT_GECKO_PLANT` ist `PLANT_REPAIRED` oder ≥ `PLANT_FIXED_PLUS_KNOWN` | `global.h`, geprüft in `vcmclure.ssl` | Vault City: +10 % |
| Marcus' Vermisstenfall gelöst (3) | `GVAR_BH_MISSING >= MISSING_FINISHED_CASH` | `global.h`, geprüft in `hcphil.ssl` | Läuferroute: Relais (−50 % Verluste) |
| Enklave zerstört (1, 4) | `Fallout2_enclave_destroyed` | `command.h` | alle Städte +10 %, Enklave-Soldaten dreimal so häufig |
| Karma (1–4) | `GVAR_PLAYER_REPUTATION` | `global.h` | Ausbeutung −1/Woche, Zwangspersonal −5/Woche |

**Für die Quest-Skripte vorgemerkt** (Phase 3/4, noch nicht im Code):

| Zweck | Abfrage |
|---|---|
| Slaver-Titel | `GVAR_REPUTATION_SLAVER` |
| Made Man (allgemein / je Familie) | `GVAR_NEW_RENO_MADE_MAN`, `GVAR_MADE_MAN_SALVATORE` / `_BISHOP` / `_MORDINO` / `_WRIGHT` |
| Porn Star, Prizefighter | `GVAR_NEW_RENO_PORN_STAR`, `GVAR_NEW_RENO_PRIZEFIGHTER` |
| Grave Digger (Golgotha) | `GVAR_GRAVES_UNEARTHED` |
| Bürgerschaft Vault City | `GVAR_VAULT_CITIZEN` |
| Vortis, Rangers | `GVAR_NCR_VORTIS_QUEST_STATE`, `GVAR_NCR_RANGERS_KNOWN`, `GVAR_NCR_PLAYER_RANGER` |
| Marcus tot | `GVAR_MARCUS_DEAD` |
| Myrons Jet-Antidot | `jet_source` ≥ `jet_source_cure_made` (`GVAR_NEW_RENO_JET_SOURCE`) |
| Salvatores Übergabe (Segen) | `GVAR_NEW_RENO_SALVATORE_RESPECT` |
| Anteil der Malamute-Mädchen (Vanilla) | `GVAR_REDDING_WHORE_CUT`, relevant für die Übernahme des Malamute |

---

## 4. Zeit und Wochentakt

- **Global script:** sfall lädt `gl_rotlicht.int` beim Spielstart. In `start` setzt es bei `game_loaded` den Takt (`set_global_script_repeat(600)`, etwa alle 10 Sekunden) und lädt die Arrays neu. Array-IDs können sich beim Laden ändern, darum merkt sich kein Skript eine ID über das Laden hinweg.
- **Wochenzähler:** `game_time_in_seconds / 604800`.
  - Nicht `game_time`: Das zählt in Zehntelsekunden und kann als 32-Bit-Zahl nach etwa 6,8 Spieljahren das Vorzeichen wechseln. Das Zeitlimit von Fallout 2 liegt bei 13 Jahren.
- **Nachrechnung:** Stehen seit der letzten Abrechnung *n* Wochen aus, rechnet der Tick *n* Wochen nacheinander, höchstens 12 (Phase 1). Der Tick läuft nur auf lokalen Karten. Reisen auf der Weltkarte werden bei der Ankunft nachgeholt.
- **Reihenfolge pro Woche:**
  1. Stadt-Modifikatoren aus der Vanilla-Welt (einmal pro Tick).
  2. Für jedes eigene Haus die Wochenrechnung. Der Gewinn kommt in die Kasse des Hauses.
  3. Offene Krise: Wochenzähler hoch, nach drei Wochen Eskalation (Moral −10, Hausruf −10).
  4. Ohne Krise: Ereigniswurf.
  5. Läufer bringen die Kassen ins Hauptquartier.

---

## 5. Die Wochenrechnung in SSL

`rl_rechne_woche(haus, h, stadt)` setzt Phase 1 und 2 vollständig um: Attraktivität, Preisstufe mit Kaufkraft, Sicherheit gegen Bedrohung, Kapazität (Zimmer und Personal), Krise, Umsatz, alle Kostenarten, VIP-Trakt, Moral mit Obergrenze, Hausruf, Talent-Zulauf und Karma.

**Zwei Fallstricke der 32-Bit-Ganzzahlen und wie der Code sie löst:**

1. **Überlauf.**
   - *Problem:* Das Produkt `Kunden × Attraktivität × Nachfrage × Sicherheit × Stadt` erreicht bis zu 2 · 10¹⁰.
   - *Lösung:* Der Code teilt nach jedem Faktor durch 100, behält aber zwei Nachkommastellen bis zum Schluss. Die Zwischenwerte bleiben unter 3 Mio., und das Ergebnis ist identisch mit der Rechnung am Stück.
2. **Rundung.**
   - *Problem:* SSL schneidet bei der Division Richtung null ab, Python rundet ab. Beim Hausruf (`(Score − Ruf) ÷ 8`) wird der Zähler negativ, und dann unterscheiden sich die beiden.
   - *Lösung:* `rl_fdiv` rundet wie Python.

Damit bleiben alle Zahlen aus den Phasen 1–4 unverändert gültig. Der Simulator wurde angepasst und liefert dieselben Tabellen wie vorher.

---

## 6. Ereignisse technisch

- **Wurf pro Haus und Woche** (Phase 4, 4.1):

  ```
  Chance = 10 + Hitze ÷ 5 + max(0, Bedrohung − Sicherheit) ÷ 2
         + 10 bei Moral < 40 + 10 bei Zwangspersonal       (höchstens 60 %)
  ```

- **Gewichtete Auswahl** (`rl_ereignis_waehlen`):

  | Ereignis | Grundgewicht | Zu- und Abschläge |
  |---|---|---|
  | Soldaten | 3 | nach dem Fall der Enklave 9 |
  | Stoff | 10 | Jet-Flut in Redding ×2, Jet-Theke ×2, Moral < 40 ×1,5 |
  | Razzia | 5 + Risiko × 3 + Hitze ÷ 2 | – |
  | Freier | 5 | bei zu wenig Sicherheit 15 |
  | Seuche | 8 | 0 mit Krankenstube |
  | Kasse | 3 | bei Moral < 40 10 |
  | Flucht | 0 | bei Moral < 25 oder Zwangspersonal 20 |

- **Die Madame zuerst:** Mit der Chance ihrer Führung regelt sie das Ereignis selbst. Das kostet wenig: Moral −2, eine Person weniger, Hausruf −2 oder 100 $. Eine Meldung erscheint im Nachrichtenfenster.
- **Sonst Krise:** `RL_F_KRISE` wird gesetzt, das Haus verliert 20 % Kunden pro Woche (höchstens 60 %), und der Manager-Dialog bietet die Lösungen an.
- **Stadtspezifische Folgen** hängen an den Lösungsknoten der Manager- und Quest-Skripte, nicht am Tick. Dazu gehört die Dienstboten-Folge der Razzia in Vault City. So bleibt der Tick schlank und testbar.

---

## 7. Läufer

- Sobald das Strumpfband dem Spieler gehört, tragen Läufer jede Woche die Kassen aller anderen Häuser dorthin (`RL_W_HQ_KASSE`).
- **Verlustchance** = Hitze des Hauses ÷ 4 (höchstens 25 %). Für Redding, Vault City und die NCR (Route durch Broken Hills) wird sie mit Marcus' Faktor multipliziert: 100 / 50 / 25 / 125 %.
- Löst der Spieler Marcus' Vanilla-Quest, stellt der Tick die Route selbst auf „Relais“.
- Solange es kein Hauptquartier gibt, bleibt das Geld in der Kasse des Hauses und wird beim Manager abgeholt. Wer vor dem Wochenwechsel vor Ort abholt, spart sich das Läufer-Risiko (Phase 1).

---

## 8. Der Manager-Dialog (Beispiel Essie)

Das angefragte Beispiel aus dem Auftrag. `rlessie.ssl` zeigt den Wochenbericht und zahlt die Kasse aus. Außerdem kann man dort Preise und Anteil einstellen, nach der Moral fragen und die Krise „Der Stoff“ mit einem Doctor-Check lösen.

```c
procedure Node001 begin
   Reply(mstr(100) + " " + mstr(101) + haus[rl_idx(h, RL_F_KUNDEN)]
         + mstr(102) + haus[rl_idx(h, RL_F_GEWINN)]
         + mstr(103) + haus[rl_idx(h, RL_F_KASSE)] + mstr(104));

   if (haus[rl_idx(h, RL_F_KASSE)] > 0) then
      NOption(110, Node010, 004);          // "Gib mir, was in der Kasse ist."
   NOption(111, Node020, 004);             // Preise
   NOption(112, Node030, 004);             // Personal-Anteil
   NOption(113, Node040, 004);             // Moral
   if (haus[rl_idx(h, RL_F_KRISE)] != RL_EV_KEINS) then
      NOption(114, Node050, 004);          // Krise
   NOption(115, Node999, 004);
   NLowOption(116, Node010);               // "Geld?"
end

procedure Node010 begin
   variable betrag := haus[rl_idx(h, RL_F_KASSE)];
   if (betrag > 0) then begin
      item_caps_adjust(dude_obj, betrag);
      haus[rl_idx(h, RL_F_KASSE)] := 0;
      Reply(mstr(120) + betrag + mstr(121));   // "Hier. 412 $. Zähl nach, wenn du willst. ..."
   end else begin
      Reply(122);                              // "Da ist nichts. ..."
   end
   NOption(123, Node001, 004);
   NOption(124, Node999, 004);
   NLowOption(124, Node999);
end
```

**Weitere Details**
- **Texte:** Sie liegen in `text_src/german/dialog/rlessie.msg` als UTF-8. Der Build wandelt sie standardmäßig nach Windows-1252 um: Die Engine und sfall lesen Textdateien byteweise ohne Umwandlung, und die deutsche Fallout-2-Schrift erwartet Windows-1252.
- **Achtung beim RPU:** Die deutschen Texte liegen im RPU-Repository als UTF-8 vor. Welche Kodierung deine installierte deutsche RPU-Übersetzung tatsächlich nutzt, lässt sich nur im Spiel sicher prüfen. Zeigt Essie die Umlaute falsch an, baust du mit `TEXT_ENCODING=UTF-8`.
- **Skriptindex:** Die Datei wird über den Skriptindex (`NAME = SCRIPT_RLESSIE`) gefunden.
- **Moral im Dialog:** Die Wahl des Anteils kommentiert Essie im Ton aus Phase 1 bis 4. Die Tyrannen-Option „Jet statt Lohn“ setzt dauerhaft das Flag `RL_MOD_LEINE`: Die Moral des Hauses bleibt höchstens bei 40, und es kostet 3 Karma pro Woche (Phase 4).

---

## 9. Maps, Installation und Kompatibilität

- **Skriptindizes:** Einträge in `scripts.lst` werden ab 1 gezählt. `RL_SCRIPT_BASE` ist die Zeilenzahl der `scripts.lst` der Zielinstallation plus 1.
  - **Restoration Project (RPU): 1558 Zeilen, also 1559** (Standard im Build).
  - Unofficial Patch: 1308 Zeilen, also 1309 (mit `RL_SCRIPT_BASE=1309` bauen).
  - Die Zeilen zum Anhängen stehen in `install/scripts.lst.add`.
- **Globale Skripte** (`gl_*.int`) brauchen keinen Eintrag in `scripts.lst`.
- **Maps (Umsetzung von Phase 2, Abschnitt 6):**
  - Pro Haus ein Tür-Skript auf der Vanilla-Map. Es bleibt verschlossen, solange `RL_F_BESITZ = 0`.
  - Eine eigene Innen-Map (`RLDEN01` …) mit Map-Skript. Das schaltet in `map_enter_p_proc` Platzhalter und Ausbau-Objekte nach `RL_F_MODULE` und `RL_F_KLASSE` um.
  - Der Stadtkarten-Eintrag wird per `mark_area_known` nach der Übernahme freigeschaltet.
- **Voraussetzungen:** sfall 4.x (gespeicherte Arrays, `set_global_script_repeat`, temporäre Arrays, String-Verkettung). Grundlage ist das Restoration Project (RPU), gegen dessen Header der Code gebaut wird. Der Unofficial Patch wird ebenfalls unterstützt, dafür genügt ein eigener Build mit `RL_SCRIPT_BASE=1309`.
- **Spielstände:** Die Arrays entstehen beim ersten Zugriff. Das Addon kann in laufende Spiele installiert werden. Wird es deinstalliert, bleiben zwei ungenutzte Arrays im Spielstand, ohne Wirkung.

---

## 10. Bauen und Testen

### 10.1 Compiler bauen (Linux)

```bash
git clone https://github.com/sfall-team/sslc.git
cd sslc && mkdir build && cd build
sudo apt-get install gcc-multilib      # sslc wird als 32-Bit-Programm gebaut
cmake .. && make                       # Ergebnis: build/bin/sslc
```

Unter Windows gibt es `sslc.exe` fertig im sfall-Modderpaket.

### 10.2 Header besorgen

```bash
git clone --depth 1 https://github.com/BGforgeNet/Fallout2_Restoration_Project.git rpu
git clone --depth 1 https://github.com/sfall-team/sfall.git sfall
ln -s "$PWD/sfall/artifacts/scripting/headers" rpu/scripts_src/sfall   # define.h erwartet ../sfall/sfall.h
```

### 10.3 Bauen

```bash
SSLC=/pfad/sslc/build/bin/sslc FO2_SCRIPTS_SRC=/pfad/rpu/scripts_src tools/build_scripts.sh
# Ergebnis: build/scripts/gl_rotlicht.int, build/scripts/rlessie.int, build/text/german/dialog/rlessie.msg
```

Zusätzliche Schalter (Umgebungsvariablen):
- `RL_SELBSTTEST=1` baut den Selbsttest ein (10.4).
- `RL_DEBUG=1` baut Debug-Optionen ein: Essie bietet dann „[Debug] Die Gosse übernehmen“ an, damit man ohne Prolog testen kann.
- `RL_SCRIPT_BASE=...` setzt den Skriptindex für eine andere Grundinstallation (Abschnitt 9).
- `RL_GVAR_BASE=...` setzt die erste neue GVAR (RPU 791, Unofficial Patch 696; siehe Phase 6).
- `TEXT_ENCODING=...` setzt die Kodierung der Texte (Standard `WINDOWS-1252`, siehe Abschnitt 8).

**Wichtig:** `sslc` wertet nur **einen** `-m`-Schalter und nur **einen** `-I`-Pfad aus. Deshalb gibt das Build-Skript keine `-m`-Schalter weiter. Es kompiliert eine Kopie von `scripts_src` und schreibt alle Einstellungen in deren `config/rl_build.h`. Beim Kompilieren von Hand gilt `scripts_src/config/rl_build.h` mit den RPU-Standardwerten.

**Stand dieser Phase:** Alle Ausgaben bauen fehlerfrei. *Korrektur (Phase 6):* In der ersten Fassung dieses Build-Skripts wirkte bei kombinierten Schaltern nur der letzte. Das ist behoben und am Kompilat geprüft (siehe Phase 6, Abschnitt 5.5).

### 10.4 Selbsttest im Spiel

1. Mit `RL_SELBSTTEST=1` bauen und `gl_rotlicht.int` nach `data/scripts/` kopieren.
2. In der `ddraw.ini` von sfall im Abschnitt `[Debugging]` den Debugmodus mit Ausgabe in eine Datei einschalten (`DebugMode=2`). Die Ausgabe von `debug_msg` landet dann in `debug.log`.
3. Einen Spielstand laden. Das Skript rechnet das Beispielhaus aus Phase 1 dreißig Wochen lang mit allen drei Anteilsstufen und schreibt 90 Zeilen `RLTEST <Anteil> W<Woche> <Gewinn>`.
4. Mit den Soll-Werten vergleichen:

   ```bash
   python3 tools/economy_sim.py --vektoren > soll.txt
   grep RLTEST debug.log | diff - soll.txt      # muss leer bleiben
   ```

   Erste Soll-Werte: `RLTEST 0 W1 634`, `RLTEST 1 W1 442`, `RLTEST 2 W1 249` (die Werte aus Phase 1, Abschnitt 3.8).

### 10.5 Manuelle Prüfliste

| Test | Erwartung |
|---|---|
| Mit `RL_DEBUG=1` gebaut: bei Essie „[Debug] Die Gosse übernehmen“, dann 7 Tage warten | Essie meldet Kunden, Gewinn und Kasse der Woche |
| Auszahlung | Geld im Inventar steigt um den Kassenstand, Kasse 0 |
| 3 Wochen auf der Weltkarte reisen | bei Ankunft drei Wochen nachgerechnet |
| Anteil auf „ausbeuterisch“, 8 Wochen warten | Moral fällt um 4 pro Woche, Karma −1 pro Woche |
| Metzger töten (Vanilla) | Den-Kunden sinken beim nächsten Tick (Stadtmodifikator −25) |
| Krise „Stoff“ mit Doctor 60 lösen | Krise weg, Moral +5 |
| Spielstand speichern und laden | alle Werte bleiben erhalten |

---

## 11. Nächste Schritte der Umsetzung

1. Prolog „Essies Schulden“ in `rlessie.ssl` (Phase 1/3) mit den fünf Lösungswegen und `rl_haus_uebernehmen`.
2. Ausbau-Dialog: Module kaufen, Bauzeit, `RL_F_MODULE`/`RL_F_STUFEN` setzen (Katalog aus Phase 2).
3. Innen-Map `RLDEN01` mit Map-Skript für sichtbare Ausbauten.
4. Consigliere im Strumpfband mit Auszahlung der HQ-Kasse und den Familientreffen.
5. Die übrigen fünf Manager und die Lösungsknoten aller Ereignisse aus Phase 4.
6. Texte des globalen Skripts in eine eigene `.msg` verschieben (sie stehen jetzt ohne Umlaute im Code).

---

## 12. Offene Entscheidungen (für die Freigabe von Phase 6)

1. **Speicherung in sfall-Arrays** statt neuer GVARs, mit genau zwei echten GVARs für die Endslides: einverstanden?
2. **Grundlage Unofficial Patch** (Build-Standard), mit dem Restoration Project als zweitem Ziel: passt das zu deiner Installation?
3. **Takt:** Soll die Wochenabrechnung auch auf der Weltkarte laufen (sofortige Läufer-Meldungen unterwegs), oder reicht die Nachrechnung bei Ankunft (aktuell, weniger Last)?
4. **Nächster Schritt:** Soll ich parallel zu Phase 6 schon den Prolog „Essies Schulden“ und den Ausbau-Dialog umsetzen, oder erst das Konzept mit Phase 6 abschließen?
