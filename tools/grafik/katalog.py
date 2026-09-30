"""Eigene Szenerie der Mod: was es gibt, wie gross, wo es steht.

Wird von den Blender-Skripten (Modell, Felder) und vom Paketbau (Prototypen,
Texte, Platzierung) gelesen. Kein Blender noetig.

Je Objekt:
  titel, text   Name und Beschreibung (pro_scen.msg, englisch, ASCII)
  material      fuer das Geraeusch beim Anfassen (frm.MATERIAL)
  felder        belegte Hexfelder relativ zum Bezugsfeld (Spalten, Reihen); das
                Bezugsfeld ist (0, 0). Grosse Moebel werden in senkrechte Streifen
                geschnitten, jeder Streifen steht auf seinem vordersten Feld.
  bezug         Bezugsfeld beim Rendern. Plaetze mehrfeldriger Objekte muessen in der
                Spalte dieselbe Paritaet haben (Hex-Zickzack), sonst neu rendern.
  platz         Bezugsfelder in der Gosse (RLDEN01), leer = nicht aufgestellt.
                Die Gosse hat zwei Raeume (geprueft an einem Bildschirmfoto aus dem Spiel):
                - Treppenraum, Spalten 61-71: Treppe 16666 an der Rueckwand, langer Tisch
                  Spalten 67-68 in den Reihen 87-91, Regal und Kisten an der rechten Wand.
                - Zimmer hinter der Tuer 16872, sichtbar nur die Spalten 73-76 (die Wand
                  links deckt 77-79 zu): Bett oben an der Rueckwand, Teppichboden,
                  Buecherregal an der Trennwand (Spalte 73).
                Die Trennwand (Spalte 72) und das Regal verdecken alles, was im
                Treppenraum in den Spalten 69-71 steht.
  ersetzt       Vanilla-Objekte, die dafuer wegfallen, soweit vorhanden: [(PID, Hexfeld)].
                Von jeder PID ausser Blockern muss mindestens eins da sein.
  licht         (Weite in Hexfeldern, Staerke 0-65536) fuer Lampen
  flach         liegt auf dem Boden (Teppich): wird vor allem anderen gezeichnet
                und blockiert nichts
  leucht        hat Flaechen in Farbe 254 (pulsierendes Rot)
"""

# Flags der Kartenobjekte wie bei Vanilla-Moebeln in denbus1:
# ShootThru | LightThru | TransNone, flach zusaetzlich Flat | NoBlock
FLAGS_MOEBEL = 0xA0008000
FLAGS_FLACH = 0xA0008018
PID_BLOCKER = 0x2000043          # "Secret Blocking Hex" (unsichtbar, blockiert)
FLAGS_BLOCKER = 0xA0000008
FID_BLOCKER = 0x2000015          # block.frm

OBJEKTE = {
    "rllatern": dict(
        titel="Red lantern",
        text="A lantern with red glass on an iron pole. In its light everyone looks younger and nobody looks closely.",
        material="metall", felder=[(0, 0)], platz=[17063, 17075], licht=(4, 40000), leucht=True),
    "rlbett": dict(
        titel="Bed",
        text="A wide bed with a red blanket. The blanket has been washed so often it has almost forgotten its color.",
        material="holz", felder=[(0, 0), (0, -1), (0, -2), (-1, 0), (-1, -1), (-1, -2)], bezug=17070,
        # im Zimmer an der Stelle des Vanilla-Betts (ss122.frm) und seiner Blocker im Raum
        # (RPU 2.4.34: zwei Teile auf 16675 und 17075, 2.3.34: ein Teil auf 16675)
        platz=[16876], ersetzt=[(0x20002A8, 16675), (0x20002A8, 17075)] + [(PID_BLOCKER, t) for t in
                                                       (16476, 16675, 16676, 16874, 16875, 16876, 17075)]),
    "rlparavnt": dict(
        titel="Folding screen",
        text="A folding screen of wood and faded red cloth. It hides nothing from anyone who wants to look.",
        material="holz", felder=[(0, 0), (0, -1), (0, -2)], bezug=17068,
        platz=[]),                        # in der Gosse ist kein sinnvoller Platz frei
    "rlwasch": dict(
        titel="Washstand",
        text="A washstand with a chipped bowl and a jug. The water is changed every morning, whether it needs it or not.",
        material="holz", felder=[(0, 0)], platz=[16474]),      # Wandnische neben dem Kopfende
    "rlteppich": dict(
        titel="Rug",
        text="A threadbare red rug. Someone has scrubbed a dark stain out of the middle, almost.",
        material="leder", felder=[(0, 0)], platz=[17067], flach=True),   # am Fuss der Treppe
    "rlschild": dict(
        titel="Price board",
        text="A slate board on a stand. In chalk: ROOMS. DRINKS. NO GUNS. Someone has wiped out the prices and written them again, higher.",
        material="holz", felder=[(0, 0)], platz=[17065]),      # neben der Ankunft
}


def bezug(name):
    obj = OBJEKTE[name]
    return obj.get("bezug") or obj["platz"][0]
