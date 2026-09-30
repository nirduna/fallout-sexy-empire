/*
   rl_ketten.h - Questline "Ketten", Akt 2-5 (Phase 3, Abschnitt 3.2)
   und Mara als Madame der Gosse (Phase 4, Abschnitt 3.5). Umsetzung 5.

   Gemeinsam genutzt vom globalen Skript (Wochentakt), dem Kartenskript der
   Gosse und den Figuren Essie, Kolbe, Mara, Deke und Jess.
   Wird am Ende von rotlicht.h eingebunden.

   Ablauf:
     Akt 2  Mara im Keller: verstecken, in Sicherheit bringen oder ausliefern.
            Ausliefern fuehrt in den Tyrannen-Zweig.
     Akt 3  Fluchtzweig: Transporte nach Sueden (Auftrag, 1 Woche, Sneak oder
            Outdoorsman). Tyrannen-Zweig: Lieferungen nach Norden fuer Metzger
            (Auftrag, 1 Woche, Speech oder Barter). Nach je drei gelungenen: Akt 4.
     Akt 4  Fluchtzweig: Tylers Preis (Deke). Tyrannen-Zweig: Laras Sturm (Jess).
     Akt 5  Fluchtzweig: Sturm auf die Gilde (Metzger toeten) oder der stille
            Krieg. Tyrannen-Zweig: Metzgers Mann oder der neue Metzger.
*/
#ifndef RL_KETTEN_H
#define RL_KETTEN_H

// Maras Weg (RL_W_MARA_WEG)
#define RL_MARA_KEINE               (0)
#define RL_MARA_KELLER              (1)     // Akt 2: im Keller, Entscheidung offen
#define RL_MARA_VERSTECKT           (2)     // bleibt in der Gosse versteckt
#define RL_MARA_SICHER              (3)     // in die NCR gebracht (taucht bei "Die Reinen" wieder auf)
#define RL_MARA_AUSGELIEFERT        (4)
#define RL_MARA_VERSCHLEPPT         (5)     // Metzgers Leute haben sie gefunden
#define RL_MARA_ZURUECK             (6)     // nach dem Ende im Fluchtzweig: Anwerbung als Madame offen
#define RL_MARA_MADAME              (7)     // Madame der Gosse (dazu RL_W_MARA = 1)
#define RL_MARA_CALLOWAY            (8)     // gedraengt: zu Ruth Calloway in die NCR gegangen
#define RL_MARA_GEGANGEN            (9)     // wegen Zwangspersonal gegangen, Beweise bei den Rangers
#define RL_MARA_TOT                 (10)

#define RL_RANGERS_UNBEKANNT        (0)
#define RL_RANGERS_KONTAKT          (1)     // Versteck der Rangers bekannt (Perception oder Mara)
#define RL_RANGERS_VERBUENDET       (2)     // nach "Die Gilde faellt"
#define RL_RANGERS_FEIND            (3)     // nach "Der neue Metzger"

#define RL_AUFTRAG_KEINER           (0)
#define RL_AUFTRAG_SUEDEN           (1)     // Fluchtzweig: Transport in die NCR
#define RL_AUFTRAG_VC               (2)     // Tyrannen-Zweig: an die Dienstboten-Zuteilung (Vault City)
#define RL_AUFTRAG_VORTIS           (3)     // Tyrannen-Zweig: an Vortis (NCR-Bazaar)

#define RL_TYLER_OFFEN              (0)
#define RL_TYLER_GEKAUFT            (1)
#define RL_TYLER_LARA               (2)     // Lara auf Tyler gehetzt
#define RL_TYLER_UMGEDREHT          (3)
#define RL_TYLER_BESIEGT            (4)
#define RL_TYLER_TOT                (5)     // Vanilla: Tyler ist schon tot
#define RL_TYLER_KAMPF              (6)     // Kampf laeuft

#define RL_LARA_OFFEN               (0)
#define RL_LARA_KAMPF               (1)
#define RL_LARA_ABGEWEHRT           (2)
#define RL_LARA_ZIEHEN              (3)     // die Gefangenen gehen mit Lara

#define RL_ANGRIFF_KEINER           (0)
#define RL_ANGRIFF_TYLER            (1)
#define RL_ANGRIFF_LARA             (2)

#define RL_KETTEN_ZIEL              (3)     // Transporte bzw. Lieferungen bis Akt 4
#define RL_MARA_PREIS               (500)   // zahlt Metzger fuer Mara
#define RL_TYLER_PREIS              (400)
#define RL_METZGERS_MANN_WOCHE      (200)   // Einnahmen aus den Lieferungen je Woche
#define RL_VERGELTUNG_ABSTAND       (6)     // Wochen zwischen Metzgers Schlaegen im stillen Krieg
#define RL_MARA_FUEHRUNG            (70)
#define RL_KOLBE_FUEHRUNG           (30)

