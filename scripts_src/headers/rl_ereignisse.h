/*
   rl_ereignisse.h - Ereignisse vollstaendig (Phase 4, Abschnitte 4.2 und 4.3). Umsetzung 15.

   Gemeinsam genutzt vom globalen Skript (Wochenwurf, Eskalation, Razzia) und
   von allen Madames (Loesungswege im Krisenmenue, rl_manager.h).

   Razzien je Stadt (4.2):
     The Den      Maenner der Sklavengilde suchen Fluechtlinge (Mara, die Transporte)
     New Reno     "Besuch" einer Familie: Schaeden (Kasse -200), E -10
     Redding      Sheriff Marion sucht die gezinkte Waage und das Schutzgeld
     NCR          Polizei (illegal: 500 $ Strafe), Rangers (Zwangspersonal)
     Vault City, San Francisco: seit Umsetzung 9 und 11
   Angekuendigt (E >= 60 oder bestochen: Tyler, Polizist) wird die Razzia eine
   Woche vorher zur Krise; wer die Beweise verschwinden laesst, besteht sie.
   Sonst kommt sie sofort.

   Tod im Haus (4.3): nach einer Ueberdosis, nach Gewalt (Soldaten, Freier)
   und beim Zwangspersonal (Flucht). Beerdigung, Schweigen oder Rache.

   Wird am Ende von rotlicht.h eingebunden, nach rl_jobs.h.
*/
#ifndef RL_EREIGNISSE_H
#define RL_EREIGNISSE_H

// Bits in RL_W_EREIGNIS_FLAGS
#define RL_EF_RICHTER               (1)     // "Der Richter" war schon
#define RL_EF_LEX_VERWIRKT          (2)     // die Inspektion der Liga ist durchgefallen

// Beweise fuer eine Razzia (rl_razzia_beweise)
#define RL_BEWEIS_FLUECHTLINGE      (1)
#define RL_BEWEIS_WAAGE             (2)
#define RL_BEWEIS_SCHUTZGELD        (4)
#define RL_BEWEIS_ILLEGAL           (8)
#define RL_BEWEIS_ZWANG             (16)

#define RL_SOLDATEN_PREIS           (200)
#define RL_SOLDATEN_WIEDER          (4)     // Wochen, bis sie (vielleicht) wiederkommen
#define RL_DESERTEUR_SICHERHEIT     (50)
#define RL_BESUCH_SCHADEN           (200)
#define RL_NCR_STRAFE               (500)
#define RL_BEERDIGUNG_PREIS         (100)
#define RL_ABWERBUNG_GEGENANGEBOT   (100)
#define RL_GEHEIMNIS_PREIS          (200)

procedure rl_krise_setzen(variable haus, variable h, variable typ);
procedure rl_tod_im_haus(variable haus, variable welt, variable h, variable gewalt, variable zwang);
procedure rl_razzia_stadt(variable h);
procedure rl_razzia_angekuendigt(variable haus, variable welt, variable h);
procedure rl_razzia_beweise(variable haus, variable welt, variable h);
procedure rl_razzia_ausfuehren(variable haus, variable welt, variable h);
procedure rl_inspektion(variable haus, variable welt, variable h);
procedure rl_bar2_hier(variable haus, variable h);

// Eine Krise beginnt, wenn im Haus gerade keine ist
procedure rl_krise_setzen(variable haus, variable h, variable typ) begin
   if (haus[rl_idx(h, RL_F_KRISE)] != RL_EV_KEINS) then return 0;
   haus[rl_idx(h, RL_F_KRISE)] := typ;
   haus[rl_idx(h, RL_F_KRISENWOCHEN)] := 0;
   return 1;
end

/* Eine Person stirbt. Die Krise "Tod im Haus" ersetzt die Krise, aus der sie
   kam. Gewalt: Leichen fuer den Totengraeber, Rache ist moeglich. */
procedure rl_tod_im_haus(variable haus, variable welt, variable h, variable gewalt, variable zwang) begin
   variable wer := -1;
   if (zwang) then wer := rl_personal_verlust(haus, h, RL_VERLUST_FLUCHT);
   if (wer < 0) then wer := rl_personal_verlust(haus, h, RL_VERLUST_ABGANG);
   if (wer < 0) then wer := rl_personal_verlust(haus, h, RL_VERLUST_FLUCHT);
   haus[rl_idx(h, RL_F_KRISE)] := RL_EV_TOD;
   haus[rl_idx(h, RL_F_KRISENWOCHEN)] := 0;
   call rl_haus_plus(haus, h, RL_F_MORAL, -10);
   if (gewalt) then begin
      welt[RL_W_TOD_GEWALT] := welt[RL_W_TOD_GEWALT] bwor rl_bit(h);
      welt[RL_W_GEWALT_HAUS] := h + 1;
   end else if (welt[RL_W_TOD_GEWALT] bwand rl_bit(h)) then
      welt[RL_W_TOD_GEWALT] := welt[RL_W_TOD_GEWALT] - rl_bit(h);
end

// Die Staedte mit eigener Razzia in diesem Header (Vault City und San Francisco haben ihre eigene)
procedure rl_razzia_stadt(variable h) begin
   return ((h == RL_DEN) or (h == RL_NEW_RENO) or (h == RL_REDDING) or (h == RL_NCR));
end

