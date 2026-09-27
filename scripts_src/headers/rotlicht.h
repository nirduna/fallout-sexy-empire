/*
   rotlicht.h - Gemeinsame Definitionen fuer "Rotlicht ueber dem Oedland"

   Enthaelt:
     - Speicherlayout (zwei sfall-Arrays, die mit dem Spielstand gespeichert werden)
     - Stadt- und Stufentabellen aus Phase 1/2
     - die Wochenrechnung eines Hauses (rl_rechne_woche)

   Die Rechnung ist Zeile fuer Zeile identisch mit tools/economy_sim.py
   (Funktion simulate). Aenderungen immer in beiden Dateien vornehmen und
   mit dem Selbsttest pruefen (siehe docs/phase-5-technik.md).

   Voraussetzung: define.h und command.h sind vorher eingebunden, der
   Compiler ist sslc (sfall edition) mit Array-Syntax.
*/
#ifndef ROTLICHT_H
#define ROTLICHT_H

// Build-Einstellungen: RL_SCRIPT_BASE, RL_GVAR_BASE, RL_SELBSTTEST, RL_DEBUG
#include "../config/rl_build.h"

/* ------------------------------------------------------------------ */
/* Skript-Indizes (Zeilennummer in scripts.lst, gezaehlt ab 1).         */
/* RL_SCRIPT_BASE = Zeilenzahl der scripts.lst der Zielinstallation + 1 */
/* Restoration Project (RPU): 1558 Zeilen -> 1559 (Standard).           */
/* Unofficial Patch: 1308 Zeilen -> 1309 (mit RL_SCRIPT_BASE=1309).     */
/* ------------------------------------------------------------------ */
#ifndef RL_SCRIPT_BASE
#define RL_SCRIPT_BASE              (1559)
#endif
#define SCRIPT_RLESSIE              (RL_SCRIPT_BASE + 0)
#define SCRIPT_RLKOLBE              (RL_SCRIPT_BASE + 1)

/* ------------------------------------------------------------------ */
/* Echte GVARs (Phase 6). Nur dort, wo die Engine sie verlangt:        */
/* Endslides (endgame.txt) und Titel im Charakterbogen (karmavar.txt). */
/* RL_GVAR_BASE = Anzahl der GVARs in vault13.gam der Zielinstallation */
/* RPU: 791 (Standard), Unofficial Patch: 696.                         */
/* ------------------------------------------------------------------ */
#ifndef RL_GVAR_BASE
#define RL_GVAR_BASE                (791)
#endif
#define GVAR_RL_ENDE                (RL_GVAR_BASE + 0)
#define GVAR_RL_NACHSATZ            (RL_GVAR_BASE + 1)
#define GVAR_RL_TITEL_SEELE         (RL_GVAR_BASE + 2)   // "Seelenverkaeufer"
#define GVAR_RL_TITEL_ANSTAND       (RL_GVAR_BASE + 3)   // "Anstaendiges Haus"
#define GVAR_RL_TITEL_FAMILIE       (RL_GVAR_BASE + 4)   // "Die Fuenfte Familie"

#define RL_ENDE_KEINS               (0)
#define RL_ENDE_TYRANN              (1)
#define RL_ENDE_GESCHAEFT           (2)
#define RL_ENDE_BANKROTT            (3)

#define RL_NACHSATZ_KEINER          (0)
#define RL_NACHSATZ_KETTEN          (1)     // Der neue Metzger
#define RL_NACHSATZ_LEX_NEUN        (2)
#define RL_NACHSATZ_SCHWEIGEN       (3)     // Liga zerschlagen
#define RL_NACHSATZ_UEBERLEBENDE    (4)     // Mara als Madame
#define RL_NACHSATZ_KRALLE          (5)     // Kitty als Rivalin
#define RL_NACHSATZ_STIMME          (6)     // Vesper im Strumpfband

/* ------------------------------------------------------------------ */
/* Speicherung                                                        */
/* ------------------------------------------------------------------ */
#define RL_ARR_HAEUSER              "RL_HAUS"
#define RL_ARR_WELT                 "RL_WELT"