// Kolbe: Bit in RL_W_KOLBE, wenn er getoetet wurde (nicht, wenn er nur geht)
#define RL_KOLBE_TOT                (64)

procedure rl_ketten_akt3(variable welt);
procedure rl_mara_verstecken(variable welt);
procedure rl_mara_retten(variable welt);
procedure rl_mara_ausliefern(variable haus, variable welt);
procedure rl_auftrag_starten(variable welt, variable typ, variable chance);
procedure rl_transport_chance(variable welt);
procedure rl_liefer_chance;
procedure rl_zwang_irgendwo(variable haus);
procedure rl_kolbe_bleibt(variable welt);
procedure rl_mara_da(variable welt);
procedure rl_ketten_ende(variable haus, variable welt, variable ende);
procedure rl_haus_plus(variable haus, variable h, variable feld, variable n);
procedure rl_kampf_ende(variable haus, variable welt);
procedure rl_deke_bleibt(variable welt);
procedure rl_jess_bleibt(variable welt);
procedure rl_zahlbar(variable haus, variable h, variable kosten);
procedure rl_zahlen(variable haus, variable h, variable kosten);
procedure rl_angriff_starten(variable welt, variable typ, variable anfuehrer, variable pid);

// Akt 3 beginnt: Maras Wissen fuehrt zu den Rangers (Fluchtzweig)
procedure rl_ketten_akt3(variable welt) begin
   welt[RL_W_KETTEN]       := RL_KETTEN_KETTE;
   welt[RL_W_KETTEN_WOCHE] := rl_woche_jetzt;
   if ((welt[RL_W_MARA_WEG] == RL_MARA_VERSTECKT) or (welt[RL_W_MARA_WEG] == RL_MARA_SICHER)) then
      welt[RL_W_RANGERS] := rl_max(welt[RL_W_RANGERS], RL_RANGERS_KONTAKT);
end

// Verstecken: Karma +10, Metzgers Leute durchsuchen die Den in einer Woche
procedure rl_mara_verstecken(variable welt) begin
   welt[RL_W_MARA_WEG] := RL_MARA_VERSTECKT;
   welt[RL_W_SUCHE]    := rl_woche_jetzt + 1;
   rl_karma(10);
   call rl_ketten_akt3(welt);
end

procedure rl_mara_retten(variable welt) begin
   welt[RL_W_MARA_WEG] := RL_MARA_SICHER;
   call rl_ketten_akt3(welt);
end

/* Ausliefern: 500 $, Metzgers Vertrauen, Karma -25. Essie kuendigt, ausser
   sie ist laengst gebrochen (Tyrannen-Zweig). Die Linie geht im Tyrannen-Zweig
   weiter; fuehrt Essie nicht mehr, uebernimmt Kolbe fuer Metzger. */
procedure rl_mara_ausliefern(variable haus, variable welt) begin
   welt[RL_W_MARA_WEG] := RL_MARA_AUSGELIEFERT;
   welt[RL_W_METZGER]  := RL_METZGER_FREUND;
   item_caps_adjust(dude_obj, RL_MARA_PREIS);
   rl_karma(-25);
   if ((welt[RL_W_ESSIE] == RL_ESSIE_DA) and (welt[RL_W_KETTEN_ZWEIG] != RL_KETTEN_ZWEIG_TYRANN)) then begin
      welt[RL_W_ESSIE] := RL_ESSIE_GEKUENDIGT;
      haus[rl_idx(RL_DEN, RL_F_FUEHRUNG)] := RL_KOLBE_FUEHRUNG;
   end
   welt[RL_W_KETTEN_ZWEIG] := RL_KETTEN_ZWEIG_TYRANN;
   call rl_ketten_akt3(welt);
end

// Auftrag annehmen: die Probe faellt jetzt, das Ergebnis kommt in einer Woche
procedure rl_auftrag_starten(variable welt, variable typ, variable chance) begin
   welt[RL_W_AUFTRAG]       := typ;
   welt[RL_W_AUFTRAG_WOCHE] := rl_woche_jetzt + 1;
   welt[RL_W_AUFTRAG_WURF]  := (random(1, 100) <= chance);
end

