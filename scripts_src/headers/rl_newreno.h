/*
   rl_newreno.h - New Reno: Das Silberne Strumpfband und das Hauptquartier
   (Phase 1 Ansatz C, Phase 2 Abschnitt 2.2, Phase 3 Abschnitt 2.2). Umsetzung 7.

   Uebernahme "Der Segen": die Urkunde (Witwe, Grab in Golgotha oder Faelschung)
   und der Segen einer Familie (je ein Auftrag) oder unabhaengig mit der
   Eroeffnungsnacht. Der Pate bestimmt Tribut, Bonus und wer misstrauisch wird
   (Phase 1, Tabelle der Paten).

   Hauptquartier: Der Consigliere zahlt die HQ-Kasse aus, berichtet ueber alle
   Haeuser und leitet ab dem Familiensitz (Hausklasse 3) alle vier Wochen das
   Familientreffen.

   Figuren auf der Innenkarte RLREN01 (rl_nr_figuren):
     vor der Uebernahme  Loretta Varga (Witwe, Urkunde), Frankie Pagano (Segen)
     danach              Roz Mercer (Madame), Leopold Asch (Consigliere)

   Wird am Ende von rotlicht.h eingebunden.
*/
#ifndef RL_NEWRENO_H
#define RL_NEWRENO_H

// Wie die Urkunde beschafft wurde (RL_W_NR_URKUNDE)
#define RL_URKUNDE_KEINE            (0)
#define RL_URKUNDE_REDE             (1)     // Speech 60 bei der Witwe
#define RL_URKUNDE_KAUF             (2)     // 1.000 $ (Barter 60: 750 $)
#define RL_URKUNDE_GRAB             (3)     // Golgotha: Schaufel (Sneak 40 unbemerkt), Grave Digger, Karma -10
#define RL_URKUNDE_FAELSCHUNG       (4)     // Science 60 und 100 $ fuer Papier, 15 % fliegt auf

// Der Pate (RL_W_NR_SEGEN); zugleich Bitnummer in RL_W_NR_MISSTRAUEN
#define RL_SEGEN_KEINER             (0)
#define RL_SEGEN_MORDINO            (1)
#define RL_SEGEN_WRIGHT             (2)
#define RL_SEGEN_SALVATORE          (3)
#define RL_SEGEN_BISHOP             (4)
#define RL_SEGEN_UNABHAENGIG        (5)

// Bishops Brief an Westin (RL_W_NR_BRIEF)
#define RL_BRIEF_KEINER             (0)
#define RL_BRIEF_UNTERWEGS          (1)
#define RL_BRIEF_GEOEFFNET          (2)     // unterwegs, aber gelesen (Erpressungsmaterial)
#define RL_BRIEF_ABGEGEBEN          (3)
#define RL_BRIEF_ABGEGEBEN_OFFEN    (4)
#define RL_BRIEF_ERLEDIGT           (5)     // bei Pagano abgerechnet
#define RL_BRIEF_ERLEDIGT_OFFEN     (6)     // abgerechnet, und der Spieler weiss, was drinstand

#define RL_EROEFFNUNG_KEINE         (0)
#define RL_EROEFFNUNG_KAMPF         (1)
#define RL_EROEFFNUNG_UEBERSTANDEN  (2)

#define RL_ANGRIFF_EROEFFNUNG       (3)     // Kampf in der Eroeffnungsnacht (RL_F_ANGRIFF)

// Die Witwe nach der Faelschung (RL_W_NR_WITWE)
#define RL_WITWE_KEINE              (0)
#define RL_WITWE_FORDERT            (1)
#define RL_WITWE_BEZAHLT            (2)
#define RL_WITWE_VERWEIGERT         (3)

// Familientreffen (RL_W_TREFFEN_OFFEN)
#define RL_TREFFEN_KEINS            (0)
#define RL_TREFFEN_SALVATORE        (1)     // Salvatore will mehr
#define RL_TREFFEN_JET              (2)     // die Mordinos wollen durch die Hintertuer verkaufen
#define RL_TREFFEN_WRIGHT           (3)     // Wright will wissen, wer das Jet verkauft hat
#define RL_TREFFEN_SHARK            (4)     // Bishop bietet einen Anteil am Shark Club
#define RL_TREFFEN_LAEUFER          (5)     // ein Laeufer zweigt ab
#define RL_TREFFEN_ANZAHL           (5)

