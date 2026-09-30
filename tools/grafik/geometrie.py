"""Geometrie der Fallout-2-Grafik: Kamera, Massstab, Hexfelder (ohne Blender).

Hergeleitet aus fallout2-ce (tile.cc tileToScreenXY, object.cc objectGetRect)
und an Grafiken des Restoration Project gemessen:

  Eine Bodenkachel ist ein Parallelogramm mit den Kanten A = (48, -12) und
  B = (32, 24) Pixel (Bildschirm, y nach unten); gemessen an gras004.frm.
  Eine orthografische Kamera bildet zwei rechtwinklige Kanten der Laengen
  L1, L2 genau so ab, wenn L1 : L2 = sqrt(3) : 2 und die Kamera 25,66 Grad nach
  unten blickt. Die Hexfelder (2 x 2 je Kachel) sind dann regelmaessige Sechsecke.

Weltkoordinaten (Blender): Kante A laeuft entlang +X, Kante B entlang -Y, Z nach
oben. Massstab K Pixel je Meter: 43, so ist eine Figur von 1,75 m etwa 68 Pixel
hoch wie die Menschen-Critter des RPU.
"""
import math

K = 43.0                                   # Pixel je Meter
A = (48, -12)                              # Kachelkante entlang +X (Bildschirm, y nach unten)
B = (32, 24)                               # Kachelkante entlang -Y
L1 = 48 / 0.8660254 / K                    # Weltlaenge der Kante A (m)
L2 = 64 / K                                # Weltlaenge der Kante B (m)

# Kamera: rechts, oben, rueckwaerts (Blickrichtung ist -z)
KAMERA_R = (math.sqrt(3) / 2, -0.5, 0.0)
KAMERA_U = (0.21650635, 0.375, 0.90138782)
KAMERA_Z = (-0.45069390, -0.78062475, 0.43301270)


def welt_zu_bild(x, y, z):
    """Weltpunkt -> Bildschirmversatz in Pixel (x nach rechts, y nach unten)."""
    rx = x * KAMERA_R[0] + y * KAMERA_R[1] + z * KAMERA_R[2]
    uy = x * KAMERA_U[0] + y * KAMERA_U[1] + z * KAMERA_U[2]
    return rx * K, -uy * K


def boden_aus_bild(sx, sy):
    """Bildschirmversatz eines Bodenpunkts -> Welt (x, y) auf z = 0."""
    det = A[0] * B[1] - A[1] * B[0]
    alpha = (sx * B[1] - B[0] * sy) / det
    beta = (A[0] * sy - A[1] * sx) / det
    return alpha * L1, -beta * L2


def hex_bild(tile):
    """Bildschirmposition eines Hexfelds (fallout2-ce tileToScreenXY, ohne Kameraversatz)."""
    v3 = 199 - tile % 200
    v4 = tile // 200
    return 48 * (v3 // 2) + (32 if v3 & 1 else 0) + 16 * v4, -12 * (v3 // 2) + 12 * v4


def hex_welt(tile, anker):
    """Weltposition (x, y) der Mitte von tile relativ zur Mitte von anker."""
    ax, ay = hex_bild(anker)
    tx, ty = hex_bild(tile)
    return boden_aus_bild(tx - ax, ty - ay)


def versatz(tile, dx, dy):
    """Hexfeld um dx Spalten und dy Reihen verschoben (Kartenkoordinaten)."""
    return (tile // 200 + dy) * 200 + tile % 200 + dx
