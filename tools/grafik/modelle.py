"""Die Modelle der eigenen Szenerie (laeuft mit bpy).

Alle Masse in Metern, Ursprung = Mitte des Bezugsfelds auf dem Boden.
Weltachsen wie in geometrie.py: +X nach rechts hinten, +Y nach links hinten
(vom Betrachter weg), Z nach oben. Rot nur aus der reinen Rotreihe der Palette
(Gruen und Blau 0), sonst kippt es beim Umrechnen ins Braune.
"""
import math

import szene as s

# Blickrichtung der Kamera waagerecht (vom Objekt zur Kamera)
ZUR_KAMERA = math.atan2(-0.78062475, -0.45069390)


def materialien():
    return dict(
        holz=s.material("holz", (0.16, 0.085, 0.045), rauheit=0.75, textur="holz", textur_staerke=0.55,
                        relief=0.4, massstab=8, glanz=0.3),
        holz_hell=s.material("holz_hell", (0.30, 0.19, 0.10), rauheit=0.8, textur="holz", textur_staerke=0.5,
                             relief=0.35, massstab=10, glanz=0.3),
        eisen=s.material("eisen", (0.10, 0.095, 0.09), rauheit=0.55, metall=0.8, textur="rost",
                         textur_staerke=0.5, relief=0.2, massstab=20),
        stoff_rot=s.material("stoff_rot", (0.40, 0.0, 0.0), rauheit=0.95, textur="stoff", textur_staerke=0.5,
                             relief=0.9, massstab=2, glanz=0.05, schmutz=0.4),
        stoff_rot_alt=s.material("stoff_rot_alt", (0.30, 0.0, 0.0), rauheit=0.95, textur="stoff",
                                 textur_staerke=0.55, relief=0.7, massstab=3, glanz=0.05, schmutz=0.4),
        leinen=s.material("leinen", (0.55, 0.52, 0.46), rauheit=0.95, textur="stoff", textur_staerke=0.35,
                          relief=0.8, massstab=2, glanz=0.1, schmutz=0.35),
        keramik=s.material("keramik", (0.62, 0.60, 0.54), rauheit=0.35, textur="rauschen", textur_staerke=0.15,
                           massstab=30),
        schiefer=s.material("schiefer", (0.07, 0.08, 0.08), rauheit=0.9, textur="rauschen", textur_staerke=0.4,
                            massstab=25),
        kreide=s.material("kreide", (0.75, 0.75, 0.72), rauheit=1.0),
        glas_rot=s.material("glas_rot", (1.0, 0.0, 0.0), rauheit=0.2, leucht=6.0),
    )


# ------------------------------------------------------------------ Laterne
def latern(m, felder):
    s.zylinder((0, 0, 0.025), 0.17, 0.05, m["eisen"], ecken=20, fase=0.01)
    s.zylinder((0, 0, 0.8), 0.018, 1.55, m["eisen"], ecken=8)
    # Arm nach vorn (zur Kamera), daran die Laterne
    arm = 0.22
    ax, ay = math.cos(ZUR_KAMERA) * arm, math.sin(ZUR_KAMERA) * arm
    s.quader((ax / 2, ay / 2, 1.56), (abs(ax) + 0.03, abs(ay) + 0.03, 0.025), m["eisen"], fase=0.005)
    z = 1.28
    s.zylinder((ax, ay, 1.5), 0.006, 0.12, m["eisen"], ecken=6)
    s.quader((ax, ay, z), (0.15, 0.15, 0.22), m["glas_rot"], fase=0.01)
    for ex in (-1, 1):
        for ey in (-1, 1):
            s.quader((ax + ex * 0.078, ay + ey * 0.078, z), (0.02, 0.02, 0.25), m["eisen"], fase=0)
    s.zylinder((ax, ay, z + 0.14), 0.11, 0.05, m["eisen"], ecken=4, fase=0.01)
    s.zylinder((ax, ay, z - 0.13), 0.10, 0.03, m["eisen"], ecken=4)


# ------------------------------------------------------------------ Bett
def bett(m, felder):
    xs = [p[0] for p in felder]
    ys = [p[1] for p in felder]
    x0, x1 = min(xs) - 0.28, max(xs) + 0.28           # Breite ~1,2 m
    y0, y1 = min(ys) - 0.12, max(ys) + 0.12           # Laenge ~2,1 m, Kopf bei y1
    bx, by = (x0 + x1) / 2, (y0 + y1) / 2
    b, l = x1 - x0, y1 - y0
    pf = 0.07
    for px in (x0 + pf / 2, x1 - pf / 2):
        s.quader((px, y0 + pf / 2, 0.3), (pf, pf, 0.6), m["holz"])
        s.quader((px, y1 - pf / 2, 0.5), (pf, pf, 1.0), m["holz"])
    s.quader((bx, y1 - pf / 2, 0.68), (b - pf, 0.04, 0.5), m["holz"])            # Kopfteil
    s.quader((bx, y0 + pf / 2, 0.42), (b - pf, 0.04, 0.2), m["holz"])            # Fussteil
    for px in (x0 + pf / 2, x1 - pf / 2):
        s.quader((px, by, 0.3), (0.05, l - pf, 0.12), m["holz"])                 # Seiten
    s.quader((bx, by, 0.43), (b - 0.12, l - 0.12, 0.16), m["leinen"], fase=0.04)  # Matratze
    decke = s.quader((bx, by - 0.2, 0.52), (b - 0.02, l - 0.55, 0.08), m["stoff_rot"], fase=0.03)
    s.weich(decke, 1)
    s.quader((x0 - 0.01, by - 0.2, 0.40), (0.02, l - 0.55, 0.22), m["stoff_rot"], fase=0.01)   # Decke haengt rechts ueber
    s.quader((x1 + 0.01, by - 0.2, 0.40), (0.02, l - 0.55, 0.22), m["stoff_rot"], fase=0.01)   # und links
    s.kugel((bx - 0.22, y1 - 0.3, 0.58), 0.2, m["leinen"], (1.2, 0.7, 0.35))
    s.kugel((bx + 0.24, y1 - 0.32, 0.57), 0.2, m["leinen"], (1.15, 0.7, 0.33))


