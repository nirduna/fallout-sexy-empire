# Fahrplan: der Rest der Umsetzung

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Stand:** Umsetzung 1–7 sind fertig, die Gosse ist im Spiel getestet. Das [Prüfwerkzeug](pruefwerkzeug.md) steht.
**Auftrag:** Alles Übrige aus Phase 1–6 umsetzen, prüfen und abschließen, ohne weitere Rückfragen. Wo eine Entscheidung nötig ist, gilt meine Empfehlung. Jede steht in der Doku des jeweiligen Schritts.

---

## 1. Grundsätze der Umsetzung

Diese Regeln gelten für alle folgenden Schritte. Sie halten das Addon verträglich mit dem RPU und machen es prüfbar, obwohl ich nicht im Spiel testen kann.

1. **Vanilla-Skripte bleiben unberührt.**
   - Vanilla-Figuren wie Metzger, die Paten, Ascorti, Wen oder Vortis sprechen nicht selbst.
   - Für sie treten **eigene Mittelsleute** auf, so wie Kolbe für Metzger.
   - Den Vanilla-Zustand liest das Addon aus den GVARs, etwa ob Metzger tot ist oder die Mordinos gefallen sind.
2. **Jedes Haus ist eine eigene Karte mit einer Ebene, wie die Gosse.**
   - Den Eingang setzt das globale Skript zur Laufzeit auf die Vanilla-Stadtkarte.
   - Das Innere baut `tools/bau_karten.py` aus einer Vorlage des RPU aus derselben Stadt.
   - Die drei Ebenen aus Phase 2 und sichtbare Ausbauten entfallen. Das wurde bei der Gosse schon so abgenommen.
3. **Figuren entstehen zur Laufzeit.** Das Kartenskript setzt Madame, Mittelsleute und Quest-Figuren je nach Zustand, so wie Kolbe in Umsetzung 4. Damit lassen sich Figuren nachträglich ergänzen, ohne die Karten neu zu verteilen.
4. **Aufträge sind Dialog-Aufträge mit Probe und Zeit.**
   - **Ablauf:** Transporte, Lieferungen, Beschattungen und Übergaben nimmt man im Gespräch an. Die Probe (Skill oder Attribut) fällt beim Annehmen, das Ergebnis kommt nach Ablauf der Zeit mit dem Wochentakt.
   - **Echte Kämpfe** gibt es nur dort, wo das Design ausdrücklich einen Kampf im Haus verlangt: die Eröffnungsnacht, die Nacht der langen Messer, der Sturm auf die Gosse und die Soldaten ohne Krieg. Die Angreifer erscheinen dann auf der Hauskarte.
5. **Jeder Schritt wird geprüft.**
   - Jeder Schritt bringt Tests für `tools/test_skripte.py` mit.
   - Die Erkundung deckt alle neuen Dialoge ab.
   - Danach wird gebaut (RPU 2.3.34 und 2.4.34, Unofficial Patch), dokumentiert, committet und gepusht.
6. **Spieltexte sind Englisch in reinem ASCII**, die Doku bleibt Deutsch ([Spieltexte](spieltexte-englisch.md)).

---

## 2. Die Schritte

| Nr. | Umsetzung | Inhalt |
|---|---|---|
| 5 ✔ | **„Ketten“, Akt 2–5** ([Umsetzung 5](umsetzung-5-ketten-akt2-5.md)) | Mara im Keller, Modul „Zuflucht“, Fluchtroute und Lieferungen als Aufträge, Tylers Preis, Laras Sturm, die vier Enden. Mara als Madame der Gosse (Phase 4, 3.5). Ereignis „Metzgers Vergeltung“ |
| 6 ✔ | **Technik für weitere Häuser** ([Umsetzung 6](umsetzung-6-haeuser-technik.md)) | `bau_karten.py` und `paket.py` für beliebig viele Häuser. Gemeinsames Eingangs-Skript, gemeinsames Kartenskript, Laufzeit-Figuren. Essie erzählt von den anderen Städten |
| 7 ✔ | **New Reno: Das Silberne Strumpfband** ([Umsetzung 7](umsetzung-7-new-reno.md)) | Karte, Madame, „Der Segen“ (Urkunde und Segen einer Familie oder die Eröffnungsnacht), Spieltische, Jet-Theke. **Hauptquartier:** Consigliere, Läufer ins HQ, Auszahlung, Familientreffen alle 4 Wochen, Hausklasse 3 |
| 8 | **Redding: Die Schlacke** | Karte, Madame, „Ascortis Lizenz“ mit vier Wegen, Goldwaage (ehrlich oder gezinkt), Entzugsstube, Malamute Saloon (vier Wege) |
| 9 | **Vault City: Die Kloake** | Karte, Hanne Voss, „Ein Keller im Courtyard“, Schweigegeld je Hausklasse, Wartungstunnel, **Die Akte**, Razzia mit Dienstboten-Folge, Abigail Kessler |
| 10 | **NCR: Die Tränke** | Karte, Madame, „Etablissement Nr. 9“ (vier Wege, Krankenstube als Auflage), Karawanenhof, Registratur, **Vortis' Angebot**. Questline **„Die Reinen“** mit Ruth Calloway in fünf Akten |
| 11 | **San Francisco: Die Bilge** | Karte, Madame, „Die Duldung“ mit Aufseher Wen (drei Wege), Anlegesteg, Schmuggelkammer, Siegel der Shi. Hubologen: entlarven, unterwandern oder Absprache |
| 12 | **„Blut auf der Virgin Street“** | Carlo Venuti in fünf Akten, Miss Kittys Angebot (fünf Wege für das Cat's Paw), Kitty als Partnerin oder Rivalin, „Kittys Kralle“ |
| 13 | **Talente** | Vesper (Gecko), Talus (Broken Hills), Julian Rook (Golden Globes), dazu Loyalität, Vorwarnung vor dem Tod und Tyrannen-Varianten |
| 14 | **Jobs und Läuferroute** | Bestechung je Stadt, Schutzgeld, Sabotage, Gefälligkeiten. „Die Läuferroute“ mit Marcus |
| 15 | **Ereignisse vollständig** | alle Lösungswege aus Phase 4 (4.2, 4.3) bei allen Madames, Razzien je Stadt, Tod im Haus |
| 16 | **Abschluss** | Enden und Nachsätze aller Linien im Epilog, Titel-Wirkungen, Gesamtprüfung, Pakete für RPU 2.3.34 und 2.4.34, Gesamtdoku |

---

## 3. Wie geprüft wird

- **Automatisch** ([Prüfwerkzeug](pruefwerkzeug.md)):
  - Jeder Schritt bringt Szenarien für seine Wege mit.
  - Die Erkundung läuft über alle Figuren aus mehreren Spielständen.
  - Die Wirtschaft wird gegen den Simulator abgeglichen.
- **Karten:** `bau_karten.py` prüft jede Karte:
  - Round-Trip, Skriptsätze und Besitzer
  - Start, Treppen und Figuren nicht auf Wänden
  - Der Eingang auf der Vanilla-Karte liegt auf einem freien Feld.
- **Im Spiel** bleibt offen, was das Werkzeug nicht sehen kann: Grafik, Wegfindung, Kämpfe und das Zusammenspiel mit Vanilla-Skripten. Die Prüfliste steht jeweils in der Doku des Schritts.
