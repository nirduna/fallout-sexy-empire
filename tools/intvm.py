#!/usr/bin/env python3
"""intvm.py - Pruefwerkzeug: fuehrt kompilierte Fallout-2-Skripte (.int) aus.

Im Spiel kann ich nicht testen. Dieses Werkzeug fuehrt die mit sslc
kompilierten Skripte deshalb in Python aus, mit einer kleinen Nachbildung
der Spielwelt (globale Variablen, Objekte, Karten, Zeit, sfall-Arrays,
Meldungen, Dialoge). So lassen sich Wochenrechnung, Anwerbung und ganze
Dialogbaeume automatisch durchspielen (tools/test_skripte.py).

Die Semantik folgt fallout2-ce (interpreter.cc, interpreter_extra.cc,
sfall_opcodes.cc, sfall_arrays.cc, game_dialog.cc):
  - Stapel und Ruecksprungstapel, framePointer/basePointer wie im Original
  - Ganzzahl-Addition mit Ueberlauf wird zur Gleitkommazahl
  - Division und Modulo durch null brechen das Skript ab (wie im Spiel)
  - "and"/"or" werten beide Seiten aus (keine Kurzschlussauswertung)
  - Dialoge: gsay_end startet die Schleife; waehlt der Spieler eine Option,
    wird deren Prozedur ausgefuehrt. Setzt sie keine neuen Optionen, endet
    der Dialog, und eine eben gesetzte Antwort wird nie angezeigt. Das
    meldet das Werkzeug als Fehler.

Nicht nachgebildet: Grafik, Kampf, Wegfindung, Animationen. Befehle, die
nur etwas anzeigen oder bewegen, werden protokolliert.

Aufruf zum Anschauen einer Datei:
    python3 tools/intvm.py dis build/rpu-v2.4.34/scripts/rlgosse.int
"""

import os
import random
import re
import struct
import sys

# --------------------------------------------------------------------------
# .int laden

VT_INT = 0xC001
VT_FLOAT = 0xA001
VT_STR = 0x9001
VT_DSTR = 0x9801

PROC_IMPORTED = 0x04
PROC_CRITICAL = 0x10

NAMEN = {
    0x8000: 'noop', 0x8001: 'push', 0x8002: 'critical_start', 0x8003: 'critical_done',
    0x8004: 'jmp', 0x8005: 'call', 0x800C: 'a_to_d', 0x800D: 'd_to_a',
    0x800E: 'exit', 0x8010: 'exit_prog', 0x8012: 'fetch_global', 0x8013: 'store_global',
    0x8018: 'swap', 0x8019: 'swapa', 0x801A: 'pop', 0x801B: 'dup', 0x801C: 'pop_return',
    0x801D: 'pop_exit', 0x801E: 'pop_address', 0x801F: 'pop_flags',
    0x8020: 'pop_flags_return', 0x8021: 'pop_flags_exit', 0x8027: 'check_arg_count',
    0x8028: 'lookup_string_proc', 0x8029: 'pop_base', 0x802A: 'pop_to_base',
    0x802B: 'push_base', 0x802C: 'set_global', 0x802D: 'fetch_proc_address',
    0x802E: 'dump', 0x802F: 'if', 0x8030: 'while', 0x8031: 'store', 0x8032: 'fetch',
    0x8033: '==', 0x8034: '!=', 0x8035: '<=', 0x8036: '>=', 0x8037: '<', 0x8038: '>',
    0x8039: '+', 0x803A: '-', 0x803B: '*', 0x803C: '/', 0x803D: '%', 0x803E: 'and',
    0x803F: 'or', 0x8040: 'bwand', 0x8041: 'bwor', 0x8042: 'bwxor', 0x8043: 'bwnot',
    0x8044: 'floor', 0x8045: 'not', 0x8046: 'negate',
    0x80A7: 'tile_contains_pid_obj', 0x80AA: 'has_skill', 0x80B4: 'random',
    0x80B6: 'move_to', 0x80B7: 'create_object_sid', 0x80B8: 'display_msg',
    0x80B9: 'script_overrides', 0x80BC: 'self_obj', 0x80BD: 'source_obj',
    0x80BE: 'target_obj', 0x80BF: 'dude_obj', 0x80C1: 'local_var', 0x80C2: 'set_local_var',
    0x80C3: 'map_var', 0x80C4: 'set_map_var', 0x80C5: 'global_var', 0x80C6: 'set_global_var',
    0x80CA: 'get_critter_stat', 0x80D4: 'tile_num', 0x80D5: 'tile_num_in_direction',
    0x80DE: 'start_gdialog', 0x80DF: 'end_dialogue', 0x80E4: 'load_map',
    0x80E9: 'set_light_level', 0x80EA: 'game_time', 0x80EB: 'game_time_in_seconds',
    0x80EC: 'elevation', 0x80EF: 'critter_dmg', 0x80F4: 'destroy_object',
    0x8101: 'cur_map_index', 0x8105: 'message_str', 0x810A: 'float_msg', 0x810B: 'metarule',
    0x811C: 'gsay_start', 0x811D: 'gsay_end', 0x811E: 'gsay_reply', 0x8121: 'giq_option',
    0x8128: 'combat_is_initialized', 0x8136: 'gfade_out', 0x8137: 'gfade_in',
    0x8138: 'item_caps_total', 0x8139: 'item_caps_adjust', 0x8143: 'attack_setup',
    0x8146: 'endgame_slideshow', 0x8164: 'game_loaded', 0x816A: 'set_global_script_repeat',
    0x81E4: 'get_sfall_arg', 0x81F5: 'get_script', 0x822D: 'create_array',
    0x822E: 'set_array', 0x822F: 'get_array', 0x8230: 'free_array', 0x8231: 'len_array',
    0x8233: 'temp_array', 0x8236: 'list_as_array', 0x8254: 'save_array',
    0x8255: 'load_array', 0x8256: 'array_key', 0x8257: 'arrayexpr',
    0x8262: 'register_hook_proc', 0x826B: 'message_str_game', 0x8277: 'sfall_func1',
}


class SkriptFehler(Exception):
    """Ein Fehler, der im Spiel das Skript abbrechen oder falsch laufen lassen wuerde."""


def _i32(x):
    x &= 0xFFFFFFFF
    return x - 0x100000000 if x & 0x80000000 else x


