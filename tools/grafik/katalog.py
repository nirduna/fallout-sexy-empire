"""Eigene Szenerie der Mod: was es gibt, wie gross, wo es steht.

Wird von den Blender-Skripten (Modell, Felder) und vom Paketbau (Prototypen,
Texte, Platzierung) gelesen. Kein Blender noetig.

Je Objekt:
  titel, text   Name und Beschreibung (pro_scen.msg, englisch, ASCII)
  material      fuer das Geraeusch beim Anfassen (frm.MATERIAL)
  felder        belegte Hexfelder relativ zum Bezugsfeld (Spalten, Reihen); das
                Bezugsfeld ist (0, 0). Grosse Moebel werden in senkrechte Streifen
                geschnitten, jeder Streifen steht auf seinem vordersten Feld.
  platz         Bezugsfelder in der Gosse (RLDEN01). Bei mehreren Feldern muss
                die Spalte dieselbe Paritaet haben wie beim Rendern (Hex-Zickzack).
                Raum der Gosse: Reihen 82-96, Spalten 61-71; Rueckwaende oben (Reihe 81)
                und rechts (Spalte 60), Treppe 16666, langer Tisch Spalten 67-68 in den
                Reihen 87-91, Kisten an der rechten Wand. Bett, Paravent und Waschtisch
                stehen oben links an der Rueckwand; die Treppe bleibt von 16866, 16867
                und 16667 aus erreichbar.
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
        material="metall", felder=[(0, 0)], platz=[17063, 18468], licht=(4, 40000), leucht=True),
    "rlbett": dict(
        titel="Bed",
        text="A wide bed with a red blanket. The blanket has been washed so often it has almost forgotten its color.",
        material="holz", felder=[(0, 0), (0, -1), (0, -2), (-1, 0), (-1, -1), (-1, -2)], platz=[17070]),
    "rlparavnt": dict(
        titel="Folding screen",
        text="A folding screen of wood and faded red cloth. It hides nothing from anyone who wants to look.",
        material="holz", felder=[(0, 0), (0, -1), (0, -2)], platz=[17068]),
    "rlwasch": dict(
        titel="Washstand",
        text="A washstand with a chipped bowl and a jug. The water is changed every morning, whether it needs it or not.",
        material="holz", felder=[(0, 0)], platz=[16671]),
    "rlteppich": dict(
        titel="Rug",
        text="A threadbare red rug. Someone has scrubbed a dark stain out of the middle, almost.",
        material="leder", felder=[(0, 0)], platz=[17269], flach=True),
    "rlschild": dict(
        titel="Price board",
        text="A slate board on a stand. In chalk: ROOMS. DRINKS. NO GUNS. Someone has wiped out the prices and written them again, higher.",
        material="holz", felder=[(0, 0)], platz=[17065]),
}