#define RL_DEN                      (0)
#define RL_NEW_RENO                 (1)
#define RL_REDDING                  (2)
#define RL_VAULT_CITY               (3)
#define RL_NCR                      (4)
#define RL_SAN_FRAN                 (5)
#define RL_ANZAHL_HAEUSER           (6)
#define RL_TESTHAUS                 (6)     // Slot nur fuer den Selbsttest
#define RL_SLOTS                    (7)

// Felder pro Haus (Index = Haus * RL_FELDER + Feld)
#define RL_FELDER                   (48)
#define RL_F_BESITZ                 (0)     // 0 = nicht uebernommen, 1 = eigenes Haus
#define RL_F_KLASSE                 (1)     // Hausklasse 1..3
#define RL_F_ZIMMER                 (2)
#define RL_F_PERSONAL               (3)     // Arbeitende (Phase 4: ein Zimmer braucht eine Person)
#define RL_F_QUALI                  (4)     // Grundqualitaet des Personals 0..100
#define RL_F_MORAL                  (5)     // 0..100
#define RL_F_RUF                    (6)     // Hausruf 0..100
#define RL_F_AUSSTATTUNG            (7)     // 0..100
#define RL_F_SICHERHEIT             (8)
#define RL_F_HITZE                  (9)     // 0..100, sinkt um 5 pro Woche
#define RL_F_EINFLUSS               (10)    // 0..100
#define RL_F_PREISSTUFE             (11)    // RL_PREIS_*
#define RL_F_ANTEIL                 (12)    // RL_ANTEIL_*
#define RL_F_BAR                    (13)    // Bar-Stufe 0..2
#define RL_F_NEBEN                  (14)    // zusaetzlicher Nebenumsatz $ je Kunde (Spieltische ...)
#define RL_F_MODULE                 (15)    // Bitmaske RL_MOD_*
#define RL_F_STUFEN                 (16)    // Summe aller Modulstufen (Unterhalt)
#define RL_F_LOEHNE                 (17)    // Fixloehne $/Woche
#define RL_F_MORALBONUS             (18)    // Quartiere, Riegel innen ...
#define RL_F_STADTMOD               (19)    // Kunden-Modifikator in % (0 = neutral), vom Tick gesetzt
#define RL_F_TRIBUTMOD              (20)    // Abweichung vom Basis-Tribut in Prozentpunkten
#define RL_F_KASSE                  (21)    // Bargeld im Haus
#define RL_F_GEWINN                 (22)    // Gewinn der letzten Woche
#define RL_F_KUNDEN                 (23)    // Kunden der letzten Woche
#define RL_F_KRISE                  (24)    // 0 = keine, sonst RL_EV_*
#define RL_F_KRISENWOCHEN           (25)
#define RL_F_FUEHRUNG               (26)    // Fuehrung der Madame (Phase 4)
#define RL_F_ZWANG                  (27)    // 1 = Zwangspersonal im Haus (Tyrannen-Route)
#define RL_F_ZUSTAND_TEST           (31)    // nur Selbsttest
#define RL_F_MODUL_STADTMOD         (32)    // Kunden-% aus gebauten Modulen (Goldwaage, Tunnel ...)
#define RL_F_GEKAUFT                (33)    // Bitmaske der gekauften Module (rl_katalog.h)
#define RL_F_BAU_ID                 (34)    // Modul-ID + 1 der laufenden Baustelle, 0 = keine
#define RL_F_BAU_WOCHEN             (35)    // verbleibende Bauwochen

// Modul-Bitmaske
#define RL_MOD_KONTOR               (1)
#define RL_MOD_KRANKENSTUBE         (2)
#define RL_MOD_VIP                  (4)
#define RL_MOD_JET_THEKE            (8)
#define RL_MOD_RIEGEL_AUSSEN        (16)
#define RL_MOD_AKTE                 (32)
#define RL_MOD_LEINE                (64)    // "An der Leine halten": Jet statt Lohn (Phase 4)