class Programm:
    """Eine geladene .int-Datei (nur lesen)."""

    def __init__(self, pfad):
        self.pfad = pfad
        self.name = os.path.splitext(os.path.basename(pfad))[0].lower()
        d = open(pfad, 'rb').read()
        self.daten = d
        n = struct.unpack('>i', d[42:46])[0]
        self.ident_basis = 46 + 24 * n
        ilen = struct.unpack('>i', d[self.ident_basis:self.ident_basis + 4])[0]
        self.str_basis = self.ident_basis + ilen + 4 + 4   # programGetString: staticStrings + 4
        self.prozeduren = []
        for p in range(n):
            name_off, flags, zeit, bed, rumpf, argc = struct.unpack('>6i', d[46 + 24 * p:70 + 24 * p])
            self.prozeduren.append(dict(name=self.ident(name_off).lower(), flags=flags,
                                        rumpf=rumpf, argc=argc, index=p))
        self.nach_name = {}
        for p in self.prozeduren:
            self.nach_name.setdefault(p['name'], p)

    def _cstr(self, pos):
        e = self.daten.index(b'\0', pos)
        return self.daten[pos:e].decode('latin-1')

    def ident(self, off):
        return self._cstr(self.ident_basis + off)

    def string(self, off):
        return self._cstr(self.str_basis + off)

    def prozedur(self, name):
        return self.nach_name.get(name.lower())

    def disassemblieren(self):
        """Liefert (adresse, befehl, wert) fuer den Kopf und den Code ab init."""
        d = self.daten
        init = struct.unpack('>i', d[12:16])[0]
        zeilen = []
        for von, bis in ((0, 42), (init, len(d))):
            ip = von
            while ip < bis:
                op = struct.unpack('>H', d[ip:ip + 2])[0]
                if (op & 0x3FF) == 1 and op != 0x8001:
                    raw = d[ip + 2:ip + 6]
                    if op == VT_FLOAT:
                        wert = struct.unpack('>f', raw)[0]
                    elif op == VT_STR:
                        wert = repr(self.string(struct.unpack('>i', raw)[0]))
                    else:
                        wert = struct.unpack('>i', raw)[0]
                    zeilen.append((ip, 'push', wert))
                    ip += 6
                else:
                    zeilen.append((ip, NAMEN.get(op, hex(op)), None))
                    ip += 2
        return zeilen


# --------------------------------------------------------------------------
# Konstanten aus den Headern (#define NAME wert)

class Konstanten:
    """Liest einfache #define-Konstanten, damit Tests GVAR_..., SCRIPT_... usw.
    beim Namen nennen koennen."""

    DEF = re.compile(r'^\s*#define\s+([A-Za-z_]\w*)\s+(.+?)\s*(//.*)?$')

    def __init__(self):
        self.roh = {}
        self.cache = {}

    def lade(self, pfad, extra=None):
        text = open(pfad, encoding='latin-1').read()
        text = re.sub(r'/\*.*?\*/', ' ', text, flags=re.S)
        for zeile in text.splitlines():
            m = self.DEF.match(zeile)
            if m and '(' not in m.group(1):
                self.roh.setdefault(m.group(1), m.group(2).strip())
        if extra:
            self.roh.update(extra)

    def __getitem__(self, name):
        if name in self.cache:
            return self.cache[name]
        if name not in self.roh:
            raise KeyError(name)
        ausdruck = self.roh[name]
        py = ausdruck.replace('bwor', '|').replace('bwand', '&')
        py = re.sub(r'\b([A-Za-z_]\w*)\b',
                    lambda m: str(self[m.group(1)]) if m.group(1) in self.roh else m.group(1), py)
        try:
            wert = eval(py, {'__builtins__': {}}, {})
        except Exception:
            raise KeyError(f'{name} = {ausdruck} nicht auswertbar')
        if isinstance(wert, float):
            wert = int(wert)
        self.cache[name] = wert
        return wert

    def get(self, name, vorgabe=None):
        try:
            return self[name]
        except KeyError:
            return vorgabe


# --------------------------------------------------------------------------
# Meldungsdateien

def lade_msg(pfad):
    """{nr}{ton}{text}; Text darf ueber Zeilen gehen; alles ausserhalb der
    Klammern ist Kommentar (wie der Parser des Spiels)."""
    text = open(pfad, encoding='latin-1').read()
    eintraege = {}
    for m in re.finditer(r'\{(\d+)\}\{[^}]*\}\{([^}]*)\}', text):
        nr = int(m.group(1))
        if nr in eintraege:
            raise SkriptFehler(f'{pfad}: Nummer {nr} doppelt')
        eintraege[nr] = m.group(2).replace('\n', ' ')
    return eintraege


# --------------------------------------------------------------------------
# Spielwelt

class Obj:
    zaehler = 0

    def __init__(self, pid, tile=-1, elev=0, name=None, skript=None):
        Obj.zaehler += 1
        self.id = Obj.zaehler
        self.pid = pid
        self.tile = tile
        self.elev = elev
        self.name = name or f'obj{self.id}:{pid:#x}'
        self.skript = skript          # Instanz oder None
        self.skript_nr = -1           # 1-basiert wie get_script
        self.stats = {}
        self.skills = {}
        self.kronkorken = 0
        self.lvars = {}
        self.tot = False
        self.zerstoert = False

    def __repr__(self):
        return f'<{self.name}>'


