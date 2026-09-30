"""Blender-Szene fuer Fallout-2-Szenerie (laeuft mit dem Python-Modul bpy).

Kamera und Massstab aus geometrie.py. Das Licht folgt den Vanilla-Grafiken:
ein Hauptlicht von links oben, ein schwaches Gegenlicht, gedaempftes Umgebungslicht,
keine Schatten auf dem Boden (die Engine hat keine). Gerendert wird mit Cycles
auf der CPU, Filter 1 Pixel fuer harte Kanten, Farbraum "Standard", damit die
Farben so bleiben, wie sie gewaehlt sind (wichtig fuer die reine Rotreihe der Palette).

Zwei Durchgaenge je Objekt:
  bild.png    das Objekt mit Licht und Material
  leucht.png  weiss, wo leuchtende Flaechen sichtbar sind (Farbe 254 im FRM)
"""
import math

import bpy
from mathutils import Matrix, Vector

import geometrie as g


def leeren():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 96
    sc.cycles.use_denoising = False
    sc.cycles.max_bounces = 4
    sc.cycles.filter_width = 1.0
    sc.render.film_transparent = True
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    welt = bpy.data.worlds.new("welt")
    sc.world = welt
    welt.use_nodes = True
    welt.node_tree.nodes["Background"].inputs["Color"].default_value = (0.5, 0.5, 0.5, 1)
    welt.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.12
    return sc


def kamera(sc, breite, hoehe, ursprung_x, ursprung_y):
    """Orthografische Kamera; der Weltursprung landet auf Pixel (ursprung_x, ursprung_y)."""
    bpy.ops.object.camera_add()
    cam = bpy.context.object
    cam.data.type = "ORTHO"
    cam.data.sensor_fit = "HORIZONTAL"
    cam.data.ortho_scale = breite / g.K
    cam.data.clip_start = 0.1
    cam.data.clip_end = 100
    r, u, z = Vector(g.KAMERA_R), Vector(g.KAMERA_U), Vector(g.KAMERA_Z)
    a = (breite / 2 - ursprung_x) / g.K
    b = (ursprung_y - hoehe / 2) / g.K
    pos = z * 30 + r * a + u * b
    m = Matrix((r, u, z)).transposed().to_4x4()
    m.translation = pos
    cam.matrix_world = m
    sc.camera = cam
    sc.render.resolution_x = breite
    sc.render.resolution_y = hoehe
    sc.render.resolution_percentage = 100
    return cam


def licht():
    # Hauptlicht von links oben (aus Sicht der Kamera), leicht warm
    bpy.ops.object.light_add(type="SUN")
    haupt = bpy.context.object
    haupt.data.energy = 5.0
    haupt.data.color = (1.0, 0.97, 0.92)
    haupt.data.angle = math.radians(8)
    haupt.rotation_euler = (math.radians(48), 0, math.radians(-75))
    # Gegenlicht, schwach und kuehl
    bpy.ops.object.light_add(type="SUN")
    gegen = bpy.context.object
    gegen.data.energy = 0.6
    gegen.data.color = (0.85, 0.9, 1.0)
    gegen.rotation_euler = (math.radians(60), 0, math.radians(110))
    return haupt, gegen


