# Prüfwerkzeug: die Skripte ohne das Spiel testen

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2

Im Spiel kann ich nicht testen. Deshalb gibt es zwei Werkzeuge, die die **kompilierten** Skripte (`.int`) in Python ausführen:

| Datei | Inhalt |
|---|---|
| [`tools/intvm.py`](../tools/intvm.py) | Interpreter für `.int`-Dateien und eine kleine Nachbildung der Spielwelt |
| [`tools/test_skripte.py`](../tools/test_skripte.py) | Testszenarien und die Erkundung aller Dialogpfade |

---

## 1. Was nachgebildet ist

**Der Interpreter** folgt dem Quelltext von fallout2-ce (`interpreter.cc`, `interpreter_extra.cc`, `sfall_opcodes.cc`, `sfall_arrays.cc`, `game_dialog.cc`):
- Stapel, Rücksprungstapel und Prozeduraufrufe wie in der Engine
- Rechenregeln der Engine:
  - Addition mit Überlauf wird zur Gleitkommazahl.
  - Division und Modulo durch null brechen das Skript ab.
  - `and`/`or` werten beide Seiten aus.
- **sfall-Arrays:**
  - Listen und assoziative Arrays, `temp_array` wird nach jedem Aufruf freigegeben.
  - Array-Ausdrücke wie `[1, 2, 3]`.
  - `save_array`/`load_array`.
- **Dialoge wie im Spiel:**
  - `gsay_end` startet die Schleife.
  - Die gewählte Option ruft ihre Prozedur.
  - Setzt die Prozedur keine neue Option, endet der Dialog.
  - Optionen mit IQ-Grenze (`NLowOption` usw.) erscheinen nur bei passender Intelligenz.

**Die Spielwelt:**
- globale, lokale und Karten-Variablen
- Objekte mit Skripten (`create_object_sid`, `destroy_object` mit `destroy_p_proc`)
- Kronkorken, Fertigkeiten, Werte
- Spielzeit, Karte, Kartenwechsel
- Meldungsdateien aus dem Build, Zufall (fest oder mit Startwert)

**Nicht nachgebildet** sind Grafik, Kampf, Wegfindung und Animationen. Befehle wie `attack_setup` oder `gfade_out` werden nur protokolliert.

---

## 2. Was geprüft wird

Nach jedem Test laufen allgemeine Prüfungen:

| Prüfung | Im Spiel wäre das … |
|---|---|
| kein Skriptfehler | Absturz des Skripts (Division durch null, falscher Typ, Endlosschleife) |
| kein fehlender Text | „Error“ im Dialog oder in der Meldungszeile |
| keine Antwort ohne Option | Text, der nie angezeigt wird, weil der Dialog vorher endet |
| kein Array-Zugriff außerhalb der Grenzen | still falsche Werte (0) |

**Szenarien:**

| Test | Inhalt |
|---|---|
| `test_wirtschaft_paritaet` | Die kompilierte Wochenrechnung gegen `tools/economy_sim.py`: 400 zufällige Häuser (alle Städte, Preise, Anteile, Module, Anwerbung, Zwangspersonal) über je 10 Wochen. Kunden, Gewinn und Karma müssen auf den Dollar gleich sein |
| `test_erkundung` | Alle Dialogpfade von Essie und Kolbe aus 16 Spielständen (neu, Prolog, jeder Prolog-Weg, Pferch, jede Krise, pleite). Jede Antwort mit ihren Optionen wird einmal erreicht, jede Option einmal gewählt |
| `test_eingang` | Kellertreppe auf Den Business 2: einmalig gesetzt, führt nur den Spieler und nur außerhalb des Kampfs in die Gosse |
| `test_prolog_wege` | alle sechs Wege des Prologs, mit Kosten und Essies Reaktion |
| `test_diebstahl_erwischt` | Metzger wird Feind, Kolbe greift an |
| `test_ketten_*`, `test_kolbe_*` | Akt 1: annehmen, ablehnen, zu wenig Geld, Kolbe stirbt, Kolbe kommt in alte Spielstände zurück |
| `test_wochen` | Wochen vergehen, die Kasse ändert sich, es kommen Kunden |
| `test_anwerbung_*` | Werben und Zwingen: Tempo, Kopfgeld, Lohn, Moral-Deckel, Hitze, Karma, Abgänge |
| `test_pferch_flucht_und_nachschub` | Flucht aus dem Pferch, Kündigung, Metzgers Nachschub bis das Haus voll ist |

---

## 3. Was das Werkzeug schon gefunden hat

1. **Der Compiler hat die Kundenberechnung gelöscht.**
   - **Ursache:** `sslc -O2` (sfall 4.5.1) verwirft Zuweisungen, die sich auf sich selbst beziehen (`v := v * x / 100`).
   - **Folge:** Die Gosse hatte in allen bisherigen Testpaketen **jede Woche 0 Kunden** und nur Kosten.
   - **Nachweis:**
     - An einem Minimalbeispiel lässt sich der Fehler nachstellen.
     - Das Handbuch von sslc warnt selbst, dass die höheren Stufen komplexen Code brechen können.
   - **Behebung:** Der Build nutzt jetzt `-O1`. Diese Stufe entfernt nur ungenutzte Variablen und Prozeduren. Seitdem stimmt die Wochenrechnung mit dem Simulator überein.
2. **Essie nach der Auslieferung:** Bis ihr Skript sie entfernte, konnte man sie noch ansprechen, und dann erschien „Error“. Jetzt beendet sie das Gespräch sofort.

---

## 4. Aufruf

```
RL_DEBUG=1 ... bash tools/build_scripts.sh          # wie in Umsetzung 2, Abschnitt 4.1
python3 tools/test_skripte.py --build build/rpu-v2.4.34 --fo2 <RPU>/scripts_src
python3 tools/test_skripte.py ... -k erkundung -v    # nur ein Test, mit Traceback
python3 tools/intvm.py dis build/rpu-v2.4.34/scripts/rlgosse.int   # disassemblieren
```

`--fo2` zeigt auf die `scripts_src` des RPU-Releases, gegen das gebaut wurde. Daraus liest der Test die Konstanten (`GVAR_…`, `MAP_…`, `STAT_…`).

**Grenze:** Das Werkzeug ersetzt keinen Test im Spiel. Karten, Grafik, Wegfindung und das Zusammenspiel mit Vanilla-Skripten zeigt nur das Spiel selbst. Es findet aber Logik-, Text- und Dialogfehler, bevor ein Paket gebaut wird.
