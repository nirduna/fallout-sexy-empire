/*
   rl_ncr.h - NCR: Die Traenke und "Die Reinen" (Phase 2 Abschnitt 2.5,
   Phase 3 Abschnitte 2.5 und 3.3, Phase 4 Abschnitt 2.3). Umsetzung 10.

   "Etablissement Nr. 9": Inspektorin Grieve vom Lizenzamt des Rats sitzt in
   der leeren Nr. 9. Vier Wege zur Lizenz:
     Dienstweg      500 $ (Bishop-Pate: 250 $), 3 Wochen Wartezeit
     beschleunigt   dazu Barter 40 und 300 $: 1 Woche, H +5
     Westin         Speech 60 (nur, solange Westin lebt): sofort, Tribut +5, E +10
     ohne Lizenz    sofort, aber illegal (Risiko +3), H +30, "Die Reinen" beginnt sofort
   Auflage: eine Krankenstube. Ohne sie ist die Lizenz nach 4 Wochen ausgesetzt.

   Vortis' Angebot (Tyrannen-Route): 200 $ je Person aus dem Pferch als
   Zwangspersonal. Die Rangers finden es mit 5 % + Hitze / 10 je Woche:
   Razzia, Lizenzentzug, die Rangers werden Feinde, die Menschen sind frei.

   "Die Reinen" mit Ruth Calloway (Liga fuer eine reine Republik):
     Akt 1  Flugblaetter: Kampagne -15 %. Calloway reden (Speech 60, mit Maras
            Buergschaft -5 %), Gegenkampagne (Barter 60: -10 %, H +5),
            Streikposten vertreiben (Unarmed 60: keine Kampagne, H +10, K -5, Maertyrer)
     Akt 2  Die Anhoerung: Rede (Speech 80), Stimmen kaufen (Barter 60, 2.000 $,
            20 % Skandal), Westin (Speech 60, oder erpresst mit dem VIP-Trakt).
            Tandi (E >= 60) +10, Registratur und Krankenstube +10, Maertyrer -10.
     Akt 3  Feuer: loeschen (Repair 60 oder Traps 60), sonst 4 Wochen -40 %.
            Ermitteln: Science 60, Speech 60 oder CH 6, Sneak 60 und Lockpick 60.
     Akt 4  Beweise: den Rangers, Vortis erpressen (150 $/Woche), der Liga
            anhaengen (Science 60, K -30).
     Akt 5  Enden: Musterhaus (Lex Neun), Diskreditierung, Verbot, gescheitert.

   Wird am Ende von rotlicht.h eingebunden.
*/
#ifndef RL_NCR_H
#define RL_NCR_H

#define RL_LIZENZ_NCR_KEINE         (0)
#define RL_LIZENZ_NCR_DIENSTWEG     (1)
#define RL_LIZENZ_NCR_SCHNELL       (2)
#define RL_LIZENZ_NCR_WESTIN        (3)
#define RL_LIZENZ_NCR_OHNE          (4)

// Aktstand in RL_W_REINE (Enden ab 10)
#define RL_REINE_OFFEN              (0)
#define RL_REINE_FLUGBLAETTER       (1)
#define RL_REINE_ANHOERUNG          (2)
#define RL_REINE_FEUER              (3)
#define RL_REINE_BEWEISE            (4)
#define RL_REINE_MUSTERHAUS         (10)
#define RL_REINE_DISKREDITIERUNG    (11)
#define RL_REINE_VERBOT             (12)
#define RL_REINE_GESCHEITERT        (13)    // Anhoerung gewonnen, aber kein Musterhaus: Das Gesetz faellt durch

#define RL_AKT1_OFFEN               (0)
#define RL_AKT1_MARA                (1)
#define RL_AKT1_GEGENKAMPAGNE       (2)
#define RL_AKT1_STREIKPOSTEN        (3)     // Maertyrer: -10 auf die Checks der Anhoerung
#define RL_AKT1_GESCHICHTE          (4)     // Calloway hat erzaehlt, ohne Mara aendert sich nichts

#define RL_ANHOERUNG_OFFEN          (0)
#define RL_ANHOERUNG_GEWONNEN       (1)
#define RL_ANHOERUNG_VERLOREN       (2)

#define RL_BRAND_KEINER             (0)
#define RL_BRAND_BRENNT             (1)
#define RL_BRAND_GELOESCHT          (2)
#define RL_BRAND_ABGEBRANNT         (3)

#define RL_BEWEIS_KEINER            (0)
#define RL_BEWEIS_VORTIS            (1)
#define RL_BEWEIS_FLUEGEL           (2)     // Tyrannen-Zweig: ein radikaler Fluegel der Liga

#define RL_AKT4_OFFEN               (0)
#define RL_AKT4_RANGERS             (1)
#define RL_AKT4_ERPRESST            (2)
#define RL_AKT4_ANGEHAENGT          (3)

