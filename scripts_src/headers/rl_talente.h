/*
   rl_talente.h - Die Talente (Phase 4, Abschnitt 3). Umsetzung 13.

   Vier Figuren mit Namen, Geschichte und Anwerbe-Auftrag. Angeworben wird im
   Gespraech mit der Madame ("People worth knowing about", rl_manager.h); wer
   anderswo gebraucht wird, muss dorthin reisen (Gecko, Broken Hills).
     Vesper       Strumpfband: Qualitaet +10, Ausstattung +10, Nebenumsatz +2 $,
                  Kunden +5 %. Singt erst mit Bar II (Buehne). Geht, sobald irgendwo
                  Zwangspersonal arbeitet.
     Abigail      Kloake: Doc (Krankenstube, Lohn +120 $), Stoff-Ereignisse halbiert,
                  Razzien -25 %. Erpresst: Loyalitaet 20, sie kann verraten.
     Talus        ein Haus nach Wahl (nie Vault City): Sicherheit +45 fuer 50 $
                  Lohn, gewalttaetige Freier erledigt er selbst. In der NCR -5 %.
                  Geht und zeigt dich bei Marcus an, sobald in seinem Haus jemand
                  hinter einem Riegel sitzt.
     Julian Rook  jedes Haus mit VIP-Trakt: VIP-Kundschaft +3, Ruf +1/Woche.
                  Rueckfall 3 % je Woche (10 % mit Jet-Theke). Ohne Krankenstube liegt
                  er eine Woche im Sterben; rettet ihn keiner, stirbt er.
   Loyalitaet unter 30: Die Figur geht.

   Wird am Ende von rotlicht.h eingebunden.
*/
#ifndef RL_TALENTE_H
#define RL_TALENTE_H

#define RL_TALENT_VESPER            (0)
#define RL_TALENT_ABIGAIL           (1)
#define RL_TALENT_TALUS             (2)
#define RL_TALENT_JULIAN            (3)

// Stand (RL_W_VESPER_STAND, RL_W_ABIGAIL, RL_W_TALUS, RL_W_JULIAN)
#define RL_TS_OFFEN                 (0)
#define RL_TS_AUFTRAG               (1)     // angenommen: Reise noetig (Vesper, Talus) bzw. Julian noch am Jet
#define RL_TS_UNTERWEGS             (2)
#define RL_TS_WARTET                (3)     // Vesper: wartet auf die Buehne
#define RL_TS_DA                    (4)
#define RL_TS_GEGANGEN              (5)
#define RL_TS_TOT                   (6)
#define RL_TS_KRITISCH              (7)     // schwer verletzt: eine Woche, um ihn zu retten (Phase 4, Leitlinie 5)

#define RL_ABIGAIL_BUERGERIN        (1)
#define RL_ABIGAIL_AKTE             (2)
#define RL_ABIGAIL_ERPRESST         (3)

#define RL_TALUS_WAHRHEIT           (1)
#define RL_TALUS_AUSBRUCH           (2)

#define RL_JULIAN_BARTER            (1)
#define RL_JULIAN_GAMBLING          (2)
#define RL_JULIAN_PORNOSTAR         (3)
#define RL_JULIAN_TYRANN            (4)

#define RL_JULIAN_PREIS             (800)
#define RL_JULIAN_VIP               (3)
#define RL_ABIGAIL_LOHN             (120)   // 60 $ wie ein Doc, dazu ihr Anteil
#define RL_TALUS_LOHN               (50)
#define RL_TALUS_SICHERHEIT         (45)
#define RL_LOYAL_GRENZE             (30)

procedure rl_talent_bit(variable wer);
procedure rl_talent_anwenden(variable haus, variable welt, variable wer, variable an);
procedure rl_talus_haus(variable welt);
procedure rl_bar2_steht(variable haus);
procedure rl_julian_aktiv(variable welt);

procedure rl_talent_bit(variable wer) begin
   return rl_bit(wer);
end

// Talus arbeitet in diesem Haus (-1: nirgends)
procedure rl_talus_haus(variable welt) begin
   if (welt[RL_W_TALUS] != RL_TS_DA) then return -1;
   return welt[RL_W_TALUS_HAUS] - 1;