// Transport: bessere von Sneak und Outdoorsman; mit Mara als Madame +25 (Phase 4)
procedure rl_transport_chance(variable welt) begin
   variable c := rl_max(has_skill(dude_obj, SKILL_SNEAK), has_skill(dude_obj, SKILL_OUTDOORSMAN));
   if (welt[RL_W_MARA] == 1) then c := c + 25;
   return rl_clamp(c, 5, 95);
end

// Uebergabe: bessere von Speech und Barter
procedure rl_liefer_chance begin
   return rl_clamp(rl_max(has_skill(dude_obj, SKILL_SPEECH), has_skill(dude_obj, SKILL_BARTER)), 5, 95);
end

// Zwangspersonal, Gezwungene oder Leine in irgendeinem eigenen Haus
procedure rl_zwang_irgendwo(variable haus) begin
   variable h := 0;
   while (h < RL_ANZAHL_HAEUSER) do begin
      if (haus[rl_idx(h, RL_F_BESITZ)]) then begin
         if ((haus[rl_idx(h, RL_F_ZWANG)] > 0) or (haus[rl_idx(h, RL_F_GEZWUNGEN)] > 0)
             or (haus[rl_idx(h, RL_F_MODULE)] bwand RL_MOD_LEINE)) then return 1;
      end
      h := h + 1;
   end
   return 0;
end

/* Bleibt Kolbe in der Gosse? (nach dem Prolog; im Prolog steht er ohnehin da)
   - solange Metzgers Angebot aussteht
   - solange er das Haus fuer Metzger fuehrt (Essie ist weg)
   - im Tyrannen-Zweig als Metzgers Bote bis zum Ende, danach als dein Mann */
procedure rl_kolbe_bleibt(variable welt) begin
   variable akt := welt[RL_W_KETTEN];
   if (welt[RL_W_KOLBE] bwand RL_KOLBE_TOT) then return 0;
   if (akt == RL_KETTEN_ANGEBOT) then return 1;
   if (welt[RL_W_ESSIE] != RL_ESSIE_DA) then return 1;
   if (welt[RL_W_KETTEN_ZWEIG] == RL_KETTEN_ZWEIG_TYRANN) then begin
      if ((akt >= RL_KETTEN_KETTE) and (akt <= RL_KETTEN_WAHL)) then return 1;
      if ((akt == RL_KETTEN_NEUER_METZGER) or (akt == RL_KETTEN_METZGERS_MANN)) then return 1;
   end
   return 0;
end

procedure rl_mara_da(variable welt) begin
   variable w := welt[RL_W_MARA_WEG];
   return ((w == RL_MARA_KELLER) or (w == RL_MARA_VERSTECKT) or (w == RL_MARA_ZURUECK)
           or (w == RL_MARA_MADAME));
end

procedure rl_haus_plus(variable haus, variable h, variable feld, variable n) begin
   haus[rl_idx(h, feld)] := rl_clamp(haus[rl_idx(h, feld)] + n, 0, 100);
end

/* Akt 5: ein Ende tritt ein (Phase 3, Abschnitt 3.2). Der stille Krieg kann
   spaeter noch zu "Die Gilde faellt" werden, wenn Metzger doch stirbt. */
procedure rl_ketten_ende(variable haus, variable welt, variable ende) begin
   variable alt := welt[RL_W_KETTEN];
   if ((alt >= RL_KETTEN_NEUER_METZGER) and not ((alt == RL_KETTEN_STILLER_KRIEG) and (ende == RL_KETTEN_GILDE_FAELLT))) then
      return;
   welt[RL_W_KETTEN]       := ende;
   welt[RL_W_KETTEN_WOCHE] := rl_woche_jetzt;
   welt[RL_W_AUFTRAG]      := RL_AUFTRAG_KEINER;
   if (ende == RL_KETTEN_GILDE_FAELLT) then begin
      rl_karma(50);
      call rl_haus_plus(haus, RL_DEN, RL_F_HITZE, -20);
      call rl_haus_plus(haus, RL_NCR, RL_F_EINFLUSS, 15);
      welt[RL_W_RANGERS] := RL_RANGERS_VERBUENDET;
      welt[RL_W_VORTIS]  := 1;
   end else if (ende == RL_KETTEN_STILLER_KRIEG) then begin
      welt[RL_W_VERGELTUNG] := rl_woche_jetzt + RL_VERGELTUNG_ABSTAND;
   end else if (ende == RL_KETTEN_METZGERS_MANN) then begin
      if (global_var(GVAR_REPUTATION_SLAVER) == 0) then set_global_var(GVAR_REPUTATION_SLAVER, 1);
   end else if (ende == RL_KETTEN_NEUER_METZGER) then begin
      rl_karma(-100);
      if (global_var(GVAR_REPUTATION_SLAVER) == 0) then set_global_var(GVAR_REPUTATION_SLAVER, 1);
      welt[RL_W_RANGERS] := RL_RANGERS_FEIND;
   end
   // Im Fluchtzweig kehrt eine versteckte Mara sofort zurueck, eine gerettete spaeter (Wochentakt)
   if (((ende == RL_KETTEN_GILDE_FAELLT) or (ende == RL_KETTEN_STILLER_KRIEG))
       and (welt[RL_W_MARA_WEG] == RL_MARA_VERSTECKT)) then
      welt[RL_W_MARA_WEG] := RL_MARA_ZURUECK;
