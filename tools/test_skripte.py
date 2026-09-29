#!/usr/bin/env python3
"""test_skripte.py - spielt die kompilierten Skripte im Pruefwerkzeug durch.

Aufruf (nach tools/build_scripts.sh mit RL_DEBUG=1):
    python3 tools/test_skripte.py [--build build/rpu-v2.4.34] [--fo2 <scripts_src der RPU>]
                                  [-k name] [-v]

Jeder Test startet eine frische Spielwelt (tools/intvm.py), laedt das
globale Skript wie beim Laden eines Spielstands und spielt Dialoge,
Kartenwechsel und Wochen durch. Geprueft wird der Zustand danach; dazu
laufen bei jedem Test die allgemeinen Pruefungen:
  - kein Skriptfehler (Division durch null, falscher Typ, Endlosschleife)
  - kein fehlender Text ("Error" im Spiel)
  - keine Dialog-Antwort, die nie angezeigt wird
  - kein Array-Zugriff ausserhalb der Grenzen

Dazu kommt die Erkundung: Alle Dialogpfade der Figuren werden bis zu einer
Tiefe durchprobiert, aus mehreren Spielstaenden heraus.
"""

import argparse
import copy
import os
import sys
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import intvm  # noqa: E402
from intvm import Konstanten, Spiel, SkriptFehler, Programm  # noqa: E402

WURZEL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Programme sind unveraenderlich; beim Kopieren der Welt nicht mitkopieren
Programm.__deepcopy__ = lambda self, memo: self


class Halt(Exception):
    """Bricht einen Dialog an einer Entscheidung ab (Erkundung)."""

    def __init__(self, antwort, optionen):
        super().__init__(antwort)
        self.antwort = antwort
        self.optionen = optionen


def lies_build(build):
    werte = {}
    for zeile in open(os.path.join(build, 'scripts', 'rl_build.txt')):
        if '=' in zeile:
            k, v = zeile.strip().split('=', 1)
            werte[k] = int(v)
    return werte


def skriptliste():
    namen = []
    for zeile in open(os.path.join(WURZEL, 'install', 'scripts.lst.add'), encoding='latin-1'):
        zeile = zeile.strip()
        if zeile and not zeile.startswith('#'):
            namen.append(zeile.split('.')[0].lower())
    return namen


class Umgebung:
    def __init__(self, build, fo2):
        self.build = build
        self.cfg = lies_build(build)
        self.k = Konstanten()
        extra = {'RL_SCRIPT_BASE': str(self.cfg['RL_SCRIPT_BASE']),
                 'RL_GVAR_BASE': str(self.cfg['RL_GVAR_BASE']),
                 'RL_MAP_INDEX': str(self.cfg['RL_MAP_INDEX'])}
        hdr = os.path.join(WURZEL, 'scripts_src', 'headers')
        for f in ['rotlicht.h'] + sorted(n for n in os.listdir(hdr) if n.startswith('rl_') and n.endswith('.h')):
            self.k.lade(os.path.join(hdr, f), extra)
        for f in ('global.h', 'maps.h', 'critrpid.h', 'itempid.h', 'define.h', 'den.h'):
            p = os.path.join(fo2, 'headers', f)
            if os.path.exists(p):
                self.k.lade(p)
        self.namen = skriptliste()

    def neues_spiel(self, seed=1):
        sp = Spiel(os.path.join(self.build, 'scripts'),
                   os.path.join(self.build, 'text', 'english'),
                   self.cfg['RL_SCRIPT_BASE'], self.k, seed)
        for n in self.namen:
            sp.registriere(n)
        sp.dude.stats[self.k['STAT_iq']] = 6
        sp.dude.kronkorken = 3000
        sp.lade_global('gl_rotlicht')
        return sp


# --------------------------------------------------------------------------
# Hilfen

class Welt:
    """Bequemer Zugriff auf die sfall-Arrays des Mods."""

    def __init__(self, sp, k):
        self.sp = sp
        self.k = k

    @property
    def w(self):
        return self.sp.welt_array('RL_WELT')

    @property
    def haeuser(self):
        return self.sp.welt_array('RL_HAUS')

    def welt(self, feld):
        return self.w[self.k[feld]]

    def setze_welt(self, feld, wert):
        self.w[self.k[feld]] = wert

    def haus(self, h, feld):
        return self.haeuser[h * self.k['RL_FELDER'] + self.k[feld]]

    def setze_haus(self, h, feld, wert):
        self.haeuser[h * self.k['RL_FELDER'] + self.k[feld]] = wert


def figuren(sp, k):
    """Essie, Kolbe und das Kartenskript wie auf der Karte RLDEN01 (bau_karten.py)."""
    sp.karte = k['RL_MAP_INDEX']
    essie = sp.erzeuge(0x1000042, k['RL_GOSSE_ESSIE_HEX'], 0, k['SCRIPT_RLESSIE'], 'Essie')
    kolbe = sp.erzeuge(0x100001E, k['RL_GOSSE_KOLBE_HEX'], 0, k['SCRIPT_RLKOLBE'], 'Kolbe')
    sp.erzeuge(0, -1, 0, k['SCRIPT_RLDEN01'], 'Kartenskript')
    return essie, kolbe


def gosse(sp, k):
    """Die Gosse betreten: Kartenskript und Figuren reagieren (map_enter_p_proc)."""
    sp.betrete_karte(k['RL_MAP_INDEX'])
    sp.temp_freigeben()


def figur(sp, k, name):
    """Die (eine) lebende Figur mit dem Skript SCRIPT_<NAME>."""
    fs = sp.finde(k['SCRIPT_' + name])
    pruefe(len(fs) == 1, f'{name}: {len(fs)} Figuren statt einer')
    return fs[0]


def keine_figur(sp, k, name):
    pruefe(not sp.finde(k['SCRIPT_' + name]), f'{name} ist noch da')


def woche(sp, n=1):
    for _ in range(n):
        sp.zeit += 604800 * 10
        sp.tick()
        sp.temp_freigeben()


def allgemein(sp, name):
    fehler = []
    if sp.fehlende_texte:
        fehler.append(f'fehlende Texte: {sorted(set(sp.fehlende_texte))[:8]}')
    if sp.dialog_fehler:
        fehler.append(f'Dialog: {sp.dialog_fehler[:3]}')
    if sp.array_ausserhalb:
        fehler.append(f'Array ausserhalb: {sp.array_ausserhalb[:5]}')
    if sp.ungueltige_arrays:
        fehler.append(f'ungueltige Array-IDs: {sp.ungueltige_arrays[:5]}')
    for m in sp.meldungen:
        if 'Error' in m:
            fehler.append(f'Meldung mit Error: {m}')
    if sp.abgeblendet:
        fehler.append('Bildschirm bleibt schwarz (gfade_out ohne gfade_in)')
    if fehler:
        raise AssertionError(f'{name}: ' + '; '.join(fehler))


def pruefe(bed, text):
    if not bed:
        raise AssertionError(text)


def rede(sp, obj, plan):
    verlauf = sp.rede(obj, plan)
    sp.temp_freigeben()
    return verlauf


def texte(verlauf):
    return ' | '.join(a for a, _, _ in verlauf)


# --------------------------------------------------------------------------
# Erkundung aller Dialogpfade

class Erkunder(intvm.Spieler):
    def waehle(self, antwort, optionen):
        if self.plan:
            i = self.plan.pop(0)
            if i >= len(optionen):
                raise SkriptFehler(f'Erkundung: Option {i} fehlt')
            return i
        raise Halt(antwort, optionen)


def _signatur(sp):
    teile = []
    for key in ('RL_WELT', 'RL_HAUS'):
        a = sp.welt_array(key)
        teile.append(tuple(a) if a else ())
    return (tuple(teile), sp.dude.kronkorken, len(sp.meldungen))


def erkunde(sp, obj, name, max_laeufe=4000, max_tiefe=40):
    """Probiert alle Dialogpfade von obj aus dem Zustand sp heraus.
    Liefert (Zahl der Laeufe, Zahl der Knoten). Fehler werfen AssertionError."""
    offen = [[]]
    gesehen = set()
    laeufe = 0
    knoten = 0
    while offen:
        plan = offen.pop(0)            # Breitensuche: kurze Wege zuerst
        laeufe += 1
        if laeufe > max_laeufe:
            raise AssertionError(f'{name}: Erkundung bricht nach {max_laeufe} Laeufen ab')
        kopie, o = copy.deepcopy((sp, obj))
        kopie.spieler = Erkunder(plan)
        kopie.dialog_verlauf = []
        kopie.dialog_optionen = []
        kopie.dialog_antwort = None
        halt = None
        try:
            o.skript.rufe('talk_p_proc', self_obj=o, source=kopie.dude)
        except Halt as h:
            halt = h
        except SkriptFehler as e:
            raise AssertionError(f'{name}: Pfad {plan}: {e}')
        pfad = ' > '.join(t for _, _, t in kopie.dialog_verlauf)
        try:
            allgemein(kopie, name)
        except AssertionError as e:
            raise AssertionError(f'{e} (Pfad: {pfad})')
        if halt is None:
            continue
        # Knotenabdeckung: jede Antwort mit ihren Optionen einmal ausklappen.
        # Zustandsabhaengige Zweige kommen aus den verschiedenen Startzustaenden.
        sig = (halt.antwort, tuple(o[0] for o in halt.optionen))
        if sig in gesehen:
            continue
        gesehen.add(sig)
        knoten += 1
        if not halt.antwort or 'Error' in halt.antwort:
            raise AssertionError(f'{name}: leere Antwort (Pfad: {pfad})')
        if len(plan) >= max_tiefe:
            raise AssertionError(f'{name}: Dialog tiefer als {max_tiefe} (Pfad: {pfad})')
        for i, opt in enumerate(halt.optionen):
            if 'Error' in opt[0] or not opt[0].strip():
                raise AssertionError(f'{name}: Option ohne Text nach "{halt.antwort[:50]}" (Pfad: {pfad})')
            if opt[0].startswith('[Debug]'):
                continue          # Debug-Optionen testen die Szenarien gezielt
            offen.append(plan + [i])
    return laeufe, knoten


# --------------------------------------------------------------------------
# Tests

def test_eingang(u):
    sp = u.neues_spiel()
    k = u.k
    sp.betrete_karte(k['MAP_DEN_BUSINESS'])
    treppen = [o for o in sp.objekte if o.pid == k['RL_GOSSE_TREPPE_PID']]
    pruefe(len(treppen) == 1, f'eine Treppe erwartet, {treppen}')
    t = treppen[0]
    pruefe(t.tile == k['RL_GOSSE_TREPPE_HEX'] and t.skript_nr == k['SCRIPT_RLGOSSE'], 'Treppe falsch')
    # zweites Betreten: keine zweite Treppe
    sp.betrete_karte(k['MAP_DEN_BUSINESS'])
    sp.tick()
    pruefe(len([o for o in sp.objekte if o.pid == k['RL_GOSSE_TREPPE_PID']]) == 1, 'Treppe doppelt')
    # Benutzen fuehrt in die Gosse
    t.skript.rufe('use_p_proc', self_obj=t, source=sp.dude)
    pruefe(t.skript.overrides, 'use_p_proc ohne script_overrides')
    pruefe(sp.karten_wechsel == [('rlden01.map', 0)], f'Kartenwechsel {sp.karten_wechsel}')
    # Ein anderer Benutzer (z. B. Begleiter) loest nichts aus
    andere = sp.erzeuge(0x1000001, 100, 0, -1, 'Begleiter')
    t.skript.rufe('use_p_proc', self_obj=t, source=andere)
    pruefe(len(sp.karten_wechsel) == 1, 'Begleiter hat die Karte gewechselt')
    # Im Kampf nicht
    sp.kampf = True
    t.skript.rufe('use_p_proc', self_obj=t, source=sp.dude)
    pruefe(len(sp.karten_wechsel) == 1, 'Kartenwechsel im Kampf')
    # Die Gosse selbst: erster Besuch zeigt die Stimmung
    sp.kampf = False
    gosse = sp.erzeuge(0, -1, 0, k['SCRIPT_RLDEN01'], 'Kartenskript')
    sp.meldungen.clear()
    sp.karte = k['RL_MAP_INDEX']
    sp.erster_besuch = True
    gosse.skript.rufe('map_enter_p_proc', self_obj=gosse)
    pruefe(len(sp.meldungen) == 1, f'Meldung beim ersten Besuch {sp.meldungen}')
    allgemein(sp, 'eingang')


def prolog(u, weg='bezahlt', sp=None):
    """Spielt den Prolog auf einem Weg durch; liefert (sp, essie, kolbe, w)."""
    k = u.k
    sp = sp or u.neues_spiel()
    w = Welt(sp, k)
    essie, kolbe = figuren(sp, k)
    v = rede(sp, essie, ['How much', 'deal with Kolbe', 'go see him'])
    pruefe(w.welt('RL_W_PROLOG') == k['RL_PROLOG_LAEUFT'], 'Prolog nicht gestartet')
    pruefe('Twelve hundred' in texte(v), 'Schuldenhoehe fehlt')
    v = rede(sp, essie, [])
    pruefe('1200' in texte(v), f'Essie nennt die Schulden nicht: {texte(v)}')
    geld = sp.dude.kronkorken
    if weg == 'bezahlt':
        rede(sp, kolbe, ["Here's the money", 'Good'])
        pruefe(sp.dude.kronkorken == geld - 1200, f'Kronkorken {sp.dude.kronkorken}')
        pruefe(w.welt('RL_W_PROLOG_WEG') == k['RL_WEG_BEZAHLT'], 'Weg')
    elif weg == 'barter':
        sp.dude.skills[k['SKILL_BARTER']] = 60
        rede(sp, kolbe, ['[Barter]', "Here's the money", 'Good'])
        pruefe(sp.dude.kronkorken == geld - 900, f'Rabatt: {geld - sp.dude.kronkorken}')
    elif weg == 'speech':
        sp.dude.skills[k['SKILL_SPEECH']] = 70
        rede(sp, kolbe, ['[Speech]', 'Good'])
        pruefe(w.welt('RL_W_PROLOG_WEG') == k['RL_WEG_PARTNER'], 'Partner')
    elif weg == 'faust':
        sp.dude.stats[k['STAT_st']] = 8
        rede(sp, kolbe, ['Get lost', 'keep talking', "Here's the money", 'Good'])
        pruefe(sp.dude.kronkorken == geld - 600, f'halbe Schulden: {geld - sp.dude.kronkorken}')
        pruefe(w.welt('RL_W_PROLOG_WEG') == k['RL_WEG_VERPRUEGELT'], 'verpruegelt')
    elif weg == 'diebstahl':
        sp.dude.skills[k['SKILL_STEAL']] = 80
        sp.zufall_folge = [1]
        rede(sp, kolbe, ['[Steal]', 'Good'])
        pruefe(w.welt('RL_W_PROLOG_WEG') == k['RL_WEG_GESTOHLEN'], 'gestohlen')
    elif weg == 'ausliefern':
        rede(sp, kolbe, ['Take her with you', 'Do it', 'Good'])
        pruefe(w.welt('RL_W_PROLOG_WEG') == k['RL_WEG_AUSGELIEFERT'], 'ausgeliefert')
    else:
        raise ValueError(weg)
    pruefe(w.welt('RL_W_PROLOG') == k['RL_PROLOG_FERTIG'], 'Prolog nicht fertig')
    pruefe(w.haus(0, 'RL_F_BESITZ') == 1, 'Gosse nicht uebernommen')
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_ANGEBOT'], 'Ketten Akt 1 nicht offen')
    return sp, essie, kolbe, w


def test_prolog_wege(u):
    for weg in ('bezahlt', 'barter', 'speech', 'faust', 'diebstahl', 'ausliefern'):
        sp, essie, kolbe, w = prolog(u, weg)
        if weg == 'ausliefern':
            sp.meldungen.clear()
            essie.skript.rufe('critter_p_proc', self_obj=essie)
            pruefe(essie.zerstoert, 'Essie noch da nach der Auslieferung')
        else:
            v = rede(sp, essie, ['Go on', 'Later'])
            pruefe(v[0][0].startswith(('You paid', 'Now Metzger', 'Nobody', 'The debt')), f'Reaktion: {v[0][0]}')
        allgemein(sp, f'prolog {weg}')


def test_diebstahl_erwischt(u):
    k = u.k
    sp = u.neues_spiel()
    w = Welt(sp, k)
    essie, kolbe = figuren(sp, k)
    rede(sp, essie, ['deal with Kolbe', 'go see him'])
    sp.dude.skills[k['SKILL_STEAL']] = 55
    sp.zufall_folge = [99]
    rede(sp, kolbe, ['[Steal]', None])
    pruefe(w.welt('RL_W_METZGER') == k['RL_METZGER_FEIND'], 'Metzger nicht Feind')
    pruefe(sp.angriffe and sp.angriffe[-1][0] is kolbe, 'Kolbe greift nicht an')
    allgemein(sp, 'diebstahl erwischt')


def test_ketten_annehmen(u):
    k = u.k
    sp, essie, kolbe, w = prolog(u, 'bezahlt')
    rede(sp, essie, ['Go on', 'Later'])
    zimmer, personal = w.haus(0, 'RL_F_ZIMMER'), w.haus(0, 'RL_F_PERSONAL')
    w.setze_haus(0, 'RL_F_KASSE', 100)
    geld = sp.dude.kronkorken
    v = rede(sp, kolbe, ['And if I say no', 'Deal. Bring them', 'Pleasure' if False else None])
    pruefe('Two from the pens' in v[0][0], f'Angebot: {v[0][0]}')
    pruefe(w.haus(0, 'RL_F_KASSE') == 0 and sp.dude.kronkorken == geld - 250,
           f'Bezahlung Kasse {w.haus(0, "RL_F_KASSE")}, Tasche {geld - sp.dude.kronkorken}')
    pruefe(w.haus(0, 'RL_F_ZWANG') == 2, 'Zwangspersonal')
    pruefe(w.haus(0, 'RL_F_PERSONAL') == personal + 2 and w.haus(0, 'RL_F_ZIMMER') == zimmer + 2, 'Zimmer/Personal')
    pruefe(w.welt('RL_W_METZGER') == k['RL_METZGER_FREUND'], 'Metzger Freund')
    pruefe(w.welt('RL_W_KETTEN_ZWEIG') == k['RL_KETTEN_ZWEIG_TYRANN'], 'Zweig')
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_KELLER'], 'Akt 2')
    v = rede(sp, essie, ['Go on', 'Later'])
    pruefe(v[0][0].startswith("Metzger's men came"), f'Essie: {v[0][0]}')
    # Kolbe geht beim naechsten Betreten
    sp.betrete_karte(k['RL_MAP_INDEX'])
    pruefe(kolbe.zerstoert, 'Kolbe noch da')
    pruefe(w.welt('RL_W_METZGER') == k['RL_METZGER_FREUND'], 'destroy_p_proc hat Metzger veraendert')
    allgemein(sp, 'ketten annehmen')


def test_ketten_ablehnen(u):
    k = u.k
    sp, essie, kolbe, w = prolog(u, 'bezahlt')
    rede(sp, essie, ['Go on', 'Later'])
    rede(sp, kolbe, ['No. Not in my house', None])
    pruefe(w.welt('RL_W_METZGER_NEIN') == 1 and w.welt('RL_W_KETTEN_ZWEIG') == k['RL_KETTEN_ZWEIG_FLUCHT'], 'Ablehnung')
    v = rede(sp, essie, ['Go on', 'Later'])
    pruefe(v[0][0].startswith('Kolbe told half the Den'), f'Essie: {v[0][0]}')
    allgemein(sp, 'ketten ablehnen')


def test_ketten_kein_geld(u):
    k = u.k
    sp, essie, kolbe, w = prolog(u, 'bezahlt')
    sp.dude.kronkorken = 100
    w.setze_haus(0, 'RL_F_KASSE', 0)
    v = rede(sp, kolbe, ["I don't have that kind", None])
    pruefe('The offer stands' in v[-1][0] or 'offer stands' in texte(v), 'kein Hinweis')
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_ANGEBOT'], 'Angebot verfallen')
    allgemein(sp, 'ketten kein geld')


def test_kolbe_stirbt(u):
    k = u.k
    sp, essie, kolbe, w = prolog(u, 'bezahlt')
    sp.zerstoere(kolbe)
    pruefe(w.welt('RL_W_METZGER') == k['RL_METZGER_FEIND'], 'Metzger nicht Feind')
    pruefe(w.welt('RL_W_KETTEN_ZWEIG') == k['RL_KETTEN_ZWEIG_FLUCHT'], 'Zweig')
    allgemein(sp, 'kolbe stirbt')


def test_kolbe_kommt_zurueck(u):
    """Spielstand aus Umsetzung 1-3: Prolog fertig, Kolbe weg, Angebot offen."""
    k = u.k
    sp, essie, kolbe, w = prolog(u, 'bezahlt')
    kolbe.zerstoert = True
    sp.objekte.remove(kolbe)
    karte = sp.erzeuge(0, -1, 0, k['SCRIPT_RLDEN01'], 'Kartenskript')
    sp.karte = k['RL_MAP_INDEX']
    karte.skript.rufe('map_enter_p_proc', self_obj=karte)
    neu = sp.finde(k['SCRIPT_RLKOLBE'])
    pruefe(len(neu) == 1 and neu[0].tile == k['RL_GOSSE_KOLBE_HEX'], f'Kolbe nicht zurueck: {neu}')
    karte.skript.rufe('map_enter_p_proc', self_obj=karte)
    pruefe(len(sp.finde(k['SCRIPT_RLKOLBE'])) == 1, 'Kolbe doppelt')
    allgemein(sp, 'kolbe kommt zurueck')