end

// Die Buehne im Strumpfband: Bar II ist gebaut
procedure rl_bar2_steht(variable haus) begin
   variable id := RL_M_BAR_2;
   return ((haus[rl_idx(RL_NEW_RENO, RL_F_GEKAUFT)] bwand rl_bit(id))
           and (haus[rl_idx(RL_NEW_RENO, RL_F_BAU_ID)] != id + 1));
end

procedure rl_julian_aktiv(variable welt) begin
   variable s := welt[RL_W_JULIAN];
   return ((s == RL_TS_AUFTRAG) or (s == RL_TS_DA));
end

/* Wirkung an- (an = 1) oder abschalten (an = -1), jeweils nur einmal */
procedure rl_talent_anwenden(variable haus, variable welt, variable wer, variable an) begin
   variable h, aktiv := ((welt[RL_W_TALENTE_AKTIV] bwand rl_talent_bit(wer)) != 0);
   if ((an > 0) and aktiv) then return;
   if ((an < 0) and not aktiv) then return;
   if (an > 0) then welt[RL_W_TALENTE_AKTIV] := welt[RL_W_TALENTE_AKTIV] bwor rl_talent_bit(wer);
   else welt[RL_W_TALENTE_AKTIV] := welt[RL_W_TALENTE_AKTIV] - rl_talent_bit(wer);

   if (wer == RL_TALENT_VESPER) then begin
      h := RL_NEW_RENO;
      haus[rl_idx(h, RL_F_QUALI)]         := rl_clamp(haus[rl_idx(h, RL_F_QUALI)] + 10 * an, 0, 100);
      haus[rl_idx(h, RL_F_AUSSTATTUNG)]   := rl_max(0, haus[rl_idx(h, RL_F_AUSSTATTUNG)] + 10 * an);
      haus[rl_idx(h, RL_F_NEBEN)]         := rl_max(0, haus[rl_idx(h, RL_F_NEBEN)] + 2 * an);
      haus[rl_idx(h, RL_F_MODUL_STADTMOD)] := haus[rl_idx(h, RL_F_MODUL_STADTMOD)] + 5 * an;
   end else if (wer == RL_TALENT_ABIGAIL) then begin
      h := RL_VAULT_CITY;
      haus[rl_idx(h, RL_F_LOEHNE)] := rl_max(0, haus[rl_idx(h, RL_F_LOEHNE)] + RL_ABIGAIL_LOHN * an);
      if ((an > 0) and ((haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_KRANKENSTUBE) == 0)) then begin
         haus[rl_idx(h, RL_F_MODULE)] := haus[rl_idx(h, RL_F_MODULE)] bwor RL_MOD_KRANKENSTUBE;
         welt[RL_W_TALENTE_AKTIV] := welt[RL_W_TALENTE_AKTIV] bwor 16;       // Krankenstube kommt von ihr
      end else if ((an < 0) and (welt[RL_W_TALENTE_AKTIV] bwand 16)) then begin
         haus[rl_idx(h, RL_F_MODULE)] := haus[rl_idx(h, RL_F_MODULE)] - RL_MOD_KRANKENSTUBE;
         welt[RL_W_TALENTE_AKTIV] := welt[RL_W_TALENTE_AKTIV] - 16;
      end
   end else if (wer == RL_TALENT_TALUS) then begin
      h := welt[RL_W_TALUS_HAUS] - 1;
      if (h < 0) then return;
      haus[rl_idx(h, RL_F_SICHERHEIT)] := rl_max(0, haus[rl_idx(h, RL_F_SICHERHEIT)] + RL_TALUS_SICHERHEIT * an);
      haus[rl_idx(h, RL_F_LOEHNE)]     := rl_max(0, haus[rl_idx(h, RL_F_LOEHNE)] + RL_TALUS_LOHN * an);
      if (h == RL_NCR) then
         haus[rl_idx(h, RL_F_MODUL_STADTMOD)] := haus[rl_idx(h, RL_F_MODUL_STADTMOD)] - 5 * an;   // Vorurteile
   end
end

#endif
