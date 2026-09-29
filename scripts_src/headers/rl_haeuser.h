/*
   rl_haeuser.h - Die weiteren Haeuser (Umsetzung 6)

   Tabellen je Haus (1 New Reno, 2 Redding, 3 Vault City, 4 NCR, 5 San Francisco)
   aus den Positionen in rl_karten.h (erzeugt von tools/bau_karten.py), dazu die
   gemeinsamen Hilfen der Kartenskripte: Figuren zur Laufzeit setzen.

   Die Gosse (Haus 0) hat ihre eigenen Namen (RL_GOSSE_*) und bleibt, wie sie ist.
*/
#ifndef RL_HAEUSER_H
#define RL_HAEUSER_H

// Plaetze auf den Innenkarten (rl_haus_platz)
#define RL_PLATZ_MADAME             (0)
#define RL_PLATZ_GAST1              (1)
#define RL_PLATZ_GAST2              (2)
#define RL_PLATZ_GAST3              (3)
#define RL_PLATZ_GAST4              (4)
#define RL_PLATZ_ANGREIFER1         (5)
#define RL_PLATZ_ANGREIFER2         (6)

procedure rl_eingang_stadtkarte(variable h);
procedure rl_eingang_hex(variable h);
procedure rl_haus_karte(variable h);
procedure rl_haus_platz(variable h, variable platz);
procedure rl_haus_von_stadtkarte(variable karte);
procedure rl_figur_da(variable skript);
procedure rl_figur(variable pid, variable hex, variable skript);

// Vanilla-Stadtkarte, auf der der Eingang steht (0 fuer die Gosse: eigene Logik)
procedure rl_eingang_stadtkarte(variable h) begin
   return get_array([0, RL_STRUMPF_STADTKARTE, RL_SCHLACKE_STADTKARTE, RL_KLOAKE_STADTKARTE,
                     RL_TRAENKE_STADTKARTE, RL_BILGE_STADTKARTE], h);
end

procedure rl_eingang_hex(variable h) begin
   return get_array([RL_GOSSE_TREPPE_HEX, RL_STRUMPF_TREPPE_HEX, RL_SCHLACKE_TREPPE_HEX,
                     RL_KLOAKE_TREPPE_HEX, RL_TRAENKE_TREPPE_HEX, RL_BILGE_TREPPE_HEX], h);
end

// Dateiname der Innenkarte (fuer load_map)
procedure rl_haus_karte(variable h) begin
   if (h == RL_NEW_RENO) then return RL_KARTE_STRUMPF;
   if (h == RL_REDDING) then return RL_KARTE_SCHLACKE;
   if (h == RL_VAULT_CITY) then return RL_KARTE_KLOAKE;
   if (h == RL_NCR) then return RL_KARTE_TRAENKE;
   if (h == RL_SAN_FRAN) then return RL_KARTE_BILGE;
   return RL_KARTE_GOSSE;
end

procedure rl_haus_platz(variable h, variable platz) begin
   variable werte;
   if (h == RL_NEW_RENO) then
      werte := [RL_STRUMPF_MADAME_HEX, RL_STRUMPF_GAST1_HEX, RL_STRUMPF_GAST2_HEX, RL_STRUMPF_GAST3_HEX,
                RL_STRUMPF_GAST4_HEX, RL_STRUMPF_ANGREIFER1_HEX, RL_STRUMPF_ANGREIFER2_HEX];
   else if (h == RL_REDDING) then
      werte := [RL_SCHLACKE_MADAME_HEX, RL_SCHLACKE_GAST1_HEX, RL_SCHLACKE_GAST2_HEX, RL_SCHLACKE_GAST3_HEX,
                RL_SCHLACKE_GAST4_HEX, RL_SCHLACKE_ANGREIFER1_HEX, RL_SCHLACKE_ANGREIFER2_HEX];
   else if (h == RL_VAULT_CITY) then
      werte := [RL_KLOAKE_MADAME_HEX, RL_KLOAKE_GAST1_HEX, RL_KLOAKE_GAST2_HEX, RL_KLOAKE_GAST3_HEX,
                RL_KLOAKE_GAST4_HEX, RL_KLOAKE_ANGREIFER1_HEX, RL_KLOAKE_ANGREIFER2_HEX];
   else if (h == RL_NCR) then
      werte := [RL_TRAENKE_MADAME_HEX, RL_TRAENKE_GAST1_HEX, RL_TRAENKE_GAST2_HEX, RL_TRAENKE_GAST3_HEX,
                RL_TRAENKE_GAST4_HEX, RL_TRAENKE_ANGREIFER1_HEX, RL_TRAENKE_ANGREIFER2_HEX];
   else
      werte := [RL_BILGE_MADAME_HEX, RL_BILGE_GAST1_HEX, RL_BILGE_GAST2_HEX, RL_BILGE_GAST3_HEX,
                RL_BILGE_GAST4_HEX, RL_BILGE_ANGREIFER1_HEX, RL_BILGE_ANGREIFER2_HEX];
   return get_array(werte, platz);
end

// Welches Haus hat seinen Eingang auf dieser Stadtkarte? (-1: keines)
procedure rl_haus_von_stadtkarte(variable karte) begin
   variable h := 1;
   while (h < RL_ANZAHL_HAEUSER) do begin
      if (rl_eingang_stadtkarte(h) == karte) then return h;
      h := h + 1;
   end
   return -1;
end

// Lebt eine Figur mit diesem Skript auf der Karte? Tote zaehlen nicht: Wer
// nachruecken kann (Ascortis Schreiber), rueckt nach; wer nicht, hat ein Tot-Bit.
procedure rl_figur_da(variable skript) begin
   variable o;
   foreach o in list_as_array(LIST_CRITTERS) begin
      if ((get_script(o) == skript) and ((critter_state(o) bwand 1) == 0)) then return 1;
   end
   return 0;
end

// Setzt eine Figur, wenn sie nicht schon auf der Karte steht
procedure rl_figur(variable pid, variable hex, variable skript) begin
   variable obj;
   if (not rl_figur_da(skript)) then
      obj := create_object_sid(pid, hex, 0, skript);
end

#endif