def test_wochen(u):
    """Wochenabrechnung laeuft, die Kasse waechst, nichts bricht."""
    k = u.k
    sp, essie, kolbe, w = prolog(u, 'bezahlt')
    sp.zeit = 0
    sp.tick()
    kasse = w.haus(0, 'RL_F_KASSE')
    woche(sp, 4)
    pruefe(w.haus(0, 'RL_F_KASSE') != kasse, 'Kasse unveraendert nach 4 Wochen')
    pruefe(w.haus(0, 'RL_F_KUNDEN') > 0, 'keine Kunden')
    allgemein(sp, 'wochen')


def test_wirtschaft_paritaet(u):
    """Die kompilierte Wochenrechnung gegen tools/economy_sim.py: 400 zufaellige
    Haeuser, je 10 Wochen, alle Staedte, Preise, Anteile und Anwerbung."""
    import random
    import economy_sim as E
    k = u.k
    sp = u.neues_spiel()
    w = Welt(sp, k)
    g = sp.globale[0]
    hid = sp.gespeichert['RL_HAUS']
    staedte = ['den', 'new_reno', 'redding', 'vault_city', 'ncr', 'san_fran']
    preise = ['ramsch', 'standard', 'gehoben', 'exklusiv']
    anteile = ['ausbeuterisch', 'branchenueblich', 'fair']
    rng = random.Random(7)
    karma_gvar = k['GVAR_PLAYER_REPUTATION']
    for fall in range(400):
        c = dict(stadt=rng.randrange(6), quali=rng.randint(20, 85), moral=rng.randint(0, 100),
                 ruf=rng.randint(0, 100), aus=rng.randint(0, 100), sich=rng.randint(0, 120),
                 hitze=rng.randint(0, 60), preis=rng.randrange(4), anteil=rng.randrange(3),
                 bar=rng.randint(0, 2), neben=rng.randint(0, 10), kontor=rng.random() < 0.5,
                 kranken=rng.random() < 0.3, stufen=rng.randint(0, 12), loehne=rng.randint(0, 400),
                 smod=rng.randint(-40, 40), mmod=rng.randint(0, 30), zimmer=rng.randint(1, 10),
                 personal=rng.randint(1, 10), bonus=rng.randint(0, 3),
                 gezwungen=rng.choice([0, 0, 1, 2]), anwerber=rng.randrange(3),
                 pmod=rng.choice([0, 0, 15, rng.randint(0, 40)]), bmod=rng.choice([0, 0, -75, 50, 400]),
                 zu=rng.random() < 0.1, rmod=rng.choice([0, 0, 3]))
        c['zwang'] = rng.choice([0, 0, min(2, c['personal'])])
        for i in range(k['RL_FELDER']):
            sp.arrays[hid].werte[i] = 0
        felder = dict(RL_F_BESITZ=1, RL_F_QUALI=c['quali'], RL_F_MORAL=c['moral'], RL_F_RUF=c['ruf'],
                      RL_F_AUSSTATTUNG=c['aus'], RL_F_SICHERHEIT=c['sich'], RL_F_HITZE=c['hitze'],
                      RL_F_PREISSTUFE=c['preis'], RL_F_ANTEIL=c['anteil'], RL_F_BAR=c['bar'],
                      RL_F_NEBEN=c['neben'], RL_F_STUFEN=c['stufen'], RL_F_LOEHNE=c['loehne'],
                      RL_F_STADTMOD=c['smod'], RL_F_MODUL_STADTMOD=c['mmod'], RL_F_ZIMMER=c['zimmer'],
                      RL_F_PERSONAL=c['personal'], RL_F_MORALBONUS=c['bonus'],
                      RL_F_GEZWUNGEN=c['gezwungen'], RL_F_ANWERBER=c['anwerber'], RL_F_ZWANG=c['zwang'],
                      RL_F_PREISMOD=c['pmod'], RL_F_BESTECHUNG_MOD=c['bmod'], RL_F_GESCHLOSSEN=1 if c['zu'] else 0, RL_F_RISIKO_MOD=c['rmod'],
                      RL_F_MODULE=(k['RL_MOD_KONTOR'] if c['kontor'] else 0)
                      | (k['RL_MOD_KRANKENSTUBE'] if c['kranken'] else 0))
        for f, v in felder.items():
            w.setze_haus(0, f, v)
        sp.gvars[karma_gvar] = 0
        ist = []
        for _ in range(10):
            gewinn = g.rufe_mit('rl_rechne_woche', hid, 0, c['stadt'])
            ist.append((w.haus(0, 'RL_F_KUNDEN'), gewinn))
            sp.temp_freigeben()
        rows, _, karma = E.simulate(
            staedte[c['stadt']], weeks=10, staff_q=c['quali'], furnishing=c['aus'], rep=c['ruf'],
            moral=c['moral'], price_tier=preise[c['preis']], share_tier=anteile[c['anteil']],
            security=c['sich'], heat=c['hitze'], accountant=c['kontor'], doc=c['kranken'],
            bar_level=c['bar'], upgrade_levels=c['stufen'], fixed_wages=c['loehne'],
            city_mod=100 + c['smod'] + c['mmod'], rooms=min(c['zimmer'], c['personal']),
            side_per_client=c['neben'], moral_bonus=c['bonus'], forced_staff=c['gezwungen'] > 0,
            forcing=c['anwerber'] == k['RL_ANWERBER_ZWINGEN'], staff=c['personal'],
            forced_labor=c['zwang'], price_mod=c['pmod'], bribe_mod=c['bmod'], closed=c['zu'], risk_mod=c['rmod'])
        soll = [(r[3], r[6]) for r in rows]
        pruefe(ist == soll, f'Fall {fall} {c}: Skript {ist[:4]} ... Simulator {soll[:4]} ...')
        pruefe(sp.gvars.get(karma_gvar, 0) == karma, f'Fall {fall}: Karma {sp.gvars.get(karma_gvar)} statt {karma}')
    allgemein(sp, 'paritaet')


def test_erkundung(u):
    """Alle Dialogpfade von Essie und Kolbe aus vielen Spielstaenden."""
    k = u.k
    faelle = []
    sp = u.neues_spiel()
    e, ko = figuren(sp, k)
    faelle.append(('neu', sp, e, ko))
    sp = u.neues_spiel()
    e, ko = figuren(sp, k)
    rede(sp, e, ['deal with Kolbe', 'go see him'])
    faelle.append(('prolog laeuft', sp, e, ko))
    for weg in ('bezahlt', 'speech', 'ausliefern', 'faust'):
        sp, e, ko, w = prolog(u, weg)
        faelle.append((f'nach {weg}', sp, e, ko))
    sp, e, ko, w = prolog(u, 'bezahlt')
    rede(sp, e, ['Go on', 'Later'])
    rede(sp, ko, ['Deal. Bring them', None])
    faelle.append(('Pferch', sp, e, ko))
    sp2 = copy.deepcopy(sp)
    faelle.append(('Pferch, Essie reagiert', sp2, *[o for o in sp2.objekte if o.name in ('Essie',)], None))
    for krise in range(1, 8):
        sp, e, ko, w = prolog(u, 'bezahlt')
        rede(sp, e, ['Go on', 'Later'])
        w.setze_haus(0, 'RL_F_KRISE', krise)
        w.setze_haus(0, 'RL_F_KASSE', 500)
        faelle.append((f'Krise {krise}', sp, e, None))
    sp, e, ko, w = prolog(u, 'bezahlt')
    rede(sp, e, ['Go on', 'Later'])
    sp.dude.kronkorken = 0
    w.setze_haus(0, 'RL_F_KASSE', 0)
    faelle.append(('pleite', sp, e, ko))
    gesamt = 0
    for name, sp, e, ko in faelle:
        for obj in (e, ko):
            if obj is None or obj.zerstoert:
                continue
            laeufe, knoten = erkunde(sp, obj, f'{name}/{obj.name}')
            gesamt += knoten
    pruefe(gesamt > 50, f'zu wenige Dialogknoten erkundet: {gesamt}')
    print(f'      {gesamt} Dialogzustaende in {len(faelle)} Spielstaenden erkundet')


def _gosse_bereit(u):
    """Prolog bezahlt, Essies Reaktion gesehen, Angebot abgelehnt, 5 Zimmer."""
    sp, e, ko, w = prolog(u, 'bezahlt')
    rede(sp, e, ['Go on', 'Later'])
    rede(sp, ko, ['No. Not in my house', None])
    rede(sp, e, ['Go on', 'Later'])
    w.setze_haus(0, 'RL_F_ZIMMER', 5)
    w.setze_haus(0, 'RL_F_KASSE', 1000)
    w.setze_welt('RL_W_MARA_GESEHEN', 1)      # Akt 2 soll die Anwerbe-Tests nicht unterbrechen
    sp.zeit = 0
    sp.tick()
    sp.zufall_fest = 'max'           # keine Ereignisse, neue Leute mit Hoechstwerten
    return sp, e, ko, w


def test_anwerbung_werben(u):
    k = u.k
    sp, e, ko, w = _gosse_bereit(u)
    loehne = w.haus(0, 'RL_F_LOEHNE')
    v = rede(sp, e, ['about our people', 'talks people into it'])
    pruefe('sad story' in texte(v), f'Antwort: {texte(v)}')
    pruefe(w.haus(0, 'RL_F_ANWERBER') == k['RL_ANWERBER_WERBEN'], 'Anwerber')
    pruefe(w.haus(0, 'RL_F_LOEHNE') == loehne + 40, 'Lohn')
    personal = []
    for _ in range(5):
        woche(sp)
        personal.append(w.haus(0, 'RL_F_PERSONAL'))
    pruefe(personal == [3, 4, 4, 5, 5], f'Personal je Woche {personal}')
    pruefe(sum('New girl' in m or 'new' in m.lower() for m in sp.meldungen) >= 2, f'Meldungen {sp.meldungen}')
    v = rede(sp, e, ['about our people', 'Back'])
    pruefe('Every room is taken' in texte(v), f'Hinweis volle Zimmer fehlt: {texte(v)}')
    rede(sp, e, ['about our people', 'Let the recruiter go'])
    pruefe(w.haus(0, 'RL_F_LOEHNE') == loehne and w.haus(0, 'RL_F_ANWERBER') == 0, 'Entlassen')
    allgemein(sp, 'werben')


def test_anwerbung_zwingen(u):
    k = u.k
    sp, e, ko, w = _gosse_bereit(u)
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    rede(sp, e, ['about our people', "doesn't ask"])
    woche(sp)
    pruefe(w.haus(0, 'RL_F_PERSONAL') == 4 and w.haus(0, 'RL_F_GEZWUNGEN') == 1, 'eine Person pro Woche')
    woche(sp)
    pruefe(w.haus(0, 'RL_F_PERSONAL') == 5 and w.haus(0, 'RL_F_GEZWUNGEN') == 2, 'zweite Person')
    pruefe(w.haus(0, 'RL_F_MORAL') <= 50, 'Moral-Deckel')
    pruefe(w.haus(0, 'RL_F_HITZE') == 10, f'Hitze {w.haus(0, "RL_F_HITZE")}')
    pruefe(sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0) <= karma - 6, 'Karma')
    # Abgang bei Moral unter 25: zuerst die Gezwungenen; der Anwerber zwingt
    # in derselben Woche den Naechsten ins Haus
    w.setze_haus(0, 'RL_F_MORAL', 10)
    g = sp.globale[0]
    sp.meldungen.clear()
    g.rufe_mit('rl_personalwechsel', 0)
    pruefe(w.haus(0, 'RL_F_GEZWUNGEN') == 2 and w.haus(0, 'RL_F_PERSONAL') == 5, 'Abgang und Ersatz')
    pruefe(len(sp.meldungen) == 2 and 'ran off' in sp.meldungen[0], f'Meldungen {sp.meldungen}')
    # ohne Anwerber bleibt die Stelle leer
    rede(sp, e, ['about our people', 'Let the recruiter go'])
    g.rufe_mit('rl_personalwechsel', 0)
    pruefe(w.haus(0, 'RL_F_GEZWUNGEN') == 1 and w.haus(0, 'RL_F_PERSONAL') == 4, 'Abgang')
    allgemein(sp, 'zwingen')


def test_pferch_flucht_und_nachschub(u):
    k = u.k
    sp, e, ko, w = prolog(u, 'bezahlt')
    rede(sp, e, ['Go on', 'Later'])
    rede(sp, ko, ['Deal. Bring them', None])
    rede(sp, e, ['Go on', 'Later'])
    g = sp.globale[0]
    hid = sp.gespeichert['RL_HAUS']
    r = g.rufe_mit('rl_personal_verlust', hid, 0, k['RL_VERLUST_FLUCHT'])
    pruefe(r == 2 and w.haus(0, 'RL_F_ZWANG') == 1, 'Flucht aus dem Pferch')
    r = g.rufe_mit('rl_personal_verlust', hid, 0, k['RL_VERLUST_ABGANG'])
    pruefe(r == 0 and w.haus(0, 'RL_F_ZWANG') == 1, 'Kuendigung trifft den Pferch')
    geld = sp.dude.kronkorken
    w.setze_haus(0, 'RL_F_KASSE', 0)
    v = rede(sp, e, ['about our people', 'Send word to Metzger'])
    pruefe('Kolbe brings one' in texte(v), f'Nachschub: {texte(v)}')
    pruefe(w.haus(0, 'RL_F_ZWANG') == 2 and sp.dude.kronkorken == geld - 150, 'Nachschub bezahlt')
    rede(sp, e, ['about our people', 'Send word to Metzger'])
    pruefe(w.haus(0, 'RL_F_PERSONAL') == w.haus(0, 'RL_F_ZIMMER'), 'Haus nicht voll')
    v = rede(sp, e, ['about our people', 'Back'])
    pruefe(not any('Send word' in o for _, opts, _ in v for o in opts), 'Nachschub trotz vollem Haus')
    allgemein(sp, 'pferch')


# --------------------------------------------------------------------------
# Umsetzung 5: "Ketten", Akt 2-5

def _akt2(u, annehmen=False):
    """Prolog bezahlt, Akt 1 entschieden, eine Woche spaeter: Mara im Keller."""
    k = u.k
    sp, e, ko, w = prolog(u, 'bezahlt')
    rede(sp, e, ['Go on', 'Later'])
    if annehmen:
        rede(sp, ko, ['Deal. Bring them', None])
    else:
        rede(sp, ko, ['No. Not in my house', None])
    rede(sp, e, ['Go on', 'Later'])
    sp.zeit = 0
    sp.tick()
    sp.zufall_fest = 'min'           # Proben gelingen, keine Zufallsereignisse
    woche(sp)
    pruefe(w.welt('RL_W_MARA_WEG') == k['RL_MARA_KELLER'], 'Mara nicht im Keller')
    pruefe(any('Essie wants to see you' in m for m in sp.meldungen), f'Meldung fehlt: {sp.meldungen}')
    gosse(sp, k)
    mara = figur(sp, k, 'RLMARA')
    pruefe(mara.tile == k['RL_GOSSE_MARA_HEX'], 'Mara am falschen Platz')
    if annehmen:
        keine_figur(sp, k, 'RLKOLBE')      # im Tyrannen-Zweig kommt Kolbe erst mit Akt 3 zurueck
        ko = None
    return sp, e, ko, mara, w


def test_akt2_verstecken_bis_madame(u):
    """Fluchtzweig komplett: verstecken, Zuflucht, drei Transporte, Tyler abkaufen,
    Sturm, Metzger stirbt, die Gilde faellt, Mara wird Madame."""
    k = u.k
    sp, e, ko, mara, w = _akt2(u)
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    v = rede(sp, e, ['What do you want me to do', "I'll talk to her"])
    pruefe('girl in the cellar' in v[0][0], 'Essie zeigt Mara nicht')
    rede(sp, mara, ['Who are you', 'You can stay', None])
    pruefe(w.welt('RL_W_MARA_WEG') == k['RL_MARA_VERSTECKT'], 'nicht versteckt')
    pruefe(sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma + 10, 'Karma +10')
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_KETTE'], 'Akt 3')
    pruefe(w.welt('RL_W_RANGERS') == k['RL_RANGERS_KONTAKT'], 'Maras Wissen')
    # Essie warnt und fuehrt direkt zum Ausbau; die Zuflucht bauen
    w.setze_haus(0, 'RL_F_KASSE', 1000)
    v = rede(sp, e, ['Build the hidden room', 'Something you only get here', 'The Hidden Room', 'Build it'])
    pruefe('asking about a runaway' in v[0][0], 'Warnung fehlt')
    pruefe(w.haus(0, 'RL_F_BAU_ID') == 51, f'Bau {w.haus(0, "RL_F_BAU_ID")}')
    sp.meldungen.clear()
    woche(sp)
    pruefe(w.haus(0, 'RL_F_MODULE') & k['RL_MOD_ZUFLUCHT'], 'Zuflucht nicht fertig')
    pruefe(w.welt('RL_W_MARA_WEG') == k['RL_MARA_VERSTECKT'], 'Mara trotz Zuflucht gefunden')
    pruefe(any('never found the door' in m for m in sp.meldungen), f'Meldungen {sp.meldungen}')
    # drei Transporte ueber das Manager-Menue
    sp.dude.skills[k['SKILL_SNEAK']] = 70
    for n in range(3):
        rede(sp, e, ['The route south', 'take them myself'])
        pruefe(w.welt('RL_W_AUFTRAG') == k['RL_AUFTRAG_SUEDEN'], 'kein Auftrag')
        v = rede(sp, e, ['The route south', 'Back'])
        pruefe("on the road" in texte(v), 'laufender Auftrag nicht gemeldet')
        woche(sp)
        pruefe(w.welt('RL_W_TRANSPORTE') == n + 1, f'Transporte {w.welt("RL_W_TRANSPORTE")}')
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_TYLER'], 'Akt 4')
    pruefe(any("Tyler's boys" in m for m in sp.meldungen), 'Tyler-Meldung fehlt')
    gosse(sp, k)
    deke = figur(sp, k, 'RLDEKE')
    sp.dude.skills[k['SKILL_BARTER']] = 60
    geld = sp.dude.kronkorken + max(0, w.haus(0, 'RL_F_KASSE'))
    rede(sp, deke, ['[Barter]', None])
    pruefe(deke.zerstoert and w.welt('RL_W_TYLER') == k['RL_TYLER_GEKAUFT'], 'Tyler nicht abgekauft')
    pruefe(sp.dude.kronkorken + max(0, w.haus(0, 'RL_F_KASSE')) == geld - 400, 'Preis 400')
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_WAHL'], 'Akt 5')
    v = rede(sp, e, ['Tonight', None])
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_STURM'], 'Sturm')
    # Metzger stirbt (Vanilla: GVAR_DEN_FLAG_1, bit 1)
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    sp.gvars[k['GVAR_DEN_FLAG_1']] = sp.gvars.get(k['GVAR_DEN_FLAG_1'], 0) | 1
    sp.tick()
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_GILDE_FAELLT'], 'Die Gilde faellt nicht')
    pruefe(sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma + 50, 'Karma +50')
    pruefe(w.welt('RL_W_RANGERS') == k['RL_RANGERS_VERBUENDET'], 'Rangers')
    pruefe(w.welt('RL_W_MARA_WEG') == k['RL_MARA_ZURUECK'], 'Mara kehrt nicht zurueck')
    sp.dude.skills[k['SKILL_SPEECH']] = 50
    v = rede(sp, mara, ['Why did you come back', '[Speech] Run the Gutter', None])
    pruefe(w.welt('RL_W_MARA') == 1 and w.welt('RL_W_MARA_WEG') == k['RL_MARA_MADAME'], 'keine Madame')
    pruefe(w.haus(0, 'RL_F_FUEHRUNG') >= 70, 'Fuehrung')
    v = rede(sp, mara, ["Let's talk prices", 'Back' if False else 'Leave it'])
    pruefe('Everyone in the house can leave' in v[0][0], f'Mara-Menue: {v[0][0]}')
    sp.tick()
    pruefe(sp.gvars.get(k['GVAR_RL_NACHSATZ']) == k['RL_NACHSATZ_UEBERLEBENDE'], 'Nachsatz Die Ueberlebende')
    # Mara geht, sobald irgendwo jemand gezwungen wurde (freies Zimmer noetig)
    w.setze_haus(0, 'RL_F_ZIMMER', w.haus(0, 'RL_F_PERSONAL') + 1)
    rede(sp, e, ['about our people', "doesn't ask"])
    sp.meldungen.clear()
    woche(sp)
    woche(sp)
    pruefe(w.welt('RL_W_MARA_WEG') == k['RL_MARA_GEGANGEN'] and w.welt('RL_W_MARA') == 0, 'Mara bleibt trotz Zwang')
    pruefe(any('You know why' in m for m in sp.meldungen), f'Meldungen {sp.meldungen}')
    gosse(sp, k)
    keine_figur(sp, k, 'RLMARA')
    allgemein(sp, 'akt2 verstecken bis madame')


def test_suche_ohne_zuflucht(u):
    k = u.k
    sp, e, ko, mara, w = _akt2(u)
    rede(sp, mara, ['You can stay', None])
    woche(sp)
    pruefe(w.welt('RL_W_MARA_WEG') == k['RL_MARA_VERSCHLEPPT'], 'Mara nicht gefunden')
    pruefe(w.welt('RL_W_METZGER') == k['RL_METZGER_FEIND'], 'Metzger nicht Feind')
    pruefe(any('found Mara' in m for m in sp.meldungen), 'Meldung')
    gosse(sp, k)
    keine_figur(sp, k, 'RLMARA')
    allgemein(sp, 'suche')


