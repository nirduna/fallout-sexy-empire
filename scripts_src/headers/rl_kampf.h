/*
   rl_kampf.h - Kaempfe in den Haeusern (Fahrplan, Grundsatz 4)

   Die Gosse fuehrt ihren Kampf in den Welt-Feldern RL_W_ANGRIFF und
   RL_W_ANGREIFER (Ketten, Akt 4). Die weiteren Haeuser haben je Haus
   RL_F_ANGRIFF und RL_F_ANGREIFER, damit Kaempfe in zwei Haeusern sich nicht
   ueberschreiben (Eroeffnungsnacht, spaeter die Virgin Street).

   Die Angreifer (rlangreifer.ssl) erfahren ihr Haus aus RL_W_HAUS_HIER: Das
   Kartenskript jeder Innenkarte setzt es in map_enter_p_proc, und das laeuft
   in der Engine vor den Skripten der Figuren.

   Wird ganz am Ende von rotlicht.h eingebunden (nach allen Stadt-Headern).
*/
#ifndef RL_KAMPF_H
#define RL_KAMPF_H

procedure rl_hier(variable welt);
procedure rl_angriff_typ(variable haus, variable welt, variable h);
procedure rl_angriff_haus(variable haus, variable welt, variable typ, variable h, variable pid);
procedure rl_angreifer_faellt(variable haus, variable welt, variable h);
procedure rl_haus_kampf_ende(variable haus, variable welt, variable h);

// Das Haus der Innenkarte, auf der der Spieler steht (-1: keine)
procedure rl_hier(variable welt) begin
   return welt[RL_W_HAUS_HIER] - 1;
end

procedure rl_angriff_typ(variable haus, variable welt, variable h) begin
   if (h <= RL_DEN) then return welt[RL_W_ANGRIFF];
   return haus[rl_idx(h, RL_F_ANGRIFF)];
end

/* Drei Angreifer an den Plaetzen ANGREIFER1, ANGREIFER2 und GAST4 (rl_karten.h) */
procedure rl_angriff_haus(variable haus, variable welt, variable typ, variable h, variable pid) begin
   variable o1, o2, o3;
   haus[rl_idx(h, RL_F_ANGRIFF)]   := typ;
   haus[rl_idx(h, RL_F_ANGREIFER)] := 3;
   o1 := create_object_sid(pid, rl_haus_platz(h, RL_PLATZ_ANGREIFER1), 0, SCRIPT_RLANGREIFER);
   o2 := create_object_sid(pid, rl_haus_platz(h, RL_PLATZ_ANGREIFER2), 0, SCRIPT_RLANGREIFER);
   o3 := create_object_sid(pid, rl_haus_platz(h, RL_PLATZ_GAST4), 0, SCRIPT_RLANGREIFER);
   attack_setup(o1, dude_obj);
   attack_setup(o2, dude_obj);
   attack_setup(o3, dude_obj);
end

// Ein Angreifer ist gefallen; faellt der letzte, endet der Kampf
procedure rl_angreifer_faellt(variable haus, variable welt, variable h) begin
   if (h <= RL_DEN) then begin
      welt[RL_W_ANGREIFER] := welt[RL_W_ANGREIFER] - 1;
      if (welt[RL_W_ANGREIFER] <= 0) then call rl_kampf_ende(haus, welt);
      return;
   end
   haus[rl_idx(h, RL_F_ANGREIFER)] := haus[rl_idx(h, RL_F_ANGREIFER)] - 1;
   if (haus[rl_idx(h, RL_F_ANGREIFER)] <= 0) then call rl_haus_kampf_ende(haus, welt, h);
end

/* Der Kampf in einem der weiteren Haeuser ist vorbei (alle Angreifer liegen). */
procedure rl_haus_kampf_ende(variable haus, variable welt, variable h) begin
   variable typ := haus[rl_idx(h, RL_F_ANGRIFF)];
   haus[rl_idx(h, RL_F_ANGRIFF)]   := RL_ANGRIFF_KEINER;
   haus[rl_idx(h, RL_F_ANGREIFER)] := 0;
   if (typ == RL_ANGRIFF_EROEFFNUNG) then begin
      // Die Eroeffnungsnacht ist ueberstanden: unabhaengig, mit Respekt (Phase 3, 2.2)
      welt[RL_W_NR_EROEFFNUNG] := RL_EROEFFNUNG_UEBERSTANDEN;
      call rl_haus_plus(haus, RL_NEW_RENO, RL_F_EINFLUSS, 10);
      call rl_nr_segen(haus, welt, RL_SEGEN_UNABHAENGIG);
      if (rl_hier(welt) == RL_NEW_RENO) then call rl_nr_figuren(haus, welt);
   end else if (typ == RL_ANGRIFF_VIRGIN) then begin
      // Die Nacht der langen Messer ist ueberstanden: Venuti ist erledigt (Phase 3, 3.1)
      welt[RL_W_VIRGIN_TOTE] := welt[RL_W_VIRGIN_TOTE] bwor RL_VIRGIN_TOT_VENUTI;
      call rl_haus_plus(haus, RL_NEW_RENO, RL_F_HITZE, 20);
      call rl_virgin_ende(haus, welt, RL_VIRGIN_LEERER_STUHL);
   end
end

#endif