#define RL_NCR_TOT_DORA             (1)     // Bits in RL_W_NCR_TOTE
#define RL_NCR_TOT_CALLOWAY         (2)
#define RL_NCR_TOT_GRIEVE           (4)

#define RL_VORTIS_FEIND             (1)     // Werte in RL_W_VORTIS
#define RL_VORTIS_VERHAFTET         (2)

#define RL_NCR_LIZENZ_PREIS         (500)
#define RL_NCR_BESCHLEUNIGT         (300)
#define RL_VORTIS_PREIS             (200)
#define RL_STIMMEN_PREIS            (2000)
#define RL_VORTIS_SCHWEIGEGELD      (150)
#define RL_DORA_FUEHRUNG            (50)
#define RL_OHNE_DORA_FUEHRUNG       (30)
#define RL_REINE_ABSTAND            (2)     // Wochen zwischen den Akten
#define RL_REINE_FRIST              (4)     // so lange wartet ein Akt auf den Spieler
#define RL_AUFLAGE_WOCHEN           (4)     // Krankenstube bis dahin
#define RL_BRAND_WOCHEN             (4)
#define RL_ILLEGAL_RISIKO           (3)     // Risiko 1 -> 4

// Westin lebt noch (Vanilla: GVAR_NEWRENO_SNUFF_WESTIN, WESTIN_DEAD)
#define rl_westin_lebt              ((global_var(GVAR_NEWRENO_SNUFF_WESTIN) bwand bit_2) == 0)

procedure rl_ncr_besitz(variable haus);
procedure rl_ncr_lizenzpreis(variable welt);
procedure rl_ncr_eroeffnen(variable haus, variable welt);
procedure rl_ncr_illegal(variable haus, variable welt);
procedure rl_ncr_mara_buergt(variable welt);
procedure rl_reine_bonus(variable haus, variable welt);
procedure rl_reine_weiter(variable welt, variable akt);
procedure rl_reine_ende(variable haus, variable welt);
procedure rl_ncr_rangers_razzia(variable haus, variable welt);
procedure rl_ncr_figuren(variable haus, variable welt);

procedure rl_ncr_besitz(variable haus) begin
   return haus[rl_idx(RL_NCR, RL_F_BESITZ)];
end

// Bishop als Pate: Lizenz -50 % (Phase 1, Tabelle der Paten)
procedure rl_ncr_lizenzpreis(variable welt) begin
   if (welt[RL_W_NR_SEGEN] == RL_SEGEN_BISHOP) then return RL_NCR_LIZENZ_PREIS / 2;
   return RL_NCR_LIZENZ_PREIS;
end

/* Die Traenke oeffnet (mit oder ohne Lizenz) */
procedure rl_ncr_eroeffnen(variable haus, variable welt) begin
   variable h := RL_NCR;
   if (rl_ncr_besitz(haus)) then return;
   call rl_haus_uebernehmen(haus, welt, h);
   haus[rl_idx(h, RL_F_FUEHRUNG)] := RL_DORA_FUEHRUNG;
   haus[rl_idx(h, RL_F_EINFLUSS)] := rl_max(haus[rl_idx(h, RL_F_EINFLUSS)], 20);
   welt[RL_W_NCR_OFFEN_WOCHE] := rl_woche_jetzt;
   welt[RL_W_NCR_LIZENZ_WOCHE] := 0;
   // "Die Reinen" beginnt zwei Wochen nach der Eroeffnung, ohne Lizenz sofort
   if (welt[RL_W_REINE] == RL_REINE_OFFEN) then begin
      if (welt[RL_W_NCR_LIZENZ] == RL_LIZENZ_NCR_OHNE) then begin
         welt[RL_W_REINE] := RL_REINE_FLUGBLAETTER;
         welt[RL_W_REINE_WOCHE] := rl_woche_jetzt;
         welt[RL_W_LIGA] := RL_LIGA_KAMPAGNE;
      end else
         welt[RL_W_REINE_WOCHE] := rl_woche_jetzt + RL_REINE_ABSTAND;     // immer > 0: geplant
   end
end

/* Illegal: ohne Lizenz, entzogen, verboten, oder die Auflage (Krankenstube) nicht erfuellt */
procedure rl_ncr_illegal(variable haus, variable welt) begin
   if (welt[RL_W_NCR_LIZENZ] == RL_LIZENZ_NCR_OHNE) then return 1;
   if (welt[RL_W_NCR_ENTZOGEN]) then return 1;
   if (welt[RL_W_REINE] == RL_REINE_VERBOT) then return 1;
   if (((haus[rl_idx(RL_NCR, RL_F_MODULE)] bwand RL_MOD_KRANKENSTUBE) == 0)
       and (rl_woche_jetzt >= welt[RL_W_NCR_OFFEN_WOCHE] + RL_AUFLAGE_WOCHEN)) then return 2;
   return 0;
end

