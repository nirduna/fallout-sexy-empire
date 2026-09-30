/*
   rl_jobs.h - Jobs und Laeuferroute (Phase 3, Abschnitte 5 und 6). Umsetzung 14.

   Bestechung (5.1), angeboten von der Madame der Stadt:
     The Den      Tyler           100 $/Woche, H -5/Woche; endet, wenn Tyler faellt
     New Reno     Totengraeber    300 $ einmalig nach einem gewaltsamen Vorfall: H -15
     Vault City   Torwache        (Umsetzung 9, bei Hanne)
     Vault City   McClure         1.000 $ Spende fuer den Gecko-Frieden: E VC +10
     NCR          Polizist        80 $/Woche, H -5/Woche
     Redding, San Francisco, Broken Hills: Lizenz, Duldung, Marcus (eigene Wege)
   Schutzgeld (5.2) in der Den, in Redding und in der NCR: Unarmed 60, ST 7 oder
     Speech 60. 50-150 $/Woche in die Kasse, E +2, H +5 (NCR +10), K -2, zaehlt
     als Tyrannen-Woche. In Redding wird Sheriff Marion zum Feind.
   Sabotage (5.3) gegen einen Rivalen der Stadt, einmal in vier Wochen:
     Lieferung abfangen (Sneak 60 oder Kampfwert 60): E +5, H +5
     Buecher stehlen (Steal 60 oder Lockpick 60): Erpressungsmaterial, H +5.
       Verwendbar bei Jade (Druck auf Kitty) oder fuer 300 $ zurueckverkauft.
   Gefaelligkeiten (5.3): Krankenstube in der Den (500 $: K +10, E Den +5),
     Spende an die Rangers (1.000 $: E NCR +5, H NCR -10), Gecko friedlich
     geloest (Vanilla: E VC +10).
   Laeuferroute (6) mit Sheriff Marcus: Vertrauen (Missing-Quest oder Speech 70,
     nach einem Geldangebot 80), Anstaendigkeit (Karma >= 250 und drei Haeuser
     mit Moral >= 60), Sperre (Slaver-Titel, der neue Metzger, Talus, Marcus tot).

   Wird am Ende von rotlicht.h eingebunden.
*/
#ifndef RL_JOBS_H
#define RL_JOBS_H

// Bits in RL_W_JOBS
#define RL_JOB_TYLER                (1)
#define RL_JOB_POLIZEI              (2)
#define RL_JOB_SCHUTZ_DEN           (4)
#define RL_JOB_SCHUTZ_RED           (8)
#define RL_JOB_SCHUTZ_NCR           (16)
#define RL_JOB_KLINIK               (32)
#define RL_JOB_RANGERS              (64)
#define RL_JOB_MCCLURE              (128)
#define RL_JOB_GECKO                (256)   // E VC +10 fuer den Gecko-Frieden ist vergeben
#define RL_JOB_MARCUS_GELD          (512)   // Marcus wurde Geld angeboten: Checks -10
#define RL_JOB_BH_BESUCHT           (1024)  // der Spieler war in Broken Hills
#define RL_JOB_MARCUS_TOT           (2048)  // die Folgen von Marcus' Tod sind angewendet

#define RL_TYLER_WOCHE              (100)
#define RL_POLIZEI_WOCHE            (80)
#define RL_TOTENGRAEBER_PREIS       (300)
#define RL_MCCLURE_SPENDE           (1000)
#define RL_KLINIK_SPENDE            (500)
#define RL_RANGERS_SPENDE           (1000)
#define RL_BUECHER_PREIS            (300)
#define RL_SABOTAGE_ABSTAND         (4)
#define RL_KARMA_GUT                (250)   // "Defender" und besser

procedure rl_schutz_bit(variable h);
procedure rl_job_bestechung(variable haus, variable welt, variable bit, variable an);
procedure rl_rivale_da(variable welt, variable h);
procedure rl_gecko_offen;
procedure rl_anstaendige_haeuser(variable haus);

// Schutzgeld gibt es nur in der Den, in Redding und in der NCR
procedure rl_schutz_bit(variable h) begin
   if (h == RL_DEN) then return RL_JOB_SCHUTZ_DEN;
   if (h == RL_REDDING) then return RL_JOB_SCHUTZ_RED;
   if (h == RL_NCR) then return RL_JOB_SCHUTZ_NCR;
   return 0;
end

/* Tyler (Den) oder der Polizist (NCR): Das Schmiergeld laeuft ueber die
   Schmiergeld-Abweichung des Hauses, also mitten in der Wochenrechnung. */
procedure rl_job_bestechung(variable haus, variable welt, variable bit, variable an) begin
   variable h := RL_DEN, betrag := RL_TYLER_WOCHE;
   if (bit == RL_JOB_POLIZEI) then begin
      h := RL_NCR;
      betrag := RL_POLIZEI_WOCHE;
   end
   if (an and ((welt[RL_W_JOBS] bwand bit) == 0)) then begin
      welt[RL_W_JOBS] := welt[RL_W_JOBS] bwor bit;
      haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] := haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] + betrag;
   end else if ((not an) and (welt[RL_W_JOBS] bwand bit)) then begin
      welt[RL_W_JOBS] := welt[RL_W_JOBS] - bit;
      haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] := haus[rl_idx(h, RL_F_BESTECHUNG_MOD)] - betrag;
   end
end

// Ein Rivale, dem man eine Lieferung abfangen oder die Buecher stehlen kann
procedure rl_rivale_da(variable welt, variable h) begin
   variable v := welt[RL_W_VIRGIN];
   if (h == RL_DEN) then
      return ((not rl_gvar_bit(GVAR_DEN_FLAG_1, bit_1)) and (welt[RL_W_KETTEN] != RL_KETTEN_NEUER_METZGER));
   if (h == RL_NEW_RENO) then
      return ((welt[RL_W_CATSPAW] == 0) or (welt[RL_W_CATSPAW] == RL_CATSPAW_MORDINO)
              or ((v >= RL_VIRGIN_GEBUEHR) and (v <= RL_VIRGIN_MESSER)));
   if (h == RL_REDDING) then
      return ((welt[RL_W_MALAMUTE] == 0) or welt[RL_W_KITTY_RIVALIN]);
   if (h == RL_NCR) then
      return ((welt[RL_W_LIGA] >= RL_LIGA_KAMPAGNE) and (welt[RL_W_LIGA] <= RL_LIGA_GEGENKAMPAGNE));
   if (h == RL_SAN_FRAN) then
      return (welt[RL_W_HUBOLOGEN] == RL_HUBOLOGEN_OFFEN);
   return 0;
end

// Der Gecko-Konflikt ist noch offen: weder repariert, optimiert noch zerstoert
procedure rl_gecko_offen begin
   variable p := global_var(GVAR_VAULT_GECKO_PLANT);
   return ((p != PLANT_REPAIRED) and (p != PLANT_DESTROYED) and (p < PLANT_FIXED_PLUS_KNOWN));
end

// Eigene Haeuser mit Moral >= 60 (Anstaendigkeit fuer Marcus)
procedure rl_anstaendige_haeuser(variable haus) begin
   variable h := 0, n := 0;
   while (h < RL_ANZAHL_HAEUSER) do begin
      if (haus[rl_idx(h, RL_F_BESITZ)] and (haus[rl_idx(h, RL_F_MORAL)] >= 60)) then n := n + 1;
      h := h + 1;
   end
   return n;
end

#endif