class Instanz:
    """Ein geladenes Skript mit eigenem Stapel (wie ein Program in der Engine)."""

    def __init__(self, spiel, programm, besitzer=None, nr=-1):
        self.spiel = spiel
        self.p = programm
        self.besitzer = besitzer
        self.nr = nr
        self.stack = []
        self.rstack = []
        self.fp = 0
        self.bp = 0
        self.ip = 0
        self.flags = 0
        self.overrides = False
        self.initialisiert = False
        self.fang = False
        self.rueckgabe = None
        self.spur = None              # Liste: jeder Schritt (ip, befehl, Stapelspitze)

    # -- Ausfuehrung ------------------------------------------------------

    def initialisieren(self):
        """Code ab Adresse 0: legt die Skript-Variablen an und springt in
        'start' (so erzeugt sslc den Init-Code), wie beim Laden im Spiel."""
        sp = self.spiel
        alt = sp.self_obj
        sp.self_obj = self.besitzer
        self.ip = 0
        self.flags = 0
        self.initialisiert = True
        try:
            self._schleife()
        finally:
            sp.self_obj = alt
        self.flags &= ~0x41

    def rufe(self, name, self_obj=None, source=None, target=None, fixed=0):
        """Wie _executeProcedure: fuehrt eine Prozedur (ohne Argumente) aus."""
        if not self.initialisiert:
            self.initialisieren()
        pr = self.p.prozedur(name)
        if pr is None:
            return False
        sp = self.spiel
        alt = (sp.self_obj, sp.source_obj, sp.target_obj, sp.fixed_param, sp.aktiv)
        sp.self_obj = self_obj if self_obj is not None else self.besitzer
        sp.source_obj, sp.target_obj, sp.fixed_param, sp.aktiv = source, target, fixed, self
        if sp.aktiv_tiefe == 0:
            self.overrides = False
        sp.aktiv_tiefe += 1
        try:
            if self.flags & 0x100:
                return False          # Objekt hat sich selbst zerstoert
            self._setup_call(pr['rumpf'], 24)
            self._schleife()
            self.flags &= ~0x40
        finally:
            sp.aktiv_tiefe -= 1
            sp.self_obj, sp.source_obj, sp.target_obj, sp.fixed_param, sp.aktiv = alt
        return True

    def rufe_mit(self, name, *args, self_obj=None):
        """Ruft eine Prozedur mit Argumenten und liefert ihren Rueckgabewert
        (fuer Tests einzelner Prozeduren wie rl_rechne_woche)."""
        if not self.initialisiert:
            self.initialisieren()
        pr = self.p.prozedur(name)
        if pr is None:
            raise SkriptFehler(f'{self.p.name}: Prozedur {name} fehlt')
        if pr['argc'] != len(args):
            raise SkriptFehler(f'{name} erwartet {pr["argc"]} Argumente')
        sp = self.spiel
        alt = (sp.self_obj, sp.aktiv)
        sp.self_obj, sp.aktiv = self_obj if self_obj is not None else self.besitzer, self
        sp.aktiv_tiefe += 1
        try:
            self._setup_call(pr['rumpf'], 24)
            self.stack.pop()                # statt argc 0: Argumente und ihre Zahl
            self.stack.extend(args)
            self.stack.append(len(args))
            self.fang = True
            self._schleife()
            self.flags &= ~0x40
            return self.rueckgabe
        finally:
            self.fang = False
            sp.aktiv_tiefe -= 1
            sp.self_obj, sp.aktiv = alt

    def _setup_call(self, adresse, ruecksprung):
        self.rstack.append(('i', self.ip))
        self.rstack.append(('i', ruecksprung))
        self.stack.append(self.flags & 0xFFFF)
        self.stack.append(0)          # checkWaitFunc
        self.stack.append(0)          # windowId
        self.flags &= ~0xFFFF
        self.ip = adresse
        self.stack.append(0)          # Rueckgabewert-Platz (_setupCall)

    def pop(self):
        if not self.stack:
            raise SkriptFehler(f'{self.p.name}: Stapel leer bei {self.ip}')
        return self.stack.pop()

    def pop_int(self):
        v = self.pop()
        if isinstance(v, bool):
            return int(v)
        if isinstance(v, int):
            return v
        if isinstance(v, float):
            return int(v)
        if isinstance(v, Obj):
            return v.id
        raise SkriptFehler(f'{self.p.name}: Zahl erwartet, {v!r} bekommen (ip {self.ip})')

    def pop_obj(self):
        v = self.pop()
        if isinstance(v, Obj):
            return v
        if v == 0:
            return None
        raise SkriptFehler(f'{self.p.name}: Objekt erwartet, {v!r} bekommen (ip {self.ip})')

    def _schleife(self):
        d = self.p.daten
        sp = self.spiel
        schritte = 0
        while True:
            if self.fang and self.ip == 24 and self.stack:
                self.rueckgabe = self.stack[-1]   # Rueckgabewert vor dem 'pop' bei 24
            if self.flags & 0x14D:    # EXITED, 0x04, STOPPED, 0x40 (Prozedur fertig), 0x100 (self zerstoert)
                break
            if self.ip < 0 or self.ip + 2 > len(d):
                raise SkriptFehler(f'{self.p.name}: Sprung ins Leere ({self.ip})')
            op = (d[self.ip] << 8) | d[self.ip + 1]
            if self.spur is not None:
                self.spur.append((self.ip, NAMEN.get(op, hex(op)), self.stack[-3:]))
            self.ip += 2
            schritte += 1
            if schritte > sp.max_schritte:
                raise SkriptFehler(f'{self.p.name}: Endlosschleife? (> {sp.max_schritte} Schritte)')
            if (op & 0x3FF) == 1 and op != 0x8001:
                raw = d[self.ip:self.ip + 4]
                self.ip += 4
                if op == VT_INT:
                    self.stack.append(struct.unpack('>i', raw)[0])
                elif op == VT_FLOAT:
                    self.stack.append(struct.unpack('>f', raw)[0])
                elif op == VT_STR:
                    self.stack.append(self.p.string(struct.unpack('>i', raw)[0]))
                else:
                    raise SkriptFehler(f'unbekannter push-Typ {op:#x}')
                continue
            h = KERN.get(op)
            if h is not None:
                h(self)
                continue
            h = SPIEL.get(op)
            if h is None:
                raise SkriptFehler(f'{self.p.name}: Befehl {op:#x} ({NAMEN.get(op, "?")}) '
                                   f'ist im Pruefwerkzeug nicht nachgebildet')
            h(self, sp)


# --------------------------------------------------------------------------
# Kernbefehle (interpreter.cc)

def _leer(v):
    if isinstance(v, str):
        return False
    if isinstance(v, Obj):
        return False
    return v == 0


def _vergleich(a, b):
    """-1/0/1 wie die Vergleichsbefehle der Engine (a links, b rechts)."""
    if isinstance(a, Obj) or isinstance(b, Obj):
        ai = a.id if isinstance(a, Obj) else a
        bi = b.id if isinstance(b, Obj) else b
        if isinstance(ai, str) or isinstance(bi, str):
            raise SkriptFehler('Objekt mit Text verglichen')
        return (ai > bi) - (ai < bi)
    if isinstance(a, str) or isinstance(b, str):
        sa = a if isinstance(a, str) else (f'{a:.5f}' if isinstance(a, float) else str(a))
        sb = b if isinstance(b, str) else (f'{b:.5f}' if isinstance(b, float) else str(b))
        return (sa > sb) - (sa < sb)
    return (a > b) - (a < b)


def _bin(fn):
    def h(vm):
        b = vm.pop()
        a = vm.pop()
        vm.stack.append(fn(vm, a, b))
    return h


def _add(vm, a, b):
    if isinstance(a, str) or isinstance(b, str):
        def s(x):
            if isinstance(x, str):
                return x
            if isinstance(x, float):
                return f'{x:.5f}'
            if isinstance(x, Obj):
                return f'{x.id:#x}'
            return str(x)
        return s(a) + s(b)
    if isinstance(a, Obj) or isinstance(b, Obj):
        raise SkriptFehler('Rechnen mit Objekt')
    if isinstance(a, float) or isinstance(b, float):
        return float(a) + float(b)
    r = a + b
    if r > 0x7FFFFFFF or r < -0x80000000:
        return float(r)
    return r


def _num(vm, x):
    if isinstance(x, (int, float)) and not isinstance(x, bool):
        return x
    raise SkriptFehler(f'{vm.p.name}: Zahl erwartet, {x!r} (ip {vm.ip})')


def _sub(vm, a, b):
    a, b = _num(vm, a), _num(vm, b)
    if isinstance(a, float) or isinstance(b, float):
        return float(a) - float(b)
    return _i32(a - b)


def _mul(vm, a, b):
    a, b = _num(vm, a), _num(vm, b)
    if isinstance(a, float) or isinstance(b, float):
        return float(a) * float(b)
    return _i32(a * b)