// Welt-Felder
#define RL_WELT_FELDER              (32)
#define RL_W_WOCHE                  (0)     // zuletzt abgerechnete Woche
#define RL_W_AKTIV                  (1)     // 1, sobald das erste Haus uebernommen ist
#define RL_W_HQ_KASSE               (2)     // Geld, das Laeufer ins Hauptquartier gebracht haben
#define RL_W_MARCUS                 (3)     // RL_MARCUS_*
#define RL_W_LIGA                   (4)     // RL_LIGA_*
#define RL_W_CATSPAW                (5)     // 0 offen, 1 Buendnis, 2 geloest
#define RL_W_MALAMUTE               (6)     // 0 offen, 1 geloest
#define RL_W_HUBOLOGEN              (7)     // 0 offen, 1 geloest, 2 unterwandert
#define RL_W_KITTY_RIVALIN          (8)     // 1 = "Kittys Kralle" in Redding
#define RL_W_KETTEN                 (9)     // Aktstand der Questline "Ketten"
#define RL_W_VIRGIN                 (10)    // Aktstand "Blut auf der Virgin Street"
#define RL_W_REINE                  (11)    // Aktstand "Die Reinen"
#define RL_W_TYRANN_WOCHEN          (12)    // Wochen mit Zwangspersonal oder Leine (Phase 6)
#define RL_W_AUSBEUTUNG_WOCHEN      (13)    // Wochen mit ausbeuterischem Anteil in mind. einem Haus
#define RL_W_MARA                   (14)    // 1 = Mara ist Madame der Gosse
#define RL_W_VESPER                 (15)    // 1 = Vesper singt im Strumpfband
#define RL_W_SHI_GEFALLEN           (16)    // 1 = Gefallen fuer die Shi erledigt (Siegel der Shi)
// Prolog "Essies Schulden" (Umsetzung 1)
#define RL_W_PROLOG                 (17)    // RL_PROLOG_*
#define RL_W_SCHULDEN               (18)    // Grundbetrag ohne Zinsen
#define RL_W_PROLOG_START           (19)    // Woche, in der der Prolog begann
#define RL_W_PROLOG_WEG             (20)    // RL_WEG_*
#define RL_W_METZGER                (21)    // RL_METZGER_*
#define RL_W_ESSIE                  (22)    // RL_ESSIE_*
#define RL_W_KOLBE                  (23)    // Bitfeld RL_KOLBE_*: was schon versucht wurde
#define RL_W_DIEBSTAHL_WOCHE        (24)    // Woche des Diebstahls (Metzger merkt es 2 Wochen spaeter)
#define RL_W_KETTEN_ZWEIG           (25)    // 0 offen, 1 Flucht, 2 Tyrann
#define RL_W_ESSIE_REAKTION         (26)    // 1 = Essies Reaktion auf die Uebernahme gezeigt

#define RL_PROLOG_OFFEN             (0)
#define RL_PROLOG_LAEUFT            (1)
#define RL_PROLOG_FERTIG            (2)

#define RL_WEG_BEZAHLT              (1)
#define RL_WEG_PARTNER              (2)
#define RL_WEG_VERPRUEGELT          (3)     // Schulden halbiert, dann bezahlt
#define RL_WEG_GESTOHLEN            (4)
#define RL_WEG_AUSGELIEFERT         (5)

#define RL_METZGER_NEUTRAL          (0)
#define RL_METZGER_PARTNER          (1)
#define RL_METZGER_RESPEKT          (2)
#define RL_METZGER_FEIND            (3)
#define RL_METZGER_FREUND           (4)

#define RL_ESSIE_DA                 (0)
#define RL_ESSIE_AUSGELIEFERT       (1)
#define RL_ESSIE_GEKUENDIGT         (2)

#define RL_KOLBE_GEWONNEN           (1)     // Faustkampf gewonnen
#define RL_KOLBE_VERLOREN           (2)     // Faustkampf verloren
#define RL_KOLBE_SPEECH             (4)     // Ueberreden versucht
#define RL_KOLBE_RABATT             (8)     // Barter-Rabatt erhalten
#define RL_KOLBE_BARTER             (16)    // Handeln versucht
#define RL_KOLBE_DIEBSTAHL          (32)    // Diebstahl versucht

#define RL_KETTEN_ZWEIG_FLUCHT      (1)
#define RL_KETTEN_ZWEIG_TYRANN      (2)

#define RL_SCHULDEN_START           (1200)
#define RL_ZINS_JE_WOCHE            (50)