// Wer auf der Karte gestorben ist (RL_W_NR_TOTE)
#define RL_NR_TOT_WITWE             (1)
#define RL_NR_TOT_FIXER             (2)
#define RL_NR_TOT_ROZ               (4)
#define RL_NR_TOT_ASCH              (8)

#define RL_NR_KENNT_ROZ             (1)
#define RL_NR_KENNT_ASCH            (2)

#define RL_URKUNDE_PREIS            (1000)
#define RL_URKUNDE_RABATT           (750)
#define RL_FAELSCHUNG_PAPIER        (100)
#define RL_WITWE_FORDERUNG          (500)
#define RL_WITWE_FRIST              (2)     // Wochen, bis sie es ganz Virgin Street erzaehlt
#define RL_SHARK_EINSATZ            (1000)
#define RL_SHARK_WOCHE              (100)
#define RL_JET_VERTRAG_WOCHE        (300)
#define RL_SALVATORE_SCHADEN        (300)
#define RL_LAEUFER_BEUTE            (200)
#define RL_TREFFEN_ABSTAND          (4)
#define RL_TREFFEN_FRIST_WOCHEN     (2)
#define RL_ROZ_FUEHRUNG             (55)
#define RL_OHNE_ROZ_FUEHRUNG        (30)
#define RL_MISSTRAUEN_HITZE         (2)     // Hitze je Woche und misstrauischer Familie

// Vanilla: Familienoberhaeupter tot (newreno.h, ohne den ganzen Header). Ohne
// gvar_bit aus command.h, weil die Header vor command.h eingebunden werden.
#define rl_gvar_bit(g, b)           ((global_var(g) bwand (b)) != 0)
#define rl_mordino_weg              rl_gvar_bit(GVAR_NEW_RENO_FLAG_2, bit_26)       // big_jesus_dead
#define rl_wright_weg               rl_gvar_bit(GVAR_NEW_RENO_WRIGHT_FLAGS, bit_4)  // wright_dead
#define rl_salvatore_weg            rl_gvar_bit(GVAR_NEW_RENO_SALVATORE, bit_10)    // salvatore_dead
#define rl_bishop_weg               rl_gvar_bit(GVAR_NEW_RENO_BISHOP, bit_10)       // bishop_dead
// Salvatores Vanilla-Auftrag "Uebergabe bewachen" erledigt (guard_assignment_success)
#define rl_salvatore_vorleistung    (global_var(GVAR_NEW_RENO_GUARD_ASSIGNMENT) == 3)

procedure rl_kampfwert;
procedure rl_familie_weg(variable familie);
procedure rl_made_man(variable familie);
procedure rl_nr_misstrauen(variable welt, variable familie);
procedure rl_nr_misstrauisch(variable welt, variable familie);
procedure rl_nr_segen(variable haus, variable welt, variable familie);
procedure rl_nr_urkunde(variable haus, variable welt, variable weg);
procedure rl_nr_pruefen(variable haus, variable welt);
procedure rl_nr_pate_anwenden(variable haus, variable welt);
procedure rl_nr_besitz(variable haus);
procedure rl_nr_figuren(variable haus, variable welt);
procedure rl_nr_witwe_da(variable welt);
procedure rl_nr_fixer_da(variable haus, variable welt);
procedure rl_treffen_bonus;
procedure rl_treffen_thema(variable welt);
procedure rl_treffen_ende(variable welt);
procedure rl_treffen_verpasst(variable haus, variable welt);
procedure rl_hq_zahlbar(variable welt, variable kosten);
procedure rl_hq_zahlen(variable welt, variable kosten);

// Der beste Kampf-Skill (Auftraege mit "Kampf" ohne echten Kampf, Fahrplan 1.4)
procedure rl_kampfwert begin
   return rl_max(rl_max(rl_max(has_skill(dude_obj, SKILL_SMALL_GUNS), has_skill(dude_obj, SKILL_BIG_GUNS)),
                        rl_max(has_skill(dude_obj, SKILL_ENERGY_WEAPONS), has_skill(dude_obj, SKILL_MELEE))),
                 has_skill(dude_obj, SKILL_UNARMED_COMBAT));
end

procedure rl_familie_weg(variable familie) begin
   if (familie == RL_SEGEN_MORDINO) then return rl_mordino_weg;
   if (familie == RL_SEGEN_WRIGHT) then return rl_wright_weg;
   if (familie == RL_SEGEN_SALVATORE) then return rl_salvatore_weg;
   if (familie == RL_SEGEN_BISHOP) then return rl_bishop_weg;
   return 0;