def test_akt2_retten_stiller_krieg(u):
    k = u.k
    sp, e, ko, mara, w = _akt2(u)
    sp.dude.skills[k['SKILL_OUTDOORSMAN']] = 60
    rede(sp, mara, ['[Outdoorsman]', None])
    pruefe(mara.zerstoert and w.welt('RL_W_MARA_WEG') == k['RL_MARA_SICHER'], 'nicht gerettet')
    # Ohne Perception 7 kennt man das Versteck der Rangers durch Mara
    pruefe(w.welt('RL_W_RANGERS') == k['RL_RANGERS_KONTAKT'], 'Rangers-Kontakt')
    # direkt zu Akt 5 springen und den stillen Krieg waehlen
    w.setze_welt('RL_W_KETTEN', k['RL_KETTEN_WAHL'])
    v = rede(sp, e, ['Not yet', None])
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_STILLER_KRIEG'], 'stiller Krieg')
    sp.meldungen.clear()
    woche(sp, 2)
    pruefe(w.welt('RL_W_MARA_WEG') == k['RL_MARA_ZURUECK'], 'Mara nicht zurueck')
    pruefe(any('Someone is waiting' in m for m in sp.meldungen), 'Meldung Rueckkehr')
    gosse(sp, k)
    mara = figur(sp, k, 'RLMARA')
    # Vergeltung nach 6 Wochen: Krise in der Gosse, die Rangers helfen
    woche(sp, 4)
    pruefe(w.haus(0, 'RL_F_KRISE') == k['RL_EV_VERGELTUNG'], f'Krise {w.haus(0, "RL_F_KRISE")}')
    v = rede(sp, e, ["You said there's a problem", 'Rangers'])
    pruefe(w.haus(0, 'RL_F_KRISE') == 0, 'Krise nicht geloest')
    # Mara draengen: sie geht zu Calloway
    rede(sp, mara, ['Why did you come back', 'You owe me', None])
    pruefe(w.welt('RL_W_MARA_WEG') == k['RL_MARA_CALLOWAY'] and mara.zerstoert, 'Calloway')
    # Metzger stirbt spaeter doch: aus dem stillen Krieg wird "Die Gilde faellt"
    sp.gvars[k['GVAR_DEN_FLAG_1']] = 1
    sp.tick()
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_GILDE_FAELLT'], 'Gilde faellt nach stillem Krieg')
    allgemein(sp, 'retten')


def test_akt2_ausliefern_essie_geht(u):
    k = u.k
    sp, e, ko, mara, w = _akt2(u)
    geld = sp.dude.kronkorken
    rede(sp, mara, ['(Hand her over', None])
    pruefe(mara.zerstoert and w.welt('RL_W_MARA_WEG') == k['RL_MARA_AUSGELIEFERT'], 'nicht ausgeliefert')
    pruefe(sp.dude.kronkorken == geld + 500, '500 $')
    pruefe(w.welt('RL_W_ESSIE') == k['RL_ESSIE_GEKUENDIGT'], 'Essie kuendigt nicht')
    pruefe(w.welt('RL_W_KETTEN_ZWEIG') == k['RL_KETTEN_ZWEIG_TYRANN'], 'Tyrannen-Zweig')
    v = rede(sp, e, [None])
    pruefe('My bag is packed' in v[0][0] and e.zerstoert, 'Essies Abschied')
    gosse(sp, k)
    ko = figur(sp, k, 'RLKOLBE')
    v = rede(sp, ko, ["Let's talk about the house", 'Later'])
    pruefe('Metzger has work' in v[0][0], f'Kolbe: {v[0][0]}')
    pruefe(any('Metzger sends his regards. The house is running' in a for a, _, _ in v), 'Kolbe fuehrt nicht')
    allgemein(sp, 'ausliefern')


def test_tyrann_bis_metzgers_mann(u):
    k = u.k
    sp, e, ko, mara, w = _akt2(u, annehmen=True)
    # Pferch: verstecken geht nicht, Essie (gebrochen) bleibt beim Ausliefern
    v = rede(sp, mara, ['(Hand her over', None])
    pruefe(not any('You can stay' in o for _, opts, _ in v for o in opts), 'Verstecken trotz Pferch')
    pruefe(w.welt('RL_W_ESSIE') == k['RL_ESSIE_DA'], 'Essie ging im Tyrannen-Zweig')
    gosse(sp, k)
    ko = figur(sp, k, 'RLKOLBE')
    sp.dude.skills[k['SKILL_SPEECH']] = 80
    for n in range(3):
        v = rede(sp, ko, ['Vault City' if n % 2 == 0 else 'Vortis', None])
        pruefe(w.welt('RL_W_AUFTRAG') in (2, 3), 'kein Auftrag')
        kasse = w.haus(0, 'RL_F_KASSE')
        sp.meldungen.clear()
        woche(sp)
        pruefe(w.welt('RL_W_LIEFERUNGEN') == n + 1, 'Lieferung')
        pruefe(any('The shipment arrived' in m for m in sp.meldungen), f'Meldung {sp.meldungen}')
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_TYLER'], 'Akt 4 (Lara)')
    gosse(sp, k)
    jess = figur(sp, k, 'RLJESS')
    zwang = w.haus(0, 'RL_F_ZWANG')
    personal = w.haus(0, 'RL_F_PERSONAL')
    rede(sp, jess, ['Take them', None])
    pruefe(jess.zerstoert and w.haus(0, 'RL_F_ZWANG') == 0 and w.haus(0, 'RL_F_PERSONAL') == personal - zwang, 'Pferch leer')
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_WAHL'], 'Akt 5')
    rede(sp, ko, ['Tell him yes', None])
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_METZGERS_MANN'], 'Metzgers Mann')
    pruefe(sp.gvars.get(k['GVAR_REPUTATION_SLAVER']) == 1, 'Slaver-Titel')
    kasse = w.haus(0, 'RL_F_KASSE')
    sp.tick()
    pruefe(sp.gvars.get(k['GVAR_RL_TITEL_SEELE']) == 1, 'Seelenverkaeufer')
    gosse(sp, k)
    figur(sp, k, 'RLKOLBE')
    allgemein(sp, 'metzgers mann')


def test_neuer_metzger(u):
    k = u.k
    sp, e, ko, mara, w = _akt2(u, annehmen=True)
    rede(sp, mara, ['(Hand her over', None])
    w.setze_welt('RL_W_KETTEN', k['RL_KETTEN_WAHL'])
    gosse(sp, k)
    ko = figur(sp, k, 'RLKOLBE')
    rede(sp, ko, ['accident', None])
    pruefe(w.welt('RL_W_METZGER_VERRAT') == 1, 'Verrat')
    v = rede(sp, ko, [None])
    pruefe('still breathing' in v[0][0], 'Erinnerung')
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    sp.gvars[k['GVAR_DEN_FLAG_1']] = 1
    sp.meldungen.clear()
    sp.tick()
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_NEUER_METZGER'], 'Der neue Metzger')
    pruefe(sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 100, 'Karma -100')
    pruefe(any('The Guild is yours' in m for m in sp.meldungen), 'Meldung')
    woche(sp)
    pruefe(w.haus(0, 'RL_F_STADTMOD') == 70, f'Den-Modifikator {w.haus(0, "RL_F_STADTMOD")}')
    pruefe(sp.gvars.get(k['GVAR_RL_NACHSATZ']) == k['RL_NACHSATZ_KETTEN'], 'Nachsatz Ketten')
    allgemein(sp, 'neuer metzger')


def test_kampf_deke_und_jess(u):
    k = u.k
    # Fluchtzweig: Kampf gegen Deke und zwei von Tylers Leuten
    sp, e, ko, mara, w = _akt2(u)
    rede(sp, mara, ['You can stay', None])
    w.setze_welt('RL_W_KETTEN', k['RL_KETTEN_TYLER'])
    gosse(sp, k)
    deke = figur(sp, k, 'RLDEKE')
    rede(sp, deke, ['Get out of my house', None])
    angreifer = sp.finde(k['SCRIPT_RLANGREIFER'])
    pruefe(len(angreifer) == 2 and w.welt('RL_W_ANGREIFER') == 3, 'Angreifer fehlen')
    pruefe(len(sp.angriffe) >= 3, f'Angriffe {sp.angriffe}')
    # Karte verlassen und wiederkommen: Sie greifen wieder an, Deke bleibt
    gosse(sp, k)
    figur(sp, k, 'RLDEKE')
    for o in [deke] + angreifer:
        sp.zerstoere(o)             # im Kampf gefallen: destroy_p_proc
    pruefe(w.welt('RL_W_TYLER') == k['RL_TYLER_BESIEGT'] and w.welt('RL_W_KETTEN') == k['RL_KETTEN_WAHL'], 'Kampf nicht beendet')
    pruefe(w.welt('RL_W_ANGRIFF') == 0, 'Angriff offen')
    # Tyrannen-Zweig: Laras Leute
    sp, e, ko, mara, w = _akt2(u, annehmen=True)
    rede(sp, mara, ['(Hand her over', None])
    w.setze_welt('RL_W_KETTEN', k['RL_KETTEN_TYLER'])
    gosse(sp, k)
    jess = figur(sp, k, 'RLJESS')
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    rede(sp, jess, ['Over my dead body', None])
    for o in [jess] + sp.finde(k['SCRIPT_RLANGREIFER']):
        sp.zerstoere(o)
    pruefe(w.welt('RL_W_LARA') == k['RL_LARA_ABGEWEHRT'] and w.welt('RL_W_KETTEN') == k['RL_KETTEN_WAHL'], 'Lara abgewehrt')
    pruefe(sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 10, 'Karma -10')
    allgemein(sp, 'kaempfe')


def test_tyler_tot_vanilla(u):
    k = u.k
    sp, e, ko, mara, w = _akt2(u)
    rede(sp, mara, ['You can stay', None])
    w.setze_welt('RL_W_KETTEN', k['RL_KETTEN_TYLER'])
    sp.gvars[k['GVAR_DEN_FLAG_2']] = sp.gvars.get(k['GVAR_DEN_FLAG_2'], 0) | k['bit_32']
    sp.tick()
    pruefe(w.welt('RL_W_TYLER') == k['RL_TYLER_TOT'] and w.welt('RL_W_KETTEN') == k['RL_KETTEN_WAHL'], 'Tyler tot')
    gosse(sp, k)
    keine_figur(sp, k, 'RLDEKE')
    allgemein(sp, 'tyler tot')


def test_eingaenge_haeuser(u):
    """Umsetzung 6: je Stadt eine Treppe auf der Vanilla-Karte, die ins Haus fuehrt;
    die Kartenskripte zeigen beim ersten Besuch ihren Satz."""
    import bau_karten
    k = u.k
    sp = u.neues_spiel()
    for nr, h in enumerate(bau_karten.HAEUSER, 1):
        sp.betrete_karte(h['stadtkarte_index'])
        treppen = [o for o in sp.objekte if o.pid == bau_karten.TREPPE_PID and o.tile == h['treppe_hex']]
        pruefe(len(treppen) == 1 and treppen[0].skript_nr == k['SCRIPT_RLTUER'], f'{h["kuerzel"]}: Treppe')
        sp.betrete_karte(h['stadtkarte_index'])
        pruefe(len([o for o in sp.objekte if o.pid == bau_karten.TREPPE_PID and o.tile == h['treppe_hex']]) == 1,
               f'{h["kuerzel"]}: Treppe doppelt')
        t = treppen[0]
        sp.meldungen.clear()
        t.skript.rufe('look_at_p_proc', self_obj=t, source=sp.dude)
        t.skript.rufe('use_p_proc', self_obj=t, source=sp.dude)
        pruefe(sp.karten_wechsel[-1] == (h['datei'], 0), f'{h["kuerzel"]}: {sp.karten_wechsel[-1]}')
        pruefe(sp.meldungen and 'Error' not in sp.meldungen[0], f'{h["kuerzel"]}: Ansehen {sp.meldungen}')
        # Kartenskript: Satz beim ersten Besuch
        karte = sp.erzeuge(0, -1, 0, k[h['kartenskript']], 'Kartenskript ' + h['kuerzel'])
        sp.karte = u.cfg['RL_MAP_INDEX'] + nr
        sp.erster_besuch = True
        sp.meldungen.clear()
        karte.skript.rufe('map_enter_p_proc', self_obj=karte)
        pruefe(len(sp.meldungen) == 1, f'{h["kuerzel"]}: erster Besuch {sp.meldungen}')
        # Treppe im Kampf und fuer Begleiter: nichts
        n = len(sp.karten_wechsel)
        sp.kampf = True
        t.skript.rufe('use_p_proc', self_obj=t, source=sp.dude)
        sp.kampf = False
        t.skript.rufe('use_p_proc', self_obj=t, source=karte)
        pruefe(len(sp.karten_wechsel) == n, f'{h["kuerzel"]}: Kartenwechsel im Kampf/fuer andere')
    # Essie kennt die anderen Staedte
    sp, e, ko, w = prolog(u, 'bezahlt')
    v = rede(sp, e, ['Go on', 'Where else', 'New Reno', 'another town', 'San Francisco'])
    pruefe('Silver Garter' in texte(v) and 'ferry terminal' in texte(v), 'Staedte')
    pruefe(w.welt('RL_W_STAEDTE_ERZAEHLT') == (1 << k['RL_NEW_RENO']) | (1 << k['RL_SAN_FRAN']), 'Bits')
    allgemein(sp, 'eingaenge')


def test_alter_spielstand(u):
    """Spielstand aus Umsetzung 4: Welt-Array mit 32 Feldern wird erweitert."""
    k = u.k
    sp = u.neues_spiel()
    alt = intvm.Liste(32)
    alt.werte[k['RL_W_PROLOG']] = k['RL_PROLOG_FERTIG']
    alt.werte[k['RL_W_KETTEN']] = k['RL_KETTEN_KELLER']
    alt.werte[k['RL_W_METZGER_NEIN']] = 1
    aid = sp.naechstes_array
    sp.naechstes_array += 1
    sp.arrays[aid] = alt
    sp.gespeichert['RL_WELT'] = aid
    sp.globale = []
    sp.lade_global('gl_rotlicht')
    w = Welt(sp, k)
    pruefe(len(w.w) == k['RL_WELT_FELDER'], f'Welt hat {len(w.w)} Felder')
    pruefe(w.welt('RL_W_KETTEN') == k['RL_KETTEN_KELLER'] and w.welt('RL_W_METZGER_NEIN') == 1, 'Werte verloren')
    pruefe(aid not in sp.arrays, 'altes Array nicht freigegeben')
    allgemein(sp, 'alter spielstand')


def test_erkundung_ketten(u):
    """Alle Dialogpfade der neuen Figuren in den Zustaenden von Akt 2-5."""
    k = u.k
    gesamt = 0
    sp, e, ko, mara, w = _akt2(u)
    gesamt += erkunde(sp, mara, 'Mara im Keller')[1]
    gesamt += erkunde(sp, e, 'Essie Akt 2')[1]
    rede(sp, mara, ['You can stay', None])
    gesamt += erkunde(sp, mara, 'Mara versteckt')[1]
    gesamt += erkunde(sp, e, 'Essie Suche')[1]
    w.setze_welt('RL_W_KETTEN', k['RL_KETTEN_TYLER'])
    gosse(sp, k)
    for bar, spr in ((0, 0), (60, 60), (60, 80)):
        sp.dude.skills[k['SKILL_BARTER']] = bar
        sp.dude.skills[k['SKILL_SPEECH']] = spr
        gesamt += erkunde(sp, figur(sp, k, 'RLDEKE'), f'Deke {bar}/{spr}')[1]
    w.setze_welt('RL_W_KETTEN', k['RL_KETTEN_WAHL'])
    gesamt += erkunde(sp, e, 'Essie Akt 5')[1]
    w.setze_welt('RL_W_MARA_WEG', k['RL_MARA_ZURUECK'])
    w.setze_welt('RL_W_KETTEN', k['RL_KETTEN_GILDE_FAELLT'])
    for spr in (0, 50):
        sp.dude.skills[k['SKILL_SPEECH']] = spr
        gesamt += erkunde(sp, mara, f'Mara zurueck {spr}')[1]
    w.setze_welt('RL_W_MARA_WEG', k['RL_MARA_MADAME'])
    w.setze_welt('RL_W_MARA', 1)
    gesamt += erkunde(sp, mara, 'Mara Madame')[1]
    sp, e, ko, mara, w = _akt2(u, annehmen=True)
    gesamt += erkunde(sp, mara, 'Mara im Pferch-Haus')[1]
    rede(sp, mara, ['(Hand her over', None])
    gosse(sp, k)
    ko = figur(sp, k, 'RLKOLBE')
    for akt in ('RL_KETTEN_KETTE', 'RL_KETTEN_TYLER', 'RL_KETTEN_WAHL', 'RL_KETTEN_METZGERS_MANN', 'RL_KETTEN_NEUER_METZGER'):
        w.setze_welt('RL_W_KETTEN', k[akt])
        gesamt += erkunde(sp, ko, f'Kolbe {akt}')[1]
    w.setze_welt('RL_W_KETTEN', k['RL_KETTEN_TYLER'])
    gosse(sp, k)
    gesamt += erkunde(sp, figur(sp, k, 'RLJESS'), 'Jess')[1]
    print(f'      {gesamt} Dialogzustaende der Akte 2-5 erkundet')


# --------------------------------------------------------------------------
# Umsetzung 7: New Reno, Der Segen und das Hauptquartier

NR = 1


def strumpfband(u, sp=None):
    """Das Silberne Strumpfband betreten (Kartenskript RLREN01); liefert (sp, w)."""
    k = u.k
    sp = sp or u.neues_spiel()
    if not sp.finde(k['SCRIPT_RLREN01']):
        sp.erzeuge(0, -1, 0, k['SCRIPT_RLREN01'], 'Kartenskript RLREN01')
    betrete_strumpfband(u, sp)
    return sp, Welt(sp, k)


def betrete_strumpfband(u, sp):
    sp.betrete_karte(u.cfg['RL_MAP_INDEX'] + NR)
    sp.temp_freigeben()


def _nr_uebernommen(u, pate='Salvatore', sp=None):
    """Urkunde gekauft und Segen einer Familie: Das Strumpfband gehoert dem Spieler."""
    k = u.k
    sp, w = strumpfband(u, sp)
    rede(sp, figur(sp, k, 'RLWITWE'), ['buy the deed', "Here's a thousand", None])
    if pate == 'Salvatore':
        sp.dude.skills[k['SKILL_SMALL_GUNS']] = 60
        rede(sp, figur(sp, k, 'RLFIXER'), ['families', 'Salvatore', '[Combat]', None])
    elif pate == 'Mordino':
        sp.dude.skills[k['SKILL_SNEAK']] = 60
        rede(sp, figur(sp, k, 'RLFIXER'), ['families', 'Mordino', '[Sneak]', None])
    elif pate == 'Wright':
        sp.dude.stats[k['STAT_pe']] = 7
        rede(sp, figur(sp, k, 'RLFIXER'), ['families', 'Wright', '[Perception]', None])
    pruefe(w.haus(NR, 'RL_F_BESITZ') == 1, f'Strumpfband nicht uebernommen ({pate})')
    return sp, w


def test_nr_kauf_und_mordino(u):
    k = u.k
    sp, w = strumpfband(u)
    witwe = figur(sp, k, 'RLWITWE')
    fixer = figur(sp, k, 'RLFIXER')
    keine_figur(sp, k, 'RLROZ')
    keine_figur(sp, k, 'RLCONSIG')
    pruefe(w.welt('RL_W_HAUS_HIER') == NR + 1, 'Haus hier')
    geld = sp.dude.kronkorken
    rede(sp, witwe, ['buy the deed', "Here's a thousand", None])
    pruefe(w.welt('RL_W_NR_URKUNDE') == k['RL_URKUNDE_KAUF'] and sp.dude.kronkorken == geld - 1000, 'Kauf')
    pruefe(w.haus(NR, 'RL_F_EINFLUSS') == 5 and w.haus(NR, 'RL_F_BESITZ') == 0, 'E +5, noch kein Besitz')
    keine_figur(sp, k, 'RLWITWE')
    v = rede(sp, fixer, ['families', 'Mordino'])
    pruefe('Stables' in texte(v), 'Mordino-Auftrag')
    pruefe(not any('[Sneak]' in o[0] for o in sp.dialog_optionen), 'Sneak ohne Skill angeboten')
    sp.dude.skills[k['SKILL_SNEAK']] = 60
    v = rede(sp, fixer, ['families', 'Mordino', '[Sneak]', None])
    pruefe('Roz Mercer' in texte(v), 'Uebergabe an Roz')
    pruefe(w.haus(NR, 'RL_F_BESITZ') == 1 and w.welt('RL_W_NR_SEGEN') == k['RL_SEGEN_MORDINO'], 'Segen Mordino')
    pruefe(w.haus(NR, 'RL_F_TRIBUTMOD') == 5 and w.haus(NR, 'RL_F_MODUL_STADTMOD') == 15
           and w.haus(NR, 'RL_F_NEBEN') == 3, 'Paten-Wirkung Mordino')
    pruefe(w.welt('RL_W_NR_MISSTRAUEN') == 1 << k['RL_SEGEN_WRIGHT'], 'Wright misstrauisch')
    pruefe(w.haus(NR, 'RL_F_EINFLUSS') == 20 and w.haus(NR, 'RL_F_FUEHRUNG') == 55 and w.haus(NR, 'RL_F_HITZE') == 10,
           f'E {w.haus(NR, "RL_F_EINFLUSS")} F {w.haus(NR, "RL_F_FUEHRUNG")} H {w.haus(NR, "RL_F_HITZE")}')
    pruefe(w.welt('RL_W_AKTIV') == 1 and w.welt('RL_W_TREFFEN_WOCHE') > 0, 'aktiv, Treffen geplant')
    keine_figur(sp, k, 'RLFIXER')
    figur(sp, k, 'RLROZ')
    figur(sp, k, 'RLCONSIG')
    betrete_strumpfband(u, sp)
    figur(sp, k, 'RLROZ')
    figur(sp, k, 'RLCONSIG')
    keine_figur(sp, k, 'RLWITWE')
    keine_figur(sp, k, 'RLFIXER')
    # Roz: erstes Gespraech, dann das Manager-Menue des Strumpfbands
    roz = figur(sp, k, 'RLROZ')
    v = rede(sp, roz, ['how the house', 'How are our people'])
    pruefe('Shark Club' in texte(v) and 'Last week we had' in texte(v), f'Roz: {texte(v)[:200]}')
    v = rede(sp, roz, [])
    pruefe('cards' in texte(v).lower(), 'Roz ohne Einleitung')
    allgemein(sp, 'nr kauf mordino')