def _div(vm, a, b):
    a, b = _num(vm, a), _num(vm, b)
    if b == 0:
        raise SkriptFehler(f'{vm.p.name}: Division durch null (ip {vm.ip})')
    if isinstance(a, float) or isinstance(b, float):
        return float(a) / float(b)
    q = abs(a) // abs(b)
    return q if (a >= 0) == (b > 0) else -q


def _mod(vm, a, b):
    if isinstance(a, float) or isinstance(b, float):
        raise SkriptFehler(f'{vm.p.name}: Modulo mit Gleitkomma (ip {vm.ip})')
    a, b = _num(vm, a), _num(vm, b)
    if b == 0:
        raise SkriptFehler(f'{vm.p.name}: Modulo durch null (ip {vm.ip})')
    r = abs(a) % abs(b)
    return r if a >= 0 else -r


def _as_int(x):
    if isinstance(x, float):
        return int(x)
    if isinstance(x, Obj):
        return x.id
    if isinstance(x, str):
        raise SkriptFehler('Bitoperation mit Text')
    return x


def _wahr(x):
    return 0 if _leer(x) else 1


def _k_push_base(vm):
    argc = vm.pop_int()
    vm.rstack.append(('i', vm.fp))
    vm.fp = len(vm.stack) - argc


def _k_pop_base(vm):
    vm.fp = vm.rstack.pop()[1]


def _k_pop_to_base(vm):
    del vm.stack[vm.fp:]


def _k_store(vm):
    adr = vm.pop_int()
    vm.stack[vm.fp + adr] = vm.pop()


def _k_fetch(vm):
    adr = vm.pop_int()
    vm.stack.append(vm.stack[vm.fp + adr])


def _k_fetch_global(vm):
    adr = vm.pop_int()
    vm.stack.append(vm.stack[vm.bp + adr])


def _k_store_global(vm):
    adr = vm.pop_int()
    vm.stack[vm.bp + adr] = vm.pop()


def _k_if(vm):
    v = vm.pop()
    if not _leer(v):
        vm.pop()
    else:
        vm.ip = vm.pop_int()


def _k_while(vm):
    v = vm.pop()
    if _leer(v):
        vm.ip = vm.pop_int()


def _k_call(vm):
    idx = vm.pop_int()
    pr = vm.p.prozeduren[idx]
    if pr['flags'] & PROC_IMPORTED:
        raise SkriptFehler(f'importierte Prozedur {pr["name"]}')
    vm.ip = pr['rumpf']


def _k_pop_flags(vm):
    vm.pop()
    vm.pop()
    vm.flags = vm.pop_int() & 0xFFFF


def _k_pop_flags_return(vm):
    _k_pop_flags(vm)
    vm.ip = vm.rstack.pop()[1]


def _k_pop_flags_exit(vm):
    _k_pop_flags(vm)
    vm.ip = vm.rstack.pop()[1]
    vm.flags |= 0x40


def _k_check_args(vm):
    erwartet = vm.pop_int()
    idx = vm.pop_int()
    pr = vm.p.prozeduren[idx]
    if pr['argc'] != erwartet:
        raise SkriptFehler(f'Falsche Argumentzahl fuer {pr["name"]}')


def _k_swapa(vm):
    a = vm.rstack.pop()
    b = vm.rstack.pop()
    vm.rstack.append(a)
    vm.rstack.append(b)


def _k_swap(vm):
    a = vm.pop()
    b = vm.pop()
    vm.stack.append(a)
    vm.stack.append(b)


def _k_dup(vm):
    v = vm.pop()
    vm.stack.append(v)
    vm.stack.append(v)


def _k_negate(vm):
    v = vm.pop()
    if isinstance(v, (int, float)):
        vm.stack.append(-v)
    else:
        raise SkriptFehler('negate auf Nicht-Zahl')


def _k_not(vm):
    v = vm.pop()
    if isinstance(v, Obj):
        vm.stack.append(0)
    elif isinstance(v, str):
        vm.stack.append(0)
    else:
        vm.stack.append(1 if v == 0 else 0)


def _k_floor(vm):
    v = vm.pop()
    import math
    vm.stack.append(int(math.floor(v)) if isinstance(v, float) else v)


def _k_dump(vm):
    n = vm.pop_int()
    for _ in range(n):
        vm.pop()


def _k_fetch_proc_address(vm):
    idx = vm.pop_int()
    vm.stack.append(vm.p.prozeduren[idx]['rumpf'])


def _k_lookup_string_proc(vm):
    name = vm.pop()
    pr = vm.p.prozedur(name)
    if pr is None:
        raise SkriptFehler(f'Prozedur {name} nicht gefunden')
    vm.stack.append(pr['index'])


KERN = {
    0x8000: lambda vm: None,
    0x8002: lambda vm: None,
    0x8003: lambda vm: None,
    0x804A: lambda vm: None,
    0x804B: lambda vm: None,
    0x8004: lambda vm: setattr(vm, 'ip', vm.pop_int()),
    0x8005: _k_call,
    0x800C: lambda vm: vm.stack.append(vm.rstack.pop()[1]),
    0x800D: lambda vm: vm.rstack.append(('i', vm.pop())),
    0x800E: lambda vm: setattr(vm, 'flags', vm.flags | 0x01),
    0x8010: lambda vm: setattr(vm, 'flags', vm.flags | 0x01),
    0x8011: lambda vm: setattr(vm, 'flags', vm.flags | 0x08),
    0x8012: _k_fetch_global,
    0x8013: _k_store_global,
    0x8018: _k_swap,
    0x8019: _k_swapa,
    0x801A: lambda vm: vm.pop(),
    0x801B: _k_dup,
    0x801C: lambda vm: setattr(vm, 'ip', vm.rstack.pop()[1]),
    0x801D: lambda vm: (setattr(vm, 'ip', vm.rstack.pop()[1]), setattr(vm, 'flags', vm.flags | 0x40)),
    0x801E: lambda vm: vm.rstack.pop(),
    0x801F: _k_pop_flags,
    0x8020: _k_pop_flags_return,
    0x8021: _k_pop_flags_exit,
    0x8027: _k_check_args,
    0x8028: _k_lookup_string_proc,
    0x8029: _k_pop_base,
    0x802A: _k_pop_to_base,
    0x802B: _k_push_base,
    0x802C: lambda vm: setattr(vm, 'bp', len(vm.stack)),
    0x802D: _k_fetch_proc_address,
    0x802E: _k_dump,
    0x802F: _k_if,
    0x8030: _k_while,
    0x8031: _k_store,
    0x8032: _k_fetch,
    0x8033: _bin(lambda vm, a, b: int(_vergleich(a, b) == 0)),
    0x8034: _bin(lambda vm, a, b: int(_vergleich(a, b) != 0)),
    0x8035: _bin(lambda vm, a, b: int(_vergleich(a, b) <= 0)),
    0x8036: _bin(lambda vm, a, b: int(_vergleich(a, b) >= 0)),
    0x8037: _bin(lambda vm, a, b: int(_vergleich(a, b) < 0)),
    0x8038: _bin(lambda vm, a, b: int(_vergleich(a, b) > 0)),
    0x8039: _bin(_add),
    0x803A: _bin(_sub),
    0x803B: _bin(_mul),
    0x803C: _bin(_div),
    0x803D: _bin(_mod),
    0x803E: _bin(lambda vm, a, b: _wahr(a) & _wahr(b)),
    0x803F: _bin(lambda vm, a, b: _wahr(a) | _wahr(b)),
    0x8040: _bin(lambda vm, a, b: _i32(_as_int(a) & _as_int(b))),
    0x8041: _bin(lambda vm, a, b: _i32(_as_int(a) | _as_int(b))),
    0x8042: _bin(lambda vm, a, b: _i32(_as_int(a) ^ _as_int(b))),
    0x8043: lambda vm: vm.stack.append(_i32(~_as_int(vm.pop()))),
    0x8044: _k_floor,
    0x8045: _k_not,
    0x8046: _k_negate,
}