// Hat der Spieler Mara gerettet? Dann buergt sie bei Calloway (Phase 3, 3.3)
procedure rl_ncr_mara_buergt(variable welt) begin
   variable m := welt[RL_W_MARA_WEG];
   return ((m == RL_MARA_SICHER) or (m == RL_MARA_ZURUECK) or (m == RL_MARA_MADAME));
end

// Bonus auf die Checks der Anhoerung
procedure rl_reine_bonus(variable haus, variable welt) begin
   variable b := 0, module := haus[rl_idx(RL_NCR, RL_F_MODULE)];
   if (haus[rl_idx(RL_NCR, RL_F_EINFLUSS)] >= 60) then b := b + 10;             // Tandis Buero
   if ((module bwand RL_MOD_REGISTRATUR) and (module bwand RL_MOD_KRANKENSTUBE)) then b := b + 10;
   if (welt[RL_W_REINE_AKT1] == RL_AKT1_STREIKPOSTEN) then b := b - 10;       // die Liga hat Maertyrer
   if (welt[RL_W_KITTY_RIVALIN]) then b := b - 10;                            // Kitty sagt gegen dich aus
   return b;
end

procedure rl_reine_weiter(variable welt, variable akt) begin
   welt[RL_W_REINE] := akt;
   welt[RL_W_REINE_WOCHE] := rl_woche_jetzt;
end

/* Akt 5: das Ende aus dem, was geschehen ist (Phase 3, 3.3) */
procedure rl_reine_ende(variable haus, variable welt) begin
   variable a4 := welt[RL_W_REINE_AKT4];
   if ((a4 == RL_AKT4_ANGEHAENGT) or (a4 == RL_AKT4_ERPRESST)) then begin
      welt[RL_W_REINE] := RL_REINE_DISKREDITIERUNG;
      welt[RL_W_LIGA]  := RL_LIGA_ZERSCHLAGEN;
   end else if ((a4 == RL_AKT4_RANGERS) and (haus[rl_idx(RL_NCR, RL_F_MORAL)] >= 60)
                and (global_var(GVAR_REPUTATION_SLAVER) == 0)) then begin
      welt[RL_W_REINE] := RL_REINE_MUSTERHAUS;
      welt[RL_W_LIGA]  := RL_LIGA_LEX_NEUN;
   end else if (welt[RL_W_REINE_ANHOERUNG] == RL_ANHOERUNG_GEWONNEN) then begin
      welt[RL_W_REINE] := RL_REINE_GESCHEITERT;
      welt[RL_W_LIGA]  := RL_LIGA_GEBREMST;
   end else begin
      welt[RL_W_REINE] := RL_REINE_VERBOT;
      welt[RL_W_LIGA]  := RL_LIGA_VERBOT;
      call rl_haus_plus(haus, RL_NCR, RL_F_HITZE, 30);
   end
   welt[RL_W_REINE_WOCHE] := rl_woche_jetzt;
end

/* Die Rangers finden Vortis' Leute: Razzia, Lizenzentzug, Feindschaft, Freiheit */
procedure rl_ncr_rangers_razzia(variable haus, variable welt) begin
   variable h := RL_NCR, n := haus[rl_idx(h, RL_F_ZWANG)];
   haus[rl_idx(h, RL_F_ZWANG)]    := 0;
   haus[rl_idx(h, RL_F_PERSONAL)] := rl_max(0, haus[rl_idx(h, RL_F_PERSONAL)] - n);
   welt[RL_W_NCR_ENTZOGEN] := 1;
   welt[RL_W_RANGERS] := RL_RANGERS_FEIND;
   call rl_haus_plus(haus, h, RL_F_HITZE, 30);
   call rl_haus_plus(haus, h, RL_F_EINFLUSS, -20);
end

/* Figuren in der Traenke: vor der Eroeffnung die Inspektorin, danach Dora;
   Calloway in den Akten 1 und 2 */
procedure rl_ncr_figuren(variable haus, variable welt) begin
   variable tote := welt[RL_W_NCR_TOTE];
   if ((not rl_ncr_besitz(haus)) and ((tote bwand RL_NCR_TOT_GRIEVE) == 0)) then
      call rl_figur(PID_AVERAGE_PEASANT_FEMALE, rl_haus_platz(RL_NCR, RL_PLATZ_GAST1), SCRIPT_RLGRIEVE);
   if (rl_ncr_besitz(haus) and ((tote bwand RL_NCR_TOT_DORA) == 0)) then
      call rl_figur(PID_AVERAGE_PEASANT_FEMALE, rl_haus_platz(RL_NCR, RL_PLATZ_MADAME), SCRIPT_RLDORA);
   if (((welt[RL_W_REINE] == RL_REINE_FLUGBLAETTER) or (welt[RL_W_REINE] == RL_REINE_ANHOERUNG))
       and ((tote bwand RL_NCR_TOT_CALLOWAY) == 0)) then
      call rl_figur(PID_STRONG_PEASANT_FEMALE, rl_haus_platz(RL_NCR, RL_PLATZ_GAST2), SCRIPT_RLCALLOWAY);
end

#endif