def test_nr_urkunde_wege(u):
    k = u.k
    # Barter: 750
    sp, w = strumpfband(u)
    sp.dude.skills[k['SKILL_BARTER']] = 60
    geld = sp.dude.kronkorken
    rede(sp, figur(sp, k, 'RLWITWE'), ['buy the deed', '[Barter]', None])
    pruefe(sp.dude.kronkorken == geld - 750 and w.welt('RL_W_NR_URKUNDE') == k['RL_URKUNDE_KAUF'], 'Barter')
    # Speech: umsonst
    sp, w = strumpfband(u)
    sp.dude.skills[k['SKILL_SPEECH']] = 60
    geld = sp.dude.kronkorken
    rede(sp, figur(sp, k, 'RLWITWE'), ['[Speech]', None])
    pruefe(sp.dude.kronkorken == geld and w.welt('RL_W_NR_URKUNDE') == k['RL_URKUNDE_REDE'], 'Speech')
    pruefe(w.haus(NR, 'RL_F_EINFLUSS') == 5, 'E +5')
    # Das Grab: nur mit Schaufel; ohne Sneak 40 gesehen
    for sneak, hitze in ((20, 10), (40, 0)):
        sp, w = strumpfband(u)
        sp.dude.skills[k['SKILL_SNEAK']] = sneak
        witwe = figur(sp, k, 'RLWITWE')
        rede(sp, witwe, ['Where is the deed', None])
        pruefe(not any('Golgotha' in o[0] for o in sp.dialog_optionen), 'Grab ohne Schaufel')
        sp.dude.inventar[k['PID_SHOVEL']] = 1
        karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
        v = rede(sp, witwe, ['Where is the deed', 'Golgotha', None])
        pruefe(w.welt('RL_W_NR_URKUNDE') == k['RL_URKUNDE_GRAB'], 'Grab')
        pruefe(sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 10 and sp.gvars[k['GVAR_GRAVES_UNEARTHED']] == 1,
               'Karma -10, Grave Digger')
        pruefe(w.haus(NR, 'RL_F_HITZE') == hitze, f'Sneak {sneak}: Hitze {w.haus(NR, "RL_F_HITZE")}')
        pruefe(('gravedigger' in texte(v)) == (sneak < 40), 'gesehen')
        keine_figur(sp, k, 'RLWITWE')
        betrete_strumpfband(u, sp)
        keine_figur(sp, k, 'RLWITWE')
    allgemein(sp, 'nr urkunde')


def test_nr_faelschung(u):
    k = u.k
    for zahlen in (True, False):
        sp, w = strumpfband(u)
        sp.dude.skills[k['SKILL_SMALL_GUNS']] = 60
        fixer = figur(sp, k, 'RLFIXER')
        rede(sp, fixer, ['families', 'Salvatore', '[Combat]', None])
        pruefe(w.welt('RL_W_NR_SEGEN') == k['RL_SEGEN_SALVATORE'] and w.haus(NR, 'RL_F_BESITZ') == 0, 'Segen ohne Urkunde')
        figur(sp, k, 'RLFIXER')             # bleibt, bis die Urkunde da ist
        rede(sp, fixer, ['About the deed'])
        pruefe(not any('[Science]' in o[0] for o in sp.dialog_optionen), 'Science ohne Skill')
        sp.dude.skills[k['SKILL_SCIENCE']] = 60
        sp.zufall_fest = 'min'              # die 15 % treffen
        v = rede(sp, fixer, ['About the deed', '[Science]', 'hundred', None])
        sp.zufall_fest = None
        pruefe(w.welt('RL_W_NR_URKUNDE') == k['RL_URKUNDE_FAELSCHUNG'] and w.haus(NR, 'RL_F_BESITZ') == 1, 'Faelschung')
        pruefe('Roz Mercer' in texte(v), 'Uebernahme nach der Faelschung')
        pruefe(w.welt('RL_W_NR_FAELSCHUNG') > 0, 'fliegt auf')
        pruefe(w.haus(NR, 'RL_F_SICHERHEIT') == 75 and w.haus(NR, 'RL_F_TRIBUTMOD') == 10, 'Salvatore-Wirkung')
        pruefe(w.welt('RL_W_NR_MISSTRAUEN') == 1 << k['RL_SEGEN_BISHOP'], 'Bishop misstrauisch')
        betrete_strumpfband(u, sp)
        keine_figur(sp, k, 'RLWITWE')           # sie geht, sobald das Haus vergeben ist
        woche(sp, 2)
        pruefe(w.welt('RL_W_NR_WITWE') == k['RL_WITWE_FORDERT'], 'Witwe fordert')
        pruefe(any('forged' in m for m in sp.meldungen), 'Meldung Faelschung')
        betrete_strumpfband(u, sp)
        witwe = figur(sp, k, 'RLWITWE')
        if zahlen:
            geld = sp.dude.kronkorken
            rede(sp, witwe, ['five hundred', None])
            pruefe(sp.dude.kronkorken == geld - 500 and w.welt('RL_W_NR_WITWE') == k['RL_WITWE_BEZAHLT'], 'bezahlt')
            keine_figur(sp, k, 'RLWITWE')
        else:
            e = w.haus(NR, 'RL_F_EINFLUSS')
            woche(sp, 2)
            pruefe(w.welt('RL_W_NR_WITWE') == k['RL_WITWE_VERWEIGERT'] and w.haus(NR, 'RL_F_EINFLUSS') == e - 10,
                   'Frist verstrichen')
            betrete_strumpfband(u, sp)
            keine_figur(sp, k, 'RLWITWE')
        allgemein(sp, f'nr faelschung {zahlen}')


def test_nr_bishop_brief(u):
    k = u.k
    for oeffnen in (False, True):
        sp, w = strumpfband(u)
        fixer = figur(sp, k, 'RLFIXER')
        if oeffnen:
            sp.dude.skills[k['SKILL_LOCKPICK']] = 60
            v = rede(sp, fixer, ['families', 'Bishop', '[Lockpick]', None])
            pruefe(w.welt('RL_W_NR_BRIEF') == k['RL_BRIEF_GEOEFFNET'] and w.haus(NR, 'RL_F_HITZE') == 15, 'geoeffnet')
            pruefe('councilmen' in texte(v), 'Inhalt')
        else:
            rede(sp, fixer, ['families', 'Bishop', 'Give me the letter', None])
            pruefe(w.welt('RL_W_NR_BRIEF') == k['RL_BRIEF_UNTERWEGS'], 'Brief unterwegs')
        v = rede(sp, fixer, ["Bishop's letter", None])
        pruefe('Until that letter' in texte(v), 'wartet auf den Brief')
        sp.betrete_karte(k['MAP_NCR_DOWNTOWN'])
        pruefe(w.welt('RL_W_NR_BRIEF') in (k['RL_BRIEF_UNTERWEGS'], k['RL_BRIEF_GEOEFFNET']), 'nicht in Downtown abgeben')
        sp.betrete_karte(k['MAP_NCR_WESTIN_RANCH'])
        erwartet = k['RL_BRIEF_ABGEGEBEN_OFFEN'] if oeffnen else k['RL_BRIEF_ABGEGEBEN']
        pruefe(w.welt('RL_W_NR_BRIEF') == erwartet and any('Westin' in m for m in sp.meldungen), 'abgegeben')
        betrete_strumpfband(u, sp)
        v = rede(sp, figur(sp, k, 'RLFIXER'), [None])
        pruefe(w.welt('RL_W_NR_SEGEN') == k['RL_SEGEN_BISHOP'], 'Bishops Segen')
        pruefe(w.haus(k['RL_NCR'], 'RL_F_EINFLUSS') == 10, 'E NCR +10')
        erledigt = k['RL_BRIEF_ERLEDIGT_OFFEN'] if oeffnen else k['RL_BRIEF_ERLEDIGT']
        pruefe(w.welt('RL_W_NR_BRIEF') == erledigt, 'erledigt')
        rede(sp, figur(sp, k, 'RLWITWE'), ['buy the deed', "Here's a thousand", None])
        pruefe(w.haus(NR, 'RL_F_BESITZ') == 1 and w.haus(k['RL_NCR'], 'RL_F_EINFLUSS') == 30, 'Bishop-Pate: E NCR +20')
        pruefe(w.welt('RL_W_NR_MISSTRAUEN') == 1 << k['RL_SEGEN_SALVATORE'], 'Salvatore misstrauisch')
        allgemein(sp, f'nr bishop {oeffnen}')


def test_nr_made_man_und_vanilla(u):
    k = u.k
    sp, w = strumpfband(u)
    sp.gvars[k['GVAR_MADE_MAN_WRIGHT']] = 1
    rede(sp, figur(sp, k, 'RLFIXER'), ['families', 'already family', None])
    pruefe(w.welt('RL_W_NR_SEGEN') == k['RL_SEGEN_WRIGHT'], 'Made Man Wright')
    sp, w = strumpfband(u)
    sp.gvars[k['GVAR_NEW_RENO_GUARD_ASSIGNMENT']] = 3
    rede(sp, figur(sp, k, 'RLFIXER'), ['families', 'Salvatore', "guarded Salvatore's exchange", None])
    pruefe(w.welt('RL_W_NR_SEGEN') == k['RL_SEGEN_SALVATORE'], 'Salvatore-Vorleistung')
    # Tote Familien bieten nichts an
    sp, w = strumpfband(u)
    sp.gvars[k['GVAR_NEW_RENO_FLAG_2']] = k['bit_26']
    v = rede(sp, figur(sp, k, 'RLFIXER'), ['families'])
    pruefe(not any(o[0] == 'Mordino.' for o in sp.dialog_optionen), 'Mordino tot, trotzdem angeboten')
    allgemein(sp, 'nr made man')


def test_nr_eroeffnungsnacht(u):
    k = u.k
    sp, w = strumpfband(u)
    fixer = figur(sp, k, 'RLFIXER')
    v = rede(sp, fixer, ['families', 'What if', None])
    pruefe('First the deed' in texte(v) and not sp.finde(k['SCRIPT_RLANGREIFER']), 'ohne Urkunde keine Eroeffnung')
    rede(sp, figur(sp, k, 'RLWITWE'), ['buy the deed', "Here's a thousand", None])
    angriffe = len(sp.angriffe)
    rede(sp, fixer, ['families', 'What if', 'Let them come', None])
    angreifer = sp.finde(k['SCRIPT_RLANGREIFER'])
    pruefe(len(angreifer) == 3 and w.haus(NR, 'RL_F_ANGREIFER') == 3
           and w.haus(NR, 'RL_F_ANGRIFF') == k['RL_ANGRIFF_EROEFFNUNG'], 'drei Angreifer')
    pruefe(len(sp.angriffe) >= angriffe + 3, 'greifen an')
    pruefe(w.welt('RL_W_NR_EROEFFNUNG') == k['RL_EROEFFNUNG_KAMPF'] and w.welt('RL_W_ANGRIFF') == 0, 'Gosse unberuehrt')
    keine_figur(sp, k, 'RLFIXER')
    pruefe(not (w.welt('RL_W_NR_TOTE') & k['RL_NR_TOT_FIXER']), 'Pagano ist gegangen, nicht tot')
    # Karte verlassen und wiederkommen: die Angreifer bleiben, Pagano nicht
    betrete_strumpfband(u, sp)
    pruefe(len(sp.finde(k['SCRIPT_RLANGREIFER'])) == 3, 'Angreifer weg')
    keine_figur(sp, k, 'RLFIXER')
    o = angreifer[0]
    sp.meldungen.clear()
    o.skript.rufe('description_p_proc', self_obj=o, source=sp.dude)
    pruefe('colors' in sp.meldungen[-1], 'Beschreibung')
    for o in angreifer:
        sp.zerstoere(o)
    pruefe(w.haus(NR, 'RL_F_BESITZ') == 1 and w.welt('RL_W_NR_SEGEN') == k['RL_SEGEN_UNABHAENGIG'], 'unabhaengig')
    pruefe(w.welt('RL_W_NR_EROEFFNUNG') == k['RL_EROEFFNUNG_UEBERSTANDEN'] and w.haus(NR, 'RL_F_ANGRIFF') == 0, 'ueberstanden')
    pruefe(w.haus(NR, 'RL_F_TRIBUTMOD') == -20 and w.haus(NR, 'RL_F_HITZE') == 20, 'kein Tribut, Hitze +20')
    alle = sum(1 << k[f] for f in ('RL_SEGEN_MORDINO', 'RL_SEGEN_WRIGHT', 'RL_SEGEN_SALVATORE', 'RL_SEGEN_BISHOP'))
    pruefe(w.welt('RL_W_NR_MISSTRAUEN') == alle, 'alle misstrauisch')
    pruefe(w.haus(NR, 'RL_F_EINFLUSS') == 20, f'E {w.haus(NR, "RL_F_EINFLUSS")}')
    figur(sp, k, 'RLROZ')
    figur(sp, k, 'RLCONSIG')
    # Misstrauen: Hitze +2 je Familie und Woche, Abbau -5
    h = w.haus(NR, 'RL_F_HITZE')
    woche(sp)
    pruefe(w.haus(NR, 'RL_F_HITZE') == h + 8 - 5, f'Hitze {h} -> {w.haus(NR, "RL_F_HITZE")}')
    betrete_strumpfband(u, sp)
    pruefe(not sp.finde(k['SCRIPT_RLANGREIFER']), 'Angreifer nach dem Kampf')
    allgemein(sp, 'eroeffnung')


def test_nr_pagano_tot(u):
    k = u.k
    sp, w = strumpfband(u)
    sp.zerstoere(figur(sp, k, 'RLFIXER'))
    pruefe(w.welt('RL_W_NR_TOTE') & k['RL_NR_TOT_FIXER'], 'Tod vermerkt')
    betrete_strumpfband(u, sp)
    keine_figur(sp, k, 'RLFIXER')
    pruefe(not sp.finde(k['SCRIPT_RLANGREIFER']), 'Eroeffnung ohne Urkunde')
    rede(sp, figur(sp, k, 'RLWITWE'), ['buy the deed', "Here's a thousand", None])
    sp.meldungen.clear()
    betrete_strumpfband(u, sp)
    pruefe(len(sp.finde(k['SCRIPT_RLANGREIFER'])) == 3 and any('Two Chairs is dead' in m for m in sp.meldungen),
           'Eroeffnung von selbst')
    betrete_strumpfband(u, sp)
    pruefe(len(sp.finde(k['SCRIPT_RLANGREIFER'])) == 3, 'nur einmal')
    # Die Witwe tot: Pagano weiss vom Grab
    sp, w = strumpfband(u)
    sp.zerstoere(figur(sp, k, 'RLWITWE'))
    sp.dude.inventar[k['PID_SHOVEL']] = 1
    rede(sp, figur(sp, k, 'RLFIXER'), ['About the deed', 'grave', None])
    pruefe(w.welt('RL_W_NR_URKUNDE') == k['RL_URKUNDE_GRAB'], 'Grab ueber Pagano')
    allgemein(sp, 'pagano tot')


def test_nr_hauptquartier(u):
    k = u.k
    sp, e, ko, w = prolog(u, 'bezahlt')
    sp, w = _nr_uebernommen(u, 'Salvatore', sp)
    asch = figur(sp, k, 'RLCONSIG')
    v = rede(sp, asch, ['houses doing'])
    pruefe('The Gutter' in texte(v) and 'The Silver Garter' in texte(v), f'Bericht: {texte(v)[-200:]}')
    v = rede(sp, asch, ['families think'])
    pruefe('Salvatore is our godfather' in texte(v) and 'Bishop asks' in texte(v), f'Familien: {texte(v)[-200:]}')
    v = rede(sp, asch, ['next family meeting'])
    pruefe('family seat' in texte(v), 'kein Treffen ohne Familiensitz')
    # Laeufer: die Kasse der Gosse geht ins Hauptquartier
    sp.zufall_fest = 'max'
    woche(sp)
    sp.zufall_fest = None
    pruefe(w.haus(0, 'RL_F_KASSE') == 0 and w.welt('RL_W_HQ_KASSE') != 0, 'Laeufer')
    w.setze_welt('RL_W_HQ_KASSE', 700)
    geld = sp.dude.kronkorken
    rede(sp, asch, ['treasury', 'Pay it out', None])
    pruefe(sp.dude.kronkorken == geld + 700 and w.welt('RL_W_HQ_KASSE') == 0, 'Auszahlung')
    # Familiensitz: alle vier Wochen ein Treffen
    w.setze_haus(NR, 'RL_F_KLASSE', 3)
    woche(sp, 4)
    pruefe(w.welt('RL_W_TREFFEN_OFFEN') == k['RL_TREFFEN_SALVATORE'], f'Treffen {w.welt("RL_W_TREFFEN_OFFEN")}')
    pruefe(any('Asch is keeping a chair' in m for m in sp.meldungen), 'Meldung Treffen')
    trib = w.haus(NR, 'RL_F_TRIBUTMOD')
    rede(sp, asch, ['family meeting', 'Pay him', None])
    pruefe(w.haus(NR, 'RL_F_TRIBUTMOD') == trib + 5 and w.welt('RL_W_TREFFEN_OFFEN') == 0
           and w.welt('RL_W_TREFFEN_NR') == 1, 'Salvatore bezahlt')
    # Die weiteren Themen
    def treffen(thema, plan):
        w.setze_welt('RL_W_TREFFEN_OFFEN', k[thema])
        return rede(sp, asch, ['family meeting'] + plan + [None])
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    treffen('RL_TREFFEN_JET', ['Take the deal'])
    pruefe(w.welt('RL_W_JET_VERTRAG') == 1 and sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 10, 'Jet-Vertrag')
    pruefe(w.welt('RL_W_NR_MISSTRAUEN') & (1 << k['RL_SEGEN_WRIGHT']), 'Wright misstrauisch nach Jet')
    kasse = w.haus(NR, 'RL_F_KASSE')
    sp.zufall_fest = 'max'
    woche(sp)
    sp.zufall_fest = None
    pruefe(w.haus(NR, 'RL_F_KASSE') == kasse + 300 + w.haus(NR, 'RL_F_GEWINN'), 'Jet-Vertrag zahlt')
    e0 = w.haus(NR, 'RL_F_EINFLUSS')
    treffen('RL_TREFFEN_WRIGHT', ['Tell him'])
    pruefe(w.haus(NR, 'RL_F_EINFLUSS') == e0 + 10 and w.welt('RL_W_NR_MISSTRAUEN') & (1 << k['RL_SEGEN_MORDINO']), 'Wright')
    w.setze_welt('RL_W_HQ_KASSE', 400)
    geld = sp.dude.kronkorken
    treffen('RL_TREFFEN_SHARK', ['Pay the thousand'])
    pruefe(w.welt('RL_W_SHARK_ANTEIL') == 1 and w.welt('RL_W_HQ_KASSE') == 0 and sp.dude.kronkorken == geld - 600, 'Shark')
    hq = w.welt('RL_W_HQ_KASSE')
    w.setze_haus(0, 'RL_F_BESITZ', 0)          # nur der Anteil soll ins HQ fliessen
    woche(sp)
    pruefe(w.welt('RL_W_HQ_KASSE') == hq + 100, f'Shark zahlt: {w.welt("RL_W_HQ_KASSE") - hq}')
    sp.dude.stats[k['STAT_pe']] = 7
    treffen('RL_TREFFEN_LAEUFER', ['[Perception]'])
    pruefe(w.welt('RL_W_HQ_KASSE') == hq + 300, 'Laeufer gefunden')
    # Verpasst: die Folgen des Nein
    w.setze_welt('RL_W_TREFFEN_OFFEN', k['RL_TREFFEN_SALVATORE'])
    w.setze_welt('RL_W_TREFFEN_FRIST', 0)
    w.setze_welt('RL_W_NR_MISSTRAUEN', 0)
    woche(sp)
    pruefe(w.welt('RL_W_TREFFEN_OFFEN') == 0 and w.welt('RL_W_NR_MISSTRAUEN') == 1 << k['RL_SEGEN_SALVATORE'], 'verpasst')
    pruefe(any('decided without us' in m for m in sp.meldungen), 'Meldung verpasst')
    # Themen toter Familien entfallen
    for g, b in (('GVAR_NEW_RENO_SALVATORE', 'bit_10'), ('GVAR_NEW_RENO_WRIGHT_FLAGS', 'bit_4'),
                 ('GVAR_NEW_RENO_BISHOP', 'bit_10'), ('GVAR_NEW_RENO_FLAG_2', 'bit_26')):
        sp.gvars[k[g]] = sp.gvars.get(k[g], 0) | k[b]
    w.setze_welt('RL_W_TREFFEN_WOCHE', 0)
    w.setze_welt('RL_W_JET_VERTRAG', 1)
    woche(sp)
    pruefe(w.welt('RL_W_TREFFEN_OFFEN') == k['RL_TREFFEN_LAEUFER'], 'nur der Laeufer bleibt')
    pruefe(w.welt('RL_W_JET_VERTRAG') == 0, 'Jet-Vertrag endet mit den Mordinos')
    allgemein(sp, 'hauptquartier')


def _optionen_bei(verlauf, gewaehlt):
    """Die Optionen des Knotens, der nach der Wahl `gewaehlt` angezeigt wurde."""
    for i, (_, _, t) in enumerate(verlauf):
        if gewaehlt in t and i + 1 < len(verlauf):
            return verlauf[i + 1][1]
    return []


def _sondermodule(sp, roz):
    """Die Optionen der Gruppe "nur hier" im Ausbau-Menue (leer, wenn es sie nicht gibt)."""
    v = rede(sp, roz, ['build'])
    if not any('only get in New Reno' in o for o in _optionen_bei(v, 'What could we build')):
        return []
    return _optionen_bei(rede(sp, roz, ['build', 'only get in New Reno']), 'only get in New Reno')


