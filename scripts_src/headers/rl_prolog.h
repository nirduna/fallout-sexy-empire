/*
   rl_prolog.h - Prolog "Essies Schulden" (Phase 1, Ansatz A; Phase 3, Abschnitt 2.1)

   Gemeinsam genutzt von rlessie.ssl (Essie) und rlkolbe.ssl (Metzgers Eintreiber).
   Voraussetzung: rotlicht.h ist eingebunden.
*/
#ifndef RL_PROLOG_H
#define RL_PROLOG_H

procedure rl_aktuelle_schulden(variable welt);
procedure rl_prolog_starten(variable welt);
procedure rl_prolog_abschliessen(variable haus, variable welt, variable weg);

// Schulden = Grundbetrag + 50 $ Zinsen fuer jede Woche seit Beginn des Prologs
procedure rl_aktuelle_schulden(variable welt) begin
   variable betrag;
   betrag := welt[RL_W_SCHULDEN] + RL_ZINS_JE_WOCHE * (rl_woche_jetzt - welt[RL_W_PROLOG_START]);
   if (welt[RL_W_KOLBE] bwand RL_KOLBE_RABATT) then
      betrag := betrag * 75 / 100;         // Barter >= 50: ein Viertel weniger
   return betrag;
end

procedure rl_prolog_starten(variable welt) begin
   if (welt[RL_W_PROLOG] != RL_PROLOG_OFFEN) then return;
   welt[RL_W_PROLOG]       := RL_PROLOG_LAEUFT;
   welt[RL_W_SCHULDEN]     := RL_SCHULDEN_START;
   welt[RL_W_PROLOG_START] := rl_woche_jetzt;
end

/* Die Gosse geht an den Spieler. Die Folgen je Weg stehen in Phase 1
   (Tabelle "Akquise") und Phase 3 (Abschnitt 2.1). */
procedure rl_prolog_abschliessen(variable haus, variable welt, variable weg) begin
   call rl_haus_uebernehmen(haus, welt, RL_DEN);
   welt[RL_W_PROLOG]     := RL_PROLOG_FERTIG;
   welt[RL_W_PROLOG_WEG] := weg;
   welt[RL_W_KETTEN]     := 1;             // Questline "Ketten", Akt 1 beginnt

   if (weg == RL_WEG_BEZAHLT) then begin
      welt[RL_W_METZGER] := RL_METZGER_NEUTRAL;
      haus[rl_idx(RL_DEN, RL_F_FUEHRUNG)] := 45;          // Essie: loyal
   end else if (weg == RL_WEG_PARTNER) then begin
      welt[RL_W_METZGER] := RL_METZGER_PARTNER;
      haus[rl_idx(RL_DEN, RL_F_TRIBUTMOD)] := 10;         // 10 % Dauerabgabe an die Gilde
      haus[rl_idx(RL_DEN, RL_F_FUEHRUNG)] := 35;          // Essie: misstrauisch
   end else if (weg == RL_WEG_VERPRUEGELT) then begin
      welt[RL_W_METZGER] := RL_METZGER_RESPEKT;
      haus[rl_idx(RL_DEN, RL_F_HITZE)] := 10;
      haus[rl_idx(RL_DEN, RL_F_FUEHRUNG)] := 50;          // Essie: beeindruckt
   end else if (weg == RL_WEG_GESTOHLEN) then begin
      welt[RL_W_METZGER] := RL_METZGER_NEUTRAL;           // bis er es merkt (gl_rotlicht)
      welt[RL_W_DIEBSTAHL_WOCHE] := rl_woche_jetzt;
      haus[rl_idx(RL_DEN, RL_F_FUEHRUNG)] := 45;          // Essie: loyal
   end else if (weg == RL_WEG_AUSGELIEFERT) then begin
      welt[RL_W_METZGER] := RL_METZGER_FREUND;
      welt[RL_W_ESSIE] := RL_ESSIE_AUSGELIEFERT;
      welt[RL_W_KETTEN_ZWEIG] := RL_KETTEN_ZWEIG_TYRANN;  // "Ketten" startet im Tyrannen-Zweig
      haus[rl_idx(RL_DEN, RL_F_TRIBUTMOD)] := 10;         // Metzgers Anteil fuer Kolbes "Aufsicht"
      haus[rl_idx(RL_DEN, RL_F_FUEHRUNG)] := 30;          // Kolbe fuehrt das Haus
      set_global_var(GVAR_PLAYER_REPUTATION, global_var(GVAR_PLAYER_REPUTATION) - 25);
   end
end

#endif