// Enden der Questlines (Werte in RL_W_KETTEN / RL_W_VIRGIN ab 10)
#define RL_KETTEN_NEUER_METZGER     (10)
#define RL_KETTEN_METZGERS_MANN     (11)
#define RL_KETTEN_GILDE_FAELLT      (12)
#define RL_KETTEN_STILLER_KRIEG     (13)
#define RL_VIRGIN_UMARMUNG          (10)
#define RL_VIRGIN_LEERER_STUHL      (11)
#define RL_VIRGIN_WAFFENSTILLSTAND  (12)

#define RL_MARCUS_KEIN              (0)
#define RL_MARCUS_RELAIS            (1)     // Verluste -50 %
#define RL_MARCUS_ESKORTE           (2)     // Verluste -75 %
#define RL_MARCUS_GESPERRT          (3)     // Umweg, Verluste +25 %

#define RL_LIGA_KEINE               (0)
#define RL_LIGA_KAMPAGNE            (1)     // -15 %
#define RL_LIGA_GEBREMST            (2)     // -5 %
#define RL_LIGA_GEGENKAMPAGNE       (3)     // -10 %
#define RL_LIGA_LEX_NEUN            (4)     // +20 %
#define RL_LIGA_VERBOT              (5)     // Haus illegal
#define RL_LIGA_ZERSCHLAGEN         (6)     // Diskreditierung (normale Nachfrage)

// Preisstufen und Anteilsstufen
#define RL_PREIS_RAMSCH             (0)
#define RL_PREIS_STANDARD           (1)
#define RL_PREIS_GEHOBEN            (2)
#define RL_PREIS_EXKLUSIV           (3)

#define RL_ANTEIL_AUSBEUTERISCH     (0)
#define RL_ANTEIL_BRANCHENUEBLICH   (1)
#define RL_ANTEIL_FAIR              (2)

// Ereignisse (Phase 4)
#define RL_EV_KEINS                 (0)
#define RL_EV_SOLDATEN              (1)
#define RL_EV_STOFF                 (2)
#define RL_EV_RAZZIA                (3)
#define RL_EV_FREIER                (4)
#define RL_EV_SEUCHE                (5)
#define RL_EV_KASSE                 (6)
#define RL_EV_FLUCHT                (7)

// Stadtwerte (rl_stadt)
#define RL_S_KUNDEN                 (0)
#define RL_S_PREIS                  (1)
#define RL_S_TRIBUT                 (2)
#define RL_S_BESTECHUNG             (3)
#define RL_S_RISIKO                 (4)
#define RL_S_KAUFKRAFT              (5)     // 0 arm, 1 mittel, 2 reich

// Feste Werte aus Phase 1/2
#define RL_VERBRAUCH_JE_KUNDE       (3)
#define RL_UNTERHALT_JE_STUFE       (25)
#define RL_BAR_JE_KUNDE             (5)
#define RL_KUNDEN_JE_ZIMMER         (12)
#define RL_FLUCHT_MORAL             (25)
#define RL_FLUCHT_KOSTEN            (30)
#define RL_SEKUNDEN_WOCHE           (604800)
#define RL_MAX_NACHRECHNUNG         (12)

/* ------------------------------------------------------------------ */
/* Hilfsfunktionen                                                     */
/* ------------------------------------------------------------------ */
#define rl_idx(h, f)                ((h) * RL_FELDER + (f))
#define rl_min(a, b)                (((a) < (b)) * (a) + ((a) >= (b)) * (b))
#define rl_max(a, b)                (((a) > (b)) * (a) + ((a) <= (b)) * (b))

#include "rl_katalog.h"

procedure rl_clamp(variable v, variable lo, variable hi);
procedure rl_fdiv(variable a, variable b);
procedure rl_bit(variable n);
procedure rl_woche_jetzt;
procedure rl_bau_fertig(variable haus, variable h);
procedure rl_lade_haeuser;
procedure rl_lade_welt;
procedure rl_stadt(variable stadt, variable was);
procedure rl_haus_uebernehmen(variable haus, variable welt, variable h);
procedure rl_rechne_woche(variable haus, variable h, variable stadt);