# ------------------------------------------------------------------ Paravent
def paravent(m, felder):
    ys = [p[1] for p in felder]
    y0, y1 = min(ys) - 0.3, max(ys) + 0.3
    n = 3
    breite = (y1 - y0) / n
    for i in range(n):
        yc = y0 + breite * (i + 0.5)
        winkel = math.radians(18 if i % 2 else -18)
        rahmen = 0.04
        h = 1.7
        # Rahmen: zwei Pfosten, oben und unten Querlatten; dazwischen Stoff
        for dy in (-breite / 2 + rahmen / 2, breite / 2 - rahmen / 2):
            px = -math.sin(winkel) * dy
            py = yc + math.cos(winkel) * dy
            s.quader((px, py, h / 2), (rahmen, rahmen, h), m["holz_hell"], drehung=winkel)
        for hz in (0.12, h - 0.03):
            s.quader((0, yc, hz), (0.03, breite, 0.05), m["holz_hell"], drehung=winkel)
        s.quader((0, yc, (0.12 + h) / 2), (0.012, breite - rahmen, h - 0.2), m["stoff_rot_alt"], fase=0,
                 drehung=winkel)


# ------------------------------------------------------------------ Waschtisch
def wasch(m, felder):
    s.quader((0, 0, 0.78), (0.55, 0.42, 0.04), m["holz"], fase=0.01)
    for ex in (-1, 1):
        for ey in (-1, 1):
            s.quader((ex * 0.24, ey * 0.17, 0.39), (0.04, 0.04, 0.78), m["holz"], fase=0.005)
    s.quader((0, 0, 0.18), (0.5, 0.38, 0.03), m["holz"], fase=0.005)
    s.kugel((0.06, 0.02, 0.83), 0.18, m["keramik"], (1, 1, 0.35))
    s.zylinder((-0.17, -0.06, 0.9), 0.06, 0.2, m["keramik"], ecken=16, fase=0.01)
    s.zylinder((-0.1, 0.08, 0.26), 0.07, 0.14, m["keramik"], ecken=16)
    s.quader((0.26, 0.0, 0.62), (0.02, 0.25, 0.35), m["leinen"], fase=0.01)        # Handtuch


# ------------------------------------------------------------------ Teppich
def teppich(m, felder):
    s.quader((0, 0, 0.004), (0.85, 1.25, 0.008), m["stoff_rot_alt"], fase=0)
    s.quader((0, 0, 0.009), (0.65, 1.05, 0.004), m["stoff_rot"], fase=0)


# ------------------------------------------------------------------ Preistafel
def schild(m, felder):
    import bpy
    w = ZUR_KAMERA + math.pi / 2          # Tafel quer zur Blickrichtung
    nx, ny = math.cos(ZUR_KAMERA), math.sin(ZUR_KAMERA)
    for seite in (-1, 1):
        # zwei Beine je Seite (Aufsteller), leicht gespreizt
        for vorn in (-1, 1):
            px = math.cos(w) * seite * 0.32 + nx * vorn * 0.12
            py = math.sin(w) * seite * 0.32 + ny * vorn * 0.12
            s.quader((px, py, 0.5), (0.035, 0.035, 1.0), m["holz_hell"], drehung=w)
    s.quader((nx * 0.02, ny * 0.02, 0.6), (0.62, 0.03, 0.72), m["schiefer"], drehung=w, fase=0.005)
    s.quader((nx * 0.02, ny * 0.02, 0.97), (0.66, 0.05, 0.04), m["holz_hell"], drehung=w)
    s.quader((nx * 0.02, ny * 0.02, 0.23), (0.66, 0.05, 0.04), m["holz_hell"], drehung=w)
    zeilen = ["ROOMS", "DRINKS", "NO GUNS"]
    for i, t in enumerate(zeilen):
        bpy.ops.object.text_add(location=(nx * 0.04, ny * 0.04, 0.83 - i * 0.2),
                                rotation=(math.pi / 2, 0, w))
        o = bpy.context.object
        o.data.body = t
        o.data.size = 0.10
        o.data.align_x = "CENTER"
        o.data.extrude = 0.002
        o.data.materials.append(m["kreide"])


MODELLE = dict(rllatern=latern, rlbett=bett, rlparavnt=paravent, rlwasch=wasch, rlteppich=teppich, rlschild=schild)

# Leinwand je Objekt: Breite, Hoehe, Ursprung (x, y) im Bild
LEINWAND = dict(rllatern=(160, 200, 80, 170), rlbett=(260, 240, 140, 200), rlparavnt=(200, 240, 140, 200),
                rlwasch=(140, 150, 70, 120), rlteppich=(160, 120, 80, 60), rlschild=(140, 160, 70, 130))
