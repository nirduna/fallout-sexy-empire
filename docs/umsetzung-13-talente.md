# Umsetzung 13 – Talente

**Arbeitstitel:** *Rotlicht über dem Ödland* – Addon-Modifikation für Fallout 2
**Status:**
- Umgesetzt und gebaut für RPU 2.4.34, RPU 2.3.34 und den Unofficial Patch.
- Im [Prüfwerkzeug](pruefwerkzeug.md) getestet: 70 Tests, davon 4 neu.
- **Test im Spiel offen.**

**Grundlage:**
- [Phase 4](phase-4-personal-talente-ereignisse.md), Abschnitt 3.1–3.4 und 3.7, Leitlinie 5 (Vorwarnung vor dem Tod)
- [Fahrplan](fahrplan.md), Schritt 13

Mara (3.5) kam mit Umsetzung 5, Miss Kitty (3.6) mit Umsetzung 12.

---

## 1. Was neu ist

| Datei | Inhalt |
|---|---|
| [`rl_talente.h`](../scripts_src/headers/rl_talente.h) | **neu:** Zustände, Konstanten, `rl_talent_anwenden` schaltet die Wirkung einer Figur an oder ab, jeweils genau einmal |
| [`rl_manager.h`](../scripts_src/headers/rl_manager.h) | Menüpunkt „People worth knowing about.“ bei jeder Madame, mit den Anwerbe-Wegen |
| [`_rl_talente.inc`](../text_src/english/dialog/_rl_talente.inc) | **neu:** die Texte dazu (950–999), in Erzählerstimme für alle Madames |
| [`gl_rotlicht.ssl`](../scripts_src/global/gl_rotlicht.ssl) | `rl_talente_reise` (Ankunft in Gecko und Broken Hills) und `rl_talente_woche` (Ankunft, Wirkung, Rückfall, Verrat, Abschied). Talus fängt gewalttätige Freier ab, Abigail halbiert Stoff und senkt Razzien |
| [`rl_rechne_woche`](../scripts_src/headers/rotlicht.h) | neues Hausfeld `RL_F_VIP_MOD`: zusätzliche VIP-Kunden je Woche |

---

## 2. Die Figuren

Alle vier werden im Gespräch mit einer Madame angeworben. Sie erzählt, wer die Figur ist; der Spieler wählt einen Weg. Wer woanders gebraucht wird, muss dorthin reisen: Die Ankunft löst die Karte aus, nicht ein Gespräch.

| Figur | Wo angeworben | Wege | Loyalität |
|---|---|---|---|
| **Vesper** | Strumpfband | Geleitschutz (Kampfwert 60) · Umweg (Outdoorsman 60) · Passierschein (Science 60). Dann **nach Gecko reisen** | 80 |
| **Julian Rook** | Strumpfband | Vertrag lösen: Barter 60 und 800 $ · Gambling 70 · Titel Porn Star und Speech 50. Danach vom Jet holen: Doctor 60, Myrons Antidot oder die Entzugsstube der Schlacke | 70, clean +10 |
| | | **Tyrannen-Variante:** Vertrag und Stoff übernehmen. K −10, er bleibt am Jet | 30 |
| **Abigail Kessler** | Kloake | Bürgerschaft: E Vault City ≥ 60 oder Speech 70 · Akte vernichten: Sneak 60 und Lockpick 60, H +10 | 80 / 70 |
| | | **Tyrannen-Variante:** erpressen. K −10 | 20 |
| **Talus** | jedes Haus außer der Kloake, er kommt in **dieses** Haus | Die Wahrheit: die Vanilla-Quest „Missing people“ bei Marcus lösen · Ausbruch (Lockpick 80 oder Kampfwert 80). Dann **nach Broken Hills reisen** | 90 / 60 |
| | | Lesen lernen (IN 7): Loyalität dauerhaft 100 | |

**Wirkungen:**

| Figur | Wirkung |
|---|---|
| Vesper | Nur im Strumpfband, erst wenn Bar II steht (die Bühne). Qualität +10, Ausstattung +10, Nebenumsatz +2 $ je Kunde, Kunden +5 % (Ghul-Händler aus Gecko) |
| Julian | In jedem eigenen Haus mit VIP-Trakt: +3 VIP-Kunden je Woche, Ruf +1 je Woche. Das gilt schon, solange er noch am Jet ist |
| Abigail | Doc der Kloake: Krankenstube (falls keine gebaut ist), Lohn +120 $. Stoff-Ereignisse halbiert, Razzien −25 % |
| Talus | Sicherheit +45 für 50 $ Lohn. Gewalttätige Freier erledigt er selbst: Das Ereignis fällt in seinem Haus aus. In der NCR Kunden −5 % |