procedure rl_clamp(variable v, variable lo, variable hi) begin
   if (v < lo) then return lo;
   if (v > hi) then return hi;
   return v;
end

// Abrundende Division (wie // in Python). SSL schneidet Richtung null ab,
// das macht bei negativen Zaehlern einen Unterschied (Hausruf-Drift).
procedure rl_fdiv(variable a, variable b) begin
   if (a >= 0) then return a / b;
   return -((-a + b - 1) / b);
end

procedure rl_bit(variable n) begin
   variable v := 1;
   while (n > 0) do begin
      v := v * 2;
      n := n - 1;
   end
   return v;
end

procedure rl_woche_jetzt begin
   return game_time_in_seconds / RL_SEKUNDEN_WOCHE;
end

/* Fertigstellung einer Baustelle: Effekte aus dem Katalog anwenden (Phase 2).
   Vorlaeufig werden neue Zimmer sofort besetzt, bis die Anwerbung (Phase 4)
   umgesetzt ist. */
procedure rl_bau_fertig(variable haus, variable h) begin
   variable id := haus[rl_idx(h, RL_F_BAU_ID)] - 1;
   if (id < 0) then return;
   haus[rl_idx(h, RL_F_KLASSE)]         := haus[rl_idx(h, RL_F_KLASSE)] + rl_modul(id, RL_MK_KLASSE);
   haus[rl_idx(h, RL_F_ZIMMER)]         := haus[rl_idx(h, RL_F_ZIMMER)] + rl_modul(id, RL_MK_ZIMMER);
   haus[rl_idx(h, RL_F_PERSONAL)]       := haus[rl_idx(h, RL_F_PERSONAL)] + rl_modul(id, RL_MK_ZIMMER);
   haus[rl_idx(h, RL_F_AUSSTATTUNG)]    := haus[rl_idx(h, RL_F_AUSSTATTUNG)] + rl_modul(id, RL_MK_AUSSTATTUNG);
   haus[rl_idx(h, RL_F_BAR)]            := haus[rl_idx(h, RL_F_BAR)] + rl_modul(id, RL_MK_BAR);
   haus[rl_idx(h, RL_F_SICHERHEIT)]     := haus[rl_idx(h, RL_F_SICHERHEIT)] + rl_modul(id, RL_MK_SICHERHEIT);
   haus[rl_idx(h, RL_F_MORALBONUS)]     := haus[rl_idx(h, RL_F_MORALBONUS)] + rl_modul(id, RL_MK_MORAL);
   haus[rl_idx(h, RL_F_LOEHNE)]         := haus[rl_idx(h, RL_F_LOEHNE)] + rl_modul(id, RL_MK_LOEHNE);
   haus[rl_idx(h, RL_F_MODULE)]         := haus[rl_idx(h, RL_F_MODULE)] bwor rl_modul(id, RL_MK_FLAGS);
   haus[rl_idx(h, RL_F_NEBEN)]          := haus[rl_idx(h, RL_F_NEBEN)] + rl_modul(id, RL_MK_NEBEN);
   haus[rl_idx(h, RL_F_MODUL_STADTMOD)] := haus[rl_idx(h, RL_F_MODUL_STADTMOD)] + rl_modul(id, RL_MK_STADTMOD);
   haus[rl_idx(h, RL_F_TRIBUTMOD)]      := haus[rl_idx(h, RL_F_TRIBUTMOD)] + rl_modul(id, RL_MK_TRIBUT);
   haus[rl_idx(h, RL_F_STUFEN)]         := haus[rl_idx(h, RL_F_STUFEN)] + rl_modul(id, RL_MK_STUFEN);
   haus[rl_idx(h, RL_F_BAU_ID)]         := 0;
   haus[rl_idx(h, RL_F_BAU_WOCHEN)]     := 0;
end

/* Laedt das Haus-Array oder legt es an. Stammt es aus einer aelteren Version
   mit weniger Feldern pro Haus, werden die Werte in das neue Layout kopiert. */