def test_nr_jet_theke(u):
    k = u.k
    sp, w = _nr_uebernommen(u, 'Wright')
    roz = figur(sp, k, 'RLROZ')
    rede(sp, roz, ['how the house', None])
    pruefe(not any('Jet Counter' in o for o in _sondermodule(sp, roz)), 'Jet-Theke unter Wright')
    w.setze_welt('RL_W_JET_VERTRAG', 1)
    pruefe(not any('Jet Counter' in o for o in _sondermodule(sp, roz)), 'Jet-Theke unter Wright trotz Vertrag')
    sp, w = _nr_uebernommen(u, 'Mordino')
    roz = figur(sp, k, 'RLROZ')
    rede(sp, roz, ['how the house', None])
    pruefe(any('Jet Counter ($800)' in o for o in _sondermodule(sp, roz)), 'Jet-Theke unter Mordino')
    rede(sp, roz, ['build', 'only get in New Reno', 'Jet Counter', 'Build it', None])
    pruefe(w.haus(NR, 'RL_F_BAU_ID') == k['RL_SONDER_BASIS'] + k['RL_SM_JET_THEKE'] + 1
           and w.haus(NR, 'RL_F_BAU_WOCHEN') == 2, 'Baustelle')
    woche(sp, 2)
    pruefe(w.haus(NR, 'RL_F_MODULE') & k['RL_MOD_JET_THEKE'] and w.haus(NR, 'RL_F_NEBEN') == 9, 'Jet-Theke fertig')
    pruefe(w.welt('RL_W_NR_MISSTRAUEN') & (1 << k['RL_SEGEN_WRIGHT']), 'Wright misstrauisch')
    pruefe(not any('Jet Counter' in o for o in _sondermodule(sp, roz)), 'Jet-Theke zweimal')
    allgemein(sp, 'jet-theke')


def test_nr_tote_figuren(u):
    k = u.k
    sp, w = _nr_uebernommen(u, 'Salvatore')
    w.setze_welt('RL_W_HQ_KASSE', 250)
    sp.zerstoere(figur(sp, k, 'RLCONSIG'))
    betrete_strumpfband(u, sp)
    keine_figur(sp, k, 'RLCONSIG')
    geld = sp.dude.kronkorken
    rede(sp, figur(sp, k, 'RLROZ'), ['how the house', "Asch's safe", None])
    pruefe(sp.dude.kronkorken == geld + 250 and w.welt('RL_W_HQ_KASSE') == 0, 'Roz zahlt die HQ-Kasse aus')
    sp, w = _nr_uebernommen(u, 'Salvatore')
    sp.zerstoere(figur(sp, k, 'RLROZ'))
    pruefe(w.haus(NR, 'RL_F_FUEHRUNG') == 30, 'Fuehrung ohne Roz')
    w.setze_haus(NR, 'RL_F_KASSE', 120)
    betrete_strumpfband(u, sp)
    keine_figur(sp, k, 'RLROZ')
    geld = sp.dude.kronkorken
    rede(sp, figur(sp, k, 'RLCONSIG'), ["Roz's till", None])
    pruefe(sp.dude.kronkorken == geld + 120, 'Asch zahlt die Kasse des Strumpfbands aus')
    allgemein(sp, 'tote figuren')


def test_erkundung_newreno(u):
    """Alle Dialogpfade der Figuren im Strumpfband."""
    k = u.k
    gesamt = 0
    for skill in (0, 60):
        sp, w = strumpfband(u)
        for s in ('SKILL_BARTER', 'SKILL_SPEECH', 'SKILL_SNEAK', 'SKILL_SCIENCE', 'SKILL_LOCKPICK',
                  'SKILL_STEAL', 'SKILL_SMALL_GUNS'):
            sp.dude.skills[k[s]] = skill
        sp.dude.stats[k['STAT_pe']] = 7 if skill else 5
        sp.dude.inventar[k['PID_SHOVEL']] = 1 if skill else 0
        gesamt += erkunde(sp, figur(sp, k, 'RLWITWE'), f'Witwe {skill}')[1]
        gesamt += erkunde(sp, figur(sp, k, 'RLFIXER'), f'Pagano {skill}')[1]
        rede(sp, figur(sp, k, 'RLWITWE'), ['buy the deed', "Here's a thousand", None])
        gesamt += erkunde(sp, figur(sp, k, 'RLFIXER'), f'Pagano mit Urkunde {skill}')[1]
    sp, w = strumpfband(u)
    rede(sp, figur(sp, k, 'RLFIXER'), ['families', 'Bishop', 'Give me the letter', None])
    gesamt += erkunde(sp, figur(sp, k, 'RLFIXER'), 'Pagano Brief unterwegs')[1]
    w.setze_welt('RL_W_NR_BRIEF', k['RL_BRIEF_ABGEGEBEN'])
    gesamt += erkunde(sp, figur(sp, k, 'RLFIXER'), 'Pagano Brief abgegeben')[1]
    sp.gvars[k['GVAR_MADE_MAN_BISHOP']] = 1
    w.setze_welt('RL_W_NR_BRIEF', 0)
    gesamt += erkunde(sp, figur(sp, k, 'RLFIXER'), 'Pagano Made Man')[1]
    w.setze_welt('RL_W_NR_WITWE', k['RL_WITWE_FORDERT'])
    gesamt += erkunde(sp, figur(sp, k, 'RLWITWE'), 'Witwe fordert')[1]
    sp, w = _nr_uebernommen(u, 'Mordino')
    roz = figur(sp, k, 'RLROZ')
    gesamt += erkunde(sp, roz, 'Roz erstes Gespraech')[1]
    rede(sp, roz, ['how the house', None])
    gesamt += erkunde(sp, roz, 'Roz Manager')[1]
    asch = figur(sp, k, 'RLCONSIG')
    gesamt += erkunde(sp, asch, 'Asch')[1]
    w.setze_haus(NR, 'RL_F_KLASSE', 3)
    w.setze_welt('RL_W_NR_BRIEF', k['RL_BRIEF_ERLEDIGT_OFFEN'])
    for skill in (0, 70):
        sp.dude.skills[k['SKILL_SPEECH']] = skill
        sp.dude.stats[k['STAT_pe']] = 7 if skill else 5
        for thema in range(1, k['RL_TREFFEN_ANZAHL'] + 1):
            w.setze_welt('RL_W_TREFFEN_OFFEN', thema)
            gesamt += erkunde(sp, asch, f'Asch Treffen {thema} ({skill})')[1]
    w.setze_welt('RL_W_TREFFEN_OFFEN', 0)
    w.setze_welt('RL_W_NR_TOTE', k['RL_NR_TOT_ROZ'] | k['RL_NR_TOT_ASCH'])
    w.setze_welt('RL_W_HQ_KASSE', 100)
    w.setze_haus(NR, 'RL_F_KASSE', 100)
    gesamt += erkunde(sp, asch, 'Asch ohne Roz')[1]
    gesamt += erkunde(sp, roz, 'Roz ohne Asch')[1]
    print(f'      {gesamt} Dialogzustaende in New Reno erkundet')


# --------------------------------------------------------------------------
# Umsetzung 8: Redding, Ascortis Lizenz, Waage, Malamute

RED = 2


def schlacke(u, sp=None):
    """Die Schlacke betreten (Kartenskript RLRED01); liefert (sp, w)."""
    k = u.k
    sp = sp or u.neues_spiel()
    if not sp.finde(k['SCRIPT_RLRED01']):
        sp.erzeuge(0, -1, 0, k['SCRIPT_RLRED01'], 'Kartenskript RLRED01')
    betrete_schlacke(u, sp)
    return sp, Welt(sp, k)


def betrete_schlacke(u, sp):
    sp.betrete_karte(u.cfg['RL_MAP_INDEX'] + RED)
    sp.temp_freigeben()


def _red_uebernommen(u, sp=None):
    k = u.k
    sp, w = schlacke(u, sp)
    rede(sp, figur(sp, k, 'RLSCHREIBER'), ['package cost', "Here's a thousand", None])
    pruefe(w.haus(RED, 'RL_F_BESITZ') == 1, 'Schlacke nicht uebernommen')
    return sp, w


def test_red_lizenz_wege(u):
    k = u.k
    # Paket
    sp, w = schlacke(u)
    keine_figur(sp, k, 'RLNELL')
    geld = sp.dude.kronkorken
    v = rede(sp, figur(sp, k, 'RLSCHREIBER'), ['package cost', "Here's a thousand", None])
    pruefe(sp.dude.kronkorken == geld - 1000 and w.welt('RL_W_RED_LIZENZ') == k['RL_LIZENZ_PAKET'], 'Paket')
    pruefe(w.haus(RED, 'RL_F_BESITZ') == 1 and w.haus(RED, 'RL_F_BESTECHUNG_MOD') == 0, 'Besitz, 75 $/Woche')
    pruefe(w.haus(RED, 'RL_F_FUEHRUNG') == 50 and w.haus(RED, 'RL_F_EINFLUSS') == 20, 'Fuehrung, Einfluss')
    pruefe('Nell Harrow' in texte(v), 'Nell angekuendigt')
    keine_figur(sp, k, 'RLSCHREIBER')
    nell = figur(sp, k, 'RLNELL')
    v = rede(sp, nell, ['how the house'])
    pruefe('laundress' in texte(v) or 'Nell Harrow' in texte(v), 'Nell stellt sich vor')
    betrete_schlacke(u, sp)
    figur(sp, k, 'RLNELL')
    keine_figur(sp, k, 'RLSCHREIBER')
    # Barter
    sp, w = schlacke(u)
    sp.dude.skills[k['SKILL_BARTER']] = 60
    geld = sp.dude.kronkorken
    rede(sp, figur(sp, k, 'RLSCHREIBER'), ['package cost', '[Barter]', None])
    pruefe(sp.dude.kronkorken == geld - 600, 'Barter 600')
    # Aufschlag
    sp, w = schlacke(u)
    sp.dude.skills[k['SKILL_SPEECH']] = 70
    geld = sp.dude.kronkorken
    rede(sp, figur(sp, k, 'RLSCHREIBER'), ['[Speech]', None])
    pruefe(sp.dude.kronkorken == geld and w.haus(RED, 'RL_F_BESTECHUNG_MOD') == 50
           and w.welt('RL_W_RED_LIZENZ') == k['RL_LIZENZ_AUFSCHLAG'], 'Aufschlag 125 $/Woche')
    # Blossstellen: Kassenbuch und Marion
    sp, w = schlacke(u)
    sp.dude.skills[k['SKILL_LOCKPICK']] = 60
    schreiber = figur(sp, k, 'RLSCHREIBER')
    v = rede(sp, schreiber, ['about Ascorti', '[Lockpick]', None])
    pruefe(w.welt('RL_W_RED_BELEG') == 1 and w.haus(RED, 'RL_F_BESITZ') == 0, 'Beleg ohne Speech')
    pruefe('worth nothing' in texte(v), 'ohne Speech wertlos')
    sp.dude.skills[k['SKILL_SPEECH']] = 60
    rede(sp, schreiber, ['about Ascorti', 'Sheriff Marion', None])
    pruefe(w.welt('RL_W_RED_LIZENZ') == k['RL_LIZENZ_MARION'] and w.welt('RL_W_MARION') == k['RL_MARION_SCHUTZ'], 'Marion')
    pruefe(w.haus(RED, 'RL_F_SICHERHEIT') == 55 and w.haus(RED, 'RL_F_BESTECHUNG_MOD') == -75
           and w.welt('RL_W_ASCORTI') == 1, 'Schutzherr, kein Schmiergeld, Ascorti Feind')
    # Einschuechtern
    sp, w = schlacke(u)
    sp.dude.stats[k['STAT_st']] = 7
    rede(sp, figur(sp, k, 'RLSCHREIBER'), ['[Threaten]', None])
    pruefe(w.welt('RL_W_RED_LIZENZ') == k['RL_LIZENZ_DROHUNG'] and w.haus(RED, 'RL_F_BESTECHUNG_MOD') == -75
           and w.haus(RED, 'RL_F_HITZE') == 20 and w.welt('RL_W_MARION') == k['RL_MARION_WACHSAM'], 'Drohung')
    allgemein(sp, 'red lizenz')


def test_red_schreiber_tot(u):
    k = u.k
    sp, w = schlacke(u)
    sp.zerstoere(figur(sp, k, 'RLSCHREIBER'))
    pruefe(w.welt('RL_W_RED_SCHREIBER') == 1, 'Tod gezaehlt')
    betrete_schlacke(u, sp)
    v = rede(sp, figur(sp, k, 'RLSCHREIBER'), [])
    pruefe('last clerk had an accident' in texte(v), 'der Neue')
    allgemein(sp, 'schreiber tot')


def test_red_waage(u):
    k = u.k
    sp, w = _red_uebernommen(u)
    nell = figur(sp, k, 'RLNELL')
    rede(sp, nell, ['how the house', None])
    sp.dude.kronkorken = 5000
    rede(sp, nell, ['build', 'only get in Redding', 'Rigged Scale', 'Build it', None])
    pruefe(w.haus(RED, 'RL_F_BAU_ID') == k['RL_SONDER_BASIS'] + k['RL_SM_WAAGE'] + 1, 'Baustelle Waage')
    v = rede(sp, nell, ['build'])
    pruefe(not any('Honest Gold Scale' in o for o in _optionen_bei(v, 'build')), 'ehrliche Waage trotz gezinkter')
    sp.zufall_fest = 'max'                  # keine Ereignisse, Marion findet nichts
    woche(sp)
    pruefe(w.haus(RED, 'RL_F_MODULE') & k['RL_MOD_WAAGE_GEZINKT'] and w.haus(RED, 'RL_F_PREISMOD') == 15, 'Waage fertig')
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    woche(sp)
    sp.zufall_fest = None
    pruefe(sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 2, f'Karma {karma} -> {sp.gvars[k["GVAR_PLAYER_REPUTATION"]]}')
    # Marion findet sie: Revolte
    sp.zufall_folge = [1]
    woche(sp)
    pruefe(w.haus(RED, 'RL_F_GESCHLOSSEN') == 3 - 1 or w.haus(RED, 'RL_F_GESCHLOSSEN') == 3, 'geschlossen')
    pruefe(not (w.haus(RED, 'RL_F_MODULE') & k['RL_MOD_WAAGE_GEZINKT']) and w.haus(RED, 'RL_F_PREISMOD') == 0, 'Waage weg')
    pruefe(w.haus(RED, 'RL_F_BESTECHUNG_MOD') == 75, 'Ascorti will das Doppelte')
    pruefe(w.welt('RL_W_MARION') == k['RL_MARION_WACHSAM'], 'Marion wachsam')
    pruefe(any('rigged scale' in m for m in sp.meldungen), 'Meldung Revolte')
    sp.zufall_fest = 'max'
    woche(sp)
    pruefe(w.haus(RED, 'RL_F_KUNDEN') == 0, 'keine Kunden, solange geschlossen')
    woche(sp, 3)
    sp.zufall_fest = None
    pruefe(w.haus(RED, 'RL_F_GESCHLOSSEN') == 0 and w.haus(RED, 'RL_F_KUNDEN') > 0, 'wieder offen')
    # Die ehrliche Waage schliesst die gezinkte aus
    sp, w = _red_uebernommen(u)
    nell = figur(sp, k, 'RLNELL')
    rede(sp, nell, ['how the house', None])
    rede(sp, nell, ['build', 'only get in Redding', 'Honest Gold Scale', 'Build it', None])
    pruefe(w.haus(RED, 'RL_F_BAU_ID') == k['RL_M_RED_GOLDWAAGE'] + 1, 'ehrliche Waage')
    woche(sp)
    v = rede(sp, nell, ['build'])
    gruppe = _optionen_bei(rede(sp, nell, ['build', 'only get in Redding']), 'only get in Redding') \
        if any('only get in Redding' in o for o in _optionen_bei(v, 'build')) else []
    pruefe(not any('Rigged' in o for o in gruppe), 'gezinkte Waage trotz ehrlicher')
    allgemein(sp, 'waage')


def test_red_malamute(u):
    k = u.k
    # Beteiligung
    sp, w = _red_uebernommen(u)
    nell = figur(sp, k, 'RLNELL')
    rede(sp, nell, ['how the house', None])
    sp.dude.skills[k['SKILL_BARTER']] = 60
    rede(sp, nell, ['Malamute', 'Buy a share', None])
    pruefe(w.welt('RL_W_MALAMUTE') == 1 and w.welt('RL_W_MALAMUTE_WEG') == k['RL_MALAMUTE_BETEILIGUNG'], 'Beteiligung')
    kasse = w.haus(RED, 'RL_F_KASSE')
    sp.zufall_fest = 'max'
    woche(sp)
    sp.zufall_fest = None
    pruefe(w.haus(RED, 'RL_F_KASSE') == kasse + 60 + w.haus(RED, 'RL_F_GEWINN'), 'Anteil 60 $')
    pruefe(w.haus(RED, 'RL_F_STADTMOD') > -30, 'Abzug weg')
    v = rede(sp, nell, [])
    pruefe(not any('Malamute' in o for o in v[0][1]), 'Malamute-Option nach der Loesung')
    # Preiskrieg: nur Wochen mit Ramsch zaehlen
    sp, w = _red_uebernommen(u)
    nell = figur(sp, k, 'RLNELL')
    rede(sp, nell, ['how the house', None])
    rede(sp, nell, ['Malamute', 'Undercut', None])
    pruefe(w.haus(RED, 'RL_F_PREISSTUFE') == k['RL_PREIS_RAMSCH'], 'Ramsch')
    woche(sp, 2)
    w.setze_haus(RED, 'RL_F_PREISSTUFE', k['RL_PREIS_STANDARD'])
    woche(sp)
    pruefe(w.welt('RL_W_MALAMUTE_WOCHEN') == 2 and w.welt('RL_W_MALAMUTE') == 0, 'Standard zaehlt nicht')
    v = rede(sp, nell, ['Malamute'])
    pruefe('2 week(s)' in texte(v), 'Stand des Preiskriegs')
    w.setze_haus(RED, 'RL_F_PREISSTUFE', k['RL_PREIS_RAMSCH'])
    woche(sp, 2)
    pruefe(w.welt('RL_W_MALAMUTE') == 1 and any('Malamute gave up' in m for m in sp.meldungen), 'Preiskrieg gewonnen')
    # Sabotage: erwischt oder nicht
    for wurf, feind in ((100, True), (1, False)):
        sp, w = _red_uebernommen(u)
        nell = figur(sp, k, 'RLNELL')
        rede(sp, nell, ['how the house', None])
        sp.dude.skills[k['SKILL_SNEAK']] = 60
        karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
        sp.zufall_folge = [wurf]
        rede(sp, nell, ['Malamute', '[Sneak]', None])
        pruefe(w.welt('RL_W_MALAMUTE') == 1 and sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 10, 'Sabotage')
        pruefe((w.welt('RL_W_MARION') == k['RL_MARION_FEIND']) == feind, f'Marion Feind: {feind}')
    # Uebernahme
    sp, w = _red_uebernommen(u)
    nell = figur(sp, k, 'RLNELL')
    rede(sp, nell, ['how the house', None])
    sp.dude.kronkorken = 3000
    v = rede(sp, nell, ['Malamute'])
    pruefe(not any('Buy them out' in o for o in _optionen_bei(v, 'Malamute')), 'Uebernahme ohne E 40')
    w.setze_haus(RED, 'RL_F_EINFLUSS', 40)
    zimmer = w.haus(RED, 'RL_F_ZIMMER')
    rede(sp, nell, ['Malamute', 'Buy them out', None])
    pruefe(w.welt('RL_W_MALAMUTE_WEG') == k['RL_MALAMUTE_UEBERNAHME'] and w.haus(RED, 'RL_F_ZIMMER') == zimmer + 2, 'Uebernahme')
    allgemein(sp, 'malamute')


def test_red_marion_wanamingo(u):
    k = u.k
    sp, w = _red_uebernommen(u)
    sich = w.haus(RED, 'RL_F_SICHERHEIT')
    sp.gvars[k['GVAR_WANAMINGO_OCCUPADO']] = k['WANAMINGO_CLEARED_OUT']
    woche(sp)
    pruefe(w.welt('RL_W_MARION') == k['RL_MARION_SCHUTZ'] and w.haus(RED, 'RL_F_SICHERHEIT') == sich + 10, 'Schutzherr')
    woche(sp)
    pruefe(w.haus(RED, 'RL_F_SICHERHEIT') == sich + 10, 'nur einmal')
    # Vor der Lizenz: Schutz zaehlt bei der Uebernahme
    sp, w = schlacke(u)
    sp.gvars[k['GVAR_WANAMINGO_OCCUPADO']] = k['WANAMINGO_CLEARED_OUT']
    w.setze_haus(0, 'RL_F_BESITZ', 1)          # Wochentakt laeuft erst mit einem eigenen Haus
    w.setze_welt('RL_W_AKTIV', 1)
    woche(sp)
    pruefe(w.welt('RL_W_MARION') == k['RL_MARION_SCHUTZ'], 'Schutzherr vor der Lizenz')
    rede(sp, figur(sp, k, 'RLSCHREIBER'), ['package cost', "Here's a thousand", None])
    pruefe(w.haus(RED, 'RL_F_SICHERHEIT') == 55, 'Bonus bei der Uebernahme')
    allgemein(sp, 'marion')


def test_red_entzugsstube(u):
    k = u.k
    sp, w = _red_uebernommen(u)
    g = sp.globale[0]
    hid = sp.gespeichert['RL_HAUS']
    pruefe(g.rufe_mit('rl_red_entzug', hid) == 0, 'ohne Entzugsstube')
    w.setze_haus(RED, 'RL_F_GEKAUFT', 1 << k['RL_M_RED_ENTZUGSSTUBE'])
    w.setze_haus(RED, 'RL_F_BAU_ID', k['RL_M_RED_ENTZUGSSTUBE'] + 1)
    pruefe(g.rufe_mit('rl_red_entzug', hid) == 0, 'im Bau')
    w.setze_haus(RED, 'RL_F_BAU_ID', 0)
    pruefe(g.rufe_mit('rl_red_entzug', hid) != 0, 'gebaut')
    allgemein(sp, 'entzugsstube')


