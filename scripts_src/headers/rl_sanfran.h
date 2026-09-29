/*
   rl_sanfran.h - San Francisco: Die Bilge (Phase 2 Abschnitt 2.6, Phase 3
   Abschnitte 2.6 und 4.3, Phase 4 Abschnitte 2.3 und 4.2). Umsetzung 11.

   "Die Duldung": Aufseher Wen verwaltet fuer die Shi die Docks.
     Wens Angebot     15 % Tribut
     Augen der Shi    die Bilge meldet, wer an den Docks ein- und ausgeht:
                      10 %, das Siegel der Shi wird verfuegbar. Die Tanker-Leute
                      merken es irgendwann (je Woche 15 % - Sneak / 10, mindestens 2 %):
                      H +10, Kunden -10 %
     Tribut druecken  Barter 60: 10 % ohne Spitzeldienste; das Siegel erst nach
                      einem spaeteren Gefallen (PE 7 oder Sneak 60)
     Tanker           Speech 60 beim Bootsmann: kein Tribut, keine Duldung,
                      H +15, die Schmuggelkammer sofort
   Mit der Duldung (oder dem Tanker im Ruecken) gehoert die Bilge dem Spieler.

   Die Schmuggelkammer (Sondermodul): Nebenumsatz +3 $, H +10. Die Shi werden
   misstrauisch: Razzien der Shi-Inspektoren. Finden sie die Kammer, steigt
   der Tribut um 5 Punkte, das Siegel wird entzogen, die Kammer beschlagnahmt.

   Die Hubologen (Phase 3, 4.3) ueber Madame Kwan: entlarven (Science 70),
   unterwandern (Speech 60), Absprache (Barter 60, K -20: Schuldner als
   Zwangspersonal, 100 $ je Schuldschein). Fliegen sie in Vanilla davon, entfaellt
   der Abzug.

   Wird am Ende von rotlicht.h eingebunden.
*/
#ifndef RL_SANFRAN_H
#define RL_SANFRAN_H

#define RL_DULDUNG_KEINE            (0)
#define RL_DULDUNG_TRIBUT           (1)     // 15 %
#define RL_DULDUNG_SPITZEL          (2)     // 10 %, Augen der Shi
#define RL_DULDUNG_BARTER           (3)     // 10 %
#define RL_DULDUNG_TANKER           (4)     // kein Tribut, keine Duldung

#define RL_HUBOLOGEN_OFFEN          (0)
#define RL_HUBOLOGEN_ENTLARVT       (1)
#define RL_HUBOLOGEN_UNTERWANDERT   (2)
#define RL_HUBOLOGEN_ABSPRACHE      (3)

#define RL_SF_TOT_KWAN              (1)     // Bits in RL_W_SF_TOTE
#define RL_SF_TOT_WEN               (2)
#define RL_SF_TOT_BOOTSMANN         (4)

#define RL_KWAN_FUEHRUNG            (50)
#define RL_OHNE_KWAN_FUEHRUNG       (30)
#define RL_SCHULDSCHEIN_PREIS       (100)

// Vanilla: Die Hubologen fliegen mit dem betankten Schiff davon (SF_GAS_ELRONS)
#define rl_hubologen_weg            ((global_var(GVAR_SAN_FRAN_FLAGS) bwand bit_16) != 0)

procedure rl_sf_besitz(variable haus);
procedure rl_sf_duldung(variable haus, variable welt, variable weg);
procedure rl_sf_razzia(variable haus, variable welt);
procedure rl_sf_figuren(variable haus, variable welt);

procedure rl_sf_besitz(variable haus) begin
   return haus[rl_idx(RL_SAN_FRAN, RL_F_BESITZ)];
end