procedure rl_lade_haeuser begin
   variable arr, alt, alt_felder, h, f;
   arr := load_array(RL_ARR_HAEUSER);
   if (arr == 0) then begin
      arr := create_array(RL_SLOTS * RL_FELDER, 0);
      save_array(RL_ARR_HAEUSER, arr);
   end else if (len_array(arr) < RL_SLOTS * RL_FELDER) then begin
      alt := arr;
      alt_felder := len_array(alt) / RL_SLOTS;
      arr := create_array(RL_SLOTS * RL_FELDER, 0);
      h := 0;
      while (h < RL_SLOTS) do begin
         f := 0;
         while (f < alt_felder) do begin
            arr[h * RL_FELDER + f] := get_array(alt, h * alt_felder + f);
            f := f + 1;
         end
         h := h + 1;
      end
      save_array(RL_ARR_HAEUSER, arr);
      free_array(alt);
   end
   return arr;
end

procedure rl_lade_welt begin
   variable arr;
   arr := load_array(RL_ARR_WELT);
   if (arr == 0) then begin
      arr := create_array(RL_WELT_FELDER, 0);
      save_array(RL_ARR_WELT, arr);
   end
   return arr;
end

// Stadtprofile aus Phase 1 (Index 6 = Testhaus mit New-Reno-Werten)
procedure rl_stadt(variable stadt, variable was) begin
   variable werte;
   if (was == RL_S_KUNDEN) then
      werte := [30, 55, 35, 15, 45, 40, 55];
   else if (was == RL_S_PREIS) then
      werte := [20, 25, 20, 70, 22, 30, 25];
   else if (was == RL_S_TRIBUT) then
      werte := [10, 20, 0, 0, 15, 10, 20];
   else if (was == RL_S_BESTECHUNG) then
      werte := [0, 0, 75, 200, 0, 0, 0];
   else if (was == RL_S_RISIKO) then
      werte := [4, 3, 3, 5, 1, 2, 3];
   else
      werte := [0, 1, 1, 2, 1, 1, 1];
   return get_array(werte, stadt);
end

// Startzustand nach der Uebernahme (Hausklasse 1, Phase 2 Abschnitt 3)
procedure rl_haus_uebernehmen(variable haus, variable welt, variable h) begin
   variable zimmer := 3;
   if (h == RL_VAULT_CITY) then zimmer := 2;
   haus[rl_idx(h, RL_F_BESITZ)]     := 1;
   haus[rl_idx(h, RL_F_KLASSE)]     := 1;
   haus[rl_idx(h, RL_F_ZIMMER)]     := zimmer;
   haus[rl_idx(h, RL_F_PERSONAL)]   := zimmer;
   haus[rl_idx(h, RL_F_QUALI)]      := 50;
   haus[rl_idx(h, RL_F_MORAL)]      := 50;
   haus[rl_idx(h, RL_F_RUF)]        := 35;
   haus[rl_idx(h, RL_F_AUSSTATTUNG)]:= 20;
   haus[rl_idx(h, RL_F_SICHERHEIT)] := 45;
   haus[rl_idx(h, RL_F_PREISSTUFE)] := RL_PREIS_STANDARD;
   haus[rl_idx(h, RL_F_ANTEIL)]     := RL_ANTEIL_BRANCHENUEBLICH;
   haus[rl_idx(h, RL_F_STUFEN)]     := 1;
   haus[rl_idx(h, RL_F_LOEHNE)]     := 80;
   haus[rl_idx(h, RL_F_FUEHRUNG)]   := 40;
   if (welt[RL_W_AKTIV] == 0) then begin
      welt[RL_W_AKTIV] := 1;
      welt[RL_W_WOCHE] := rl_woche_jetzt;
   end
end