end

// Made Man einer Familie (Vanilla-Titel): Der Segen dieser Familie ist Formsache
procedure rl_made_man(variable familie) begin
   if (familie == RL_SEGEN_MORDINO) then return global_var(GVAR_MADE_MAN_MORDINO);
   if (familie == RL_SEGEN_WRIGHT) then return global_var(GVAR_MADE_MAN_WRIGHT);
   if (familie == RL_SEGEN_SALVATORE) then return global_var(GVAR_MADE_MAN_SALVATORE);
   if (familie == RL_SEGEN_BISHOP) then return global_var(GVAR_MADE_MAN_BISHOP);
   return 0;
end

procedure rl_nr_misstrauen(variable welt, variable familie) begin
   welt[RL_W_NR_MISSTRAUEN] := welt[RL_W_NR_MISSTRAUEN] bwor rl_bit(familie);
end

procedure rl_nr_misstrauisch(variable welt, variable familie) begin
   return ((welt[RL_W_NR_MISSTRAUEN] bwand rl_bit(familie)) != 0);
end

// Der Segen einer Familie (der erste zaehlt)
procedure rl_nr_segen(variable haus, variable welt, variable familie) begin
   if (welt[RL_W_NR_SEGEN] != RL_SEGEN_KEINER) then return;
   welt[RL_W_NR_SEGEN] := familie;
   call rl_nr_pruefen(haus, welt);
end

procedure rl_nr_urkunde(variable haus, variable welt, variable weg) begin
   if (welt[RL_W_NR_URKUNDE] != RL_URKUNDE_KEINE) then return;
   welt[RL_W_NR_URKUNDE] := weg;
   if ((weg == RL_URKUNDE_REDE) or (weg == RL_URKUNDE_KAUF)) then
      call rl_haus_plus(haus, RL_NEW_RENO, RL_F_EINFLUSS, 5);
   else if (weg == RL_URKUNDE_GRAB) then begin
      rl_karma(-10);
      set_global_var(GVAR_GRAVES_UNEARTHED, global_var(GVAR_GRAVES_UNEARTHED) + 1);   // Titel Grave Digger
      if (has_skill(dude_obj, SKILL_SNEAK) < 40) then
         call rl_haus_plus(haus, RL_NEW_RENO, RL_F_HITZE, 10);                         // gesehen worden
   end else if (weg == RL_URKUNDE_FAELSCHUNG) then begin
      call rl_haus_plus(haus, RL_NEW_RENO, RL_F_HITZE, 5);
      if (random(1, 100) <= 15) then welt[RL_W_NR_FAELSCHUNG] := rl_woche_jetzt + 2;
   end
   call rl_nr_pruefen(haus, welt);
end

/* Urkunde und Segen beisammen: Das Strumpfband gehoert dem Spieler. Der Segen
   ist der Einfluss, den die Uebernahme verlangt (Phase 2: E New Reno >= 20).
   Unabhaengig zaehlt erst nach der ueberstandenen Eroeffnungsnacht. */
procedure rl_nr_pruefen(variable haus, variable welt) begin
   if (haus[rl_idx(RL_NEW_RENO, RL_F_BESITZ)]) then return;
   if ((welt[RL_W_NR_URKUNDE] == RL_URKUNDE_KEINE) or (welt[RL_W_NR_SEGEN] == RL_SEGEN_KEINER)) then return;
   call rl_haus_uebernehmen(haus, welt, RL_NEW_RENO);
   haus[rl_idx(RL_NEW_RENO, RL_F_FUEHRUNG)] := RL_ROZ_FUEHRUNG;
   haus[rl_idx(RL_NEW_RENO, RL_F_EINFLUSS)] := rl_max(haus[rl_idx(RL_NEW_RENO, RL_F_EINFLUSS)], 20);
   call rl_nr_pate_anwenden(haus, welt);
   welt[RL_W_TREFFEN_WOCHE] := rl_woche_jetzt + RL_TREFFEN_ABSTAND;
end