def test_erkundung_redding(u):
    k = u.k
    gesamt = 0
    for skill in (0, 70):
        sp, w = schlacke(u)
        for s in ('SKILL_BARTER', 'SKILL_SPEECH', 'SKILL_STEAL', 'SKILL_LOCKPICK', 'SKILL_UNARMED_COMBAT', 'SKILL_SNEAK'):
            sp.dude.skills[k[s]] = skill
        gesamt += erkunde(sp, figur(sp, k, 'RLSCHREIBER'), f'Schreiber {skill}')[1]
        w.setze_welt('RL_W_RED_BELEG', 1)
        w.setze_welt('RL_W_RED_SCHREIBER', 1)
        gesamt += erkunde(sp, figur(sp, k, 'RLSCHREIBER'), f'Schreiber mit Beleg {skill}')[1]
    sp, w = _red_uebernommen(u)
    nell = figur(sp, k, 'RLNELL')
    gesamt += erkunde(sp, nell, 'Nell erstes Gespraech')[1]
    rede(sp, nell, ['how the house', None])
    for skill in (0, 60):
        sp.dude.skills[k['SKILL_BARTER']] = skill
        sp.dude.skills[k['SKILL_SNEAK']] = skill
        w.setze_haus(RED, 'RL_F_EINFLUSS', 40 if skill else 20)
        gesamt += erkunde(sp, nell, f'Nell {skill}')[1]
    w.setze_welt('RL_W_MALAMUTE_WEG', k['RL_MALAMUTE_PREISKRIEG'])
    gesamt += erkunde(sp, nell, 'Nell Preiskrieg')[1]
    print(f'      {gesamt} Dialogzustaende in Redding erkundet')


# --------------------------------------------------------------------------
# Umsetzung 9: Vault City, Ein Keller im Courtyard, Razzia, Akte

VC = 3


def kloake(u, sp=None):
    """Die Kloake betreten (Kartenskript RLVCT01); liefert (sp, w)."""
    k = u.k
    sp = sp or u.neues_spiel()
    if not sp.finde(k['SCRIPT_RLVCT01']):
        sp.erzeuge(0, -1, 0, k['SCRIPT_RLVCT01'], 'Kartenskript RLVCT01')
    sp.betrete_karte(u.cfg['RL_MAP_INDEX'] + VC)
    sp.temp_freigeben()
    return sp, Welt(sp, k)


def _vc_uebernommen(u, sp=None, buerger=True):
    k = u.k
    sp, w = kloake(u, sp)
    if buerger:
        sp.gvars[k['GVAR_VAULT_CITIZEN']] = k['CITIZEN_REAL_CITIZEN']
    rede(sp, figur(sp, k, 'RLHANNE'), ['buy the house', 'talk about the house', 'citizen of Vault City', None])
    pruefe(w.haus(VC, 'RL_F_BESITZ') == 1, 'Kloake nicht uebernommen')
    return sp, w


def test_vc_uebernahme(u):
    k = u.k
    # Speech 60 und Buergerschaft
    sp, w = kloake(u)
    hanne = figur(sp, k, 'RLHANNE')
    figur(sp, k, 'RLSORENSEN')
    sp.dude.skills[k['SKILL_SPEECH']] = 60
    rede(sp, hanne, ['[Speech]', None])
    pruefe(w.welt('RL_W_VC_HANNE') == k['RL_HANNE_ANTEIL'] and w.haus(VC, 'RL_F_BESITZ') == 0, 'Hanne ohne Papiere')
    v = rede(sp, hanne, [])
    pruefe('need papers' in texte(v), 'Hanne will Papiere')
    pruefe(not any('citizen' in o for o in v[0][1]), 'Buergerschaft ohne Buergerschaft angeboten')
    sp.gvars[k['GVAR_VAULT_CITIZEN']] = k['CITIZEN_REAL_CITIZEN']
    v = rede(sp, hanne, ['citizen of Vault City', 'how the cellar', None])
    pruefe(w.haus(VC, 'RL_F_BESITZ') == 1 and w.welt('RL_W_VC_PAPIERE') == k['RL_PAPIERE_BUERGER'], 'Buergerschaft')
    pruefe(w.haus(VC, 'RL_F_TRIBUTMOD') == 10 and w.haus(VC, 'RL_F_BESTECHUNG_MOD') == -50, 'Anteil 10 %, Schweigegeld -50')
    pruefe(w.haus(VC, 'RL_F_PREISSTUFE') == k['RL_PREIS_GEHOBEN'] and w.haus(VC, 'RL_F_ZIMMER') == 2, 'Start gehoben, 2 Zimmer')
    pruefe('Last week we had' in texte(v), 'Hanne als Madame')
    # Gekauft und bei Sorensen bestochen
    sp, w = kloake(u)
    geld = sp.dude.kronkorken
    rede(sp, figur(sp, k, 'RLHANNE'), ['buy the house', None])
    sp.dude.skills[k['SKILL_BARTER']] = 40
    v = rede(sp, figur(sp, k, 'RLSORENSEN'), ['papers', '[Barter]', None])
    pruefe(w.haus(VC, 'RL_F_BESITZ') == 1 and sp.dude.kronkorken == geld - 2000
           and w.welt('RL_W_VC_PAPIERE') == k['RL_PAPIERE_SORENSEN'], 'Sorensen')
    pruefe(w.haus(VC, 'RL_F_TRIBUTMOD') == 0 and w.haus(VC, 'RL_F_BESTECHUNG_MOD') == 0, 'kein Anteil, volles Schweigegeld')
    # Faelschung
    sp, w = kloake(u)
    sp.dude.skills[k['SKILL_SCIENCE']] = 60
    rede(sp, figur(sp, k, 'RLHANNE'), ['[Science]', 'talk about the house', 'buy the house', None])
    pruefe(w.welt('RL_W_VC_PAPIERE') == k['RL_PAPIERE_FAELSCHUNG'] and w.haus(VC, 'RL_F_HITZE') == 5, 'Faelschung H +5')
    allgemein(sp, 'vc uebernahme')


def test_vc_schweigegeld_und_wache(u):
    k = u.k
    sp, w = _vc_uebernommen(u)
    w.setze_haus(VC, 'RL_F_KLASSE', 2)
    sp.zufall_fest = 'max'
    woche(sp)
    pruefe(w.haus(VC, 'RL_F_BESTECHUNG_MOD') == 150, f'Schweigegeld Klasse 2: {w.haus(VC, "RL_F_BESTECHUNG_MOD")}')
    hanne = figur(sp, k, 'RLHANNE')
    v = rede(sp, hanne, ['eye at the gate'])
    pruefe(not any('[Charisma]' in o for o in _optionen_bei(v, 'eye at the gate')), 'Charisma ohne CH 6')
    sp.dude.stats[k['STAT_ch']] = 6
    rede(sp, hanne, ['eye at the gate', '[Charisma]', None])
    pruefe(w.welt('RL_W_VC_WACHE') == k['RL_WACHE_ANGEWORBEN'] and w.haus(VC, 'RL_F_BESTECHUNG_MOD') == 200, 'Wache +50')
    woche(sp)
    sp.zufall_fest = None
    pruefe(w.haus(VC, 'RL_F_BESTECHUNG_MOD') == 200, 'bleibt')
    allgemein(sp, 'schweigegeld')


def test_vc_razzia(u):
    k = u.k
    # Ohne Warnung: sofort; freikaufen bei Sorensen
    sp, w = _vc_uebernommen(u)
    g = sp.globale[0]
    w.setze_haus(VC, 'RL_F_PERSONAL', 4)
    w.setze_haus(VC, 'RL_F_ZIMMER', 4)
    g.rufe_mit('rl_vc_razzia_kommt')
    pruefe(w.welt('RL_W_VC_GEFASST') == 2 and w.haus(VC, 'RL_F_PERSONAL') == 2 and w.haus(VC, 'RL_F_GESCHLOSSEN') == 1, 'Razzia')
    pruefe(any('Corrections Center' in m for m in sp.meldungen), 'Meldung')
    geld = sp.dude.kronkorken
    v = rede(sp, figur(sp, k, 'RLSORENSEN'), ['Corrections Center. ($600)', None])
    pruefe(w.welt('RL_W_VC_GEFASST') == 0 and w.haus(VC, 'RL_F_PERSONAL') == 4 and sp.dude.kronkorken == geld - 600, 'freigekauft')
    # Befreien
    g.rufe_mit('rl_vc_razzia_kommt')
    sp.dude.skills[k['SKILL_SNEAK']] = 70
    sp.dude.skills[k['SKILL_LOCKPICK']] = 70
    h0 = w.haus(VC, 'RL_F_HITZE')
    rede(sp, figur(sp, k, 'RLHANNE'), ['Corrections Center', 'break them out', None])
    pruefe(w.welt('RL_W_VC_GEFASST') == 0 and w.haus(VC, 'RL_F_HITZE') == min(100, h0 + 30), 'befreit')
    # Aufgeben: alle Haeuser leiden
    g.rufe_mit('rl_vc_razzia_kommt')
    w.setze_haus(VC, 'RL_F_MORAL', 60)
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    rede(sp, figur(sp, k, 'RLHANNE'), ['Corrections Center', 'Let them go', None])
    pruefe(w.welt('RL_W_VC_GEFASST') == 0 and w.haus(VC, 'RL_F_MORAL') == 30
           and sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 10, 'aufgegeben')
    allgemein(sp, 'razzia')


def test_vc_razzia_angekuendigt(u):
    k = u.k
    for schliessen in (True, False):
        sp, w = _vc_uebernommen(u)
        g = sp.globale[0]
        w.setze_welt('RL_W_VC_WACHE', k['RL_WACHE_ANGEWORBEN'])
        w.setze_haus(VC, 'RL_F_PERSONAL', 2)
        g.rufe_mit('rl_vc_razzia_kommt')
        pruefe(w.welt('RL_W_VC_RAZZIA_WOCHE') > 0 and w.welt('RL_W_VC_GEFASST') == 0, 'angekuendigt')
        pruefe(any('next week' in m for m in sp.meldungen), 'Meldung Warnung')
        if schliessen:
            rede(sp, figur(sp, k, 'RLHANNE'), ['Close the cellar', None])
            pruefe(w.haus(VC, 'RL_F_GESCHLOSSEN') == 1, 'geschlossen')
        sp.zufall_fest = 'max'
        woche(sp)
        sp.zufall_fest = None
        if schliessen:
            pruefe(w.welt('RL_W_VC_GEFASST') == 0 and any('empty cellar' in m for m in sp.meldungen), 'nichts gefunden')
            pruefe(w.haus(VC, 'RL_F_KUNDEN') == 0 and w.haus(VC, 'RL_F_GESCHLOSSEN') == 0, 'eine Woche zu')
        else:
            pruefe(w.welt('RL_W_VC_GEFASST') == 1, 'gefasst')
        pruefe(w.welt('RL_W_VC_RAZZIA_WOCHE') == 0, 'erledigt')
        allgemein(sp, f'angekuendigt {schliessen}')


def test_vc_akte_und_lynette(u):
    k = u.k
    sp, w = _vc_uebernommen(u)
    hanne = figur(sp, k, 'RLHANNE')
    sp.dude.kronkorken = 5000
    rede(sp, hanne, ['build', 'only get in Vault City', 'The File', 'Build it', None])
    pruefe(w.haus(VC, 'RL_F_BAU_ID') == k['RL_SONDER_BASIS'] + k['RL_SM_AKTE'] + 1, 'Baustelle Akte')
    sp.zufall_fest = 'max'
    woche(sp)
    pruefe(w.haus(VC, 'RL_F_MODULE') & k['RL_MOD_AKTE'] and w.haus(VC, 'RL_F_HITZE') == 10, 'Akte fertig, H +10')
    e = w.haus(VC, 'RL_F_EINFLUSS')
    woche(sp)
    sp.zufall_fest = None
    pruefe(w.haus(VC, 'RL_F_EINFLUSS') == e + 2, 'E +2')
    # Die Akte wird gefunden: sofort Razzia, Akte weg
    g = sp.globale[0]
    w.setze_haus(VC, 'RL_F_PERSONAL', 2)
    sp.zufall_fest = 'min'
    g.rufe_mit('rl_vc_woche', 999)
    sp.zufall_fest = None
    pruefe(w.welt('RL_W_VC_GEFASST') == 1 and not (w.haus(VC, 'RL_F_MODULE') & k['RL_MOD_AKTE']), 'Akte gefunden')
    pruefe(any('found the File' in m for m in sp.meldungen), 'Meldung Akte')
    # Lynette: mit der Akte enden die Razzien
    sp, w = _vc_uebernommen(u)
    w.setze_haus(VC, 'RL_F_MODULE', k['RL_MOD_AKTE'])
    e = w.haus(VC, 'RL_F_EINFLUSS')
    rede(sp, figur(sp, k, 'RLHANNE'), ['Use the File', None])
    pruefe(w.welt('RL_W_VC_LYNETTE') == 1 and w.haus(VC, 'RL_F_EINFLUSS') == e + 20, 'Lynette')
    w.setze_haus(VC, 'RL_F_PERSONAL', 2)
    sp.globale[0].rufe_mit('rl_vc_razzia_kommt')
    pruefe(w.welt('RL_W_VC_GEFASST') == 0 and w.welt('RL_W_VC_RAZZIA_WOCHE') == 0, 'keine Razzia mehr')
    allgemein(sp, 'akte')


def test_vc_pacht_und_sorensen(u):
    k = u.k
    sp, w = _vc_uebernommen(u)
    so = figur(sp, k, 'RLSORENSEN')
    w.setze_haus(VC, 'RL_F_ZIMMER', 3)
    w.setze_haus(VC, 'RL_F_PERSONAL', 2)
    loehne = w.haus(VC, 'RL_F_LOEHNE')
    rede(sp, so, ['Lease me one', None])
    pruefe(w.haus(VC, 'RL_F_ZWANG') == 1 and w.haus(VC, 'RL_F_PERSONAL') == 3 and w.haus(VC, 'RL_F_LOEHNE') == loehne + 50, 'Pacht')
    v = rede(sp, so, [])
    pruefe(not any('Lease me one' in o for o in v[0][1]), 'Pacht ohne freies Zimmer')
    # Razzia: Die Gepachteten gehen als Zeugen zurueck
    sp.globale[0].rufe_mit('rl_vc_razzia_kommt')
    pruefe(w.haus(VC, 'RL_F_ZWANG') == 0 and w.haus(VC, 'RL_F_LOEHNE') == loehne, 'Zeugen zurueck')
    # Zurueckgeben
    rede(sp, so, ['Corrections', None])
    w.setze_haus(VC, 'RL_F_PERSONAL', 1)
    rede(sp, so, ['Lease me one', None])
    rede(sp, so, ['Send the leased', None])
    pruefe(w.haus(VC, 'RL_F_ZWANG') == 0 and w.haus(VC, 'RL_F_PERSONAL') == 1, 'zurueckgegeben')
    # Die Wache ueber Sorensen: er ist erpressbar, freikaufen umsonst
    rede(sp, so, ['Lean on one of the gate guards', None])
    pruefe(w.welt('RL_W_VC_WACHE') == k['RL_WACHE_SORENSEN'] and w.welt('RL_W_VC_SORENSEN') & k['RL_SORENSEN_ERPRESSBAR'], 'Wache')
    w.setze_welt('RL_W_VC_GEFASST', 2)
    geld = sp.dude.kronkorken
    rede(sp, so, ['Corrections Center. ($0)', None])
    pruefe(sp.dude.kronkorken == geld and w.welt('RL_W_VC_GEFASST') == 0, 'umsonst')
    # Sorensen tot: Hanne weiss es
    sp, w = kloake(u)
    sp.zerstoere(figur(sp, k, 'RLSORENSEN'))
    v = rede(sp, figur(sp, k, 'RLHANNE'), ['Where would I get papers'])
    pruefe('Sorensen is dead' in texte(v), 'Sorensen tot')
    sp.betrete_karte(u.cfg['RL_MAP_INDEX'] + VC)
    keine_figur(sp, k, 'RLSORENSEN')
    allgemein(sp, 'pacht')


def test_erkundung_vaultcity(u):
    k = u.k
    gesamt = 0
    for skill in (0, 60):
        sp, w = kloake(u)
        for s in ('SKILL_SPEECH', 'SKILL_SCIENCE', 'SKILL_BARTER'):
            sp.dude.skills[k[s]] = skill
        if skill:
            sp.gvars[k['GVAR_VAULT_CITIZEN']] = k['CITIZEN_REAL_CITIZEN']
        gesamt += erkunde(sp, figur(sp, k, 'RLHANNE'), f'Hanne vorher {skill}')[1]
        gesamt += erkunde(sp, figur(sp, k, 'RLSORENSEN'), f'Sorensen vorher {skill}')[1]
    sp, w = _vc_uebernommen(u)
    hanne = figur(sp, k, 'RLHANNE')
    so = figur(sp, k, 'RLSORENSEN')
    gesamt += erkunde(sp, hanne, 'Hanne Madame')[1]
    w.setze_welt('RL_W_VC_RAZZIA_WOCHE', 99)
    w.setze_welt('RL_W_VC_GEFASST', 2)
    w.setze_haus(VC, 'RL_F_MODULE', k['RL_MOD_AKTE'])
    w.setze_haus(VC, 'RL_F_ZWANG', 1)
    w.setze_haus(VC, 'RL_F_PERSONAL', 1)
    for skill in (0, 70):
        sp.dude.skills[k['SKILL_SNEAK']] = skill
        sp.dude.skills[k['SKILL_LOCKPICK']] = skill
        sp.dude.stats[k['STAT_ch']] = 6 if skill else 4
        gesamt += erkunde(sp, hanne, f'Hanne Krise {skill}')[1]
        gesamt += erkunde(sp, so, f'Sorensen danach {skill}')[1]
    print(f'      {gesamt} Dialogzustaende in Vault City erkundet')


# --------------------------------------------------------------------------
# Umsetzung 10: NCR, Etablissement Nr. 9, Vortis, Die Reinen

NCR = 4


def traenke(u, sp=None):
    """Die Traenke betreten (Kartenskript RLNCR01); liefert (sp, w)."""
    k = u.k
    sp = sp or u.neues_spiel()
    if not sp.finde(k['SCRIPT_RLNCR01']):
        sp.erzeuge(0, -1, 0, k['SCRIPT_RLNCR01'], 'Kartenskript RLNCR01')
    betrete_traenke(u, sp)
    return sp, Welt(sp, k)


def betrete_traenke(u, sp):
    sp.betrete_karte(u.cfg['RL_MAP_INDEX'] + NCR)
    sp.temp_freigeben()


def _ncr_offen(u, sp=None):
    """Mit Westins Fuersprache sofort eroeffnet."""
    k = u.k
    sp, w = traenke(u, sp)
    sp.dude.skills[k['SKILL_SPEECH']] = 60
    rede(sp, figur(sp, k, 'RLGRIEVE'), ['Westin will vouch', None])
    pruefe(w.haus(NCR, 'RL_F_BESITZ') == 1, 'Traenke nicht eroeffnet')
    sp.dude.skills[k['SKILL_SPEECH']] = 20
    return sp, w


def ruhige_woche(sp, n=1):
    """Wochen ohne Zufallsereignisse (jeder Wurf am oberen Rand)."""
    sp.zufall_fest = 'max'
    woche(sp, n)
    sp.zufall_fest = None


def test_ncr_lizenz_wege(u):
    k = u.k
    # Dienstweg: 3 Wochen, auch ohne ein anderes Haus
    sp, w = traenke(u)
    geld = sp.dude.kronkorken
    v = rede(sp, figur(sp, k, 'RLGRIEVE'), ['license for Number Nine'])
    pruefe('$500' in texte(v), 'Gebuehr 500')
    rede(sp, figur(sp, k, 'RLGRIEVE'), ['license for Number Nine', 'File the application', None])
    pruefe(sp.dude.kronkorken == geld - 500 and w.welt('RL_W_NCR_LIZENZ') == k['RL_LIZENZ_NCR_DIENSTWEG'], 'beantragt')
    v = rede(sp, figur(sp, k, 'RLGRIEVE'), [])
    pruefe('3 week(s)' in texte(v), f'Wartezeit: {texte(v)}')
    ruhige_woche(sp, 2)
    pruefe(w.haus(NCR, 'RL_F_BESITZ') == 0, 'zu frueh')
    ruhige_woche(sp)
    pruefe(w.haus(NCR, 'RL_F_BESITZ') == 1 and any('Licensed Establishment' in m for m in sp.meldungen), 'Lizenz da')
    betrete_traenke(u, sp)
    keine_figur(sp, k, 'RLGRIEVE')
    dora = figur(sp, k, 'RLDORA')
    v = rede(sp, dora, ['how the house'])
    pruefe('Dora Quist' in texte(v) and 'Last week we had' in texte(v), 'Dora')
    # Bishop-Pate: halber Preis; beschleunigt
    sp, w = traenke(u)
    w.setze_welt('RL_W_NR_SEGEN', k['RL_SEGEN_BISHOP'])
    sp.dude.skills[k['SKILL_BARTER']] = 40
    geld = sp.dude.kronkorken
    rede(sp, figur(sp, k, 'RLGRIEVE'), ['license for Number Nine', '[Barter]', None])
    pruefe(sp.dude.kronkorken == geld - 550 and w.welt('RL_W_NCR_LIZENZ') == k['RL_LIZENZ_NCR_SCHNELL'], 'beschleunigt')
    pruefe(w.haus(NCR, 'RL_F_HITZE') == 5, 'H +5')
    ruhige_woche(sp)
    pruefe(w.haus(NCR, 'RL_F_BESITZ') == 1, 'nach einer Woche')
    # Westin: sofort, 5 % Anteil
    sp, w = _ncr_offen(u)
    pruefe(w.haus(NCR, 'RL_F_TRIBUTMOD') == 5 and w.welt('RL_W_NCR_LIZENZ') == k['RL_LIZENZ_NCR_WESTIN'], 'Westin')
    keine_figur(sp, k, 'RLGRIEVE')
    figur(sp, k, 'RLDORA')
    # Westin tot: keine Fuersprache
    sp, w = traenke(u)
    sp.gvars[k['GVAR_NEWRENO_SNUFF_WESTIN']] = k['bit_2']
    sp.dude.skills[k['SKILL_SPEECH']] = 60
    v = rede(sp, figur(sp, k, 'RLGRIEVE'), [])
    pruefe(not any('Westin' in o for o in v[0][1]), 'Westin tot')
    # Ohne Lizenz: illegal, die Reinen sofort
    sp, w = traenke(u)
    rede(sp, figur(sp, k, 'RLGRIEVE'), ['without your paper', 'Let them come', None])
    pruefe(w.haus(NCR, 'RL_F_BESITZ') == 1 and w.haus(NCR, 'RL_F_RISIKO_MOD') == 3 and w.haus(NCR, 'RL_F_HITZE') == 30, 'illegal')
    pruefe(w.welt('RL_W_REINE') == k['RL_REINE_FLUGBLAETTER'], 'Reine sofort')
    ruhige_woche(sp)
    pruefe(w.haus(NCR, 'RL_F_RISIKO_MOD') == 3, 'bleibt illegal')
    allgemein(sp, 'ncr lizenz')