end

// Deke (Tylers Mann) steht in der Gosse, solange Akt 4 im Fluchtzweig offen ist
procedure rl_deke_bleibt(variable welt) begin
   return ((welt[RL_W_KETTEN] == RL_KETTEN_TYLER) and (welt[RL_W_KETTEN_ZWEIG] == RL_KETTEN_ZWEIG_FLUCHT)
           and ((welt[RL_W_TYLER] == RL_TYLER_OFFEN) or (welt[RL_W_TYLER] == RL_TYLER_KAMPF)));
end

// Jess (Laras Leutnant) kommt in Akt 4 des Tyrannen-Zweigs
procedure rl_jess_bleibt(variable welt) begin
   return ((welt[RL_W_KETTEN] == RL_KETTEN_TYLER) and (welt[RL_W_KETTEN_ZWEIG] == RL_KETTEN_ZWEIG_TYRANN)
           and ((welt[RL_W_LARA] == RL_LARA_OFFEN) or (welt[RL_W_LARA] == RL_LARA_KAMPF)));
end

procedure rl_zahlbar(variable haus, variable h, variable kosten) begin
   return (rl_max(0, haus[rl_idx(h, RL_F_KASSE)]) + item_caps_total(dude_obj) >= kosten);
end

// Zuerst aus der Kasse des Hauses, der Rest aus der Tasche des Spielers
procedure rl_zahlen(variable haus, variable h, variable kosten) begin
   variable aus_kasse := rl_min(rl_max(0, haus[rl_idx(h, RL_F_KASSE)]), kosten);
   haus[rl_idx(h, RL_F_KASSE)] := haus[rl_idx(h, RL_F_KASSE)] - aus_kasse;
   if (kosten > aus_kasse) then
      item_caps_adjust(dude_obj, -(kosten - aus_kasse));
end

/* Kampf in der Gosse: der Anfuehrer und zwei Leute greifen an (Akt 4).
   Jeder Tote zaehlt herunter; sind alle gefallen, endet der Akt (rl_kampf_ende). */
procedure rl_angriff_starten(variable welt, variable typ, variable anfuehrer, variable pid) begin
   variable o1, o2;
   welt[RL_W_ANGRIFF]   := typ;
   welt[RL_W_ANGREIFER] := 3;
   o1 := create_object_sid(pid, RL_GOSSE_ANGREIFER1_HEX, 0, SCRIPT_RLANGREIFER);
   o2 := create_object_sid(pid, RL_GOSSE_ANGREIFER2_HEX, 0, SCRIPT_RLANGREIFER);
   attack_setup(anfuehrer, dude_obj);
   attack_setup(o1, dude_obj);
   attack_setup(o2, dude_obj);
end

/* Ein Kampf in der Gosse ist vorbei (alle Angreifer liegen). */
procedure rl_kampf_ende(variable haus, variable welt) begin
   variable typ := welt[RL_W_ANGRIFF];
   welt[RL_W_GEWALT_HAUS] := RL_DEN + 1;          // Leichen in der Gosse (Totengraeber, Umsetzung 14)
   if (typ == RL_ANGRIFF_TYLER) then begin
      welt[RL_W_TYLER] := RL_TYLER_BESIEGT;
      call rl_haus_plus(haus, RL_DEN, RL_F_HITZE, 10);
   end else if (typ == RL_ANGRIFF_LARA) then begin
      welt[RL_W_LARA] := RL_LARA_ABGEWEHRT;
      rl_karma(-10);
   end
   welt[RL_W_ANGRIFF]   := RL_ANGRIFF_KEINER;
   welt[RL_W_ANGREIFER] := 0;
   if (((typ == RL_ANGRIFF_TYLER) or (typ == RL_ANGRIFF_LARA)) and (welt[RL_W_KETTEN] == RL_KETTEN_TYLER)) then begin
      welt[RL_W_KETTEN]       := RL_KETTEN_WAHL;
      welt[RL_W_KETTEN_WOCHE] := rl_woche_jetzt;
   end
end

#endif