/* Die Paten (Phase 1, Ansatz C): Tribut (Basis 20 %), Bonus, Misstrauen */
procedure rl_nr_pate_anwenden(variable haus, variable welt) begin
   variable pate := welt[RL_W_NR_SEGEN], h := RL_NEW_RENO;
   if (pate == RL_SEGEN_MORDINO) then begin
      haus[rl_idx(h, RL_F_TRIBUTMOD)] := haus[rl_idx(h, RL_F_TRIBUTMOD)] + 5;         // 25 %
      haus[rl_idx(h, RL_F_MODUL_STADTMOD)] := haus[rl_idx(h, RL_F_MODUL_STADTMOD)] + 15; // Jet-Konzession
      haus[rl_idx(h, RL_F_NEBEN)] := haus[rl_idx(h, RL_F_NEBEN)] + 3;
      call rl_nr_misstrauen(welt, RL_SEGEN_WRIGHT);
   end else if (pate == RL_SEGEN_WRIGHT) then begin
      haus[rl_idx(h, RL_F_NEBEN)] := haus[rl_idx(h, RL_F_NEBEN)] + 3;                 // Schnaps zum Selbstkostenpreis
      call rl_nr_misstrauen(welt, RL_SEGEN_MORDINO);
   end else if (pate == RL_SEGEN_SALVATORE) then begin
      haus[rl_idx(h, RL_F_TRIBUTMOD)] := haus[rl_idx(h, RL_F_TRIBUTMOD)] + 10;        // 30 %
      haus[rl_idx(h, RL_F_SICHERHEIT)] := haus[rl_idx(h, RL_F_SICHERHEIT)] + 30;
      call rl_nr_misstrauen(welt, RL_SEGEN_BISHOP);
   end else if (pate == RL_SEGEN_BISHOP) then begin
      call rl_haus_plus(haus, RL_NCR, RL_F_EINFLUSS, 20);
      call rl_nr_misstrauen(welt, RL_SEGEN_SALVATORE);
   end else if (pate == RL_SEGEN_UNABHAENGIG) then begin
      haus[rl_idx(h, RL_F_TRIBUTMOD)] := haus[rl_idx(h, RL_F_TRIBUTMOD)] - 20;        // kein Tribut
      call rl_haus_plus(haus, h, RL_F_HITZE, 20);
      welt[RL_W_NR_MISSTRAUEN] := welt[RL_W_NR_MISSTRAUEN] bwor rl_bit(RL_SEGEN_MORDINO)
                                  bwor rl_bit(RL_SEGEN_WRIGHT) bwor rl_bit(RL_SEGEN_SALVATORE)
                                  bwor rl_bit(RL_SEGEN_BISHOP);
   end
end

procedure rl_nr_besitz(variable haus) begin
   return haus[rl_idx(RL_NEW_RENO, RL_F_BESITZ)];
end

// Die Witwe wartet im Hotel, bis die Urkunde weg ist, und kommt wieder, wenn die Faelschung auffliegt
procedure rl_nr_witwe_da(variable welt) begin
   if (welt[RL_W_NR_TOTE] bwand RL_NR_TOT_WITWE) then return 0;
   return ((welt[RL_W_NR_URKUNDE] == RL_URKUNDE_KEINE) or (welt[RL_W_NR_WITWE] == RL_WITWE_FORDERT));
end

// Pagano sitzt im Hotel, bis das Haus vergeben ist (nicht waehrend der Eroeffnungsnacht)
procedure rl_nr_fixer_da(variable haus, variable welt) begin
   if (welt[RL_W_NR_TOTE] bwand RL_NR_TOT_FIXER) then return 0;
   if (rl_nr_besitz(haus)) then return 0;
   return (welt[RL_W_NR_EROEFFNUNG] != RL_EROEFFNUNG_KAMPF);
end

/* Figuren im Strumpfband nach dem Stand der Dinge (Kartenskript, nach der Uebernahme).
   Wer gehen muss, geht selbst (map_enter_p_proc der Figur). */
procedure rl_nr_figuren(variable haus, variable welt) begin
   if (rl_nr_witwe_da(welt)) then
      call rl_figur(PID_WEAK_PEASANT_FEMALE, rl_haus_platz(RL_NEW_RENO, RL_PLATZ_GAST1), SCRIPT_RLWITWE);
   if (rl_nr_fixer_da(haus, welt)) then
      call rl_figur(PID_AVERAGE_PEASANT_MALE, rl_haus_platz(RL_NEW_RENO, RL_PLATZ_GAST2), SCRIPT_RLFIXER);
   if (rl_nr_besitz(haus)) then begin
      if ((welt[RL_W_NR_TOTE] bwand RL_NR_TOT_ROZ) == 0) then
         call rl_figur(PID_AVERAGE_PEASANT_FEMALE, rl_haus_platz(RL_NEW_RENO, RL_PLATZ_MADAME), SCRIPT_RLROZ);
      if ((welt[RL_W_NR_TOTE] bwand RL_NR_TOT_ASCH) == 0) then
         call rl_figur(PID_WEAK_PEASANT_MALE, rl_haus_platz(RL_NEW_RENO, RL_PLATZ_GAST3), SCRIPT_RLCONSIG);
   end
