# Spieltexte auf Englisch

**Entscheidung (nach dem ersten Test im Spiel):** Das Addon läuft komplett auf Englisch. Deutsch spielt vorerst keine Rolle.

**Was das bedeutet:**
- Alles, was man im Spiel liest, ist englisch: Dialoge, Meldungen, Endslides, Titel, Kartennamen.
- Die Planungsdokumente in `docs/` bleiben deutsch. Deutsche Namen darin („die Gosse“) sind Arbeitsnamen. Im Spiel gelten die englischen Namen aus der Tabelle unten.
- Die deutschen Spieltexte bis Umsetzung 2 stehen in der Git-Historie (Commit `4295240`, Ordner `text_src/german`), falls später eine deutsche Fassung kommt.

---

## 1. Wo die Texte liegen

| Datei | Inhalt |
|---|---|
| [`text_src/english/dialog/*.msg`](../text_src/english/dialog/) | Dialoge und Beschreibungen, eine Datei je Skript |
| [`text_src/english/dialog/_rl_module.inc`](../text_src/english/dialog/_rl_module.inc) | **erzeugt** von `tools/gen_katalog.py`: Modulnamen (`NAMES_EN` in `tools/ausbau_sim.py`) und Effekte |
| [`text_src/english/game/rotlicht.msg`](../text_src/english/game/rotlicht.msg) | **neu:** Meldungen des globalen Skripts (Hausnamen, Ausbau fertig, Krisen, Läufer) |
| [`text_src/english/game/editor.msg.add`](../text_src/english/game/editor.msg.add), [`map.msg.add`](../text_src/english/game/map.msg.add) | Titel im Charakterbogen, Kartenname |
| [`text_src/english/cuts/rl_*.txt`](../text_src/english/cuts/) | Untertitel der Endslides |

- **`rotlicht.msg`:** Das globale Skript lädt sie beim Laden eines Spielstands mit sfalls `add_extra_msg_file` und liest daraus mit `message_str_game`. Im Code steht damit kein Spieltext mehr.
- **Prüfung:** `tools/check_msg.py` prüft bei jedem Build, ob jede Nummer aus dem Code in der passenden Datei steht, auch für `rotlicht.msg`.

---

## 2. Regeln für englische Spieltexte

- **Nur ASCII.** Die englischen Fallout-2-Schriften haben keine Umlaute, keine typografischen Anführungszeichen und keine Gedankenstriche. Also `"` statt „“, `-` statt –, `...` statt …. `check_msg.py` bricht bei allem anderen ab.
- **Dollar vor der Zahl**, wie im Spiel: „It costs $400.“ Die Textstücke um Zahlen herum enden deshalb auf `$`.
- **Ton:** düster, knapp, kaum Humor, wie in den Phasen festgelegt. Umgangssprache nur, wo die Figur so redet (Kolbe).
- **Begriffe aus Vanilla** so, wie das englische Fallout 2 sie nennt: the Den, the Slavers Guild (kurz: the Guild), Cat's Paw, Jet, the Enclave, the Republic (NCR), the Rangers, Golgotha, Vault City, Redding, San Francisco, the Shi.

---

## 3. Namen: deutsch (Doku) → englisch (Spiel)

**Häuser**

| Doku | Spiel |
|---|---|
| Die Gosse | The Gutter |
| Das Silberne Strumpfband | The Silver Garter |
| Die Schlacke | The Slag |
| Die Kloake | The Cesspit |
| Die Tränke | The Trough |
| Die Bilge | The Bilge |
| Kittys Kralle | Kitty's Claw (in den Endslides: „her Claw“) |

**Figuren und Gruppen**

| Doku | Spiel |
|---|---|
| Madame Esther „Essie“ Kowalski | Madam Esther "Essie" Kowalski |
| Kolbe, Metzgers Eintreiber | Kolbe, Metzger's collector |
| die Gilde | the Guild |
| die Liga (Ruth Calloway) | the League |
| Freier | johns |
| Personal / die Leute | our people / the people |
| Madame | madam |

**Titel (Charakterbogen)**

| Doku | Spiel |
|---|---|
| Seelenverkäufer | Soul Seller |
| Anständiges Haus | Decent House |
| Die Fünfte Familie | The Fifth Family |

**Module**

| Doku | Spiel |
|---|---|
| Hausklasse 2 / 3 (Familiensitz) | House Class II / III (Family Seat) |
| Einrichtung I–III | Furnishings I–III |
| Bar I–II | Bar I–II |
| Sicherheit I–III | Security I–III |
| Personalquartiere I–II | Staff Quarters I–II |
| Krankenstube | Sickroom |
| Kontor | Counting Room |
| VIP-Trakt | VIP Wing |
| Riegel innen / außen | Inside Bolts / Outside Bolts |
| Spieltische | Gaming Tables |
| Ehrliche Goldwaage | Honest Gold Scale |
| Entzugsstube | Detox Room |
| Wartungstunnel | Maintenance Tunnel |
| Karawanenhof | Caravan Yard |
| Anlegesteg | Jetty |
| Siegel der Shi | Seal of the Shi |

**Weitere Begriffe**

| Doku | Spiel |
|---|---|
| Kasse | the till |
| Schuldschein | the debt note |
| Prolog „Essies Schulden“ | "Essie's Debts" |
| Hausklasse | house class |
| Ausstattung | furnishings |
| Unterhalt | upkeep |
| Bauzeit | build time |
| Lex Neun | Lex Nine |