# --------------------------------------------------------------------------
# Spiel- und sfall-Befehle

def _s_display_msg(vm, sp):
    t = vm.pop()
    sp.meldungen.append(str(t))


def _s_random(vm, sp):
    hoch = vm.pop_int()
    tief = vm.pop_int()
    sp.stats_random += 1
    vm.stack.append(sp.zufall(tief, hoch))


def _s_global_var(vm, sp):
    n = vm.pop_int()
    vm.stack.append(sp.gvars.get(n, 0))


def _s_set_global_var(vm, sp):
    v = vm.pop()
    n = vm.pop_int()
    if not isinstance(v, int):
        raise SkriptFehler(f'GVAR {n} bekommt {v!r}')
    sp.gvars[n] = v
    sp.gvar_log.append((n, v))


def _s_local_var(vm, sp):
    n = vm.pop_int()
    o = sp.self_obj
    vm.stack.append(o.lvars.get(n, 0) if o else 0)


def _s_set_local_var(vm, sp):
    v = vm.pop()
    n = vm.pop_int()
    if sp.self_obj:
        sp.self_obj.lvars[n] = v


def _s_map_var(vm, sp):
    n = vm.pop_int()
    vm.stack.append(sp.mvars.setdefault(sp.karte, {}).get(n, 0))


def _s_set_map_var(vm, sp):
    v = vm.pop()
    n = vm.pop_int()
    sp.mvars.setdefault(sp.karte, {})[n] = v


def _s_critter_stat(vm, sp):
    stat = vm.pop_int()
    o = vm.pop_obj()
    vm.stack.append(o.stats.get(stat, 5 if stat < 7 else 0) if o else 0)


def _s_has_skill(vm, sp):
    skill = vm.pop_int()
    o = vm.pop_obj()
    vm.stack.append(o.skills.get(skill, 20) if o else 0)


def _s_tile_contains_pid_obj(vm, sp):
    pid = vm.pop_int()
    elev = vm.pop_int()
    tile = vm.pop_int()
    for o in sp.objekte:
        if o.tile == tile and o.elev == elev and o.pid == pid and not o.zerstoert:
            vm.stack.append(o)
            return
    vm.stack.append(0)


def _s_create_object_sid(vm, sp):
    sid = vm.pop_int()
    elev = vm.pop_int()
    tile = vm.pop_int()
    pid = vm.pop_int()
    o = sp.erzeuge(pid, tile, elev, sid)
    vm.stack.append(o)


def _s_destroy_object(vm, sp):
    o = vm.pop_obj()
    if o is None:
        return
    sp.zerstoere(o)
    if o is sp.self_obj:
        # Wie im Spiel (PROGRAM_FLAG_0x0100): das Skript laeuft nicht weiter
        vm.flags |= 0x100


def _s_move_to(vm, sp):
    elev = vm.pop_int()
    tile = vm.pop_int()
    o = vm.pop_obj()
    if o:
        o.tile, o.elev = tile, elev
    sp.protokoll.append(f'move_to {o} {tile} {elev}')
    vm.stack.append(tile)


def _s_tile_num(vm, sp):
    o = vm.pop_obj()
    vm.stack.append(o.tile if o else -1)


def _s_elevation(vm, sp):
    o = vm.pop_obj()
    vm.stack.append(o.elev if o else 0)


def _s_tile_in_dir(vm, sp):
    dist = vm.pop_int()
    rot = vm.pop_int()
    tile = vm.pop_int()
    vm.stack.append(tile + dist)   # Naeherung: nur fuer "irgendein Nachbar-Hex"


def _s_load_map(vm, sp):
    param = vm.pop_int()
    karte = vm.pop()
    sp.karten_wechsel.append((karte, param))
    sp.protokoll.append(f'load_map {karte!r} {param}')


def _s_message_str(vm, sp):
    nr = vm.pop_int()
    liste = vm.pop_int()
    vm.stack.append(sp.msg_text(liste, nr))


def _s_message_str_game(vm, sp):
    nr = vm.pop_int()
    datei = vm.pop_int()
    texte = sp.extra_msg.get(datei)
    if texte is None:
        raise SkriptFehler(f'message_str_game: Datei-ID {datei} nicht geladen')
    if nr not in texte:
        sp.fehlende_texte.append(('game', datei, nr))
        vm.stack.append('Error')
    else:
        vm.stack.append(texte[nr])


def _s_sfall_func1(vm, sp):
    arg = vm.pop()
    name = vm.pop()
    if name == 'add_extra_msg_file':
        vm.stack.append(sp.add_extra_msg_file(arg))
    else:
        raise SkriptFehler(f'sfall_func1("{name}") nicht nachgebildet')


def _s_metarule(vm, sp):
    param = vm.pop()
    regel = vm.pop_int()
    if regel == 14:          # METARULE_TEST_FIRSTRUN: map_first_run
        vm.stack.append(1 if sp.erster_besuch else 0)
    elif regel == 22:        # METARULE_IS_LOADGAME
        vm.stack.append(0)
    elif regel == 17:        # METARULE_CURRENT_TOWN
        vm.stack.append(sp.stadt)
    else:
        sp.protokoll.append(f'metarule {regel} {param!r}')
        vm.stack.append(0)


def _s_gsay_start(vm, sp):
    sp.dialog_optionen = []
    sp.dialog_antwort = None


def _msg_oder_text(sp, liste, msg):
    if isinstance(msg, str):
        return msg
    return sp.msg_text(liste, msg)


def _s_gsay_reply(vm, sp):
    msg = vm.pop()
    liste = vm.pop_int()
    sp.dialog_antwort = _msg_oder_text(sp, liste, msg)


def _s_giq_option(vm, sp):
    reaktion = vm.pop_int()
    proc = vm.pop()
    msg = vm.pop()
    liste = vm.pop_int()
    iq = vm.pop_int()
    intel = sp.dude.stats.get(4, 5)
    if iq < 0:
        if -intel < iq:
            return
    elif intel < iq:
        return
    text = _msg_oder_text(sp, liste, msg)
    sp.dialog_optionen.append((text, proc, reaktion))