/* ------------------------------------------------------------------ */
/* Wochenrechnung eines Hauses                                         */
/* Entspricht tools/economy_sim.py:simulate() + Kapazitaet, VIP, Krise */
/* Gibt den Gewinn zurueck und schreibt den neuen Zustand ins Array.   */
/* ------------------------------------------------------------------ */
procedure rl_rechne_woche(variable haus, variable h, variable stadt) begin
   variable moral, quali, ruf, ausstattung, sicherheit, hitze;
   variable preisstufe, anteilstufe, module;
   variable preis_prozent, nachfrage, ruf_tick, anteil, moral_tick, moral_cap, karma_tick;
   variable q_eff, score, attraktiv, bedrohung, sicher_faktor, v, kunden, kapazitaet;
   variable umsatz_dienst, umsatz_neben, umsatz, schwund, tribut, kosten, gewinn;
   variable vip_kunden, vip_umsatz, basispreis, krise_faktor;

   moral       := haus[rl_idx(h, RL_F_MORAL)];
   quali       := haus[rl_idx(h, RL_F_QUALI)];
   ruf         := haus[rl_idx(h, RL_F_RUF)];
   ausstattung := rl_min(100, haus[rl_idx(h, RL_F_AUSSTATTUNG)]);
   sicherheit  := haus[rl_idx(h, RL_F_SICHERHEIT)];
   hitze       := haus[rl_idx(h, RL_F_HITZE)];
   preisstufe  := haus[rl_idx(h, RL_F_PREISSTUFE)];
   anteilstufe := haus[rl_idx(h, RL_F_ANTEIL)];
   module      := haus[rl_idx(h, RL_F_MODULE)];
   basispreis  := rl_stadt(stadt, RL_S_PREIS);

   // Preisstufe (Phase 1, Abschnitt 3.6)
   preis_prozent := get_array([60, 100, 150, 250], preisstufe);
   ruf_tick      := get_array([-1, 0, 1, 2], preisstufe);
   if (preisstufe == RL_PREIS_RAMSCH) then
      nachfrage := get_array([140, 140, 100], rl_stadt(stadt, RL_S_KAUFKRAFT));
   else if (preisstufe == RL_PREIS_STANDARD) then
      nachfrage := 100;
   else if (preisstufe == RL_PREIS_GEHOBEN) then
      nachfrage := get_array([50, 70, 85], rl_stadt(stadt, RL_S_KAUFKRAFT));
   else
      nachfrage := get_array([20, 40, 60], rl_stadt(stadt, RL_S_KAUFKRAFT));

   // Personal-Anteil mit Moral-Obergrenze (Phase 1 + Phase 2 Abschnitt 5.2)
   anteil     := get_array([25, 35, 45], anteilstufe);
   moral_tick := get_array([-4, 0, 3], anteilstufe);
   karma_tick := get_array([-1, 0, 0], anteilstufe);
   moral_cap  := get_array([50, 70, 100], anteilstufe);
   if (module bwand RL_MOD_LEINE) then begin
      moral_cap  := rl_min(moral_cap, 40);
      karma_tick := karma_tick - 3;
   end

   // Attraktivitaet
   q_eff     := quali * (40 + 8 * moral / 10) / 100;
   score     := (50 * q_eff + 30 * ausstattung + 20 * ruf) / 100;
   attraktiv := 40 + score * 2;

   // Sicherheit gegen Bedrohung
   bedrohung := rl_stadt(stadt, RL_S_RISIKO) * 20 + hitze;
   if (sicherheit >= bedrohung) then
      sicher_faktor := 100;
   else
      sicher_faktor := rl_max(60, 100 - (bedrohung - sicherheit) / 2);

   // Kunden: schrittweise teilen, Zwischenwerte bleiben unter 3 Mio.
   v := rl_stadt(stadt, RL_S_KUNDEN) * attraktiv;
   v := v * nachfrage / 100;
   v := v * sicher_faktor / 100;
   v := v * (100 + haus[rl_idx(h, RL_F_STADTMOD)] + haus[rl_idx(h, RL_F_MODUL_STADTMOD)]) / 100;
   kunden := v / 100;

   // Kapazitaet: ein Zimmer braucht eine Person (Phase 4)
   kapazitaet := rl_min(haus[rl_idx(h, RL_F_ZIMMER)], haus[rl_idx(h, RL_F_PERSONAL)]) * RL_KUNDEN_JE_ZIMMER;
   kunden := rl_min(kunden, kapazitaet);

   // Baustelle: halbe Kundschaft (Phase 2, Abschnitt 3)
   if (haus[rl_idx(h, RL_F_BAU_ID)] and (haus[rl_idx(h, RL_F_BAU_WOCHEN)] > 0)) then
      kunden := kunden * 50 / 100;

   // Offene Krise: -20 % Kunden je Woche, hoechstens -60 % (Phase 4)
   if (haus[rl_idx(h, RL_F_KRISE)] != RL_EV_KEINS) then begin
      krise_faktor := 100 - 20 * rl_min(3, haus[rl_idx(h, RL_F_KRISENWOCHEN)] + 1);
      kunden := kunden * krise_faktor / 100;
   end

   // Umsatz
   umsatz_dienst := kunden * basispreis * preis_prozent / 100;
   umsatz_neben  := kunden * (RL_BAR_JE_KUNDE * haus[rl_idx(h, RL_F_BAR)] + haus[rl_idx(h, RL_F_NEBEN)]);
   umsatz        := umsatz_dienst + umsatz_neben;

   // Kosten
   if (module bwand RL_MOD_KONTOR) then schwund := 4; else schwund := 10;
   schwund := schwund + rl_max(0, 40 - moral) / 3;
   if (moral >= 70) then schwund := schwund - 2;
   tribut  := rl_max(0, rl_stadt(stadt, RL_S_TRIBUT) + haus[rl_idx(h, RL_F_TRIBUTMOD)]);

   kosten := umsatz_dienst * anteil / 100
           + haus[rl_idx(h, RL_F_LOEHNE)]
           + kunden * RL_VERBRAUCH_JE_KUNDE
           + haus[rl_idx(h, RL_F_STUFEN)] * RL_UNTERHALT_JE_STUFE
           + umsatz * tribut / 100
           + rl_stadt(stadt, RL_S_BESTECHUNG)
           + umsatz * schwund / 100;
   if (moral < RL_FLUCHT_MORAL) then kosten := kosten + RL_FLUCHT_KOSTEN;
   gewinn := umsatz - kosten;

   // VIP-Trakt: eigene Kundschaft zum dreifachen Preis ab Moral 65 (Phase 2)
   if ((module bwand RL_MOD_VIP) and (moral >= 65)) then begin
      vip_kunden := get_array([0, 10, 0, 2, 6, 5, 0], stadt);
      vip_umsatz := vip_kunden * basispreis * 3;
      if (module bwand RL_MOD_KONTOR) then schwund := 4; else schwund := 10;
      gewinn := gewinn + vip_umsatz * (100 - anteil - tribut - schwund) / 100
                       - vip_kunden * RL_VERBRAUCH_JE_KUNDE * 2;
   end

   // Zustand fortschreiben (gleiche Reihenfolge wie im Simulator)
   if (module bwand RL_MOD_KRANKENSTUBE) then moral_tick := moral_tick + 1;
   moral_tick := moral_tick + haus[rl_idx(h, RL_F_MORALBONUS)];
   moral := rl_clamp(moral + moral_tick, 0, rl_max(moral, moral_cap));

   ruf := ruf + rl_fdiv(score - ruf, 8) + ruf_tick;
   if (moral >= 70) then ruf := ruf + 1;
   if (moral < 30) then ruf := ruf - 2;
   ruf := rl_clamp(ruf, 0, 100);

   if (moral < RL_FLUCHT_MORAL) then quali := rl_max(20, quali - 2);   // gute Leute hauen ab
   if (moral >= 75) then quali := rl_min(85, quali + 1);               // Talent-Zulauf

   haus[rl_idx(h, RL_F_MORAL)]   := moral;
   haus[rl_idx(h, RL_F_RUF)]     := ruf;
   haus[rl_idx(h, RL_F_QUALI)]   := quali;
   haus[rl_idx(h, RL_F_HITZE)]   := rl_max(0, hitze - 5);
   haus[rl_idx(h, RL_F_KUNDEN)]  := kunden;
   haus[rl_idx(h, RL_F_GEWINN)]  := gewinn;

   // Karma: Ausbeutung -1/Woche, Zwangspersonal zusaetzlich -5/Woche (Phase 2/4)
   if (haus[rl_idx(h, RL_F_ZWANG)]) then karma_tick := karma_tick - 5;
   if ((karma_tick != 0) and (h != RL_TESTHAUS)) then
      set_global_var(GVAR_PLAYER_REPUTATION, global_var(GVAR_PLAYER_REPUTATION) + karma_tick);

   return gewinn;
end

#endif