---

## 3. Wie Figuren gehen

| Figur | Anlass | Folge |
|---|---|---|
| alle | Loyalität unter 30 | Sie geht, und die Wirkung entfällt |
| Vesper | irgendwo arbeitet Zwangspersonal | Sie geht. „Sie hat genug Menschen hinter verschlossenen Türen weinen hören.“ |
| Vesper | Lüge über das Haus (statt Speech 40) | Loyalität −20 |
| Talus | in **seinem** Haus gibt es „Riegel außen“ oder Zwangspersonal | Er geht und zeigt dich bei Marcus an: Die Läuferroute ist gesperrt |
| Talus | Ausbruch | Marcus sperrt die Läuferroute sofort |
| Abigail, erpresst | 5 % je Woche | Sie verrät das Haus an die Garde: Razzia in der Kloake, und sie ist weg |
| Julian | Rückfall, 3 % je Woche, 10 % mit einer Jet-Theke irgendwo, doppelt, solange er noch am Jet ist | mit Krankenstube irgendwo: Loyalität −10. Ohne: **schwer verletzt** (Abschnitt 4) |
| Julian, Tyrann | kein Rückfall, er ist ja nie clean | Stoff-Ereignisse in Häusern mit VIP-Trakt ×2 |

---

## 4. Vorwarnung vor dem Tod

Phase 4, Leitlinie 5: Eine Figur stirbt erst nach einer Woche schwerer Verletzung, in der der Spieler sie retten kann.

- Rückfall ohne Krankenstube: Julian liegt eine Woche im Hinterzimmer. Jede Madame bietet dann „Julian is dying in the back room.“ an.
- **Retten:** Doctor 60 oder Myrons Antidot. Er kommt zurück, clean, Loyalität −20.
- Wird in dieser Woche irgendwo eine Krankenstube fertig, rettet sie ihn ebenfalls.
- Sonst stirbt er zu Beginn der nächsten Woche.

---

## 5. Entscheidungen (meine Empfehlungen)

1. **Keine eigenen Figuren auf der Karte.** Die vier wirken über die Wochenrechnung und über Ereignisse. Eine Figur, die im Saal herumsteht, bräuchte eigene Dialoge, Kampfverhalten und Schutz vor Vanilla-Skripten. Das bringt viel Risiko und im Spiel wenig.
2. **Die Madame erzählt.** Vesper, Abigail, Talus und Julian sind Geschichten, die die Madame kennt. So braucht es keine neuen Skripte in Gecko, Broken Hills, Vault City oder den Golden Globes, und Vanilla-Karten bleiben unverändert (Fahrplan, Grundsatz 1).
3. **Talus braucht die Vanilla-Quest.** Gelöst ist sie, wenn `GVAR_BH_MISSING` den Stand „erledigt“ erreicht. Wer in Broken Hills ankommt, bevor sie gelöst ist, bekommt einen Hinweis und kann später wiederkommen.
4. **Julian wirkt schon am Jet,** aber mit doppeltem Rückfallrisiko. Der Spieler soll merken, was er an ihm hat, bevor er ihn vom Stoff holt.
5. **Abigails Krankenstube** zählt nur, solange sie da ist. Hat die Kloake schon eine gebaute Krankenstube, bleibt die beim Weggang erhalten.

---

## 6. Welt-Felder

Welt 118–131: Stand, Loyalität und Weg je Figur, Talus' Haus, dazu `RL_W_TALENTE_AKTIV`: Bit je Figur, deren Wirkung angewendet ist, und Bit 16 für Abigails Krankenstube. `RL_W_VESPER` = 1, solange Vesper singt (für den Epilog).

---

## 7. Testen im Spiel

| Test | Erwartung |
|---|---|
| Strumpfband, Madame: „People worth knowing about.“ | Vesper, Julian, Talus |
| Vesper-Auftrag, dann Gecko betreten | Meldung: Sie packt ihren Koffer |
| Ohne Bar II | Meldung: Sie wartet auf die Bühne. Mit Bar II singt sie in der nächsten Woche |
| Talus-Auftrag, Broken Hills vor der Missing-Quest | Hinweis: Er sitzt noch |
| Kloake, Madame | Abigail mit drei Wegen |
| Julian: Vertrag, dann Wochen ohne Krankenstube | Irgendwann: „Julian is dying“. Die Madame bietet die Rettung an |

---

## 8. Nächste Schritte

Weiter mit **Schritt 14** des [Fahrplans](fahrplan.md): Jobs und Läuferroute.