# ------------------------------------------------------------------ Materialien
def material(name, farbe, rauheit=0.8, metall=0.0, textur=None, textur_staerke=0.25, relief=0.0,
             leucht=0.0, massstab=12.0, glanz=0.5, schmutz=0.3):
    """Principled-Material mit optionaler prozeduraler Textur:
    textur = "holz" (Maserung), "stoff" (feines Rauschen), "rost", "rauschen".
    glanz: Staerke der Spiegelung (Stoff fast 0, sonst werden rote Flaechen grau-braun).
    schmutz: wie stark grobe Flecken die Farbe abdunkeln (0 = sauber)."""
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*farbe, 1)
    bsdf.inputs["Roughness"].default_value = rauheit
    bsdf.inputs["Metallic"].default_value = metall
    bsdf.inputs["Specular IOR Level"].default_value = glanz
    if leucht:
        bsdf.inputs["Emission Color"].default_value = (*farbe, 1)
        bsdf.inputs["Emission Strength"].default_value = leucht
    if textur:
        koord = nt.nodes.new("ShaderNodeTexCoord")
        if textur == "holz":
            t = nt.nodes.new("ShaderNodeTexWave")
            t.inputs["Scale"].default_value = massstab
            t.inputs["Distortion"].default_value = 6.0
            t.inputs["Detail"].default_value = 3.0
        else:
            t = nt.nodes.new("ShaderNodeTexNoise")
            t.inputs["Scale"].default_value = massstab * (4 if textur == "stoff" else 1)
            t.inputs["Detail"].default_value = 6.0
        nt.links.new(koord.outputs["Object"], t.inputs["Vector"])
        mix = nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.inputs["A"].default_value = (*[c * (1 - textur_staerke) for c in farbe], 1)
        mix.inputs["B"].default_value = (*[min(1.0, c * (1 + textur_staerke)) for c in farbe], 1)
        if textur == "rost":
            mix.inputs["B"].default_value = (0.22, 0.09, 0.03, 1)
        nt.links.new(t.outputs["Fac"], mix.inputs["Factor"])
        farbe_aus = mix.outputs["Result"]
        if schmutz:
            # grobe dunkle Flecken ueber der Textur: Benutzungsspuren wie bei Vanilla
            fleck = nt.nodes.new("ShaderNodeTexNoise")
            fleck.inputs["Scale"].default_value = 3.0
            fleck.inputs["Detail"].default_value = 4.0
            nt.links.new(koord.outputs["Object"], fleck.inputs["Vector"])
            rampe = nt.nodes.new("ShaderNodeMapRange")
            rampe.inputs["From Min"].default_value = 0.35
            rampe.inputs["From Max"].default_value = 0.65
            rampe.inputs["To Min"].default_value = 1.0 - schmutz
            rampe.inputs["To Max"].default_value = 1.0
            nt.links.new(fleck.outputs["Fac"], rampe.inputs["Value"])
            dunkel = nt.nodes.new("ShaderNodeMix")
            dunkel.data_type = "RGBA"
            dunkel.blend_type = "MULTIPLY"
            dunkel.inputs["Factor"].default_value = 1.0
            nt.links.new(farbe_aus, dunkel.inputs["A"])
            nt.links.new(rampe.outputs["Result"], dunkel.inputs["B"])
            farbe_aus = dunkel.outputs["Result"]
        nt.links.new(farbe_aus, bsdf.inputs["Base Color"])
        if relief:
            bump = nt.nodes.new("ShaderNodeBump")
            bump.inputs["Strength"].default_value = relief
            nt.links.new(t.outputs["Fac"], bump.inputs["Height"])
            nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    m["leucht"] = 1 if leucht else 0
    return m


# ------------------------------------------------------------------ Formen
def _fertig(o, mat, fase=0.0):
    o.data.materials.append(mat)
    if fase:
        mod = o.modifiers.new("fase", "BEVEL")
        mod.width = fase
        mod.segments = 2
    return o


def quader(mitte, groesse, mat, fase=0.01, drehung=0.0):
    bpy.ops.mesh.primitive_cube_add(location=mitte, rotation=(0, 0, drehung))
    o = bpy.context.object
    o.scale = (groesse[0] / 2, groesse[1] / 2, groesse[2] / 2)
    return _fertig(o, mat, fase)


def zylinder(mitte, radius, hoehe, mat, ecken=16, fase=0.0, achse="z"):
    rot = {"z": (0, 0, 0), "x": (0, math.pi / 2, 0), "y": (math.pi / 2, 0, 0)}[achse]
    bpy.ops.mesh.primitive_cylinder_add(vertices=ecken, radius=radius, depth=hoehe, location=mitte, rotation=rot)
    return _fertig(bpy.context.object, mat, fase)


def kugel(mitte, radius, mat, skalierung=(1, 1, 1)):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=24, ring_count=12, radius=radius, location=mitte)
    o = bpy.context.object
    o.scale = skalierung
    bpy.ops.object.shade_smooth()
    return _fertig(o, mat)


def weich(o, stufen=2):
    mod = o.modifiers.new("weich", "SUBSURF")
    mod.levels = stufen
    mod.render_levels = stufen
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.shade_smooth()
    return o


# ------------------------------------------------------------------ Rendern
def rendern(sc, pfad_bild, pfad_leucht):
    sc.render.filepath = str(pfad_bild)
    bpy.ops.render.render(write_still=True)
    # Leuchtmaske: alles schwarz und undurchsichtig, Leuchtflaechen weiss, ohne Licht
    schwarz = bpy.data.materials.new("maske_schwarz")
    schwarz.use_nodes = True
    s = schwarz.node_tree.nodes["Principled BSDF"]
    s.inputs["Base Color"].default_value = (0, 0, 0, 1)
    s.inputs["Roughness"].default_value = 1
    s.inputs["Specular IOR Level"].default_value = 0
    weiss = bpy.data.materials.new("maske_weiss")
    weiss.use_nodes = True
    w = weiss.node_tree.nodes["Principled BSDF"]
    w.inputs["Base Color"].default_value = (0, 0, 0, 1)
    w.inputs["Emission Color"].default_value = (1, 1, 1, 1)
    w.inputs["Emission Strength"].default_value = 5
    for o in list(bpy.data.objects):
        if o.type == "LIGHT":
            o.hide_render = True
        elif o.type == "MESH" or o.type == "FONT":
            leuchtend = any(ms.material and ms.material.get("leucht") for ms in o.material_slots)
            for ms in o.material_slots:
                ms.material = weiss if leuchtend else schwarz
    sc.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0
    sc.render.filepath = str(pfad_leucht)
    bpy.ops.render.render(write_still=True)