end

/* ------------------------------------------------------------------ */
/* Familientreffen (Phase 1, Ansatz C): alle vier Wochen ab Hausklasse 3 */
/* ------------------------------------------------------------------ */

// Die Fuenfte Familie (Phase 6): Checks bei den Familientreffen +10
procedure rl_treffen_bonus begin
   if (global_var(GVAR_RL_TITEL_FAMILIE)) then return 10;
   return 0;
end

// Das naechste Thema der Reihe nach; Themen toter Familien entfallen
procedure rl_treffen_thema(variable welt) begin
   variable i := 0, t;
   while (i < RL_TREFFEN_ANZAHL) do begin
      t := (welt[RL_W_TREFFEN_NR] + i) % RL_TREFFEN_ANZAHL + 1;
      if ((t == RL_TREFFEN_SALVATORE) and not rl_salvatore_weg) then return t;
      if ((t == RL_TREFFEN_JET) and (welt[RL_W_JET_VERTRAG] == 0) and not rl_mordino_weg) then return t;
      if ((t == RL_TREFFEN_WRIGHT) and not rl_wright_weg) then return t;
      if ((t == RL_TREFFEN_SHARK) and (welt[RL_W_SHARK_ANTEIL] == 0) and not rl_bishop_weg) then return t;
      if (t == RL_TREFFEN_LAEUFER) then return t;
      i := i + 1;
   end
   return RL_TREFFEN_LAEUFER;
end

procedure rl_treffen_ende(variable welt) begin
   welt[RL_W_TREFFEN_OFFEN] := RL_TREFFEN_KEINS;
   welt[RL_W_TREFFEN_NR]    := welt[RL_W_TREFFEN_NR] + 1;
   welt[RL_W_TREFFEN_WOCHE] := rl_woche_jetzt + RL_TREFFEN_ABSTAND;
end

// Niemand sass fuer den Spieler am Tisch: die Folgen des Nein, ohne das Nein
procedure rl_treffen_verpasst(variable haus, variable welt) begin
   variable t := welt[RL_W_TREFFEN_OFFEN];
   if (t == RL_TREFFEN_SALVATORE) then begin
      call rl_nr_misstrauen(welt, RL_SEGEN_SALVATORE);
      call rl_haus_plus(haus, RL_NEW_RENO, RL_F_HITZE, 20);
      haus[rl_idx(RL_NEW_RENO, RL_F_KASSE)] := haus[rl_idx(RL_NEW_RENO, RL_F_KASSE)] - RL_SALVATORE_SCHADEN;
   end else if (t == RL_TREFFEN_JET) then
      call rl_nr_misstrauen(welt, RL_SEGEN_MORDINO);
   else if (t == RL_TREFFEN_WRIGHT) then
      call rl_nr_misstrauen(welt, RL_SEGEN_WRIGHT);
   else if (t == RL_TREFFEN_LAEUFER) then
      welt[RL_W_HQ_KASSE] := rl_max(0, welt[RL_W_HQ_KASSE] - RL_LAEUFER_BEUTE);
   welt[RL_W_TREFFEN_OFFEN] := RL_TREFFEN_KEINS;
   welt[RL_W_TREFFEN_NR]    := welt[RL_W_TREFFEN_NR] + 1;
   welt[RL_W_TREFFEN_WOCHE] := rl_woche_jetzt + RL_TREFFEN_ABSTAND;
end

// Bezahlt wird zuerst aus der HQ-Kasse, der Rest aus der Tasche des Spielers
procedure rl_hq_zahlbar(variable welt, variable kosten) begin
   return (rl_max(0, welt[RL_W_HQ_KASSE]) + item_caps_total(dude_obj) >= kosten);
end

procedure rl_hq_zahlen(variable welt, variable kosten) begin
   variable aus_kasse := rl_min(rl_max(0, welt[RL_W_HQ_KASSE]), kosten);
   welt[RL_W_HQ_KASSE] := welt[RL_W_HQ_KASSE] - aus_kasse;
   if (kosten > aus_kasse) then
      item_caps_adjust(dude_obj, -(kosten - aus_kasse));
end

#endif