// Fruehwarnung: E >= 60 oder eine bestochene Wache (Tyler in der Den, der Polizist in der NCR)
procedure rl_razzia_angekuendigt(variable haus, variable welt, variable h) begin
   if (haus[rl_idx(h, RL_F_EINFLUSS)] >= 60) then return 1;
   if ((h == RL_DEN) and (welt[RL_W_JOBS] bwand RL_JOB_TYLER)) then return 1;
   if ((h == RL_NCR) and (welt[RL_W_JOBS] bwand RL_JOB_POLIZEI)) then return 1;
   return 0;
end

// Was die Razzia finden kann (ohne das, was vor der angekuendigten Razzia beseitigt wurde)
procedure rl_razzia_beweise(variable haus, variable welt, variable h) begin
   variable b := 0, k := welt[RL_W_KETTEN];
   if (welt[RL_W_RAZZIA_VERSTECKT] bwand rl_bit(h)) then return 0;
   if (h == RL_DEN) then begin
      // Fluechtlinge: Mara versteckt oder die Transporte nach Sueden; die Zuflucht verbirgt sie
      if (((haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_ZUFLUCHT) == 0)
          and ((welt[RL_W_MARA_WEG] == RL_MARA_VERSTECKT)
               or ((welt[RL_W_KETTEN_ZWEIG] == RL_KETTEN_ZWEIG_FLUCHT) and (k >= RL_KETTEN_KETTE) and (k <= RL_KETTEN_STURM)))) then
         b := b bwor RL_BEWEIS_FLUECHTLINGE;
   end else if (h == RL_REDDING) then begin
      if (haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_WAAGE_GEZINKT) then b := b bwor RL_BEWEIS_WAAGE;
      if (welt[RL_W_JOBS] bwand RL_JOB_SCHUTZ_RED) then b := b bwor RL_BEWEIS_SCHUTZGELD;
   end else if (h == RL_NCR) then begin
      if (rl_ncr_illegal(haus, welt)) then b := b bwor RL_BEWEIS_ILLEGAL;
      if (haus[rl_idx(h, RL_F_ZWANG)] > 0) then b := b bwor RL_BEWEIS_ZWANG;
   end
   return b;
end

/* Die Razzia kommt. Rueckgabe: Nummer der Meldung in rotlicht.msg */
procedure rl_razzia_ausfuehren(variable haus, variable welt, variable h) begin
   variable b := rl_razzia_beweise(haus, welt, h), verteidigt;
   verteidigt := ((welt[RL_W_RAZZIA_VERSTECKT] bwand rl_bit(h)) != 0);
   if (verteidigt) then welt[RL_W_RAZZIA_VERSTECKT] := welt[RL_W_RAZZIA_VERSTECKT] - rl_bit(h);

   if (h == RL_DEN) then begin
      if (b == 0) then return 252;
      if (welt[RL_W_MARA_WEG] == RL_MARA_VERSTECKT) then welt[RL_W_MARA_WEG] := RL_MARA_VERSCHLEPPT;
      welt[RL_W_METZGER] := RL_METZGER_FEIND;
      call rl_haus_plus(haus, h, RL_F_MORAL, -15);
      return 253;
   end
   if (h == RL_NEW_RENO) then begin
      // Keine Polizei, sondern eine Familie, die Schwaeche sucht
      if (verteidigt) then return 254;
      haus[rl_idx(h, RL_F_KASSE)] := haus[rl_idx(h, RL_F_KASSE)] - RL_BESUCH_SCHADEN;
      call rl_haus_plus(haus, h, RL_F_EINFLUSS, -10);
      return 255;
   end
   if (h == RL_REDDING) then begin
      if (b == 0) then return 256;
      if (b bwand RL_BEWEIS_WAAGE) then call rl_red_revolte(haus, welt);
      if (b bwand RL_BEWEIS_SCHUTZGELD) then begin
         welt[RL_W_JOBS] := welt[RL_W_JOBS] - RL_JOB_SCHUTZ_RED;
         call rl_red_marion_feind(haus, welt);
         call rl_haus_plus(haus, h, RL_F_HITZE, 20);
      end
      return 257;
   end
   if (h == RL_NCR) then begin
      if (b == 0) then return 258;
      if (b bwand RL_BEWEIS_ZWANG) then begin
         call rl_ncr_rangers_razzia(haus, welt);
         return 195;
      end
      haus[rl_idx(h, RL_F_KASSE)] := haus[rl_idx(h, RL_F_KASSE)] - RL_NCR_STRAFE;
      return 259;
   end
   return 0;
end

/* Inspektion der Liga (Lex Neun): bestanden bei Moral >= 60 ohne Zwang, sonst
   ist die Ausnahme der Lex Neun verwirkt. Rueckgabe: Nummer der Meldung. */
procedure rl_inspektion(variable haus, variable welt, variable h) begin
   if ((haus[rl_idx(h, RL_F_MORAL)] >= 60) and (haus[rl_idx(h, RL_F_ZWANG)] == 0)) then begin
      call rl_haus_plus(haus, h, RL_F_RUF, 2);
      return 250;
   end
   welt[RL_W_EREIGNIS_FLAGS] := welt[RL_W_EREIGNIS_FLAGS] bwor RL_EF_LEX_VERWIRKT;
   return 251;
end

// Bar II steht in diesem Haus (unter den Tisch trinken)
procedure rl_bar2_hier(variable haus, variable h) begin
   variable id := RL_M_BAR_2;
   return ((haus[rl_idx(h, RL_F_GEKAUFT)] bwand rl_bit(id))
           and (haus[rl_idx(h, RL_F_BAU_ID)] != id + 1));
end

#endif