def test_ncr_auflage(u):
    k = u.k
    sp, w = _ncr_offen(u)
    ruhige_woche(sp, 3)
    pruefe(w.haus(NCR, 'RL_F_RISIKO_MOD') == 0, 'noch legal')
    ruhige_woche(sp)
    pruefe(w.haus(NCR, 'RL_F_RISIKO_MOD') == 3 and any('license is suspended' in m for m in sp.meldungen), 'Auflage')
    w.setze_haus(NCR, 'RL_F_MODULE', k['RL_MOD_KRANKENSTUBE'])
    ruhige_woche(sp)
    pruefe(w.haus(NCR, 'RL_F_RISIKO_MOD') == 0 and any('licensed again' in m for m in sp.meldungen), 'wieder legal')
    allgemein(sp, 'auflage')


def test_ncr_vortis(u):
    k = u.k
    sp, w = _ncr_offen(u)
    dora = figur(sp, k, 'RLDORA')
    rede(sp, dora, ['how the house', None])
    w.setze_haus(NCR, 'RL_F_ZIMMER', 4)
    geld = sp.dude.kronkorken
    rede(sp, dora, ['Vortis sent a man', None])
    pruefe(w.haus(NCR, 'RL_F_ZWANG') == 1 and sp.dude.kronkorken == geld - 200, 'Vortis-Personal')
    sp.zufall_fest = 'min'
    sp.globale[0].rufe_mit('rl_ncr_woche', 999)
    sp.zufall_fest = None
    pruefe(w.haus(NCR, 'RL_F_ZWANG') == 0 and w.welt('RL_W_NCR_ENTZOGEN') == 1
           and w.welt('RL_W_RANGERS') == k['RL_RANGERS_FEIND'], 'Rangers-Razzia')
    pruefe(any('Rangers raided' in m for m in sp.meldungen), 'Meldung Rangers')
    ruhige_woche(sp)
    pruefe(w.haus(NCR, 'RL_F_RISIKO_MOD') == 3, 'Lizenz entzogen')
    # Vortis ist Feind (die Gilde faellt): kein Angebot
    w.setze_welt('RL_W_VORTIS', k['RL_VORTIS_FEIND'])
    v = rede(sp, dora, [])
    pruefe(not any('Vortis' in o for o in v[0][1]), 'Vortis als Feind bietet nichts an')
    allgemein(sp, 'vortis')


def _reine_akt(sp, w, k, akt, wochen=6):
    for _ in range(wochen):
        if w.welt('RL_W_REINE') == k[akt]:
            return
        ruhige_woche(sp)
    pruefe(w.welt('RL_W_REINE') == k[akt], f'{akt} nicht erreicht ({w.welt("RL_W_REINE")})')


def test_reine_musterhaus(u):
    k = u.k
    sp, w = _ncr_offen(u)
    w.setze_welt('RL_W_MARA_WEG', k['RL_MARA_SICHER'])
    _reine_akt(sp, w, k, 'RL_REINE_FLUGBLAETTER')
    pruefe(w.welt('RL_W_LIGA') == k['RL_LIGA_KAMPAGNE'] and any('CLOSE THE PENS' in m for m in sp.meldungen), 'Akt 1')
    betrete_traenke(u, sp)
    cal = figur(sp, k, 'RLCALLOWAY')
    v = rede(sp, cal, [])
    pruefe(not any('[Speech]' in o for o in v[0][1]), 'Speech ohne Skill')
    sp.dude.skills[k['SKILL_SPEECH']] = 60
    v = rede(sp, cal, ['[Speech]', None])
    pruefe('Mara' in texte(v) and w.welt('RL_W_REINE_AKT1') == k['RL_AKT1_MARA']
           and w.welt('RL_W_LIGA') == k['RL_LIGA_GEBREMST'], 'Mara buergt')
    _reine_akt(sp, w, k, 'RL_REINE_ANHOERUNG')
    dora = figur(sp, k, 'RLDORA')
    rede(sp, dora, ['how the house', None])
    sp.dude.skills[k['SKILL_SPEECH']] = 80
    rede(sp, dora, ['League', 'speak before the Council', None])
    pruefe(w.welt('RL_W_REINE_ANHOERUNG') == k['RL_ANHOERUNG_GEWONNEN'], 'Anhoerung')
    _reine_akt(sp, w, k, 'RL_REINE_FEUER')
    pruefe(w.welt('RL_W_REINE_BRAND') == k['RL_BRAND_BRENNT'], 'Feuer')
    sp.dude.skills[k['SKILL_REPAIR']] = 60
    sp.dude.skills[k['SKILL_SCIENCE']] = 60
    rede(sp, dora, ['League', '[Repair]', 'Go on', '[Science]', 'What do we do', 'Give it to the Rangers', None])
    pruefe(w.welt('RL_W_REINE_BRAND') == k['RL_BRAND_GELOESCHT'] and w.welt('RL_W_VORTIS') == k['RL_VORTIS_VERHAFTET'], 'Rangers')
    w.setze_haus(NCR, 'RL_F_MORAL', 60)
    pruefe(w.welt('RL_W_REINE') in (k['RL_REINE_MUSTERHAUS'], k['RL_REINE_GESCHEITERT']), 'Ende')
    # Musterhaus nur mit Moral >= 60: noch einmal mit hoher Moral
    sp2, w2 = _ncr_offen(u)
    w2.setze_welt('RL_W_REINE', k['RL_REINE_BEWEISE'])
    w2.setze_welt('RL_W_REINE_BEWEIS', k['RL_BEWEIS_VORTIS'])
    w2.setze_haus(NCR, 'RL_F_MORAL', 60)
    d2 = figur(sp2, k, 'RLDORA')
    rede(sp2, d2, ['how the house', None])
    v = rede(sp2, d2, ['League', 'Give it to the Rangers', None])
    pruefe(w2.welt('RL_W_REINE') == k['RL_REINE_MUSTERHAUS'] and w2.welt('RL_W_LIGA') == k['RL_LIGA_LEX_NEUN'], 'Musterhaus')
    pruefe('Lex Nine' in texte(v), 'Text Lex Neun')
    # Lex Neun: +20 % nur mit fairem Anteil, Krankenstube, ohne Zwang
    ruhige_woche(sp2)
    pruefe(w2.haus(NCR, 'RL_F_STADTMOD') == -15, f'Lex Neun verletzt: {w2.haus(NCR, "RL_F_STADTMOD")}')
    w2.setze_haus(NCR, 'RL_F_ANTEIL', k['RL_ANTEIL_FAIR'])
    w2.setze_haus(NCR, 'RL_F_MODULE', k['RL_MOD_KRANKENSTUBE'])
    ruhige_woche(sp2)
    pruefe(w2.haus(NCR, 'RL_F_STADTMOD') == 20, f'Lex Neun: {w2.haus(NCR, "RL_F_STADTMOD")}')
    betrete_traenke(u, sp2)
    keine_figur(sp2, k, 'RLCALLOWAY')
    allgemein(sp, 'musterhaus')
    allgemein(sp2, 'musterhaus 2')


def test_reine_verbot(u):
    k = u.k
    sp, w = traenke(u)
    rede(sp, figur(sp, k, 'RLGRIEVE'), ['without your paper', 'Let them come', None])
    _reine_akt(sp, w, k, 'RL_REINE_FLUGBLAETTER')
    _reine_akt(sp, w, k, 'RL_REINE_ANHOERUNG')
    _reine_akt(sp, w, k, 'RL_REINE_FEUER')
    pruefe(w.welt('RL_W_REINE_ANHOERUNG') == k['RL_ANHOERUNG_VERLOREN'] and any('without us' in m for m in sp.meldungen), 'verloren')
    ruhige_woche(sp)
    pruefe(w.welt('RL_W_REINE_BRAND') == k['RL_BRAND_ABGEBRANNT'], 'abgebrannt')
    ruhige_woche(sp)
    pruefe(w.haus(NCR, 'RL_F_STADTMOD') <= -40, f'Brand-Abzug {w.haus(NCR, "RL_F_STADTMOD")}')
    _reine_akt(sp, w, k, 'RL_REINE_VERBOT', 8)
    pruefe(w.welt('RL_W_LIGA') == k['RL_LIGA_VERBOT'] and any('without exceptions' in m for m in sp.meldungen), 'Verbot')
    allgemein(sp, 'verbot')


def test_reine_diskreditierung(u):
    k = u.k
    sp, w = _ncr_offen(u)
    w.setze_haus(NCR, 'RL_F_ZIMMER', 4)
    _reine_akt(sp, w, k, 'RL_REINE_FLUGBLAETTER')
    dora = figur(sp, k, 'RLDORA')
    rede(sp, dora, ['how the house', None])
    sp.dude.skills[k['SKILL_UNARMED_COMBAT']] = 60
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    rede(sp, dora, ['League', '[Unarmed]', None])
    pruefe(w.welt('RL_W_REINE_AKT1') == k['RL_AKT1_STREIKPOSTEN'] and w.welt('RL_W_LIGA') == 0
           and sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 5, 'Streikposten')
    _reine_akt(sp, w, k, 'RL_REINE_ANHOERUNG')
    # Maertyrer: -10 auf die Rede; Stimmen kaufen mit Skandal
    sp.dude.skills[k['SKILL_SPEECH']] = 80
    v = rede(sp, dora, ['League'])
    pruefe(not any('speak before the Council' in o for o in _optionen_bei(v, 'League')), 'Maertyrer')
    sp.dude.skills[k['SKILL_BARTER']] = 70               # Maertyrer: -10
    h0 = w.haus(NCR, 'RL_F_HITZE')
    sp.zufall_folge = [1]
    rede(sp, dora, ['League', 'Buy enough votes', None])
    pruefe(w.welt('RL_W_REINE_ANHOERUNG') == k['RL_ANHOERUNG_GEWONNEN'] and w.haus(NCR, 'RL_F_HITZE') >= h0 + 25, 'Skandal')
    _reine_akt(sp, w, k, 'RL_REINE_FEUER')
    sp.dude.stats[k['STAT_ch']] = 6
    rede(sp, dora, ['League', 'ask around the Bazaar', 'What do we do', 'Keep it', None])
    pruefe(w.welt('RL_W_REINE') == k['RL_REINE_DISKREDITIERUNG'] and w.welt('RL_W_LIGA') == k['RL_LIGA_ZERSCHLAGEN'], 'Diskreditierung')
    kasse = w.haus(NCR, 'RL_F_KASSE')
    ruhige_woche(sp)
    pruefe(w.haus(NCR, 'RL_F_KASSE') == kasse + 150 + w.haus(NCR, 'RL_F_GEWINN'), 'Vortis zahlt')
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    rede(sp, dora, ['never speaks again', None])
    pruefe(w.welt('RL_W_NCR_TOTE') & k['RL_NCR_TOT_CALLOWAY'] and w.welt('RL_W_RANGERS') == k['RL_RANGERS_FEIND']
           and sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 30, 'Calloway tot')
    # Tyrannen-Zweig: ein radikaler Fluegel der Liga
    sp, w = _ncr_offen(u)
    w.setze_welt('RL_W_KETTEN_ZWEIG', k['RL_KETTEN_ZWEIG_TYRANN'])
    w.setze_welt('RL_W_LIEFERUNGEN', 1)
    w.setze_welt('RL_W_REINE', k['RL_REINE_FEUER'])
    w.setze_welt('RL_W_REINE_WOCHE', 999)
    dora = figur(sp, k, 'RLDORA')
    rede(sp, dora, ['how the house', None])
    sp.dude.skills[k['SKILL_SCIENCE']] = 60
    v = rede(sp, dora, ['League', '[Science]', 'What do we do'])
    pruefe(w.welt('RL_W_REINE_BEWEIS') == k['RL_BEWEIS_FLUEGEL'] and 'no clean side' in texte(v), 'Fluegel')
    pruefe(not any('Vortis will pay' in o for o in _optionen_bei(v, 'What do we do')), 'kein Vortis-Schweigegeld')
    allgemein(sp, 'diskreditierung')


def test_reine_calloway_mara_gedraengt(u):
    k = u.k
    sp, w = _ncr_offen(u)
    w.setze_welt('RL_W_MARA_WEG', k['RL_MARA_CALLOWAY'])
    _reine_akt(sp, w, k, 'RL_REINE_FLUGBLAETTER')
    betrete_traenke(u, sp)
    sp.dude.skills[k['SKILL_SPEECH']] = 60
    v = rede(sp, figur(sp, k, 'RLCALLOWAY'), ['[Speech]', None])
    pruefe('asked' in texte(v) and w.welt('RL_W_LIGA') == k['RL_LIGA_KAMPAGNE'], 'Mara bei Calloway')
    # Registratur halbiert die Kampagne
    w.setze_haus(NCR, 'RL_F_MODULE', k['RL_MOD_REGISTRATUR'])
    ruhige_woche(sp)
    pruefe(w.haus(NCR, 'RL_F_STADTMOD') == -7, f'Registratur: {w.haus(NCR, "RL_F_STADTMOD")}')
    allgemein(sp, 'calloway')


def test_erkundung_ncr(u):
    k = u.k
    gesamt = 0
    for skill in (0, 60):
        sp, w = traenke(u)
        for s in ('SKILL_SPEECH', 'SKILL_BARTER'):
            sp.dude.skills[k[s]] = skill
        gesamt += erkunde(sp, figur(sp, k, 'RLGRIEVE'), f'Grieve {skill}')[1]
    sp, w = _ncr_offen(u)
    dora = figur(sp, k, 'RLDORA')
    gesamt += erkunde(sp, dora, 'Dora erstes Gespraech')[1]
    rede(sp, dora, ['how the house', None])
    w.setze_haus(NCR, 'RL_F_ZIMMER', 5)
    w.setze_haus(NCR, 'RL_F_MODULE', k['RL_MOD_VIP'] | k['RL_MOD_REGISTRATUR'] | k['RL_MOD_KRANKENSTUBE'])
    for akt in ('RL_REINE_FLUGBLAETTER', 'RL_REINE_ANHOERUNG', 'RL_REINE_FEUER', 'RL_REINE_BEWEISE', 'RL_REINE_DISKREDITIERUNG'):
        w.setze_welt('RL_W_REINE', k[akt])
        w.setze_welt('RL_W_REINE_BRAND', k['RL_BRAND_BRENNT'])
        w.setze_welt('RL_W_REINE_BEWEIS', k['RL_BEWEIS_VORTIS'])
        for skill in (0, 80):
            for s in ('SKILL_SPEECH', 'SKILL_BARTER', 'SKILL_UNARMED_COMBAT', 'SKILL_REPAIR', 'SKILL_TRAPS',
                      'SKILL_SCIENCE', 'SKILL_SNEAK', 'SKILL_LOCKPICK'):
                sp.dude.skills[k[s]] = skill
            gesamt += erkunde(sp, dora, f'Dora {akt} {skill}')[1]
    for akt in ('RL_REINE_FLUGBLAETTER', 'RL_REINE_ANHOERUNG'):
        w.setze_welt('RL_W_REINE', k[akt])
        betrete_traenke(u, sp)
        for mara in ('RL_MARA_KEINE', 'RL_MARA_SICHER', 'RL_MARA_CALLOWAY'):
            w.setze_welt('RL_W_MARA_WEG', k[mara])
            w.setze_welt('RL_W_NCR_KENNT', 1)
            sp.dude.skills[k['SKILL_SPEECH']] = 60
            gesamt += erkunde(sp, figur(sp, k, 'RLCALLOWAY'), f'Calloway {akt} {mara}')[1]
    print(f'      {gesamt} Dialogzustaende in der NCR erkundet')


# --------------------------------------------------------------------------
# Umsetzung 11: San Francisco, Die Duldung, Schmuggelkammer, Hubologen

SF = 5


def bilge(u, sp=None):
    """Die Bilge betreten (Kartenskript RLSFR01); liefert (sp, w)."""
    k = u.k
    sp = sp or u.neues_spiel()
    if not sp.finde(k['SCRIPT_RLSFR01']):
        sp.erzeuge(0, -1, 0, k['SCRIPT_RLSFR01'], 'Kartenskript RLSFR01')
    sp.betrete_karte(u.cfg['RL_MAP_INDEX'] + SF)
    sp.temp_freigeben()
    return sp, Welt(sp, k)


def _sf_offen(u, weg='Fifteen percent. Agreed', sp=None):
    k = u.k
    sp, w = bilge(u, sp)
    rede(sp, figur(sp, k, 'RLWEN'), [weg, None])
    pruefe(w.haus(SF, 'RL_F_BESITZ') == 1, 'Bilge nicht uebernommen')
    return sp, w


def test_sf_duldung(u):
    k = u.k
    sp, w = bilge(u)
    figur(sp, k, 'RLWEN')
    figur(sp, k, 'RLBOOTSMANN')
    keine_figur(sp, k, 'RLKWAN')
    rede(sp, figur(sp, k, 'RLWEN'), ['Fifteen percent. Agreed', None])
    pruefe(w.welt('RL_W_SF_DULDUNG') == k['RL_DULDUNG_TRIBUT'] and w.haus(SF, 'RL_F_TRIBUTMOD') == 5, '15 %')
    pruefe(w.haus(SF, 'RL_F_EINFLUSS') == 20 and w.haus(SF, 'RL_F_FUEHRUNG') == 50, 'Einfluss, Fuehrung')
    kwan = figur(sp, k, 'RLKWAN')
    v = rede(sp, kwan, ['how the house'])
    pruefe('tea' in texte(v) and 'Last week we had' in texte(v), 'Kwan')
    # Augen der Shi: 10 %, Siegel sofort, bis die Tanker-Leute es merken
    sp, w = _sf_offen(u, "Shi's eyes")
    pruefe(w.haus(SF, 'RL_F_TRIBUTMOD') == 0 and w.welt('RL_W_SHI_GEFALLEN') == 1, 'Spitzel')
    sp.zufall_folge = [1]
    sp.globale[0].rufe_mit('rl_sf_woche', 999)
    pruefe(w.welt('RL_W_SF_SPITZEL_AUF') == 1 and any('tanker crew found out' in m for m in sp.meldungen), 'aufgeflogen')
    ruhige_woche(sp)
    pruefe(w.haus(SF, 'RL_F_STADTMOD') == -20, f'Tanker weg: {w.haus(SF, "RL_F_STADTMOD")}')
    v = rede(sp, figur(sp, k, 'RLBOOTSMANN'), [])
    pruefe('Shi rat' in texte(v), 'Bootsmann feindlich')
    # Barter: 10 %, das Siegel erst nach einem Gefallen
    sp, w = bilge(u)
    sp.dude.skills[k['SKILL_BARTER']] = 60
    rede(sp, figur(sp, k, 'RLWEN'), ['[Barter]', None])
    pruefe(w.welt('RL_W_SF_DULDUNG') == k['RL_DULDUNG_BARTER'] and w.welt('RL_W_SHI_GEFALLEN') == 0, 'Barter')
    sp.dude.skills[k['SKILL_SNEAK']] = 60
    rede(sp, figur(sp, k, 'RLWEN'), ['something the Shi need', '[Sneak]', None])
    pruefe(w.welt('RL_W_SHI_GEFALLEN') == 1, 'Gefallen')
    kwan = figur(sp, k, 'RLKWAN')
    rede(sp, kwan, ['how the house', None])
    sp.dude.kronkorken = 5000
    v = rede(sp, kwan, ['build', 'only get in San Francisco'])
    pruefe(any('Seal of the Shi' in o for o in _optionen_bei(v, 'only get in San Francisco')), 'Siegel verfuegbar')
    pruefe(not any("Smugglers' Room" in o for o in _optionen_bei(v, 'only get in San Francisco')), 'Kammer ohne Lager')
    # Tanker: kein Tribut, H +15, die Kammer sofort; spaeter doch zu Wen
    sp, w = bilge(u)
    sp.dude.skills[k['SKILL_SPEECH']] = 60
    rede(sp, figur(sp, k, 'RLBOOTSMANN'), ['[Speech]', None])
    pruefe(w.welt('RL_W_SF_DULDUNG') == k['RL_DULDUNG_TANKER'] and w.haus(SF, 'RL_F_TRIBUTMOD') == -10
           and w.haus(SF, 'RL_F_HITZE') == 15 and w.welt('RL_W_SF_LAGER') == 1, 'Tanker')
    figur(sp, k, 'RLKWAN')
    rede(sp, figur(sp, k, 'RLWEN'), ['start over', None])
    pruefe(w.welt('RL_W_SF_DULDUNG') == k['RL_DULDUNG_TRIBUT'] and w.haus(SF, 'RL_F_TRIBUTMOD') == 5, 'zurueck zu Wen')
    allgemein(sp, 'duldung')


