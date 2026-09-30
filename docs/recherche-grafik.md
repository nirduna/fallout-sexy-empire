# Recherche: Neue Grafiken für die Mod

**Stand:** Recherche und ein Probelauf. Die Schritte 1–3 des Vorschlags (Abschnitt 5) sind inzwischen umgesetzt: [Grafik 1](umsetzung-g1-grafik.md).
**Frage:** Kann die Mod eigene Sprites, Texturen, Köpfe und Bilder bekommen?
**Kurzantwort:** Ja. Die Engine lädt neue Grafiken problemlos, und die Werkzeugkette lässt sich hier bauen. Der Aufwand hängt stark von der Art der Grafik ab.

---

## 1. Was die Engine kann (geprüft im Quelltext von Fallout 2 CE und sfall)

| Punkt | Befund |
|---|---|
| Format | Alle Spielgrafiken sind **FRM**: 8-Bit-Indexbilder, bis zu 6 Richtungen mit je n Frames, Palette extern (`color.pal`). Index 0 ist transparent |
| Palette | 256 Farben. Die festen Farben sind 1–228. **229–254 werden von der Engine animiert** (`cycle.cc`): Schleim 229–232, Monitore 233–237, Feuer langsam 238–242, Feuer schnell 243–247, Ufer 248–253, **254 pulsiert rot** |
| Eigene Paletten | **Endslides** laden eine eigene `.pal` mit dem Namen des Bildes (`endgame.cc`). Das RPU nutzt das schon (`eg_marc.pal` usw.). Ein Endslide-Bild kann also 256 frei gewählte Farben haben |
| Wie viele neue Grafiken | Die Grafik-ID hat 12 Bit für den Index, also 4.096 Einträge je Typ. Das RPU belegt (2.3.34 / 2.4.34) Tiles 3.887 / 4.077, Szenerie 2.349 / 2.383, Wände 2.002 / 2.049, Critter 152 / 152. **Platz ist reichlich, nur bei Tiles ist es knapp: in 2.4.34 sind nur 19 frei** (Zahlen nachgezählt beim Einbau, siehe [Grafik 1](umsetzung-g1-grafik.md)) |
| sfall | Sprechköpfe dürfen **32-Bit-PNG** sein (`Use32BitHeadGraphics`, braucht den DX9-Modus). Skript-Fenster können **PCX und FRM** anzeigen (`create_win`, `draw_image`, `interface_art_draw`) |
| Einbindung | Neue Grafik = FRM + Zeile in `art/<typ>/<typ>.lst`. Für Szenerie zusätzlich ein Prototyp (`.pro` + `proto/.../*.lst`) und Name/Beschreibung in `pro_scen.msg`. `paket.py` schreibt Basisdateien schon je RPU-Release fort (wie `scripts.lst`) und kann das genauso für die Grafik-Listen |

---

## 2. Probelauf (hier in der Sandbox)

1. **FRM lesen und schreiben:** ein eigener Python-Leser an echten RPU-Dateien.
   - Getestet an Szenerie (Schreibtisch), einem Critter (6 Richtungen × 16 Frames) und einem Sprechkopf.
   - Alle drei kommen **byte-gleich** zurück.
2. **Palette:** Mit der Standardpalette werden die RPU-Grafiken farbrichtig als PNG ausgegeben.
3. **3D-Rendering:** Blender läuft hier als Python-Modul (`bpy` 5.0.1) ohne Grafikkarte.
   - Ein einfaches Bett mit roter Lampe rendert in etwa **1 Sekunde**.
   - Danach: auf die festen 228 Palettenfarben reduziert, als FRM geschrieben, zurückgelesen.
4. **Ergebnis:** Technisch funktioniert der ganze Weg. Die sichtbaren Schwächen des Probelaufs:
   - Die Palette hat wenig gesättigtes Rot, deshalb kippt reines Rot ins Braune. Man muss mit der Palette im Kopf texturieren, oder für Licht Farbe 254 (pulsierendes Rot) benutzen.
   - Ohne Texturen wirkt das Objekt glatter als Vanilla. Vanilla-Objekte haben Holzmaserung, Stoff, Schmutz, harte Schatten.
   - Kamerawinkel und Maßstab müssen an Vanilla-Objekten geeicht werden. Die Littlepip-Mod hat dafür eine eigene Blender-Szene gebaut.

**Nicht ins Repository:** Die `color.pal` gehört zum Originalspiel. Für den Probelauf habe ich eine öffentliche Kopie benutzt. Für die Mod soll der Build sie aus dem eigenen Spiel lesen (`master.dat`) oder einen Pfad dazu bekommen.

---

## 3. Was sich lohnt, was nicht