/* Die Duldung (oder der Tanker): Die Bilge gehoert dem Spieler. Grundtribut 10 %. */
procedure rl_sf_duldung(variable haus, variable welt, variable weg) begin
   variable h := RL_SAN_FRAN;
   if (welt[RL_W_SF_DULDUNG] != RL_DULDUNG_KEINE) then return;
   welt[RL_W_SF_DULDUNG] := weg;
   call rl_haus_uebernehmen(haus, welt, h);
   haus[rl_idx(h, RL_F_FUEHRUNG)] := RL_KWAN_FUEHRUNG;
   haus[rl_idx(h, RL_F_EINFLUSS)] := rl_max(haus[rl_idx(h, RL_F_EINFLUSS)], 20);
   if (weg == RL_DULDUNG_TRIBUT) then
      haus[rl_idx(h, RL_F_TRIBUTMOD)] := haus[rl_idx(h, RL_F_TRIBUTMOD)] + 5;
   else if (weg == RL_DULDUNG_SPITZEL) then
      welt[RL_W_SHI_GEFALLEN] := 1;
   else if (weg == RL_DULDUNG_TANKER) then begin
      haus[rl_idx(h, RL_F_TRIBUTMOD)] := haus[rl_idx(h, RL_F_TRIBUTMOD)] - 10;
      call rl_haus_plus(haus, h, RL_F_HITZE, 15);
      welt[RL_W_SF_LAGER] := 1;
   end
end

/* Die Inspektoren der Shi finden die Schmuggelkammer (Phase 4, 4.2) */
procedure rl_sf_razzia(variable haus, variable welt) begin
   variable h := RL_SAN_FRAN, siegel := RL_M_SF_SHI_SIEGEL;
   haus[rl_idx(h, RL_F_TRIBUTMOD)] := haus[rl_idx(h, RL_F_TRIBUTMOD)] + 5;
   // Das Siegel wird entzogen (auch eine laufende Baustelle)
   if (haus[rl_idx(h, RL_F_GEKAUFT)] bwand rl_bit(siegel)) then begin
      haus[rl_idx(h, RL_F_GEKAUFT)] := haus[rl_idx(h, RL_F_GEKAUFT)] - rl_bit(siegel);
      if (haus[rl_idx(h, RL_F_BAU_ID)] == siegel + 1) then begin
         haus[rl_idx(h, RL_F_BAU_ID)] := 0;
         haus[rl_idx(h, RL_F_BAU_WOCHEN)] := 0;
      end else begin
         haus[rl_idx(h, RL_F_TRIBUTMOD)]  := haus[rl_idx(h, RL_F_TRIBUTMOD)] - rl_modul(siegel, RL_MK_TRIBUT);
         haus[rl_idx(h, RL_F_SICHERHEIT)] := rl_max(0, haus[rl_idx(h, RL_F_SICHERHEIT)] - rl_modul(siegel, RL_MK_SICHERHEIT));
         haus[rl_idx(h, RL_F_STUFEN)]     := rl_max(0, haus[rl_idx(h, RL_F_STUFEN)] - 1);
      end
   end
   welt[RL_W_SHI_GEFALLEN] := 0;
   // Die Kammer wird beschlagnahmt
   haus[rl_idx(h, RL_F_MODULE)] := haus[rl_idx(h, RL_F_MODULE)] - RL_MOD_SCHMUGGEL;
   haus[rl_idx(h, RL_F_NEBEN)]  := rl_max(0, haus[rl_idx(h, RL_F_NEBEN)] - 3);
   haus[rl_idx(h, RL_F_STUFEN)] := rl_max(0, haus[rl_idx(h, RL_F_STUFEN)] - 1);
   call rl_haus_plus(haus, h, RL_F_EINFLUSS, -10);
end

/* Figuren in der Bilge: Wen und der Bootsmann immer, Kwan nach der Uebernahme */
procedure rl_sf_figuren(variable haus, variable welt) begin
   variable tote := welt[RL_W_SF_TOTE];
   if ((tote bwand RL_SF_TOT_WEN) == 0) then
      call rl_figur(PID_AVERAGE_PEASANT_MALE, rl_haus_platz(RL_SAN_FRAN, RL_PLATZ_GAST1), SCRIPT_RLWEN);
   if ((tote bwand RL_SF_TOT_BOOTSMANN) == 0) then
      call rl_figur(PID_TOUGH_THUG_MALE, rl_haus_platz(RL_SAN_FRAN, RL_PLATZ_GAST2), SCRIPT_RLBOOTSMANN);
   if (rl_sf_besitz(haus) and ((tote bwand RL_SF_TOT_KWAN) == 0)) then
      call rl_figur(PID_AVERAGE_PEASANT_FEMALE, rl_haus_platz(RL_SAN_FRAN, RL_PLATZ_MADAME), SCRIPT_RLKWAN);
end

#endif
