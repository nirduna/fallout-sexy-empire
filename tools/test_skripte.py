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
        for f in ('global.h', 'maps.h', 'critrpid.h', 'define.h', 'den.h'):
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
                 gezwungen=rng.choice([0, 0, 1, 2]), anwerber=rng.randrange(3))
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
            forced_labor=c['zwang'])
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


TESTS = [test_wirtschaft_paritaet, test_erkundung, test_eingang, test_prolog_wege, test_diebstahl_erwischt, test_ketten_annehmen,
         test_ketten_ablehnen, test_ketten_kein_geld, test_kolbe_stirbt, test_kolbe_kommt_zurueck,
         test_wochen, test_anwerbung_werben, test_anwerbung_zwingen, test_pferch_flucht_und_nachschub,
         test_akt2_verstecken_bis_madame, test_suche_ohne_zuflucht, test_akt2_retten_stiller_krieg,
         test_akt2_ausliefern_essie_geht, test_tyrann_bis_metzgers_mann, test_neuer_metzger,
         test_kampf_deke_und_jess, test_tyler_tot_vanilla, test_eingaenge_haeuser, test_alter_spielstand, test_erkundung_ketten]


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