def _s_gsay_end(vm, sp):
    sp.dialog_lauf(vm)


def _s_start_gdialog(vm, sp):
    for _ in range(4):
        vm.pop()
    vm.pop()
    sp.im_dialog = True


def _s_end_dialogue(vm, sp):
    sp.im_dialog = False


def _s_game_time_sec(vm, sp):
    vm.stack.append(sp.zeit // 10)


def _s_game_time(vm, sp):
    vm.stack.append(sp.zeit)


def _s_caps_total(vm, sp):
    o = vm.pop_obj()
    vm.stack.append(o.kronkorken if o else 0)


def _s_caps_adjust(vm, sp):
    n = vm.pop_int()
    o = vm.pop_obj()
    if o is None:
        vm.stack.append(-1)
        return
    if o.kronkorken + n < 0:
        vm.stack.append(-1)       # wie item_caps_adjust: nicht genug
        return
    o.kronkorken += n
    vm.stack.append(0)


def _s_critter_dmg(vm, sp):
    typ = vm.pop_int()
    n = vm.pop_int()
    o = vm.pop_obj()
    sp.protokoll.append(f'critter_dmg {o} {n}')


def _s_attack_setup(vm, sp):
    ziel = vm.pop_obj()
    wer = vm.pop_obj()
    sp.angriffe.append((wer, ziel))
    sp.protokoll.append(f'attack_setup {wer} {ziel}')


def _s_float_msg(vm, sp):
    farbe = vm.pop()
    text = vm.pop()
    o = vm.pop_obj()
    sp.schwebetexte.append((o, text))


def _s_endgame_slideshow(vm, sp):
    sp.protokoll.append('endgame_slideshow')


def _s_game_loaded(vm, sp):
    vm.stack.append(1 if sp.game_loaded else 0)


def _s_script_repeat(vm, sp):
    sp.wiederholung = vm.pop_int()


def _s_get_script(vm, sp):
    o = vm.pop_obj()
    vm.stack.append(o.skript_nr if o else -1)


def _s_register_hook_proc(vm, sp):
    proc = vm.pop()
    hook = vm.pop_int()
    sp.hooks[hook] = (vm, proc)


def _s_get_sfall_arg(vm, sp):
    vm.stack.append(sp.hook_args.pop(0) if sp.hook_args else 0)


# sfall-Arrays -------------------------------------------------------------

class Liste:
    def __init__(self, n):
        self.werte = [0] * max(0, n)

    def __len__(self):
        return len(self.werte)


class Map:
    def __init__(self):
        self.paare = []

    def __len__(self):
        return len(self.paare)

    def _finde(self, k):
        for i, (kk, _) in enumerate(self.paare):
            if type(kk) is type(k) and kk == k:
                return i
        return -1


def _neues_array(sp, n, flags, temp):
    aid = sp.naechstes_array
    sp.naechstes_array += 1
    sp.arrays[aid] = Map() if n < 0 or (flags & 1) else Liste(n)
    if temp:
        sp.temp_arrays.add(aid)
    return aid


def _s_create_array(vm, sp):
    flags = vm.pop_int()
    n = vm.pop_int()
    vm.stack.append(_neues_array(sp, n, flags, False))


def _s_temp_array(vm, sp):
    flags = vm.pop_int()
    n = vm.pop_int()
    vm.stack.append(_neues_array(sp, n, flags, True))


def _arr(sp, aid):
    if isinstance(aid, Obj) or not isinstance(aid, int):
        raise SkriptFehler(f'Array-ID erwartet, {aid!r}')
    a = sp.arrays.get(aid)
    if a is None and aid != 0:
        sp.ungueltige_arrays.append(aid)
    return a


def _s_get_array(vm, sp):
    k = vm.pop()
    aid = vm.pop()
    if isinstance(aid, str):
        # get_array auf Text liefert ein Zeichen (sfall); hier nicht gebraucht
        raise SkriptFehler('get_array auf Text')
    a = _arr(sp, aid)
    if a is None:
        vm.stack.append(0)
    elif isinstance(a, Liste):
        i = _as_int(k) if not isinstance(k, str) else -1
        vm.stack.append(a.werte[i] if 0 <= i < len(a.werte) else 0)
        if not (0 <= i < len(a.werte)):
            sp.array_ausserhalb.append((aid, k, len(a.werte), vm.p.name))
    else:
        i = a._finde(k)
        vm.stack.append(a.paare[i][1] if i >= 0 else 0)


def _set(sp, aid, k, v, erlaube_loeschen):
    a = _arr(sp, aid)
    if a is None:
        return
    if isinstance(a, Liste):
        if isinstance(k, int) and 0 <= k < len(a.werte):
            a.werte[k] = v
        else:
            sp.array_ausserhalb.append((aid, k, len(a.werte), 'set'))
    else:
        i = a._finde(k)
        if erlaube_loeschen and isinstance(v, int) and v == 0:
            if i >= 0:
                del a.paare[i]
        elif i >= 0:
            a.paare[i] = (k, v)
        else:
            a.paare.append((k, v))


def _s_set_array(vm, sp):
    v = vm.pop()
    k = vm.pop()
    aid = vm.pop_int()
    _set(sp, aid, k, v, True)


def _s_arrayexpr(vm, sp):
    v = vm.pop()
    k = vm.pop()
    aid = sp.naechstes_array - 1
    a = sp.arrays.get(aid)
    if a is not None:
        if isinstance(a, Liste) and isinstance(k, int) and k >= len(a.werte):
            a.werte.extend([0] * (k + 1 - len(a.werte)))
        _set(sp, aid, k, v, False)
    vm.stack.append(0)


def _s_free_array(vm, sp):
    aid = vm.pop_int()
    sp.arrays.pop(aid, None)
    for k, v in list(sp.gespeichert.items()):
        if v == aid:
            del sp.gespeichert[k]


def _s_len_array(vm, sp):
    aid = vm.pop_int()
    a = sp.arrays.get(aid)
    vm.stack.append(len(a) if a is not None else -1)


def _s_save_array(vm, sp):
    aid = vm.pop_int()
    key = vm.pop()
    sp.gespeichert[key] = aid
    sp.temp_arrays.discard(aid)


def _s_load_array(vm, sp):
    key = vm.pop()
    vm.stack.append(sp.gespeichert.get(key, 0))


def _s_array_key(vm, sp):
    i = vm.pop_int()
    aid = vm.pop_int()
    a = sp.arrays.get(aid)
    if a is None:
        vm.stack.append(0)
    elif i == -1:
        vm.stack.append(1 if isinstance(a, Map) else 0)
    elif isinstance(a, Liste):
        vm.stack.append(i if 0 <= i <= len(a) else 0)
    else:
        vm.stack.append(a.paare[i][0] if 0 <= i < len(a.paare) else 0)


def _s_list_as_array(vm, sp):
    typ = vm.pop_int()
    objs = [o for o in sp.objekte if not o.zerstoert and (typ != 0 or (o.pid >> 24) == 1)]
    aid = _neues_array(sp, len(objs), 0, True)
    sp.arrays[aid].werte = objs
    vm.stack.append(aid)


SPIEL = {
    0x80A7: _s_tile_contains_pid_obj,
    0x80AA: _s_has_skill,
    0x80B4: _s_random,
    0x80B6: _s_move_to,
    0x80B7: _s_create_object_sid,
    0x80B8: _s_display_msg,
    0x80B9: lambda vm, sp: setattr(vm, 'overrides', True),
    0x80BC: lambda vm, sp: vm.stack.append(sp.self_obj or 0),
    0x80BD: lambda vm, sp: vm.stack.append(sp.source_obj or 0),
    0x80BE: lambda vm, sp: vm.stack.append(sp.target_obj or 0),
    0x80BF: lambda vm, sp: vm.stack.append(sp.dude),
    0x80C1: _s_local_var,
    0x80C2: _s_set_local_var,
    0x80C3: _s_map_var,
    0x80C4: _s_set_map_var,
    0x80C5: _s_global_var,
    0x80C6: _s_set_global_var,
    0x80CA: _s_critter_stat,
    0x80D4: _s_tile_num,
    0x80D5: _s_tile_in_dir,
    0x80DE: _s_start_gdialog,
    0x80DF: _s_end_dialogue,
    0x80E4: _s_load_map,
    0x80E9: lambda vm, sp: vm.pop(),
    0x80EA: _s_game_time,
    0x80EB: _s_game_time_sec,
    0x80EC: _s_elevation,
    0x80EF: _s_critter_dmg,
    0x80F4: _s_destroy_object,
    0x8101: lambda vm, sp: vm.stack.append(sp.karte),
    0x810A: _s_float_msg,
    0x8105: _s_message_str,
    0x810B: _s_metarule,
    0x811C: _s_gsay_start,
    0x811D: _s_gsay_end,
    0x811E: _s_gsay_reply,
    0x8121: _s_giq_option,
    0x8128: lambda vm, sp: vm.stack.append(1 if sp.kampf else 0),
    0x8136: lambda vm, sp: vm.pop(),
    0x8137: lambda vm, sp: vm.pop(),
    0x8138: _s_caps_total,
    0x8139: _s_caps_adjust,
    0x8143: _s_attack_setup,
    0x8146: _s_endgame_slideshow,
    0x8164: _s_game_loaded,
    0x816A: _s_script_repeat,
    0x81E4: _s_get_sfall_arg,
    0x81F5: _s_get_script,
    0x822D: _s_create_array,
    0x822E: _s_set_array,
    0x822F: _s_get_array,
    0x8230: _s_free_array,
    0x8231: _s_len_array,
    0x8233: _s_temp_array,
    0x8236: _s_list_as_array,
    0x8254: _s_save_array,
    0x8255: _s_load_array,
    0x8256: _s_array_key,
    0x8257: _s_arrayexpr,
    0x8262: _s_register_hook_proc,
    0x826B: _s_message_str_game,
    0x8277: _s_sfall_func1,
}


# --------------------------------------------------------------------------

class Spieler:
    """Waehlt Dialogoptionen. `plan` ist eine Liste von Eintraegen:
    ein Textstueck (die erste Option, die es enthaelt), eine Zahl (Index)
    oder None (erste Option). Ist der Plan leer, wird der Dialog verlassen:
    die Option, die keine neue Antwort setzt, oder sonst die letzte."""

    def __init__(self, plan=()):
        self.plan = list(plan)

    def waehle(self, antwort, optionen):
        """optionen: Liste (text, proc_name, reaktion)."""
        if self.plan:
            p = self.plan.pop(0)
            if p is None:
                return 0
            if isinstance(p, int):
                if p >= len(optionen):
                    raise SkriptFehler(f'Option {p} fehlt: {[o[0] for o in optionen]}')
                return p
            for i, o in enumerate(optionen):
                if p.lower() in o[0].lower():
                    return i
            raise SkriptFehler(f'Option mit "{p}" fehlt nach "{antwort}": '
                               f'{[o[0] for o in optionen]}')
        return self.ausgang(optionen)

    @staticmethod
    def ausgang(optionen):
        """Die Option, die den Dialog beendet (Node999 oder ohne Prozedur),
        sonst die letzte, die keine Debug-Option ist."""
        for i, o in enumerate(optionen):
            if o[1] in (None, 'node999', 'rlm_ende'):
                return i
        for i in range(len(optionen) - 1, -1, -1):
            if not optionen[i][0].startswith('[Debug]'):
                return i
        return len(optionen) - 1


class Spiel:
    """Die nachgebildete Spielwelt."""

    def __init__(self, skripte, texte, skript_basis, konst=None, seed=1):
        """skripte: Ordner mit .int; texte: text/english (mit dialog/ und game/);
        skript_basis: Nummer (1-basiert) des ersten eigenen Skripts;
        die Namen kommen aus install/scripts.lst.add."""
        self.ordner = skripte
        self.texte = texte
        self.konst = konst
        self.rng = random.Random(seed)
        self.zufall_folge = []            # feste Wuerfe fuer Tests (vorrangig)
        self.zufall_fest = None           # 'min' oder 'max': jeder Wurf am Rand
        self.max_schritte = 5_000_000
        self.programme = {}
        self.skript_namen = {}            # nr (1-basiert) -> name
        self.gvars = {}
        self.gvar_log = []
        self.mvars = {}
        self.objekte = []
        self.dude = Obj(0x01000000, 20000, 0, 'dude')
        self.dude.stats[4] = 6            # Intelligenz
        self.dude.kronkorken = 1000
        self.karte = 0
        self.stadt = 0
        self.erster_besuch = False
        self.zeit = 0                     # Spielzeit in Zehntelsekunden
        self.meldungen = []
        self.schwebetexte = []
        self.protokoll = []
        self.karten_wechsel = []
        self.angriffe = []
        self.arrays = {}
        self.naechstes_array = 1
        self.temp_arrays = set()
        self.gespeichert = {}
        self.ungueltige_arrays = []
        self.array_ausserhalb = []
        self.extra_msg = {}
        self.extra_msg_ids = {}
        self.msg_cache = {}
        self.fehlende_texte = []
        self.hooks = {}
        self.hook_args = []
        self.self_obj = self.source_obj = self.target_obj = None
        self.fixed_param = 0
        self.aktiv = None
        self.aktiv_tiefe = 0
        self.kampf = False
        self.im_dialog = False
        self.game_loaded = False
        self.wiederholung = 0
        self.dialog_optionen = []
        self.dialog_antwort = None
        self.dialog_verlauf = []
        self.dialog_fehler = []
        self.spieler = Spieler()
        self.globale = []
        self.stats_random = 0
        self.skript_basis = skript_basis
        self.naechste_nr = skript_basis

    # -- Skripte -----------------------------------------------------------

    def registriere(self, name, nr=None):
        if nr is None:
            nr = self.naechste_nr
            self.naechste_nr += 1
        self.skript_namen[nr] = name.lower()
        return nr

    def programm(self, name):
        name = name.lower()
        if name not in self.programme:
            self.programme[name] = Programm(os.path.join(self.ordner, name + '.int'))
        return self.programme[name]

    def instanz(self, nr, besitzer):
        name = self.skript_namen.get(nr)
        if name is None:
            raise SkriptFehler(f'Skript Nr. {nr} unbekannt')
        inst = Instanz(self, self.programm(name), besitzer, nr)
        inst.initialisieren()
        return inst

    def lade_global(self, name):
        """Wie sfall beim Laden eines Spielstands: Init-Code und 'start' mit game_loaded."""
        inst = Instanz(self, self.programm(name), None, -1)
        self.game_loaded = True
        try:
            inst.initialisieren()
        finally:
            self.game_loaded = False
        self.globale.append(inst)
        return inst

    # -- Objekte -----------------------------------------------------------

    def erzeuge(self, pid, tile, elev, nr=-1, name=None):
        o = Obj(pid, tile, elev, name)
        self.objekte.append(o)
        if nr is not None and nr >= 0:
            # create_object_sid bekommt die 0-basierte Nummer? Nein: SCRIPT_* sind
            # 1-basiert wie get_script; die Engine zieht intern 1 ab.
            o.skript_nr = nr
            o.skript = self.instanz(nr, o)   # Laden fuehrt 'start' aus (Init-Code springt hinein)
        return o

    def zerstoere(self, o):
        if o.zerstoert:
            return
        if o.skript:
            o.skript.rufe('destroy_p_proc', self_obj=o)
        o.zerstoert = True
        if o in self.objekte:
            self.objekte.remove(o)

    def finde(self, nr):
        return [o for o in self.objekte if o.skript_nr == nr and not o.zerstoert]

    # -- Zufall ------------------------------------------------------------

    def zufall(self, tief, hoch):
        if self.zufall_folge:
            w = self.zufall_folge.pop(0)
            if callable(w):
                w = w(tief, hoch)
            return max(tief, min(hoch, w))
        if hoch < tief:
            return tief
        if self.zufall_fest == 'max':
            return hoch
        if self.zufall_fest == 'min':
            return tief
        return self.rng.randint(tief, hoch)

    # -- Texte ---------------------------------------------------------------

    def msg_text(self, liste, nr):
        name = self.skript_namen.get(liste)
        if name is None:
            raise SkriptFehler(f'Meldungsliste {liste} unbekannt')
        if name not in self.msg_cache:
            pfad = os.path.join(self.texte, 'dialog', name + '.msg')
            self.msg_cache[name] = lade_msg(pfad) if os.path.exists(pfad) else {}
        texte = self.msg_cache[name]
        if nr not in texte:
            self.fehlende_texte.append((name, nr))
            return 'Error'
        return texte[nr]

    def add_extra_msg_file(self, datei):
        if datei in self.extra_msg_ids:
            return self.extra_msg_ids[datei]
        pfad = os.path.join(self.texte, 'game', datei)
        if not os.path.exists(pfad):
            return -1
        fid = 0x3000 + len(self.extra_msg_ids)
        self.extra_msg_ids[datei] = fid
        self.extra_msg[fid] = lade_msg(pfad)
        return fid

    # -- Dialog --------------------------------------------------------------

    def dialog_lauf(self, vm):
        """gsay_end: wie _gdialogGo/_gdProcess/_gdProcessChoice."""
        if self.dialog_antwort is None:
            return
        if not self.dialog_optionen:
            self.dialog_optionen.append(('[Done]', 0, 50))
        tiefe = 0
        while True:
            antwort = self.dialog_antwort
            optionen = [(t, self._proc_name(vm, pr), r) for t, pr, r in self.dialog_optionen]
            i = self.spieler.waehle(antwort, optionen)
            text, _, _ = optionen[i]
            proc = self.dialog_optionen[i][1]
            self.dialog_verlauf.append((antwort, [o[0] for o in optionen], text))
            self.dialog_optionen = []
            vorher = self.dialog_antwort
            self.dialog_antwort_neu = False
            if proc != 0:
                pr = vm.p.prozeduren[proc] if isinstance(proc, int) else vm.p.prozedur(proc)
                vm.rufe(pr['name'], self_obj=self.self_obj)
            if not self.dialog_optionen:
                if self.dialog_antwort is not vorher and self.dialog_antwort != vorher:
                    self.dialog_fehler.append(
                        f'Antwort ohne Option, wird nie angezeigt: "{self.dialog_antwort[:60]}"')
                break
            tiefe += 1
            if tiefe > 500:
                raise SkriptFehler('Dialog endet nicht')

    @staticmethod
    def _proc_name(vm, proc):
        if proc == 0:
            return None
        if isinstance(proc, int):
            return vm.p.prozeduren[proc]['name']
        return str(proc).lower()

    def rede(self, obj, plan=(), proc='talk_p_proc'):
        """Spricht obj an und spielt den Dialog nach `plan` durch."""
        self.spieler = Spieler(plan)
        self.dialog_verlauf = []
        self.dialog_optionen = []
        self.dialog_antwort = None
        obj.skript.rufe(proc, self_obj=obj, source=self.dude)
        rest = self.spieler.plan
        if rest:
            raise SkriptFehler(f'Dialog vorzeitig zu Ende, offen: {rest}')
        return self.dialog_verlauf

    # -- Hilfen fuer Tests --------------------------------------------------

    def welt_array(self, key):
        aid = self.gespeichert.get(key)
        return self.arrays[aid].werte if aid else None

    def tick(self):
        for g in self.globale:
            g.rufe('start')

    def betrete_karte(self, karte, erster=False):
        self.karte = karte
        self.erster_besuch = erster
        for g in self.globale:
            g.rufe('map_enter_p_proc')
        for o in list(self.objekte):
            if o.skript:
                o.skript.rufe('map_enter_p_proc', self_obj=o)

    def temp_freigeben(self):
        """sfall gibt temp_array am Ende des Frames frei."""
        for aid in self.temp_arrays:
            self.arrays.pop(aid, None)
        self.temp_arrays.clear()


def main(argv):
    if len(argv) >= 2 and argv[0] == 'dis':
        p = Programm(argv[1])
        for pr in p.prozeduren:
            print(f'proc {pr["index"]:3} {pr["name"]:32} rumpf {pr["rumpf"]:6} argc {pr["argc"]} flags {pr["flags"]:#x}')
        for adr, befehl, wert in p.disassemblieren():
            print(f'{adr:6}  {befehl}' + (f' {wert}' if wert is not None else ''))
        return 0
    print(__doc__)
    return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