| Art | Aufwand | Wirkung | Weg | Empfehlung |
|---|---|---|---|---|
| **Szenerie** (Betten, Vorhänge, Paravents, Bar, rote Lampen, Badewanne, Schilder) | mittel | hoch: Die Häuser sehen nach Bordell aus statt nach umgeräumten Vanilla-Räumen | Blender, prozedural modelliert oder freie CC0-Modelle, eine geeichte Kamera, Texturen | **ja, zuerst** |
| **Leuchtreklame / rotes Licht** mit Farbe 254 | klein | sehr hoch für „Rotlicht“: pulsiert von selbst, ohne Animation und ohne Skript | Schild oder Lampe, Leuchtfläche auf Index 254 | **ja, zuerst** |
| **Endslide-Bilder** (Tyrann, Geschäftsmann, Bankrott, Nachsätze) | klein je Bild, wenn es eine Vorlage gibt | hoch, das Ende ist der letzte Eindruck | Bild → 640×480, eigene 256-Farben-Palette, dazu die `.pal` | **ja**, braucht Bildvorlagen |
| **Umgefärbte Figuren** (Madames, Personal) aus vorhandenen Critter-Sprites | mittel | mittel: jede Madame erkennbar | Farbindizes der Kleidung umlegen, alle Frames und Richtungen. Es gibt dafür schon ein Python-Werkzeug (FRM Recolour) | ja, nach der Szenerie |
| **Sprechköpfe** für Essie, Roz, Nell, Hanne, Dora, Kwan | hoch | sehr hoch | je Kopf 16 FRMs: 3 Stimmungen × (Phoneme, Neutral, 3 Fidgets) plus Übergänge. Quelle: 3D-Kopf in Blender (so machten es die Entwickler, mit Formzielen für die Laute) oder gemalte Vorlagen. Zusätzlich PNG für sfall | später, erst ein Probekopf |
| **Eigenes Madame-Fenster** (Hauptbuch mit Bild) | mittel | mittel | sfall `create_win` + `draw_image` mit PCX | optional |
| **Neue Tiles** (Boden, Dach) | klein bis mittel | gering, und nur 19 freie Plätze in RPU 2.4.34 | 80×36 px, Kacheln aus Texturen | nur gezielt |
| **Neue Critter von Grund auf** | sehr hoch: über 100 Animationen × 6 Richtungen, bei der Littlepip-Mod über 5.000 Frames je Figur und Rüstung | mittel | 3D-Figur, Rig, Animationen, Rendern | **nein**, lieber umfärben |

---

## 4. Wo ich an Grenzen stoße

- **Ich kann keine Bilder malen oder mit einem Bild-KI-Modell erzeugen.** Ich kann aber:
  - 3D-Szenen modellieren und rendern,
  - Texturen prozedural erzeugen,
  - Vanilla-Grafiken zerlegen, umfärben und neu zusammensetzen,
  - jede gelieferte Bildvorlage (Zeichnung, Foto, KI-Bild aus einem anderen Werkzeug) sauber ins Fallout-Format bringen.
- **Die Qualität beurteilt am Ende das Auge im Spiel.** Ich kann Vorschaubilder neben Vanilla-Objekte stellen, aber nicht sehen, wie es im Spiel wirkt.
- **Lizenzen:**
  - Community-Pakete (ModDB, Nexus, Vault-Tec Labs) haben je eigene Bedingungen.
  - Die über 150 Köpfe des „Talking Heads Addon“ (Goat_Boy) gehören ihrem Autor; ohne Erlaubnis nicht übernehmen.
  - KI-Bilder sind in der Fallout-Community umstritten; wenn, dann offen kennzeichnen.

---

## 5. Vorschlag für ein Vorgehen (wenn gewünscht)

1. **Werkzeug:** `tools/frm.py` (PNG ↔ FRM, Palette aus der eigenen `master.dat`, feste und animierte Farben), dazu Grafik-Listen, Prototypen und Texte in `paket.py`, und ein Test, der jede neue Grafik zurückliest.
2. **Blender-Szene** mit Kamera und Licht, geeicht an 3–4 Vanilla-Objekten.
3. **Erstes Paket „Rotlicht“:** rote Lampe und Leuchtschild mit Farbe 254, Bett, Paravent, Vorhang. Eingebaut in die Gosse, weil die im Spiel schon getestet ist.
4. Nach deinem Urteil im Spiel: weitere Häuser, Endslides, dann die Madames als umgefärbte Figuren, zuletzt ein Probekopf.

---

## Quellen

- [Fallout 2 CE](https://github.com/alexbatalov/fallout2-ce): `art.cc` (FRM, Grafik-ID), `endgame.cc` (Endslide-Paletten), `cycle.cc` (animierte Farben)
- [sfall](https://github.com/sfall-team/sfall): `ddraw.ini` (`Use32BitHeadGraphics`), Funktionsliste (`create_win`, `draw_image`, `interface_art_draw`)
- [Restoration Project](https://github.com/BGforgeNet/Fallout2_Restoration_Project): eigene Critter, Szenerie, Köpfe und Endslide-Paletten
- [Littlepip-Mod: Blender-Szene für Fallout-Sprites](https://art.cleberg.net/post/donitz/Littlepip-Mod-in-Blender-331367298), [Umfang](https://art.cleberg.net/post/donitz/Fallout-2-Littlepip-Mod-322083843)
- [Fallout 1/2 FRM Tools](https://www.nexusmods.com/fallout2/mods/179), [FRM2BMP/BMP2FRM](https://www.ModDB.com/downloads/frm2bmp), [FRM Recolour (Python)](https://github.com/Dr-Felix116/frm_recolour_python)
- [FRM-Format](https://falloutmods.fandom.com/wiki/FRM_File_Format), [LIP-Format](https://falloutmods.fandom.com/wiki/LIP_File_Format), [Tutorials für Critter, Tiles, Wände](https://falloutmods.fandom.com/wiki/Fallout_2_tutorials)
- [Talking Heads Addon (Goat_Boy)](https://www.ggrecon.com/articles/massive-fallout-2-expansion-adds-over-100-new-characters/)
- [Freie Tile- und Sprite-Pakete (ModDB)](https://www.moddb.com/groups/robcomodding/addons)