def test_sf_schmuggelkammer(u):
    k = u.k
    sp, w = _sf_offen(u)
    rede(sp, figur(sp, k, 'RLBOOTSMANN'), ['store things', None])
    pruefe(w.welt('RL_W_SF_LAGER') == 1, 'Lager')
    kwan = figur(sp, k, 'RLKWAN')
    rede(sp, kwan, ['how the house', None])
    sp.dude.kronkorken = 5000
    rede(sp, kwan, ['build', 'only get in San Francisco', "Smugglers' Room", 'Build it', None])
    ruhige_woche(sp)
    pruefe(w.haus(SF, 'RL_F_MODULE') & k['RL_MOD_SCHMUGGEL'] and w.haus(SF, 'RL_F_NEBEN') == 3, 'Kammer fertig')
    # Das Siegel dazu, dann finden die Inspektoren die Kammer
    w.setze_haus(SF, 'RL_F_GEKAUFT', 1 << k['RL_M_SF_SHI_SIEGEL'])
    w.setze_haus(SF, 'RL_F_TRIBUTMOD', 5 - 5)
    w.setze_haus(SF, 'RL_F_SICHERHEIT', 55)
    stufen = w.haus(SF, 'RL_F_STUFEN')
    sp.globale[0].rufe_mit('rl_sf_razzia', sp.gespeichert['RL_HAUS'], sp.gespeichert['RL_WELT'])
    pruefe(not (w.haus(SF, 'RL_F_MODULE') & k['RL_MOD_SCHMUGGEL']) and w.haus(SF, 'RL_F_NEBEN') == 0, 'beschlagnahmt')
    pruefe(w.haus(SF, 'RL_F_TRIBUTMOD') == 10 and w.haus(SF, 'RL_F_SICHERHEIT') == 45
           and not (w.haus(SF, 'RL_F_GEKAUFT') & (1 << k['RL_M_SF_SHI_SIEGEL'])), 'Siegel entzogen, Tribut +5')
    pruefe(w.haus(SF, 'RL_F_STUFEN') == stufen - 2 and w.welt('RL_W_SHI_GEFALLEN') == 0, 'Stufen, Gefallen')
    allgemein(sp, 'schmuggel')


def test_sf_hubologen(u):
    k = u.k
    for weg, skill, wert in (('[Science]', 'SKILL_SCIENCE', 'RL_HUBOLOGEN_ENTLARVT'),
                             ('[Speech]', 'SKILL_SPEECH', 'RL_HUBOLOGEN_UNTERWANDERT'),
                             ('[Barter]', 'SKILL_BARTER', 'RL_HUBOLOGEN_ABSPRACHE')):
        sp, w = _sf_offen(u)
        kwan = figur(sp, k, 'RLKWAN')
        rede(sp, kwan, ['how the house', None])
        sp.dude.skills[k[skill]] = 70
        karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
        rede(sp, kwan, ['Hubologists', weg, None])
        pruefe(w.welt('RL_W_HUBOLOGEN') == k[wert], weg)
        ruhige_woche(sp)
        soll = {'RL_HUBOLOGEN_ENTLARVT': 0, 'RL_HUBOLOGEN_UNTERWANDERT': 10, 'RL_HUBOLOGEN_ABSPRACHE': 0}[wert]
        pruefe(w.haus(SF, 'RL_F_STADTMOD') == soll, f'{weg}: Stadtmod {w.haus(SF, "RL_F_STADTMOD")}')
        if wert == 'RL_HUBOLOGEN_ABSPRACHE':
            pruefe(sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 20, 'K -20')
            w.setze_haus(SF, 'RL_F_ZIMMER', 5)
            rede(sp, kwan, ["debtor's note", None])
            pruefe(w.haus(SF, 'RL_F_ZWANG') == 1, 'Schuldner')
    # Vanilla: Die Hubologen fliegen davon
    sp, w = _sf_offen(u)
    sp.gvars[k['GVAR_SAN_FRAN_FLAGS']] = k['bit_16']
    ruhige_woche(sp)
    pruefe(w.welt('RL_W_HUBOLOGEN') == k['RL_HUBOLOGEN_ENTLARVT'] and w.haus(SF, 'RL_F_STADTMOD') == 0, 'Vanilla')
    allgemein(sp, 'hubologen')


def test_erkundung_sanfran(u):
    k = u.k
    gesamt = 0
    for skill in (0, 70):
        sp, w = bilge(u)
        for s in ('SKILL_BARTER', 'SKILL_SPEECH'):
            sp.dude.skills[k[s]] = skill
        gesamt += erkunde(sp, figur(sp, k, 'RLWEN'), f'Wen {skill}')[1]
        gesamt += erkunde(sp, figur(sp, k, 'RLBOOTSMANN'), f'Bootsmann {skill}')[1]
    sp, w = _sf_offen(u, '[Barter]' if False else 'Fifteen percent. Agreed')
    for skill in (0, 70):
        for s in ('SKILL_BARTER', 'SKILL_SPEECH', 'SKILL_SCIENCE', 'SKILL_SNEAK'):
            sp.dude.skills[k[s]] = skill
        sp.dude.stats[k['STAT_pe']] = 7 if skill else 5
        gesamt += erkunde(sp, figur(sp, k, 'RLWEN'), f'Wen danach {skill}')[1]
        gesamt += erkunde(sp, figur(sp, k, 'RLBOOTSMANN'), f'Bootsmann danach {skill}')[1]
        gesamt += erkunde(sp, figur(sp, k, 'RLKWAN'), f'Kwan {skill}')[1]
    w.setze_welt('RL_W_SF_KENNT', 1)
    w.setze_welt('RL_W_HUBOLOGEN', k['RL_HUBOLOGEN_ABSPRACHE'])
    w.setze_haus(SF, 'RL_F_ZIMMER', 5)
    gesamt += erkunde(sp, figur(sp, k, 'RLKWAN'), 'Kwan Absprache')[1]
    w.setze_welt('RL_W_SF_DULDUNG', k['RL_DULDUNG_TANKER'])
    gesamt += erkunde(sp, figur(sp, k, 'RLWEN'), 'Wen nach dem Tanker')[1]
    print(f'      {gesamt} Dialogzustaende in San Francisco erkundet')


# --------------------------------------------------------------------------
# Umsetzung 12: Blut auf der Virgin Street, Miss Kitty

def _virgin_akt(u, sp, w, akt, wochen=8):
    k = u.k
    for _ in range(wochen):
        if w.welt('RL_W_VIRGIN') == k[akt]:
            break
        ruhige_woche(sp)
    pruefe(w.welt('RL_W_VIRGIN') == k[akt], f'{akt} nicht erreicht ({w.welt("RL_W_VIRGIN")})')
    betrete_strumpfband(u, sp)


def test_virgin_gebuehr_und_kitty(u):
    k = u.k
    sp, w = _nr_uebernommen(u, 'Salvatore')
    _virgin_akt(u, sp, w, 'RL_VIRGIN_GEBUEHR')
    pruefe(any('Carlo Venuti' in m for m in sp.meldungen), 'Meldung Akt 1')
    ven = figur(sp, k, 'RLVENUTI')
    sp.dude.skills[k['SKILL_BARTER']] = 60
    rede(sp, ven, ['[Barter]', None])
    pruefe(w.welt('RL_W_VIRGIN_GEBUEHR') == 100 and w.haus(NR, 'RL_F_BESTECHUNG_MOD') == 100, 'halbiert')
    keine_figur(sp, k, 'RLVENUTI')
    kasse = w.haus(NR, 'RL_F_KASSE')
    _virgin_akt(u, sp, w, 'RL_VIRGIN_KITTY')
    jade = figur(sp, k, 'RLJADE')
    sp.dude.skills[k['SKILL_SPEECH']] = 60
    rede(sp, jade, ['refuse Venuti together', None])
    pruefe(w.welt('RL_W_KITTY_WEG') == k['RL_KITTY_BUENDNIS'] and w.welt('RL_W_CATSPAW') == 1
           and w.welt('RL_W_VIRGIN_GEBUEHR') == 0, 'Buendnis')
    keine_figur(sp, k, 'RLJADE')
    ruhige_woche(sp)
    pruefe(w.haus(NR, 'RL_F_STADTMOD') == -5, f'Cat\'s Paw -5: {w.haus(NR, "RL_F_STADTMOD")}')
    # Fusion mit Einfluss
    sp, w = _nr_uebernommen(u, 'Salvatore')
    w.setze_welt('RL_W_VIRGIN', k['RL_VIRGIN_KITTY'])
    w.setze_welt('RL_W_VIRGIN_WOCHE', 99)
    w.setze_haus(NR, 'RL_F_EINFLUSS', 40)
    betrete_strumpfband(u, sp)
    zimmer, personal = w.haus(NR, 'RL_F_ZIMMER'), w.haus(NR, 'RL_F_PERSONAL')
    rede(sp, figur(sp, k, 'RLJADE'), ['take the Cat', None])
    pruefe(w.welt('RL_W_KITTY_WEG') == k['RL_KITTY_FUSION'] and w.haus(NR, 'RL_F_ZIMMER') == zimmer + 3
           and w.haus(NR, 'RL_F_PERSONAL') == personal + 3 and w.haus(NR, 'RL_F_FUEHRUNG') == 85, 'Fusion')
    # Verrat: Rivalin, Kralle in Redding, Abwerbung, Anhoerung -10
    sp, w = _nr_uebernommen(u, 'Salvatore')
    w.setze_welt('RL_W_VIRGIN', k['RL_VIRGIN_KITTY'])
    w.setze_welt('RL_W_VIRGIN_WOCHE', 99)
    w.setze_welt('RL_W_VIRGIN_GEBUEHR', 200)
    betrete_strumpfband(u, sp)
    geld = sp.dude.kronkorken
    rede(sp, figur(sp, k, 'RLJADE'), ['Tell Venuti', None])
    pruefe(w.welt('RL_W_KITTY_RIVALIN') == 1 and w.welt('RL_W_CATSPAW') == k['RL_CATSPAW_MORDINO']
           and sp.dude.kronkorken == geld + 1000 and w.welt('RL_W_VIRGIN_GEBUEHR') == 100, 'Verrat')
    w.setze_haus(NR, 'RL_F_MORAL', 40)
    personal = w.haus(NR, 'RL_F_PERSONAL')
    ruhige_woche(sp, 4)
    pruefe(w.haus(NR, 'RL_F_PERSONAL') < personal and any("Kitty's Claw" in m for m in sp.meldungen), 'Abwerbung')
    # Die Kralle beenden: ueber Nell
    sp, w = _red_uebernommen(u, sp)
    nell = figur(sp, k, 'RLNELL')
    rede(sp, nell, ['how the house', None])
    w.setze_haus(RED, 'RL_F_EINFLUSS', 40)
    rede(sp, nell, ["Kitty's Claw", 'Buy the Claw', None])
    pruefe(w.welt('RL_W_KITTY_RIVALIN') == 0 and w.welt('RL_W_KITTY_WEG') == k['RL_KITTY_KRALLE_GEKAUFT'], 'Kralle gekauft')
    allgemein(sp, 'kitty')


def test_virgin_dealer_und_nacht(u):
    k = u.k
    sp, w = _nr_uebernommen(u, 'Salvatore')
    _virgin_akt(u, sp, w, 'RL_VIRGIN_GEBUEHR')
    rede(sp, figur(sp, k, 'RLVENUTI'), ['No.', None])
    pruefe(w.welt('RL_W_VIRGIN') == k['RL_VIRGIN_JET'] and w.haus(NR, 'RL_F_HITZE') >= 10, 'verweigert: Akt 3 sofort')
    roz = figur(sp, k, 'RLROZ')
    rede(sp, roz, ['how the house', None])
    sp.dude.stats[k['STAT_pe']] = 7
    sp.dude.skills[k['SKILL_SPEECH']] = 70
    sp.dude.skills[k['SKILL_DOCTOR']] = 60
    moral = w.haus(NR, 'RL_F_MORAL')
    rede(sp, roz, ['Jet in the house', '[Perception]', '[Speech] Turn', 'Go on', '[Doctor]', None])
    f = w.welt('RL_W_VIRGIN_FLAGS')
    pruefe(f & k['RL_VF_DEALER_WEG'] and f & k['RL_VF_BEWEISE'] and f & k['RL_VF_GEHEILT'], f'Dealer {f}')
    pruefe(w.haus(NR, 'RL_F_MORAL') == moral + 10, 'geheilt')
    _virgin_akt(u, sp, w, 'RL_VIRGIN_MESSER')
    ven = figur(sp, k, 'RLVENUTI')
    rede(sp, ven, ['Orville Wright', None])
    pruefe(w.welt('RL_W_VIRGIN') == k['RL_VIRGIN_LEERER_STUHL'], 'zuvorgekommen')
    keine_figur(sp, k, 'RLVENUTI')
    # Kampf im Haus
    sp, w = _nr_uebernommen(u, 'Salvatore')
    w.setze_welt('RL_W_VIRGIN', k['RL_VIRGIN_MESSER'])
    w.setze_welt('RL_W_VIRGIN_WOCHE', 99)
    betrete_strumpfband(u, sp)
    rede(sp, figur(sp, k, 'RLVENUTI'), ['Get out of my house', None])
    ang = sp.finde(k['SCRIPT_RLANGREIFER'])
    pruefe(len(ang) == 3 and w.haus(NR, 'RL_F_ANGRIFF') == k['RL_ANGRIFF_VIRGIN'], 'Angriff')
    keine_figur(sp, k, 'RLVENUTI')
    betrete_strumpfband(u, sp)
    keine_figur(sp, k, 'RLVENUTI')
    for o in ang:
        sp.zerstoere(o)
    pruefe(w.welt('RL_W_VIRGIN') == k['RL_VIRGIN_LEERER_STUHL'] and w.haus(NR, 'RL_F_ANGRIFF') == 0, 'verteidigt')
    # Ultimatum liegen gelassen: das Haus wird verwuestet
    sp, w = _nr_uebernommen(u, 'Salvatore')
    w.setze_welt('RL_W_VIRGIN', k['RL_VIRGIN_MESSER'])
    w.setze_welt('RL_W_VIRGIN_WOCHE', 1)
    for _ in range(6):
        ruhige_woche(sp)
        if any('shut for two weeks' in m for m in sp.meldungen):
            break
    pruefe(w.haus(NR, 'RL_F_GESCHLOSSEN') >= 1 and any('shut for two weeks' in m for m in sp.meldungen), 'verwuestet')
    pruefe(w.welt('RL_W_VIRGIN') == k['RL_VIRGIN_MESSER'], 'das Ultimatum bleibt')
    allgemein(sp, 'dealer und nacht')


def test_virgin_umarmung_und_vanilla(u):
    k = u.k
    sp, e, ko, w = prolog(u, 'bezahlt')
    sp, w = _nr_uebernommen(u, 'Mordino', sp)
    w.setze_welt('RL_W_VIRGIN', k['RL_VIRGIN_MESSER'])
    w.setze_welt('RL_W_VIRGIN_WOCHE', 99)
    betrete_strumpfband(u, sp)
    karma = sp.gvars.get(k['GVAR_PLAYER_REPUTATION'], 0)
    rede(sp, figur(sp, k, 'RLVENUTI'), ['make me family', None])
    pruefe(w.welt('RL_W_VIRGIN') == k['RL_VIRGIN_UMARMUNG'] and sp.gvars[k['GVAR_MADE_MAN_MORDINO']] == 1, 'Umarmung')
    pruefe(sp.gvars[k['GVAR_PLAYER_REPUTATION']] == karma - 30, 'K -30')
    for h in (0, NR):
        pruefe(w.haus(h, 'RL_F_MODULE') & k['RL_MOD_JET_THEKE'] and w.haus(h, 'RL_F_PREISMOD') == 20, f'Haus {h}')
    # Die Mordinos fallen in Vanilla, waehrend die Linie laeuft
    sp, w = _nr_uebernommen(u, 'Salvatore')
    _virgin_akt(u, sp, w, 'RL_VIRGIN_GEBUEHR')
    sp.gvars[k['GVAR_NEW_RENO_FLAG_2']] = k['bit_26']
    ruhige_woche(sp)
    pruefe(w.welt('RL_W_VIRGIN') == k['RL_VIRGIN_LEERER_STUHL'], 'Vanilla: leerer Stuhl')
    # Die Mordinos sind schon gefallen: Venuti will Rache, ab Akt 3
    sp, w = _nr_uebernommen(u, 'Salvatore')
    sp.gvars[k['GVAR_NEW_RENO_FLAG_2']] = k['bit_26']
    _virgin_akt(u, sp, w, 'RL_VIRGIN_JET')
    pruefe(w.welt('RL_W_VIRGIN_FLAGS') & k['RL_VF_RACHE'], 'Rache')
    allgemein(sp, 'umarmung')


def test_erkundung_virgin(u):
    k = u.k
    gesamt = 0
    sp, w = _nr_uebernommen(u, 'Mordino')
    for akt in ('RL_VIRGIN_GEBUEHR', 'RL_VIRGIN_KITTY', 'RL_VIRGIN_JET', 'RL_VIRGIN_MESSER'):
        w.setze_welt('RL_W_VIRGIN', k[akt])
        w.setze_welt('RL_W_VIRGIN_WOCHE', 99)
        betrete_strumpfband(u, sp)
        for skill in (0, 90):
            for s in ('SKILL_BARTER', 'SKILL_SPEECH', 'SKILL_UNARMED_COMBAT', 'SKILL_SNEAK', 'SKILL_DOCTOR'):
                sp.dude.skills[k[s]] = skill
            sp.dude.stats[k['STAT_pe']] = 7 if skill else 5
            w.setze_welt('RL_W_VIRGIN_FLAGS', k['RL_VF_BEWEISE'] if skill else 0)
            for name in ('RLVENUTI', 'RLJADE'):
                fs = sp.finde(k['SCRIPT_' + name])
                if fs:
                    gesamt += erkunde(sp, fs[0], f'{name} {akt} {skill}')[1]
            gesamt += erkunde(sp, figur(sp, k, 'RLROZ'), f'Roz {akt} {skill}')[1]
    sp, w = _red_uebernommen(u)
    w.setze_welt('RL_W_KITTY_RIVALIN', 1)
    w.setze_welt('RL_W_RED_KENNT', 1)
    for skill in (0, 80):
        sp.dude.skills[k['SKILL_SPEECH']] = skill
        w.setze_haus(RED, 'RL_F_EINFLUSS', 40 if skill else 20)
        gesamt += erkunde(sp, figur(sp, k, 'RLNELL'), f'Nell Kralle {skill}')[1]
    print(f'      {gesamt} Dialogzustaende der Virgin Street erkundet')


TESTS = [test_wirtschaft_paritaet, test_erkundung, test_eingang, test_prolog_wege, test_diebstahl_erwischt, test_ketten_annehmen,
         test_ketten_ablehnen, test_ketten_kein_geld, test_kolbe_stirbt, test_kolbe_kommt_zurueck,
         test_wochen, test_anwerbung_werben, test_anwerbung_zwingen, test_pferch_flucht_und_nachschub,
         test_akt2_verstecken_bis_madame, test_suche_ohne_zuflucht, test_akt2_retten_stiller_krieg,
         test_akt2_ausliefern_essie_geht, test_tyrann_bis_metzgers_mann, test_neuer_metzger,
         test_kampf_deke_und_jess, test_tyler_tot_vanilla, test_eingaenge_haeuser, test_alter_spielstand, test_erkundung_ketten,
         test_nr_kauf_und_mordino, test_nr_urkunde_wege, test_nr_faelschung, test_nr_bishop_brief,
         test_nr_made_man_und_vanilla, test_nr_eroeffnungsnacht, test_nr_pagano_tot, test_nr_hauptquartier,
         test_nr_jet_theke, test_nr_tote_figuren, test_erkundung_newreno,
         test_red_lizenz_wege, test_red_schreiber_tot, test_red_waage, test_red_malamute,
         test_red_marion_wanamingo, test_red_entzugsstube, test_erkundung_redding,
         test_vc_uebernahme, test_vc_schweigegeld_und_wache, test_vc_razzia, test_vc_razzia_angekuendigt,
         test_vc_akte_und_lynette, test_vc_pacht_und_sorensen, test_erkundung_vaultcity,
         test_ncr_lizenz_wege, test_ncr_auflage, test_ncr_vortis, test_reine_musterhaus, test_reine_verbot,
         test_reine_diskreditierung, test_reine_calloway_mara_gedraengt, test_erkundung_ncr,
         test_sf_duldung, test_sf_schmuggelkammer, test_sf_hubologen, test_erkundung_sanfran,
         test_virgin_gebuehr_und_kitty, test_virgin_dealer_und_nacht, test_virgin_umarmung_und_vanilla,
         test_erkundung_virgin]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--build', default=os.path.join(WURZEL, 'build', 'rpu-v2.4.34'))
    ap.add_argument('--fo2', default=os.environ.get('FO2_SCRIPTS_SRC', ''))
    ap.add_argument('-k', default='')
    ap.add_argument('-v', action='store_true')
    a = ap.parse_args()
    if not a.fo2:
        sys.exit('--fo2 (oder FO2_SCRIPTS_SRC) fehlt: scripts_src der RPU fuer global.h, maps.h ...')
    u = Umgebung(a.build, a.fo2)
    ok = 0
    fehl = 0
    for t in TESTS:
        if a.k and a.k not in t.__name__:
            continue
        try:
            t(u)
            ok += 1
            print(f'ok    {t.__name__}')
        except (AssertionError, SkriptFehler) as e:
            fehl += 1
            print(f'FEHLER {t.__name__}: {e}')
            if a.v:
                traceback.print_exc()
    print(f'{ok} ok, {fehl} Fehler')
    return 1 if fehl else 0


if __name__ == '__main__':
    sys.exit(main())
